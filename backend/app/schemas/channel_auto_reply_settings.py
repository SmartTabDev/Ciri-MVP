from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ChannelAutoReplySettingsBase(BaseModel):
    channel_id: str
    enable_auto_reply: bool = True


class ChannelAutoReplySettingsCreate(ChannelAutoReplySettingsBase):
    pass


class ChannelAutoReplySettingsUpdate(BaseModel):
    enable_auto_reply: Optional[bool] = None


class ChannelAutoReplySettings(ChannelAutoReplySettingsBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 