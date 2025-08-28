from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_verified: Optional[bool] = False
    company_id: Optional[int] = None

# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str = Field(..., min_length=8)
    is_verified: Optional[bool] = False

# Properties to receive via API on update
class UserUpdate(UserBase):
    password: Optional[str] = Field(None, min_length=8)

# Properties shared by models stored in DB
class UserInDBBase(UserBase):
    id: int
    email: EmailStr
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Properties to return via API
class User(UserInDBBase):
    company_gmail_box_email: Optional[str] = None
    company_outlook_box_email: Optional[str] = None

# Properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
