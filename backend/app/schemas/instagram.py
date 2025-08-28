from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class InstagramAuthResponse(BaseModel):
    instagram_auth_url: str
    message: str

class InstagramAuthCallback(BaseModel):
    code: str
    state: Optional[str] = None

class InstagramAccountInfo(BaseModel):
    account_id: Optional[str] = None
    username: Optional[str] = None
    page_id: Optional[str] = None
    connected: bool
    message: str

class InstagramMessage(BaseModel):
    id: str
    text: str
    from_user: str
    from_id: str
    created_time: datetime
    media_id: Optional[str] = None
    conversation_id: Optional[str] = None
    message_type: str  # "comment" or "direct_message"
    notification_read: bool = False

class InstagramMessageResponse(BaseModel):
    messages: List[InstagramMessage]
    count: int
    message: str

class InstagramCredentials(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[int] = None
    user_id: str
    username: str
    account_type: Optional[str] = None
