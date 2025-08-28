import logging
from pathlib import Path
from typing import Any, Dict, List
import asyncio
from googleapiclient.errors import HttpError
from google.auth.exceptions import RefreshError
from requests.exceptions import RequestException

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr

from app.core.config import settings

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
import base64
import uuid

# Configure FastMail
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.MAIL_USE_CREDENTIALS,
    VALIDATE_CERTS=settings.MAIL_VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates" / "email"
)

async def send_email(
    email_to: List[EmailStr],
    subject: str,
    body: str,
    template_name: str = None,
    template_body: Dict[str, Any] = None,
) -> None:
    message = MessageSchema(
        subject=subject,
        recipients=email_to,
        body=body,
        subtype=MessageType.html,
    )
    
    fm = FastMail(conf)
    
    try:
        if template_name and template_body:
            await fm.send_message(
                message,
                template_name=f"{template_name}.html",
                template_body=template_body,
            )
        else:
            await fm.send_message(message)
        logging.info(f"Email sent to {email_to}")
    except Exception as e:
        logging.error(f"Failed to send email to {email_to}: {str(e)}")
        raise

async def send_verification_code(email_to: EmailStr, code: str, expires_in_minutes: int) -> None:
    subject = f"Your Verification Code for {settings.PROJECT_NAME}"
    body = f"""
    <html>
    <body>
        <p>Hi there,</p>
        <p>Thank you for registering with {settings.PROJECT_NAME}!</p>
        <p>Your verification code is:</p>
        <h2 style="background-color: #f5f5f5; padding: 10px; font-family: monospace; letter-spacing: 5px; text-align: center;">{code}</h2>
        <p>This code will expire in {expires_in_minutes} minutes.</p>
        <p>If you didn't register for an account, you can safely ignore this email.</p>
        <p>Best regards,<br>The {settings.PROJECT_NAME} Team</p>
    </body>
    </html>
    """
    
    await send_email(
        email_to=[email_to],
        subject=subject,
        body=body,
    )

async def send_email_via_gmail_api(
    email_to: str,
    subject: str,
    body: str,
    from_email: str,
    credentials_data: dict,
    thread_id: str = None,
    original_message_id: str = None
) -> str:
    """
    Send an email using Gmail API and return the Gmail message ID.
    
    Args:
        email_to: Recipient email address
        subject: Email subject
        body: Email body (plain text)
        from_email: Sender email address
        credentials_data: Gmail OAuth2 credentials data
        thread_id: Gmail thread ID to reply to (optional)
        original_message_id: Original message ID to reply to (optional)
        
    Returns:
        str: The Gmail message ID of the sent email
    """
    
    async def retry_gmail_api_call(func, max_retries=3, delay=1):
        """Retry Gmail API calls with exponential backoff"""
        for attempt in range(max_retries):
            try:
                # Gmail API execute() is synchronous, so we don't await it
                return func()
            except (HttpError, RefreshError, RequestException) as e:
                if "EOF occurred in violation of protocol" in str(e) or "SSL" in str(e):
                    if attempt < max_retries - 1:
                        logging.warning(f"Gmail API SSL error, retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(delay)
                        delay *= 2  # Exponential backoff
                        continue
                raise e
            except Exception as e:
                raise e
        return None
    
    try:
        # Create credentials from the provided data
        creds = Credentials(
            credentials_data["access_token"],
            refresh_token=credentials_data.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=['https://www.googleapis.com/auth/gmail.send']
        )
        
        # Refresh token if needed
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        
        # Build Gmail service
        service = build('gmail', 'v1', credentials=creds)
        
        # Create the email message
        message = MIMEText(body)
        message['to'] = email_to
        message['from'] = from_email
        message['subject'] = subject
        
        # If this is a reply, add proper headers to maintain the thread
        if thread_id and original_message_id:
            # Generate a new Message-ID for this reply
            new_message_id = f"<{uuid.uuid4()}@{from_email.split('@')[1]}>"
            message['Message-ID'] = new_message_id
            message['In-Reply-To'] = original_message_id
            message['References'] = original_message_id
            print(f"Sending email via Gmail API to {email_to} with thread_id: {thread_id}, original_message_id: {original_message_id}")
            
            # Send the message with retry logic
            def send_message():
                return service.users().messages().send(
                    userId='me',
                    body={'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8'), 'threadId': thread_id}
                ).execute()
            
            sent_message = await retry_gmail_api_call(send_message)
        else:
            # Regular new message with retry logic
            def send_message():
                return service.users().messages().send(
                    userId='me',
                    body={'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')}
                ).execute()
            
            sent_message = await retry_gmail_api_call(send_message)
        
        if not sent_message:
            raise Exception("Failed to send email after all retry attempts")
        
        message_id = sent_message['id']
        logging.info(f"Email sent via Gmail API successfully to {email_to} with message ID: {message_id}")
        
        return message_id
        
    except Exception as e:
        error_msg = f"Failed to send email via Gmail API to {email_to}: {str(e)}"
        logging.error(error_msg)
        
        # Provide more specific error messages
        if "EOF occurred in violation of protocol" in str(e):
            raise Exception(f"Gmail API connection error. Please try again in a few moments. If the problem persists, check your internet connection and Gmail credentials. Error: {str(e)}")
        elif "SSL" in str(e):
            raise Exception(f"Gmail API SSL connection error. Please try again in a few moments. Error: {str(e)}")
        elif "insufficient authentication scopes" in str(e):
            raise Exception(f"Gmail authentication scopes are insufficient. Please re-authenticate your Gmail account. Error: {str(e)}")
        elif "invalid_grant" in str(e):
            raise Exception(f"Gmail credentials have expired. Please re-authenticate your Gmail account. Error: {str(e)}")
        else:
            raise Exception(error_msg)

