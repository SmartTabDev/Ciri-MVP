# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base
from app.models.user import User
from app.models.company import Company
from app.models.chat import Chat
from app.models.channel_auto_reply_settings import ChannelAutoReplySettings
from app.models.channel_context import ChannelContext
from app.models.company_context import CompanyContext
