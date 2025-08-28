from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime

# Shared properties
class LeadBase(BaseModel):
    name: str
    email: EmailStr

# Properties to receive via API on creation
class LeadCreate(LeadBase):
    pass

# Properties to receive via API on update
class LeadUpdate(LeadBase):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

# Properties shared by models stored in DB
class LeadInDBBase(LeadBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Properties to return via API
class Lead(LeadInDBBase):
    pass

# Properties stored in DB
class LeadInDB(LeadInDBBase):
    pass

# For bulk creation
class LeadBulkCreate(BaseModel):
    leads: List[LeadCreate] 