async def send_plain_email(
    email_to: EmailStr,
    subject: str,
    body: str,
    from_email: str = None,
    mail_username: str = None,
    mail_password: str = None,
    mail_from_name: str = None,
    gmail_api_credentials: dict = None,
    outlook_api_credentials: dict = None,
    thread_id: str = None,
    original_message_id: str = None
) -> str:
    """
    Send a plain text email using Gmail API, Outlook API (if credentials provided) or SMTP.
    Returns message ID if using API, else None.
    """
    # Try Gmail API first if credentials provided
    if gmail_api_credentials:
        try:
            return await send_email_via_gmail_api(
                email_to=email_to,
                subject=subject,
                body=body,
                from_email=from_email or settings.MAIL_FROM,
                credentials_data=gmail_api_credentials,
                thread_id=thread_id,
                original_message_id=original_message_id
            )
        except Exception as e:
            error_msg = str(e)
            if "insufficientPermissions" in error_msg or "insufficient authentication scopes" in error_msg:
                logging.warning(f"Gmail API send failed due to insufficient scopes, trying Outlook API: {error_msg}")
                # Fall back to Outlook API or SMTP
            elif "EOF occurred in violation of protocol" in error_msg or "SSL" in error_msg:
                logging.warning(f"Gmail API SSL connection error, trying Outlook API: {error_msg}")
                # Fall back to Outlook API or SMTP
            elif "invalid_grant" in error_msg:
                logging.warning(f"Gmail API credentials expired, trying Outlook API: {error_msg}")
                # Fall back to Outlook API or SMTP
            else:
                logging.error(f"Gmail API send failed with unexpected error: {error_msg}")
                # Try Outlook API or fall back to SMTP
    
    # Try Outlook API if credentials provided
    if outlook_api_credentials:
        try:
            from app.services.outlook_email_service import outlook_email_service
            
            # If this is a reply (we have thread_id and original_message_id), use the reply service
            if thread_id and original_message_id:
                logging.info(f"Using Outlook reply service for thread_id: {thread_id}, original_message_id: {original_message_id}")
                return await outlook_email_service.reply_to_message_via_outlook_api(
                    message_id=original_message_id,
                    reply_body=body,
                    credentials_data=outlook_api_credentials,
                    from_email=from_email or settings.MAIL_FROM
                )
            else:
                # Use regular send service for new messages
                return await outlook_email_service.send_email_via_outlook_api(
                    email_to=email_to,
                    subject=subject,
                    body=body,
                    from_email=from_email or settings.MAIL_FROM,
                    credentials_data=outlook_api_credentials,
                    thread_id=thread_id,
                    original_message_id=original_message_id
                )
        except Exception as e:
            error_msg = str(e)
            logging.warning(f"Outlook API send failed, falling back to SMTP: {error_msg}")
            # Fall back to SMTP with Outlook configuration
    
    # Fall back to SMTP
    try:
        # Determine which configuration to use
        use_custom_config = bool(from_email or mail_username or mail_password or mail_from_name)
        
        if use_custom_config:
            # Use custom configuration with provided credentials
            final_username = mail_username if mail_username else settings.MAIL_USERNAME
            final_password = mail_password if mail_password else settings.MAIL_PASSWORD
            final_from = from_email if from_email else settings.MAIL_FROM
            final_from_name = mail_from_name if mail_from_name else settings.MAIL_FROM_NAME
            
            # Determine SMTP server based on email domain
            if final_username and '@outlook.com' in final_username.lower():
                # Use Outlook SMTP settings
                smtp_server = 'smtp-mail.outlook.com'
                smtp_port = 587
                use_starttls = True
                use_ssl_tls = False
                logging.info(f"Using Outlook SMTP configuration for {final_username}")
            elif final_username and '@gmail.com' in final_username.lower():
                # Use Gmail SMTP settings
                smtp_server = 'smtp.gmail.com'
                smtp_port = 465
                use_starttls = False
                use_ssl_tls = True
                logging.info(f"Using Gmail SMTP configuration for {final_username}")
            else:
                # Use default settings
                smtp_server = settings.MAIL_SERVER
                smtp_port = settings.MAIL_PORT
                use_starttls = settings.MAIL_STARTTLS
                use_ssl_tls = settings.MAIL_SSL_TLS
                logging.info(f"Using default SMTP configuration for {final_username}")
            
            # Debug logging (mask password for security)
            masked_password = final_password[:4] + "*" * (len(final_password) - 4) if final_password else "None"
            logging.info(f"Using custom SMTP config - Username: {final_username}, From: {final_from}")
            logging.info(f"SMTP Server: {smtp_server}:{smtp_port}, Password: {masked_password}")
            
            custom_conf = ConnectionConfig(
                MAIL_USERNAME=final_username,
                MAIL_PASSWORD=final_password,
                MAIL_FROM=final_from,
                MAIL_PORT=smtp_port,
                MAIL_SERVER=smtp_server,
                MAIL_FROM_NAME=final_from_name,
                MAIL_STARTTLS=use_starttls,
                MAIL_SSL_TLS=use_ssl_tls,
                USE_CREDENTIALS=settings.MAIL_USE_CREDENTIALS,
                VALIDATE_CERTS=settings.MAIL_VALIDATE_CERTS,
                TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates" / "email"
            )
            print(f"custom_conf================>: {custom_conf}")
            fm = FastMail(custom_conf)
        else:
            # Use default configuration from settings
            masked_default_password = settings.MAIL_PASSWORD[:4] + "*" * (len(settings.MAIL_PASSWORD) - 4) if settings.MAIL_PASSWORD else "None"
            logging.info(f"Using default SMTP config - Server: {settings.MAIL_SERVER}:{settings.MAIL_PORT}")
            logging.info(f"Default Username: {settings.MAIL_USERNAME}, Password: {masked_default_password}")
            fm = FastMail(conf)
        
        # Create message
        message = MessageSchema(
            subject=subject,
            recipients=[email_to],
            body=body,
            subtype=MessageType.plain,
        )
        
        # Send email
        await fm.send_message(message)
        logging.info(f"Plain email sent successfully to {email_to} with subject: '{subject}'")
        
        return None
    except Exception as e:
        error_msg = f"Failed to send plain email to {email_to}: {str(e)}"
        logging.error(error_msg)
        
        # Log additional debug info for SMTP errors
        if "535" in str(e) or "authentication" in str(e).lower():
            logging.error("SMTP Authentication failed. Check username/password and ensure App Password is used for Gmail.")
        elif "connection" in str(e).lower():
            logging.error(f"SMTP Connection failed. Check server ({settings.MAIL_SERVER}) and port ({settings.MAIL_PORT}).")
        
        raise Exception(error_msg)

