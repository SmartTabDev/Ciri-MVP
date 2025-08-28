from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base
from app.schemas.ai import VoiceType

class AIAgentSettings(Base):
    __tablename__ = "ai_agent_settings"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    voice_type = Column(String, nullable=False, default=VoiceType.ALLOY)
    dialect = Column(String, nullable=False)
    goal = Column(String, nullable=False, default="Book appointments and collect customer emails")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    company = relationship("Company", back_populates="ai_agent_settings") 