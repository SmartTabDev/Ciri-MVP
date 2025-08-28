from typing import Optional, Dict, Any, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class WebCredentials(BaseModel):
    """Schema for web application credentials"""
    client_id: str
    client_secret: str
    project_id: str
    auth_uri: str = "https://accounts.google.com/o/oauth2/auth"
    token_uri: str = "https://oauth2.googleapis.com/token"
    auth_provider_x509_cert_url: str = "https://www.googleapis.com/oauth2/v1/certs"
    redirect_uris: List[str]
    javascript_origins: Optional[List[str]] = None

class CalendarCredentials(BaseModel):
    """Schema for Google Calendar credentials (input only)"""
    web: WebCredentials

class CalendarEvent(BaseModel):
    """Schema for a calendar event"""
    id: str
    summary: str
    start: datetime
    end: datetime
    description: Optional[str] = None
    location: Optional[str] = None

class CalendarResponse(BaseModel):
    """Response model for calendar access"""
    events: List[CalendarEvent]
    next_page_token: Optional[str] = None

# Shared properties
class CompanyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    follow_up_cycle: Optional[int] = None
    business_email: str = Field(..., min_length=1, max_length=100)
    business_category: str = Field(..., min_length=1, max_length=100)
    terms_of_service: str = Field(..., min_length=1)
    phone_numbers: Optional[str] = Field(None, max_length=500)  # Comma-separated list of phone numbers
    goal: str = Field(..., min_length=1, max_length=500)  # Company's primary goal
    gmail_box_credentials: Optional[Dict[str, Any]] = None  # Gmail box credentials
    calendar_credentials: Optional[Dict[str, Any]] = None  # Calendar credentials
    gmail_box_email: Optional[str] = None  # Linked Gmail address
    gmail_box_app_password: Optional[str] = None  # Gmail app password
    gmail_box_username: Optional[str] = None  # Gmail username/display name
    
    # Outlook fields
    outlook_box_credentials: Optional[Dict[str, Any]] = None  # Outlook box credentials
    outlook_box_email: Optional[str] = None  # Linked Outlook address
    outlook_box_username: Optional[str] = None  # Outlook username/display name
    
    # Instagram fields
    instagram_credentials: Optional[Dict[str, Any]] = None  # Instagram credentials
    instagram_username: Optional[str] = None  # Instagram username
    instagram_account_id: Optional[str] = None  # Instagram account ID
    instagram_page_id: Optional[str] = None  # Connected Facebook page ID
    
    # Facebook fields
    facebook_box_credentials: Optional[Dict[str, Any]] = None  # Facebook credentials
    facebook_box_page_id: Optional[str] = None  # Facebook page ID
    facebook_box_page_name: Optional[str] = None  # Facebook page name

# Properties to receive via API on creation
class CompanyCreate(CompanyBase):
    pass

# Properties to receive via API on update
class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    follow_up_cycle: Optional[int] = None
    business_email: Optional[str] = Field(None, min_length=1, max_length=100)
    business_category: Optional[str] = Field(None, min_length=1, max_length=100)
    terms_of_service: Optional[str] = Field(None, min_length=1)
    phone_numbers: Optional[str] = Field(None, max_length=500)  # Comma-separated list of phone numbers
    goal: Optional[str] = Field(None, min_length=1, max_length=500)  # Company's primary goal
    logo_url: Optional[str] = None
    gmail_box_credentials: Optional[Dict[str, Any]] = None  # Gmail box credentials
    calendar_credentials: Optional[Dict[str, Any]] = None  # Calendar credentials
    gmail_box_email: Optional[str] = None  # Linked Gmail address
    gmail_box_app_password: Optional[str] = None  # Gmail app password
    gmail_box_username: Optional[str] = None  # Gmail username/display name
    
    # Outlook fields
    outlook_box_credentials: Optional[Dict[str, Any]] = None  # Outlook box credentials
    outlook_box_email: Optional[str] = None  # Linked Outlook address
    outlook_box_username: Optional[str] = None  # Outlook username/display name
    
    # Instagram fields
    instagram_credentials: Optional[Dict[str, Any]] = None  # Instagram credentials
    instagram_username: Optional[str] = None  # Instagram username
    instagram_account_id: Optional[str] = None  # Instagram account ID
    instagram_page_id: Optional[str] = None  # Connected Facebook page ID
    
    # Facebook fields
    facebook_box_credentials: Optional[Dict[str, Any]] = None  # Facebook credentials
    facebook_box_page_id: Optional[str] = None  # Facebook page ID
    facebook_box_page_name: Optional[str] = None  # Facebook page name

# Properties shared by models stored in DB
class CompanyInDBBase(CompanyBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    logo_url: Optional[str] = None
    calendar_credentials: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

# Properties to return via API
class Company(CompanyInDBBase):
    pass

# Properties stored in DB
class CompanyInDB(CompanyInDBBase):
    calendar_credentials: Optional[Dict[str, Any]] = None
