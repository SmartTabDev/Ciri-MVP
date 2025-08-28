from typing import Optional
from datetime import datetime
from pydantic import BaseModel

# Shared properties
class CompanyContextBase(BaseModel):
    company_id: int
    text_context: Optional[str] = None
    flow_builder_data: Optional[str] = None
    flow_context: Optional[str] = None

# Properties to receive on company_context creation
class CompanyContextCreate(CompanyContextBase):
    pass

# Properties to receive on company_context update
class CompanyContextUpdate(BaseModel):
    company_id: Optional[int] = None
    text_context: Optional[str] = None
    flow_builder_data: Optional[str] = None
    flow_context: Optional[str] = None

# Properties shared by models stored in DB
class CompanyContextInDBBase(CompanyContextBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Properties to return to client
class CompanyContext(CompanyContextInDBBase):
    pass

# Properties properties stored in DB but not returned to client
class CompanyContextInDB(CompanyContextInDBBase):
    pass 