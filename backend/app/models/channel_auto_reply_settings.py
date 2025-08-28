from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base


class ChannelAutoReplySettings(Base):
    __tablename__ = "channel_auto_reply_settings"

    id = Column(Integer, primary_key=True, index=True)
    channel_id = Column(String, nullable=False, index=True)
    enable_auto_reply = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 