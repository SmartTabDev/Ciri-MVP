from pydantic import BaseModel, EmailStr
from typing import Optional

class EmailVerificationRequest(BaseModel):
    email: EmailStr

class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str

class EmailVerificationResponse(BaseModel):
    message: str

class SendEmailRequest(BaseModel):
    to: EmailStr
    subject: str
    body: str
    thread_id: str  # Keep as thread_id for API compatibility, but will be stored as channel_id
    original_message_id: str
    from_email: Optional[str] = None
    mail_username: Optional[str] = None
    mail_password: Optional[str] = None

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ForgotPasswordResponse(BaseModel):
    message: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class ResetPasswordResponse(BaseModel):
    message: str
