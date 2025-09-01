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
                    
                    logger.warning(f"Could not refresh Facebook token for company {company_id}")
                    return None
            
            return credentials
            
        except Exception as e:
            logger.error(f"Error refreshing Facebook token for company {company_id}: {str(e)}")
            return None

    async def _get_facebook_messages(self, credentials: Dict[str, Any], page_id: str) -> List[Dict[str, Any]]:
        """Get Facebook messages from a page."""
        try:
            page_access_token = credentials.get('page_access_token')
            if not page_access_token:
                logger.error("No page access token found in Facebook credentials")
                return []

            # Get messages from page conversations
            messages_data = await facebook_auth_service.get_page_messages(page_id, page_access_token, limit=10)
            if not messages_data:
                return []

            messages = []
            for conversation in messages_data.get('data', []):
                conversation_messages = conversation.get('messages', {}).get('data', [])
                for message in conversation_messages:
                    messages.append({
                        'id': message.get('id'),
                        'text': message.get('message'),
                        'from': message.get('from', {}).get('name'),
                        'from_id': message.get('from', {}).get('id'),
                        'created_time': message.get('created_time'),
                        'conversation_id': conversation.get('id'),
                        'type': 'message'
                    })
            
            return messages
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting Facebook messages: {str(e)}")
            return []

    async def _get_facebook_comments(self, credentials: Dict[str, Any], page_id: str) -> List[Dict[str, Any]]:
        """Get Facebook comments from page posts."""
        try:
            page_access_token = credentials.get('page_access_token')
            if not page_access_token:
                logger.error("No page access token found in Facebook credentials")
                return []

            # Get comments from recent posts
            posts_data = await facebook_auth_service.get_page_posts(page_id, page_access_token, limit=5)
            if not posts_data:
                return []

            comments = []
            for post in posts_data.get('data', []):
                post_id = post.get('id')
                post_comments = post.get('comments', {}).get('data', [])
                
                for comment in post_comments:
                    comments.append({
                        'id': comment.get('id'),
                        'text': comment.get('message'),
                        'from': comment.get('from', {}).get('name'),
                        'from_id': comment.get('from', {}).get('id'),
                        'created_time': comment.get('created_time'),
                        'post_id': post_id,
                        'post_message': post.get('message'),
                        'type': 'comment'
                    })
            
            return comments
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting Facebook comments: {str(e)}")
            return []

    async def _process_facebook_message(self, message: Dict[str, Any], company: Company, db: Session) -> None:
        """Process a single Facebook message and save to database."""
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

            # Check if we should reply to this message
            if not should_reply_to_facebook_message(message.get('from_id'), message.get('text', ''), settings, company.facebook_box_page_id):
                return

            # Filter message using AI
            sender = message.get('from', 'Unknown')
            content = message.get('text', '')
            
            if not await filter_email_with_ai(sender, content):
                logger.info(f"Facebook message filtered out by AI: {message_id}")
                return

            # Analyze message for action requirement
            ai_service = SimpleAIService()
            action_analysis = await ai_service.analyze_message_for_action_requirement(
                sender=sender,
                content=content,
                company_goals=company.goal,
                company_category=company.business_category,
                company_id=company.id
            )

            # Create chat record
            created_time = message.get('created_time')
            if created_time:
                try:
                    sent_at = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                except ValueError:
                    sent_at = datetime.now(timezone.utc)
            else:
                sent_at = datetime.now(timezone.utc)

            chat = Chat(
                company_id=company.id,
                channel_id=message.get('conversation_id') or message.get('post_id', 'facebook'),
                message_id=message_id,
                from_email=sender,
                to_email=company.facebook_box_page_name or '',
                subject=f"Facebook {message.get('type', 'message')}",
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

            # Broadcast new message via WebSocket
            await broadcast_new_email(company_email_ws_clients,company.id, {
                'type': 'new_facebook_message',
                'message': {
                    'id': chat.id,
                    'from': sender,
                    'text': content,
                    'created_time': sent_at.isoformat(),
                    'message_type': message.get('type', 'message'),
                    'notification_read': False
                }
            })

            logger.info(f"Processed Facebook message {message_id} for company {company.id}")

        except Exception as e:
            logger.error(f"Error processing Facebook message: {str(e)}")
            db.rollback()

    async def poll_facebook_messages(self, company_id: int) -> None:
        """Poll Facebook messages for a specific company."""
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

            # Get messages and comments
            messages = await self._get_facebook_messages(refreshed_credentials, page_id)
            comments = await self._get_facebook_comments(refreshed_credentials, page_id)
            
            all_messages = messages + comments

            # Process new messages
            for message in all_messages:
                await self._process_facebook_message(message, company, db)

            logger.info(f"Polled {len(all_messages)} Facebook messages for company {company_id}")

        except Exception as e:
            logger.error(f"Error polling Facebook messages for company {company_id}: {str(e)}")
        finally:
            db.close()

    async def poll_facebook_messages_from_companies(self) -> None:
        """Poll Facebook messages for a specific company."""
        try:
            db = SessionLocal()
            companies = db.query(Company).filter(Company.facebook_box_credentials.isnot(None)).all()
            
            for company in companies:
                company_id = company.id
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

                # Get messages and comments
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
                await asyncio.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"Error in Facebook monitoring loop for company {company_id}: {str(e)}")
                await asyncio.sleep(interval_seconds)

# Create a singleton instance
facebook_monitor_service = FacebookMonitorService()
