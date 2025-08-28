from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

# Shared properties
class NotificationBase(BaseModel):
    message_id: str = Field(..., description="Message ID to mark notification as read")
    notification_read: bool = Field(True, description="Whether the notification has been read")

# Properties to receive via API on creation
class NotificationCreate(NotificationBase):
    pass

# Properties to receive via API on update
class NotificationUpdate(BaseModel):
    notification_read: bool = Field(..., description="Whether the notification has been read")

# Properties shared by models stored in DB
class NotificationInDBBase(NotificationBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Properties to return to client
class Notification(NotificationInDBBase):
    pass

# Properties stored in DB
class NotificationInDB(NotificationInDBBase):
    pass

# Response for marking notification as read
class NotificationReadResponse(BaseModel):
    success: bool
    message: str
    notification_read: bool

# Request for marking multiple notifications as read
class BulkNotificationUpdate(BaseModel):
    message_ids: List[str] = Field(..., description="List of message IDs to mark as read")
    notification_read: bool = Field(True, description="Whether the notifications have been read") 