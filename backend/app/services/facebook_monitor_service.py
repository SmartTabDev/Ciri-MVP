import logging
import asyncio
import requests
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from pathlib import Path
import json
import sys

sys.path.append('.')
from app.models.company import Company
from app.db.session import SessionLocal
from app.core.config import settings
from app.core.ws_clients import company_email_ws_clients
from app.core.broadcast import broadcast_new_email
from app.services.ai_service import SimpleAIService, filter_email_with_ai
from app.models.chat import Chat
from app.crud.crud_channel_auto_reply_settings import channel_auto_reply_settings
from app.services.channel_context_service import channel_context_service
from app.services.facebook_auth_service import facebook_auth_service

logger = logging.getLogger(__name__)

def should_reply_to_facebook_message(sender: str, content: str, settings, company_facebook_page_id: str = None) -> bool:
    """
    Check if a Facebook message should be replied to based on filtering criteria.
    
    Args:
        sender: Facebook user ID or name
        content: Message content
        settings: Application settings
        company_facebook_page_id: Company's Facebook page ID
    
    Returns:
        bool: True if message should be replied to, False otherwise
    """
    # Don't reply if message content contains spam indicators
    if any(spam_word in content.lower() for spam_word in ['buy', 'sell', 'promote', 'advertisement', 'spam']):
        return False
    
    # Don't reply if sender is the company's own Facebook page
    if company_facebook_page_id and company_facebook_page_id == sender:
        return False
    
    # Don't reply to empty messages
    if not content or not content.strip():
        return False
    
    return True

