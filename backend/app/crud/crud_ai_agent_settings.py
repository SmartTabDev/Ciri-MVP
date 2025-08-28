from typing import Optional
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.ai_agent_settings import AIAgentSettings
from app.schemas.ai_agent_settings import AIAgentSettingsCreate, AIAgentSettingsUpdate

class CRUDAIAgentSettings(CRUDBase[AIAgentSettings, AIAgentSettingsCreate, AIAgentSettingsUpdate]):
    def get_by_company_id(self, db: Session, *, company_id: int) -> Optional[AIAgentSettings]:
        """Get AI agent settings by company ID."""
        return db.query(AIAgentSettings).filter(AIAgentSettings.company_id == company_id).first()
    
    def create_for_company(
        self, db: Session, *, company_id: int, obj_in: AIAgentSettingsCreate
    ) -> AIAgentSettings:
        """Create AI agent settings for a company."""
        db_obj = AIAgentSettings(
            company_id=company_id,
            voice_type=obj_in.voice_type,
            dialect=obj_in.dialect,
            goal=obj_in.goal
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_for_company(
        self, db: Session, *, company_id: int, obj_in: AIAgentSettingsUpdate
    ) -> Optional[AIAgentSettings]:
        """Update AI agent settings for a company."""
        db_obj = self.get_by_company_id(db, company_id=company_id)
        if not db_obj:
            return None
        
        update_data = obj_in.dict(exclude_unset=True)
        for field in update_data:
            setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

ai_agent_settings = CRUDAIAgentSettings(AIAgentSettings)