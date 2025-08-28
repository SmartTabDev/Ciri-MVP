from typing import Any, Dict, Optional, Union, List

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.channel_auto_reply_settings import ChannelAutoReplySettings
from app.schemas.channel_auto_reply_settings import ChannelAutoReplySettingsCreate, ChannelAutoReplySettingsUpdate


class CRUDChannelAutoReplySettings(CRUDBase[ChannelAutoReplySettings, ChannelAutoReplySettingsCreate, ChannelAutoReplySettingsUpdate]):
    def get_by_channel_id(self, db: Session, *, channel_id: str) -> Optional[ChannelAutoReplySettings]:
        return db.query(ChannelAutoReplySettings).filter(ChannelAutoReplySettings.channel_id == channel_id).first()
    
    def get_or_create_by_channel_id(self, db: Session, *, channel_id: str) -> ChannelAutoReplySettings:
        """Get existing settings or create default settings for a channel"""
        existing = self.get_by_channel_id(db, channel_id=channel_id)
        if existing:
            return existing
        
        # Create default settings
        settings_in = ChannelAutoReplySettingsCreate(channel_id=channel_id, enable_auto_reply=True)
        return self.create(db, obj_in=settings_in)
    
    def update_by_channel_id(
        self, db: Session, *, channel_id: str, obj_in: Union[ChannelAutoReplySettingsUpdate, Dict[str, Any]]
    ) -> ChannelAutoReplySettings:
        """Update settings for a specific channel"""
        db_obj = self.get_by_channel_id(db, channel_id=channel_id)
        if not db_obj:
            # Create if doesn't exist
            if isinstance(obj_in, dict):
                obj_in["channel_id"] = channel_id
                create_obj = ChannelAutoReplySettingsCreate(**obj_in)
            else:
                create_obj = ChannelAutoReplySettingsCreate(channel_id=channel_id, enable_auto_reply=obj_in.enable_auto_reply)
            return self.create(db, obj_in=create_obj)
        
        return self.update(db, db_obj=db_obj, obj_in=obj_in)


channel_auto_reply_settings = CRUDChannelAutoReplySettings(ChannelAutoReplySettings) 