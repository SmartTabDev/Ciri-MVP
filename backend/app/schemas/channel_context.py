from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

# Shared properties
class ChannelContextBase(BaseModel):
    channel_id: str = Field(..., description="Gmail thread_id or Outlook conversation_id")
    company_id: int = Field(..., description="Reference to company")
    channel_context: Optional[str] = Field(None, description="JSON string containing chat history and context")

# Properties to receive via API on creation
class ChannelContextCreate(ChannelContextBase):
    pass

# Properties to receive via API on update
class ChannelContextUpdate(ChannelContextBase):
    channel_id: Optional[str] = None
    company_id: Optional[int] = None
    channel_context: Optional[str] = None

# Properties shared by models stored in DB
class ChannelContextInDBBase(ChannelContextBase):
    id: int
    last_updated: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

# Properties to return via API
class ChannelContext(ChannelContextInDBBase):
    pass

# Properties stored in DB
class ChannelContextInDB(ChannelContextInDBBase):
    pass

# Message data structure for context (includes feedback)
class MessageData(BaseModel):
    message_id: str
    from_email: str
    to_email: str
    subject: str
    content: str
    timestamp: datetime
    is_incoming: bool
    action_required: Optional[bool] = False
    action_reason: Optional[str] = None
    action_type: Optional[str] = None
    urgency: Optional[str] = None
    feedback: Optional[str] = None  # Feedback stored directly in message

# Context data structure (simplified)
class ContextData(BaseModel):
    messages: List[MessageData] = [] 