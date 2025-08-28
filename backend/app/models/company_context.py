from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

class CompanyContext(Base):
    __tablename__ = "company_context"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    text_context = Column(Text, nullable=True)  # Text context for the company
    flow_builder_data = Column(Text, nullable=True)  # Flow builder data (JSON)
    flow_context = Column(Text, nullable=True)  # AI-generated text instructions from flow_builder_data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    company = relationship("Company", back_populates="company_contexts") 