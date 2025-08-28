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
from app.services.instagram_auth_service import instagram_auth_service

logger = logging.getLogger(__name__)

def should_reply_to_instagram_message(sender: str, content: str, settings, company_instagram_username: str = None) -> bool:
    """
    Check if an Instagram message should be replied to based on filtering criteria.
    
    Args:
        sender: Instagram username
        content: Message content
        settings: Application settings
        company_instagram_username: Company's Instagram username
    
    Returns:
        bool: True if message should be replied to, False otherwise
    """
    # Don't reply if message content contains spam indicators
    if any(spam_word in content.lower() for spam_word in ['buy', 'sell', 'promote', 'advertisement', 'spam']):
        return False
    
    # Don't reply if sender is the company's own Instagram account
    if company_instagram_username and company_instagram_username.lower() == sender.lower():
        return False
    
    # Don't reply to empty messages
    if not content or not content.strip():
        return False
    
    return True

class InstagramMonitorService:
    def __init__(self):
        self.last_seen_comment_ids = {}  # company_id -> last seen Instagram comment ID

    def _get_credentials(self, company: Company, db: Session = None) -> Optional[Dict[str, Any]]:
        """Get Instagram credentials for a company."""
        if not company.instagram_credentials:
            logger.warning(f"No Instagram credentials found for company {company.id}")
            return None
        
        try:
            credentials = json.loads(company.instagram_credentials) if isinstance(company.instagram_credentials, str) else company.instagram_credentials
            return credentials
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Error parsing Instagram credentials for company {company.id}: {str(e)}")
            return None

    async def _refresh_token_if_needed(self, credentials: Dict[str, Any], company_id: int) -> Optional[Dict[str, Any]]:
        """Refresh Instagram token if it's expired or about to expire."""
        try:
            expires_at = credentials.get('expires_at')
            if expires_at:
                expires_datetime = datetime.fromtimestamp(expires_at, tz=timezone.utc)
                # Refresh if token expires in less than 1 hour
                if expires_datetime - datetime.now(timezone.utc) < timedelta(hours=1):
                    logger.info(f"Refreshing Instagram token for company {company_id}")
                    
                    if credentials.get('refresh_token'):
                        new_token_data = await instagram_auth_service.refresh_instagram_token(
                            credentials['refresh_token']
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
                                    company.instagram_credentials = updated_credentials
                                    db.commit()
                                    logger.info(f"Updated Instagram credentials for company {company_id}")
                                    return updated_credentials
                            finally:
                                db.close()
                    
                    logger.warning(f"Could not refresh Instagram token for company {company_id}")
                    return None
            
            return credentials
            
        except Exception as e:
            logger.error(f"Error refreshing Instagram token for company {company_id}: {str(e)}")
            return None

    async def get_instagram_messages(self, credentials: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """Get Instagram comments for the authenticated user's media."""
        try:
            access_token = credentials.get('access_token')
            if not access_token:
                logger.error("No access token found in Instagram credentials")
                return []

            # Get user's media with comments
            url = "https://graph.instagram.com/me/media"
            params = {
                "fields": "id,caption,comments{id,text,from,created_time},timestamp",
                "access_token": access_token,
                "limit": limit
            }

            response = requests.get(url, params=params)
            response.raise_for_status()
            
            media_data = response.json()
            messages = []
            
            for media in media_data.get('data', []):
                media_id = media.get('id')
                comments = media.get('comments', {}).get('data', [])
                
                for comment in comments:
                    messages.append({
                        'id': comment.get('id'),
                        'text': comment.get('text'),
                        'from': comment.get('from', {}).get('username'),
                        'from_id': comment.get('from', {}).get('id'),
                        'created_time': comment.get('created_time'),
                        'media_id': media_id,
                        'media_caption': media.get('caption'),
                        'type': 'comment'
                    })
            
            return messages
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting Instagram messages: {str(e)}")
            return []

    async def _process_instagram_message(self, message: Dict[str, Any], company: Company, db: Session) -> None:
        """Process a single Instagram message and save to database."""
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
            if not should_reply_to_instagram_message(message.get('from'), message.get('text', ''), settings, company.instagram_username):
                return

            # Filter message using AI
            sender = message.get('from', 'Unknown')
            content = message.get('text', '')
            
            if not await filter_email_with_ai(sender, content):
                logger.info(f"Instagram message filtered out by AI: {message_id}")
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
                channel_id=message.get('media_id', 'instagram'),
                message_id=message_id,
                from_email=sender,
                to_email=company.instagram_username or '',
                subject=f"Instagram comment",
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
                email_provider='instagram'
            )

            db.add(chat)
            db.commit()

            # Broadcast new message via WebSocket
            await broadcast_new_email(company.id, {
                'type': 'new_instagram_message',
                'message': {
                    'id': chat.id,
                    'from': sender,
                    'text': content,
                    'created_time': sent_at.isoformat(),
                    'message_type': 'comment',
                    'notification_read': False
                }
            })

            logger.info(f"Processed Instagram message {message_id} for company {company.id}")

        except Exception as e:
            logger.error(f"Error processing Instagram message: {str(e)}")
            db.rollback()

    async def poll_instagram_messages(self, company_id: int) -> None:
        """Poll Instagram messages for a specific company."""
        try:
            db = SessionLocal()
            company = db.query(Company).filter(Company.id == company_id).first()
            
            if not company:
                logger.warning(f"Company {company_id} not found")
                return

            credentials = self._get_credentials(company, db)
            if not credentials:
                logger.warning(f"No Instagram credentials for company {company_id}")
                return

            # Refresh token if needed
            refreshed_credentials = await self._refresh_token_if_needed(credentials, company_id)
            if not refreshed_credentials:
                logger.error(f"Could not refresh Instagram token for company {company_id}")
                return

            # Get messages (comments)
            messages = await self.get_instagram_messages(refreshed_credentials, limit=10)

            # Process new messages
            for message in messages:
                await self._process_instagram_message(message, company, db)

            logger.info(f"Polled {len(messages)} Instagram messages for company {company_id}")

        except Exception as e:
            logger.error(f"Error polling Instagram messages for company {company_id}: {str(e)}")
        finally:
            db.close()

    async def start_monitoring(self, company_id: int, interval_seconds: int = 60) -> None:
        """Start monitoring Instagram messages for a company."""
        logger.info(f"Starting Instagram monitoring for company {company_id}")
        
        while True:
            try:
                await self.poll_instagram_messages(company_id)
                await asyncio.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"Error in Instagram monitoring loop for company {company_id}: {str(e)}")
                await asyncio.sleep(interval_seconds)

# Create a singleton instance
instagram_monitor_service = InstagramMonitorService()
