from sqlalchemy import Column, Integer, String, DateTime, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    follow_up_cycle = Column(Integer, nullable=True)  # in milliseconds
    business_email = Column(String(100), nullable=False, unique=True)
    business_category = Column(String(100), nullable=False)  # e.g., "Restaurant", "Salon", "Clinic"
    terms_of_service = Column(Text, nullable=False)  # Terms of service text
    phone_numbers = Column(String(500), nullable=True)  # Comma-separated list of phone numbers
    logo_url = Column(String(500), nullable=True)  # URL to company logo
    calendar_credentials = Column(JSON, nullable=True)  # Internal field for Google Calendar credentials
    gmail_box_credentials = Column(JSON, nullable=True)  # Internal field for Gmail box credentials
    gmail_box_email = Column(String(100), nullable=True)  # Linked Gmail address
    gmail_box_app_password = Column(String(100), nullable=True)  # Gmail app password
    gmail_box_username = Column(String(200), nullable=True)  # Gmail username/display name
    
    # Outlook fields
    outlook_box_credentials = Column(JSON, nullable=True)  # Internal field for Outlook credentials
    outlook_box_email = Column(String(100), nullable=True)  # Linked Outlook address
    outlook_box_username = Column(String(200), nullable=True)  # Outlook username/display name
    
    # Instagram fields (using existing migration field names)
    instagram_credentials = Column(JSON, nullable=True)  # Internal field for Instagram credentials
    instagram_username = Column(String(100), nullable=True)  # Instagram username
    instagram_account_id = Column(String(100), nullable=True)  # Instagram account ID
    instagram_page_id = Column(String(100), nullable=True)  # Connected Facebook page ID
    
    # Facebook fields
    facebook_box_credentials = Column(JSON, nullable=True)  # Internal field for Facebook credentials
    facebook_box_page_id = Column(String(100), nullable=True)  # Facebook page ID
    facebook_box_page_name = Column(String(200), nullable=True)  # Facebook page name
    
    goal = Column(String(500), nullable=False, default="Book appointments and collect customer emails")  # Company's primary goal
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="company")
    ai_agent_settings = relationship("AIAgentSettings", back_populates="company", uselist=False)
    leads = relationship("Lead", back_populates="company")
    channel_contexts = relationship("ChannelContext", back_populates="company")
    company_contexts = relationship("CompanyContext", back_populates="company")