async def send_password_reset_email(email_to: EmailStr, reset_token: str) -> None:
    subject = f"Password Reset for {settings.PROJECT_NAME}"
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
    body = f"""
    <html>
    <body style='font-family: Arial, sans-serif; background: #f6f8fa; margin: 0; padding: 0;'>
      <table width='100%' bgcolor='#f6f8fa' cellpadding='0' cellspacing='0' style='padding: 40px 0;'>
        <tr>
          <td align='center'>
            <table width='100%' style='max-width: 480px; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); padding: 32px;'>
              <tr>
                <td align='center' style='padding-bottom: 24px;'>
                  <h2 style='color: #222; margin: 0 0 8px 0;'>Reset your password</h2>
                  <p style='color: #555; margin: 0;'>for <b>{settings.PROJECT_NAME}</b></p>
                </td>
              </tr>
              <tr>
                <td style='padding-bottom: 24px;'>
                  <p style='color: #333; margin: 0 0 16px 0;'>Hi,</p>
                  <p style='color: #333; margin: 0 0 16px 0;'>You requested a password reset for your <b>{settings.PROJECT_NAME}</b> account.</p>
                  <p style='color: #333; margin: 0 0 24px 0;'>Click the button below to reset your password. This link will expire in 1 hour.</p>
                  <div style='text-align: center; margin: 32px 0;'>
                    <a href='{reset_link}' style='background: #2563eb; color: #fff; text-decoration: none; padding: 12px 32px; border-radius: 6px; font-size: 16px; font-weight: 600; display: inline-block;'>Reset Password</a>
                  </div>
                  <p style='color: #888; font-size: 13px; margin: 0 0 8px 0;'>If you did not request this, you can safely ignore this email.</p>
                  <p style='color: #888; font-size: 13px; margin: 0;'>Best regards,<br>The {settings.PROJECT_NAME} Team</p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """
    await send_email(
        email_to=[email_to],
        subject=subject,
        body=body,
    )