class FacebookMonitorService:
    def __init__(self):
        self.last_seen_message_ids = {}  # company_id -> last seen Facebook message ID
        self.last_seen_comment_ids = {}  # company_id -> last seen Facebook comment ID

    def _get_credentials(self, company: Company, db: Session = None) -> Optional[Dict[str, Any]]:
        """Get Facebook credentials for a company."""
        if not company.facebook_box_credentials:
            logger.warning(f"No Facebook credentials found for company {company.id}")
            return None
        
        try:
            credentials = json.loads(company.facebook_box_credentials) if isinstance(company.facebook_box_credentials, str) else company.facebook_box_credentials
            return credentials
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Error parsing Facebook credentials for company {company.id}: {str(e)}")
            return None

    async def _refresh_token_if_needed(self, credentials: Dict[str, Any], company_id: int) -> Optional[Dict[str, Any]]:
        """Refresh Facebook token if it's expired or about to expire."""
        try:
            expires_at = credentials.get('expires_at')
            if expires_at:
                expires_datetime = datetime.fromtimestamp(expires_at, tz=timezone.utc)
                # Refresh if token expires in less than 1 hour
                if expires_datetime - datetime.now(timezone.utc) < timedelta(hours=1):
                    logger.info(f"Refreshing Facebook token for company {company_id}")
                    
                    new_token_data = await facebook_auth_service.refresh_facebook_token(
                        credentials.get('access_token')
                    )
                    if new_token_data:
                        # Update credentials in database
                        db = SessionLocal()
                        try:
                            company = db.query(Company).filter(Company.id == company_id).first()
                            if company:
                                updated_credentials = {
                                    **credentials,
                                    'access_token': new_token_data.get('access_token'),
                                    'expires_at': new_token_data.get('expires_at', expires_at)
                                }
                                company.facebook_box_credentials = updated_credentials
                                db.commit()
                                logger.info(f"Updated Facebook credentials for company {company_id}")
                                return updated_credentials
                        finally:
                            db.close()
                    
            return credentials
            
        except Exception as e:
            logger.error(f"Error refreshing Facebook token for company {company_id}: {str(e)}")
            return credentials

    async def _get_facebook_messages(self, credentials: Dict[str, Any], page_id: str) -> List[Dict[str, Any]]:
        """
        Fetch conversations from a page and FLATTEN to message-level dicts.
        Each returned dict contains:
        - id, message, from, created_time (original fields)
        - conversation_id (thread id)
        - participants (list of {id, name, email} for the thread)
        """
        try:
            page_access_token = credentials.get('page_access_token')
            if not page_access_token:
                logger.warning(f"No page access token for Facebook page {page_id}")
                return []

            # Keep the conversations page small for performance; you can bump if desired.
            conversations = await facebook_auth_service.get_page_messages(
                page_id, page_access_token, limit=5
            )
            if not conversations or not conversations.get('data'):
                return []

            flattened: List[Dict[str, Any]] = []
            for conv in conversations.get('data', []):
                conv_id = conv.get('id')
                participants = (conv.get('participants') or {}).get('data', []) or []

                # Messages included in the conversation payload (first page)
                msgs = (conv.get('messages') or {}).get('data', []) or []
                for m in msgs:
                    # Attach context so downstream code knows the thread + participants
                    enriched = {
                        **m,
                        "conversation_id": conv_id,
                        "participants": participants,
                    }
                    flattened.append(enriched)

                # If you want to page deeper within EACH conversation, uncomment this block:
                # after = ((conv.get('messages') or {}).get('paging') or {}).get('cursors', {}).get('after')
                # pulls = 1
                # MAX_PULLS_PER_CONV = 2  # keep it light; tune as needed
                # while after and pulls <= MAX_PULLS_PER_CONV:
                #     more = await facebook_auth_service.get_conversation_messages(conv_id, page_access_token, after=after, limit=25)
                #     data = (more or {}).get('data', [])
                #     for m in data:
                #         enriched = {**m, "conversation_id": conv_id, "participants": participants}
                #         flattened.append(enriched)
                #     after = ((more or {}).get('paging') or {}).get('cursors', {}).get('after')
                #     pulls += 1

            logger.info(f"Flattened {len(flattened)} messages from {len(conversations.get('data', []))} conversations")
            return flattened

        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting Facebook messages: {str(e)}")
            return []

    
    async def _get_facebook_comments(self, credentials: Dict[str, Any], page_id: str) -> List[Dict[str, Any]]:
        """Get Facebook comments for a page with performance limits."""
        try:
            page_access_token = credentials.get('page_access_token')
            if not page_access_token:
                logger.warning(f"No page access token for Facebook page {page_id}")
                return []

            # Limit to 5 comments for performance
            posts = await facebook_auth_service.get_page_posts(page_id, page_access_token, limit=5)
            if posts and posts.get('data'):
                all_comments = []
                for post in posts['data']:
                    if post.get('comments') and post['comments'].get('data'):
                        # Limit to 3 comments per post for performance
                        post_comments = post['comments']['data'][:3]
                        for comment in post_comments:
                            comment['post_id'] = post['id']
                            comment['type'] = 'comment'
                        all_comments.extend(post_comments)
                return all_comments
            return []

        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting Facebook comments: {str(e)}")
            return []

    async def _process_facebook_message(self, message: Dict[str, Any], company: Company, db: Session) -> None:
        """Process a Facebook message and send AI reply if needed."""
        try:
            message_id = message.get('id')
            if not message_id:
                return
        
            # Check if message already exists
            existing_chat = db.query(Chat).filter(
                Chat.message_id == message_id,
                Chat.company_id == company.id
            ).first()
            if existing_chat:
                return
            
            # Determine message type and content
            message_type = message.get('type', 'message')
            if message_type == 'comment':
                content = message.get('message', '')
                sender = message.get('from', {}).get('name', 'Unknown')
                conversation_id = f"post_{message.get('post_id', 'unknown')}"
            else:
                content = message.get('message', '')
                sender = message.get('from', {}).get('name', 'Unknown')
                conversation_id = message.get('conversation_id', 'facebook')

            # Apply filtering
            if not should_reply_to_facebook_message(sender, content, settings, company.facebook_box_page_id):
                return

            # AI filtering
            if not await filter_email_with_ai(sender, content):
                logger.info(f"Facebook message filtered out by AI: {message_id}")
                return

            # AI action analysis
            ai_service = SimpleAIService()
            action_analysis = await ai_service.analyze_message_for_action_requirement(
                sender=sender,
                content=content,
                company_goals=company.goal,
                company_category=company.business_category,
                company_id=company.id
            )

            # Parse timestamp
            created_time = message.get('created_time')
            if created_time:
                try:
                    sent_at = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                except ValueError:
                    sent_at = datetime.now(timezone.utc)
            else:
                sent_at = datetime.now(timezone.utc)

            # Store message in database
            chat = Chat(
                company_id=company.id,
                channel_id=conversation_id,
                message_id=message_id,
                from_email=sender,
                to_email=company.facebook_box_page_name or '',
                subject=f"Facebook {message_type.title()}",
                body_text=content,
                body_html=content,
                sent_at=sent_at,
                is_read=False,
                notification_read=False,
                replied=False,
                action_required=action_analysis.get('action_required', False),
                action_reason=action_analysis.get('reason', ''),
                action_type=action_analysis.get('action_type', 'none'),
                urgency=action_analysis.get('urgency', 'none'),
                email_provider='facebook'
            )

            db.add(chat)
            db.commit()

            # Check if we should send AI reply
            if not action_analysis.get('action_required', False):
                # Check channel auto-reply settings
                channel_settings = channel_auto_reply_settings.get_by_channel_id(db, channel_id=conversation_id)
                if channel_settings and not channel_settings.enable_auto_reply:
                    logger.info(f"Auto-reply disabled for Facebook channel {conversation_id}")
                else:
                    # Check if we should reply (no recent outgoing message)
                    last_outgoing = db.query(Chat).filter_by(
                        company_id=company.id, 
                        channel_id=conversation_id,
                        from_email=company.facebook_box_page_name
                    ).order_by(Chat.sent_at.desc()).first()
                    
                    should_reply = not last_outgoing or (last_outgoing and last_outgoing.sent_at < sent_at)
                    if should_reply:
                        await self._send_ai_reply_to_facebook(message, company, db, conversation_id, sender, content)

            # Broadcast to frontend
            await broadcast_new_email(company_email_ws_clients, company.id, {
                'type': 'new_facebook_message',
                'message': {
                    'id': chat.id,
                    'from': sender,
                    'text': content,
                    'created_time': sent_at.isoformat(),
                    'message_type': message_type,
                    'notification_read': False
                }
            })

            logger.info(f"Processed Facebook message {message_id} for company {company.id}")

        except Exception as e:
            logger.error(f"Error processing Facebook message: {str(e)}")
            db.rollback()

    async def _send_ai_reply_to_facebook(self, message: Dict[str, Any], company: Company, db: Session, conversation_id: str, sender: str, content: str) -> None:
        """Send AI-generated reply to Facebook message."""
        try:
            ai_service = SimpleAIService()
            
            # Generate AI reply
            reply_text = await ai_service.generate_email_reply(
                sender=sender,
                content=content,
                company_id=company.id,
                channel_id=conversation_id
            )

            # Send reply via Facebook API
            page_id = company.facebook_box_page_id
            page_access_token = None
            
            if company.facebook_box_credentials:
                credentials = json.loads(company.facebook_box_credentials) if isinstance(company.facebook_box_credentials, str) else company.facebook_box_credentials
                page_access_token = credentials.get('page_access_token')

            if page_access_token and page_id:
                # Get recipient ID from message
                recipient_id = message.get('from', {}).get('id')
                if recipient_id:
                    # Send message via Facebook API
                    result = await facebook_auth_service.send_page_message(
                        page_id=page_id,
                        page_access_token=page_access_token,
                        recipient_id=recipient_id,
                        message=reply_text
                    )
                    
                    if result:
                        # Mark original message as replied
                        original_chat = db.query(Chat).filter(
                            Chat.message_id == message.get('id'),
                            Chat.company_id == company.id
                        ).first()
                        if original_chat:
                            original_chat.replied = True
                            db.add(original_chat)

                        # Store reply in database
                        reply_chat = Chat(
                            company_id=company.id,
                            channel_id=conversation_id,
                            message_id=f"reply-{message.get('id')}",
                            from_email=company.facebook_box_page_name or '',
                            to_email=sender,
                            subject="Facebook Reply",
                            body_text=reply_text,
                            body_html=reply_text,
                            sent_at=datetime.now(timezone.utc),
                            is_read=True,
                            notification_read=False,
                            replied=False,
                            action_required=False,
                            action_reason='',
                            action_type='',
                            urgency='',
                            email_provider='facebook'
                        )
                        db.add(reply_chat)
                        db.commit()

                        # Store in channel context
                        channel_context_service.store_message_in_context(db, reply_chat)
                        
                        logger.info(f"Sent AI reply to Facebook message {message.get('id')}")
                    else:
                        logger.error(f"Failed to send Facebook reply to message {message.get('id')}")
                else:
                    logger.warning(f"No recipient ID found for Facebook message {message.get('id')}")
            else:
                logger.warning(f"No Facebook page access token for company {company.id}")

        except Exception as e:
            logger.error(f"Error sending AI reply to Facebook: {str(e)}")

    async def poll_facebook_messages(self, company_id: int) -> None:
        """Poll Facebook messages for a specific company with performance limits."""
        db = None
        try:
            db = SessionLocal()
            company = db.query(Company).filter(Company.id == company_id).first()
            if not company:
                logger.warning(f"Company {company_id} not found")
                return

            credentials = self._get_credentials(company, db)
            if not credentials:
                logger.warning(f"No Facebook credentials for company {company_id}")
                return

            # Refresh token if needed
            refreshed_credentials = await self._refresh_token_if_needed(credentials, company_id)
            if not refreshed_credentials:
                logger.error(f"Could not refresh Facebook token for company {company_id}")
                return

            # Get Facebook page ID
            page_id = company.facebook_box_page_id
            if not page_id:
                logger.warning(f"No Facebook page ID for company {company_id}")
                return

            # Get messages (flattened from conversations) and comments with limits
            messages = await self._get_facebook_messages(refreshed_credentials, page_id)  # flattened
            comments = await self._get_facebook_comments(refreshed_credentials, page_id)

            all_items = messages + comments

            # Process new items
            for item in all_items:
                await self._process_facebook_message(item, company, db)

            logger.info(f"Polled {len(all_items)} Facebook items for company {company_id}")

        except Exception as e:
            logger.error(f"Error polling Facebook messages for company {company_id}: {str(e)}")
        finally:
            if db is not None:
                db.close()


    async def poll_facebook_messages_from_companies(self) -> None:
        """Poll Facebook messages for all companies with performance limits."""
        try:
            db = SessionLocal()
            companies = db.query(Company).filter(Company.facebook_box_credentials.isnot(None)).all()
            
            for company in companies:
                company_id = company.id
                credentials = self._get_credentials(company, db)
                if not credentials:
                    logger.warning(f"No Facebook credentials for company {company_id}")
                    continue

                # Refresh token if needed
                refreshed_credentials = await self._refresh_token_if_needed(credentials, company_id)
                if not refreshed_credentials:
                    logger.error(f"Could not refresh Facebook token for company {company_id}")
                    continue

                # Get Facebook page ID
                page_id = company.facebook_box_page_id
                if not page_id:
                    logger.warning(f"No Facebook page ID for company {company_id}")
                    continue

                # Get messages and comments with limits
                messages = await self._get_facebook_messages(refreshed_credentials, page_id)
                comments = await self._get_facebook_comments(refreshed_credentials, page_id)
                
                all_messages = messages + comments

                # Process new messages
                for message in all_messages:
                    await self._process_facebook_message(message, company, db)

                logger.info(f"Polled {len(all_messages)} Facebook messages for company {company_id}")

        except Exception as e:
            logger.error(f"Error polling Facebook messages for companies : {str(e)}")
        finally:
            db.close()

    async def start_monitoring(self, company_id: int, interval_seconds: int = 60) -> None:
        """Start monitoring Facebook messages for a company."""
        logger.info(f"Starting Facebook monitoring for company {company_id}")
        
        while True:
            try:
                await self.poll_facebook_messages(company_id)
            except Exception as e:
                logger.error(f"Error in Facebook monitoring loop for company {company_id}: {str(e)}")
            await asyncio.sleep(interval_seconds)

# Singleton instance
facebook_monitor_service = FacebookMonitorService()
