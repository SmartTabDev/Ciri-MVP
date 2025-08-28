from typing import List, Optional, Union
from typing_extensions import Annotated
from pydantic import AnyHttpUrl, PostgresDsn, field_validator, BeforeValidator, EmailStr
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Ciri Service"
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"
    API_V1_STR: str = "/api/v1"
    
    # CORS - Allow specific origins for security
    CORS_ORIGINS: List[str] = [
        "https://ciri.no",
        "https://www.ciri.no",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ]
    
    # Database
    DATABASE_URL: PostgresDsn
    
    # JWT
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email Verification
    EMAIL_VERIFICATION_CODE_EXPIRE_MINUTES: int = 15
    VERIFICATION_CODE_LENGTH: int = 6
    
    # Email settings
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: EmailStr = "noreply@example.com"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = ""
    MAIL_FROM_NAME: str = "CIRI Service"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    MAIL_USE_CREDENTIALS: bool = True
    MAIL_VALIDATE_CERTS: bool = True

    # AI
    OPENAI_API_KEY: str = ""

    # Pagination
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100

    # SQLAlchemy
    SQLALCHEMY_ECHO: bool = False

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_OAUTH_REDIRECT_URI: str = ""

    GOOGLE_CALENDAR_OAUTH_REDIRECT_URI: str = ""
    GOOGLE_GMAIL_OAUTH_REDIRECT_URI: str = ""

    # Microsoft Outlook OAuth
    OUTLOOK_CLIENT_ID: str = ""
    OUTLOOK_CLIENT_SECRET: str = ""
    OUTLOOK_OAUTH_REDIRECT_URI: str = ""

    # Instagram OAuth
    INSTAGRAM_APP_ID: str = ""
    INSTAGRAM_APP_SECRET: str = ""
    INSTAGRAM_REDIRECT_URI: str = ""

    # Facebook OAuth (for Instagram Business API)
    FACEBOOK_APP_ID: str = ""
    FACEBOOK_APP_SECRET: str = ""
    FACEBOOK_REDIRECT_URI: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()