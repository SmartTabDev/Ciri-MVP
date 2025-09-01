import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.crud.crud_channel_context import channel_context
from app.models.chat import Chat

logger = logging.getLogger(__name__)

class ChannelContextService:
    """Service for managing channel context and chat history"""
    
    def __init__(self):
        pass
    
    def store_message_in_context(self, db: Session, chat_message: Chat) -> bool:
        """Store a chat message in the channel context"""
        try:
            # Prepare message data
            message_data = {
                "message_id": chat_message.message_id,
                "from_email": chat_message.from_email,
                "to_email": chat_message.to_email,
                "subject": chat_message.subject,
                "content": chat_message.body_text or "",
                "timestamp": chat_message.sent_at.isoformat() if chat_message.sent_at else datetime.now(timezone.utc).isoformat(),
                "is_incoming": chat_message.from_email != chat_message.to_email,  # Simple heuristic
                "action_required": chat_message.action_required or False,
                "action_reason": chat_message.action_reason or None,
                "action_type": chat_message.action_type or None,
                "urgency": chat_message.urgency or None,
                "feedback": None  # Will be updated when feedback is added
            }
            
            # Store in channel context
            channel_context.add_message_to_context(
                db=db,
                channel_id=chat_message.channel_id,
                company_id=chat_message.company_id,
                message_data=message_data
            )
            
            logger.info(f"Stored message {chat_message.message_id} in context for channel {chat_message.channel_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store message in context: {str(e)}")
            return False
    
    def store_feedback_in_context(self, db: Session, message_id: str, feedback: str, user_id: Optional[int] = None) -> bool:
        """Store feedback for a specific message in the channel context"""
        try:
            # First, find the chat message to get channel_id and company_id
            chat_message = db.query(Chat).filter(Chat.message_id == message_id).first()
            if not chat_message:
                logger.error(f"Chat message with message_id {message_id} not found")
                return False
            
            # Prepare feedback data
            feedback_data = {
                "message_id": message_id,
                "feedback": feedback
            }
            
            # Store feedback in channel context
            channel_context.add_feedback_to_context(
                db=db,
                channel_id=chat_message.channel_id,
                company_id=chat_message.company_id,
                feedback_data=feedback_data
            )
            
            logger.info(f"Stored feedback for message {message_id} in context for channel {chat_message.channel_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to store feedback in context: {str(e)}")
            return False
    
    def get_channel_context(self, db: Session, channel_id: str, company_id: int) -> Optional[Dict[str, Any]]:
        """Get the full context for a channel"""
        try:
            return channel_context.get_context_data(db, channel_id=channel_id, company_id=company_id)
        except Exception as e:
            logger.error(f"Failed to get channel context: {str(e)}")
            return None
    
    def get_all_contexts_for_company(self, db: Session, company_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all channel contexts for a company"""
        try:
            contexts = channel_context.get_all_by_company(db, company_id=company_id, skip=skip, limit=limit)
            result = []
            for context in contexts:
                context_data = {
                    "id": context.id,
                    "channel_id": context.channel_id,
                    "company_id": context.company_id,
                    "last_updated": context.last_updated,
                    "created_at": context.created_at
                }
                
                # Parse the context data if available
                if context.channel_context:
                    try:
                        parsed_context = json.loads(context.channel_context)
                        context_data["context"] = parsed_context
                    except json.JSONDecodeError:
                        context_data["context"] = None
                
                result.append(context_data)
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to get contexts for company: {str(e)}")
            return []
    
    def sync_existing_chat_messages(self, db: Session, company_id: int) -> int:
        """Sync existing chat messages to channel context (for migration)"""
        try:
            # Get all chat messages for the company
            chat_messages = db.query(Chat).filter(Chat.company_id == company_id).all()
            synced_count = 0
            
            for chat_message in chat_messages:
                if self.store_message_in_context(db, chat_message):
                    synced_count += 1
            
            logger.info(f"Synced {synced_count} chat messages to channel context for company {company_id}")
            logger.info(f"Synced {chat_messages} chat messages to channel context for company {company_id}")
            return synced_count
            
        except Exception as e:
            logger.error(f"Failed to sync existing chat messages: {str(e)}")
            return 0

# Create a singleton instance
channel_context_service = ChannelContextService() 