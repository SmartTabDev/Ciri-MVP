from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

class ChannelContext(Base):
    __tablename__ = "channel_context"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(String(255), nullable=False, index=True)  # Gmail thread_id or Outlook conversation_id
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)  # Reference to company
    channel_context = Column(Text, nullable=True)  # JSON string containing chat history and context
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="channel_contexts") 