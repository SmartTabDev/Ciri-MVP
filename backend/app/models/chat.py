from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.db.base_class import Base

class Chat(Base):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False, index=True)
    channel_id = Column(Text, index=True)          # was String
    message_id = Column(Text, index=True)          # was String(unique=True) -> Text + no unique
    from_email = Column(String, index=True)
    to_email = Column(String)
    subject = Column(String)
    body_text = Column(Text)
    body_html = Column(Text)
    sent_at = Column(DateTime(timezone=True), nullable=False)
    is_read = Column(Boolean, default=False)
    notification_read = Column(Boolean, default=False)
    replied = Column(Boolean, default=False)
    action_required = Column(Boolean, default=False)
    action_reason = Column(String)
    action_type = Column(String)
    urgency = Column(String)
    feedback = Column(String)
    email_provider = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('company_id', 'message_id', name='uq_chat_company_message'),
    )
