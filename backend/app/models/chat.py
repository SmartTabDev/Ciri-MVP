from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base_class import Base

class Chat(Base):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    channel_id = Column(String, index=True)  # Gmail thread_id or Outlook conversationId
    message_id = Column(String, unique=True, index=True)
    from_email = Column(String, index=True)
    to_email = Column(String)
    subject = Column(String)
    body_text = Column(Text)
    body_html = Column(Text)
    sent_at = Column(DateTime(timezone=True), nullable=False)
    is_read = Column(Boolean, default=False)
    notification_read = Column(Boolean, default=False)  # Track if notification has been read/closed
    replied = Column(Boolean, default=False)
    action_required = Column(Boolean, default=False)
    action_reason = Column(String)
    action_type = Column(String)
    urgency = Column(String)
    feedback = Column(String)
    email_provider = Column(String(50))  # 'gmail' or 'outlook'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 