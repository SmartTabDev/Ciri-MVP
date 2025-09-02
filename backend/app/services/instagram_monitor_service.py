import logging
import asyncio
import requests
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
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
from app.services.instagram_auth_service import instagram_auth_service
from app.services.facebook_auth_service import facebook_auth_service
from app.services.channel_context_service import channel_context_service
from app.crud.crud_channel_auto_reply_settings import channel_auto_reply_settings 
logger = logging.getLogger(__name__)

GRAPH = "https://graph.instagram.com/v23.0"


def should_reply_to_instagram_message(sender: str, content: str, settings, company_instagram_username: str = None) -> bool:
    # Basic filter; keep as-is from your original code
    if any(w in (content or "").lower() for w in ['buy', 'sell', 'promote', 'advertisement', 'spam']):
        return False
    if company_instagram_username and sender and company_instagram_username.lower() == sender.lower():
        return False
    return bool(content and content.strip())


class InstagramMonitorService:
    def __init__(self):
        # if you later de-dupe by conversation, keep a map here
        self.last_seen_message_ids: Dict[int, str] = {}  # company_id -> last seen message id

    def _get_credentials(self, company: Company, db: Session = None) -> Optional[Dict[str, Any]]:
        if not company.instagram_credentials:
            logger.warning(f"No Instagram credentials found for company {company.id}")
            return None
        try:
            return json.loads(company.instagram_credentials) if isinstance(company.instagram_credentials, str) else company.instagram_credentials
        except (json.JSONDecodeError, TypeError) as e:
            logger.error(f"Error parsing Instagram credentials for company {company.id}: {e}")
            return None

    async def _refresh_token_if_needed(self, credentials: Dict[str, Any], company_id: int) -> Optional[Dict[str, Any]]:
        """
        IG Login uses a **long-lived token** (≈60 days) that you refresh with
        GET /refresh_access_token?grant_type=ig_refresh_token&access_token=<long_token>.
        No separate refresh_token is issued.
        """
        try:
            expires_at = credentials.get('expires_at')
            if expires_at:
                expires_datetime = datetime.fromtimestamp(expires_at, tz=timezone.utc)
                if expires_datetime - datetime.now(timezone.utc) < timedelta(hours=1):
                    logger.info(f"Refreshing Instagram token for company {company_id}")
                    new_token_data = await instagram_auth_service.refresh_instagram_token(credentials.get('access_token'))
                    if new_token_data and new_token_data.get('access_token'):
                        db = SessionLocal()
                        try:
                            company = db.query(Company).filter(Company.id == company_id).first()
                            if company:
                                updated = {**credentials,
                                           'access_token': new_token_data['access_token'],
                                           # if your auth service returns absolute expiry, persist it; else keep old
                                           'expires_at': new_token_data.get('expires_at', expires_at)}
                                company.instagram_credentials = updated
                                db.commit()
                                logger.info(f"Updated Instagram credentials for company {company_id}")
                                return updated
                        finally:
                            db.close()
                    logger.warning(f"Could not refresh Instagram token for company {company_id}")
                    return None
            return credentials
        except Exception as e:
            logger.error(f"Error refreshing Instagram token for company {company_id}: {e}")
            return None

    # ---------- NEW: conversations instead of comments ----------
    async def get_instagram_conversations(self, credentials: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch **DM conversations** + messages using Instagram Login (graph.instagram.com).
        - 1) Resolve IG user id via /me
        - 2) GET /{IG_ID}/conversations
        - 3) For each conversation, GET messages via fields=messages{...}
        Returns a flat list of message dicts (conversation-aware).
        """
        access_token = credentials.get('access_token')
        if not access_token:
            logger.error("No access token found in Instagram credentials")
            return []

        try:
          
            # 2) List conversations with performance limits
            conv_res = requests.get(f"{GRAPH}/me/conversations", params={
                "access_token": access_token,
                "limit": max(1, min(5, limit))  # Limit to 5 conversations for performance
            }, timeout=20)
            conv_res.raise_for_status()
            conversations = conv_res.json().get("data", [])

            messages: List[Dict[str, Any]] = []

            # 3) Load messages for each conversation
            for conv in conversations:
                conv_id = conv.get("id")
                if not conv_id:
                    continue

                # You can use the Graph Conversation node to pull messages
                # Either /{conversation_id}/messages or ?fields=messages{...}
                detail = requests.get(f"{GRAPH}/{conv_id}", params={
                    "fields": "updated_time,participants,messages.limit(3){id,from,to,created_time,message,attachments}",  # Limit to 3 messages per conversation
                    "access_token": access_token
                }, timeout=20)
                if not detail.ok:
                    logger.warning("Failed to fetch conversation %s: %s", conv_id, detail.text)
                    continue
                detail_json = detail.json()
                msgs = (detail_json.get("messages") or {}).get("data", [])

                for m in msgs:
                    text = m.get("message") or m.get("text") or ""
                    sender = (m.get("from") or {}).get("username") or (m.get("from") or {}).get("id")
                    messages.append({
                        "id": m.get("id"),
                        "text": text,
                        "from": sender,
                        "from_id": (m.get("from") or {}).get("id"),
                        "created_time": m.get("created_time"),
                        "conversation_id": conv_id,
                        "type": "dm"
                    })

            return messages

        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting Instagram conversations: {e}")
            return []

    async def _process_instagram_message(self, message: Dict[str, Any], company: Company, db: Session) -> None:
        try:
            message_id = message.get('id')
            if not message_id:
                return

            existing_chat = db.query(Chat).filter(
                Chat.message_id == message_id,
                Chat.company_id == company.id
            ).first()
            if existing_chat:
                return

            if not should_reply_to_instagram_message(message.get('from'), message.get('text', ''), settings, company.instagram_username):
                return

            sender = message.get('from', 'Unknown')
            content = message.get('text', '')

            if not await filter_email_with_ai(sender, content):
                logger.info(f"Instagram DM filtered out by AI: {message_id}")
                return

            ai_service = SimpleAIService()
            action_analysis = await ai_service.analyze_message_for_action_requirement(
                sender=sender,
                content=content,
                company_goals=company.goal,
                company_category=company.business_category,
                company_id=company.id
            )

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
                channel_id=message.get('conversation_id', 'instagram'),
                message_id=message_id,
                from_email=sender,
                to_email=company.instagram_username or '',
                subject="Instagram DM",
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

            # Check if we should send AI reply
            if not action_analysis.get('action_required', False):
                # Check channel auto-reply settings
                channel_settings = channel_auto_reply_settings.get_by_channel_id(db, channel_id=message.get('conversation_id', 'instagram'))
                if channel_settings and not channel_settings.enable_auto_reply:
                    logger.info(f"Auto-reply disabled for Instagram channel {message.get('conversation_id', 'instagram')}")
                else:
                    # Check if we should reply (no recent outgoing message)
                    last_outgoing = db.query(Chat).filter_by(
                        company_id=company.id, 
                        channel_id=message.get('conversation_id', 'instagram'),
                        from_email=company.instagram_username
                    ).order_by(Chat.sent_at.desc()).first()
                    
                    should_reply = not last_outgoing or (last_outgoing and last_outgoing.sent_at < sent_at)
                    if should_reply:
                        await self._send_ai_reply_to_instagram(message, company, db, sender, content)

            await broadcast_new_email(company_email_ws_clients, company.id, {
                'type': 'new_instagram_message',
                'message': {
                    'id': chat.id,
                    'from': sender,
                    'text': content,
                    'created_time': sent_at.isoformat(),
                    'message_type': 'dm',
                    'notification_read': False
                }
            })

            logger.info(f"Processed Instagram DM {message_id} for company {company.id}")

        except Exception as e:
            logger.error(f"Error processing Instagram DM: {e}")
            db.rollback()

    async def _send_ai_reply_to_instagram(self, message: Dict[str, Any], company: Company, db: Session, sender: str, content: str) -> None:
        """Send AI-generated reply to Instagram message.
        Attempts to send via the connected Facebook Page's Send API (Instagram Messaging).
        Falls back to storing the AI reply if sending fails or configuration is missing."""
        try:
            ai_service = SimpleAIService()
            
            # Generate AI reply
            reply_text = await ai_service.generate_email_reply(
                sender=sender,
                content=content,
                company_id=company.id,
                channel_id=message.get('conversation_id', 'instagram')
            )

            # Attempt to send via the connected Facebook Page (Instagram Messaging Send API)
            sent_successfully = False
            sent_message_id = None
            try:
                # Prefer Facebook page ID configured during FB auth; fallback to instagram_page_id if present
                page_id = getattr(company, 'facebook_box_page_id', None) or getattr(company, 'instagram_page_id', None)
                page_access_token = None
                if getattr(company, 'facebook_box_credentials', None):
                    fb_creds = company.facebook_box_credentials
                    if isinstance(fb_creds, str):
                        import json as _json
                        try:
                            fb_creds = _json.loads(fb_creds)
                        except Exception:
                            fb_creds = None
                    if isinstance(fb_creds, dict):
                        page_access_token = fb_creds.get('page_access_token')

                # Recipient IG Scoped User ID extracted when fetching messages
                recipient_id = message.get('from_id') or (message.get('from') or {}).get('id')

                if page_id and page_access_token and recipient_id:
                    result = await facebook_auth_service.send_page_message(
                        page_id=page_id,
                        page_access_token=page_access_token,
                        recipient_id=recipient_id,
                        message=reply_text
                    )
                    if result:
                        sent_successfully = True
                        sent_message_id = (result.get('message_id') if isinstance(result, dict) else None) or f"reply-{message.get('id')}"
                        logger.info(f"Instagram reply sent via Page API to recipient {recipient_id}")
                else:
                    logger.warning("Instagram send skipped: missing page_id, page_access_token, or recipient_id")
            except Exception as send_err:
                logger.error(f"Error sending Instagram reply via Page API: {send_err}")

            # Mark original message as replied
            original_chat = db.query(Chat).filter(
                Chat.message_id == message.get('id'),
                Chat.company_id == company.id
            ).first()
            if original_chat:
                original_chat.replied = True
                db.add(original_chat)

            # Store reply in database (sent or prepared)
            reply_chat = Chat(
                company_id=company.id,
                channel_id=message.get('conversation_id', 'instagram'),
                message_id=sent_message_id or f"ai-reply-{message.get('id')}",
                from_email=company.instagram_username or '',
                to_email=sender,
                subject="Instagram AI Reply",
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
                email_provider='instagram'
            )
            db.add(reply_chat)
            db.commit()

            # Store in channel context
            channel_context_service.store_message_in_context(db, reply_chat)
            
            if sent_successfully:
                logger.info(f"Sent AI reply for Instagram message {message.get('id')}")
            else:
                logger.info(f"Prepared AI reply for Instagram message {message.get('id')} (not sent automatically)")

        except Exception as e:
            logger.error(f"Error generating AI reply for Instagram: {str(e)}")

    async def poll_instagram_messages(self, company_id: int) -> None:
        """Poll Instagram **DMs** for a specific company."""
        db = None
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

            refreshed_credentials = await self._refresh_token_if_needed(credentials, company_id)
            if not refreshed_credentials:
                logger.error(f"Could not refresh Instagram token for company {company_id}")
                return

            # Fetch **conversations/messages** with performance limits
            messages = await self.get_instagram_conversations(refreshed_credentials, limit=5)

            for message in messages:
                await self._process_instagram_message(message, company, db)

            logger.info(f"Polled {len(messages)} Instagram DMs for company {company_id}")

        except Exception as e:
            logger.error(f"Error polling Instagram DMs for company {company_id}: {e}")
        finally:
            if db:
                db.close()

    async def poll_instagram_messages_from_companies(self) -> None:
        """Poll Instagram DMs for all companies."""
        db = None
        try:
            db = SessionLocal()
            for company in db.query(Company).all():
                await self.poll_instagram_messages(company.id)
        except Exception as e:
            logger.error(f"Error polling Instagram DMs from companies: {e}")
        finally:
            if db:
                db.close()

    async def start_monitoring(self, company_id: int, interval_seconds: int = 60) -> None:
        logger.info(f"Starting Instagram DM monitoring for company {company_id}")
        while True:
            try:
                await self.poll_instagram_messages(company_id)
            except Exception as e:
                logger.error(f"Error in Instagram monitoring loop for company {company_id}: {e}")
            await asyncio.sleep(interval_seconds)


# Singleton
instagram_monitor_service = InstagramMonitorService()
