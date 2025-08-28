from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class FacebookAuthResponse(BaseModel):
    facebook_auth_url: str
    message: str

class FacebookAuthCallback(BaseModel):
    code: str
    state: Optional[str] = None

class FacebookAccountInfo(BaseModel):
    page_id: Optional[str] = None
    page_name: Optional[str] = None
    connected: bool
    message: str

class FacebookMessageResponse(BaseModel):
    id: str
    text: str
    from_user: str
    from_id: str
    created_time: datetime
    conversation_id: Optional[str] = None
    post_id: Optional[str] = None
    message_type: str  # "message" or "comment"
    notification_read: bool = False

class FacebookCredentials(BaseModel):
    access_token: str
    expires_at: Optional[int] = None
    user_id: str
    page_id: str
    page_name: str
    page_access_token: str
    category: Optional[str] = None
    fan_count: Optional[int] = None

class FacebookPage(BaseModel):
    id: str
    name: str
    access_token: str
    category: Optional[str] = None
    fan_count: Optional[int] = None

class FacebookPagesResponse(BaseModel):
    pages: List[FacebookPage]
