from typing import Optional
from pydantic import BaseModel
from .ai import VoiceType

class AIAgentSettingsBase(BaseModel):
    voice_type: VoiceType = VoiceType.ALLOY
    dialect: str
    goal: str = "Book appointments and collect customer emails"

class AIAgentSettingsCreate(AIAgentSettingsBase):
    """Schema for creating AI agent settings. Company ID will be taken from user context."""
    pass

class AIAgentSettingsUpdate(AIAgentSettingsBase):
    voice_type: Optional[VoiceType] = None
    dialect: Optional[str] = None
    goal: Optional[str] = None

class AIAgentSettingsInDB(AIAgentSettingsBase):
    id: int
    company_id: int

    class Config:
        from_attributes = True 