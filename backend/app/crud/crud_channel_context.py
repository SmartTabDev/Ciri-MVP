from typing import Any, Dict, Optional, Union, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.crud.base import CRUDBase
from app.models.channel_context import ChannelContext
from app.schemas.channel_context import ChannelContextCreate, ChannelContextUpdate
import json

class CRUDChannelContext(CRUDBase[ChannelContext, ChannelContextCreate, ChannelContextUpdate]):
    
    def get_by_channel_id(self, db: Session, *, channel_id: str, company_id: int) -> Optional[ChannelContext]:
        """Get channel context by channel_id and company_id"""
        return db.query(ChannelContext).filter(
            and_(
                ChannelContext.channel_id == channel_id,
                ChannelContext.company_id == company_id
            )
        ).first()
    
    def get_context_data(self, db: Session, *, channel_id: str, company_id: int) -> Optional[Dict[str, Any]]:
        """Get parsed context data for a channel"""
        channel_context = self.get_by_channel_id(db, channel_id=channel_id, company_id=company_id)
        if channel_context and channel_context.channel_context:
            try:
                return json.loads(channel_context.channel_context)
            except json.JSONDecodeError:
                return None
        return None
    
    def update_context_data(self, db: Session, *, channel_id: str, company_id: int, context_data: Dict[str, Any]) -> ChannelContext:
        """Update or create channel context with new data"""
        channel_context = self.get_by_channel_id(db, channel_id=channel_id, company_id=company_id)
        
        if channel_context:
            # Update existing context
            channel_context.channel_context = json.dumps(context_data, ensure_ascii=False)
            db.add(channel_context)
            db.commit()
            db.refresh(channel_context)
            return channel_context
        else:
            # Create new context
            channel_context_in = ChannelContextCreate(
                channel_id=channel_id,
                company_id=company_id,
                channel_context=json.dumps(context_data, ensure_ascii=False)
            )
            return self.create(db, obj_in=channel_context_in)
    
    def add_message_to_context(self, db: Session, *, channel_id: str, company_id: int, message_data: Dict[str, Any]) -> ChannelContext:
        """Add a new message to the channel context"""
        current_context = self.get_context_data(db, channel_id=channel_id, company_id=company_id) or {
            "messages": []
        }
        
        # Add the new message
        current_context["messages"].append(message_data)
        
        # Update the context
        return self.update_context_data(db, channel_id=channel_id, company_id=company_id, context_data=current_context)
    
    def add_feedback_to_context(self, db: Session, *, channel_id: str, company_id: int, feedback_data: Dict[str, Any]) -> ChannelContext:
        """Add feedback to a specific message in the channel context"""
        current_context = self.get_context_data(db, channel_id=channel_id, company_id=company_id)
        if not current_context:
            return None
        
        # Find the message and update its feedback
        message_id = feedback_data.get("message_id")
        feedback = feedback_data.get("feedback")
        
        for message in current_context.get("messages", []):
            if message.get("message_id") == message_id:
                message["feedback"] = feedback
                break
        
        # Update the context
        return self.update_context_data(db, channel_id=channel_id, company_id=company_id, context_data=current_context)
    
    def get_all_by_company(self, db: Session, *, company_id: int, skip: int = 0, limit: int = 100) -> List[ChannelContext]:
        """Get all channel contexts for a company"""
        return db.query(ChannelContext).filter(
            ChannelContext.company_id == company_id
        ).offset(skip).limit(limit).all()

channel_context = CRUDChannelContext(ChannelContext) 