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
          
            # 2) List conversations
            conv_res = requests.get(f"{GRAPH}/me/conversations", params={
                "access_token": access_token,
                "limit": max(1, min(50, limit))
            })
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
                    "fields": "updated_time,participants,messages.limit(50){id,from,to,created_time,message,attachments}",
                    "access_token": access_token
                })
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

            # Fetch **conversations/messages**
            messages = await self.get_instagram_conversations(refreshed_credentials, limit=10)

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
