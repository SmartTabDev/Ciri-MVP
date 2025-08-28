from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

class Lead(Base):
    __tablename__ = 'leads'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    follow_up_last_sent_at = Column(DateTime(timezone=True), nullable=True)
    email_context = Column(Text, nullable=True)  # Store the context of sent emails

    # Relationship with Company
    company = relationship("Company", back_populates="leads")