from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request, Response, File, UploadFile, Form
from fastapi.responses import StreamingResponse
import os
import io
import base64
import time
import logging
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.chat import Chat
from app.schemas.ai import AIRequest, AIResponse, InputType, AudioFormat, VoiceType
from app.services.ai_service import SimpleAIService
from app.crud.crud_company import company
from app.crud.crud_ai_agent_settings import ai_agent_settings
from app.schemas.email import SendEmailRequest, SendFacebookMessageRequest, SendInstagramMessageRequest
from app.core.email import send_plain_email
from app.services.channel_context_service import channel_context_service
from app.util import extract_email_address
from app.services.facebook_auth_service import facebook_auth_service
from app.models.company import Company

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize OpenAI service
try:
    ai_service = SimpleAIService()
except Exception as e:
    logger.error(f"Failed to initialize AI service: {str(e)}")
    ai_service = None

@router.post("/chat", response_model=AIResponse)
async def process_ai_request(
    text: str = Form(None),
    audio_file: UploadFile = File(None),
    audio_format: AudioFormat = Form(AudioFormat.MP3),
    max_tokens: int = Form(1000),
    temperature: float = Form(0.7),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Process an AI request with text or audio input.
    Returns response in the same format as the input (text for text, audio for audio).
    """
    if ai_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is not available. Check server logs for details.",
        )
    
    try:
        # Get company information
        if not current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not associated with any company",
            )
        
        db_company = company.get(db=db, id=current_user.company_id)
        if not db_company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found",
            )
        
        # Get company's AI agent settings
        db_settings = ai_agent_settings.get_by_company_id(db=db, company_id=current_user.company_id)
        if not db_settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI agent settings not found for company",
            )
        
        # Create request object
        request = AIRequest(
            text=text,
            audio_file=audio_file,
            audio_format=audio_format,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Process the request with company context and settings
        response = await ai_service.process_request(
            request=request,
            company=db_company,
            ai_settings=db_settings
        )
        
        # Log the request for analytics
        logger.info(
            f"AI request processed: user_id={current_user.id}, "
            f"input_type={response.input_type}, output_type={response.output_type}, "
            f"processing_time={response.processing_time:.2f}s, model={response.model_used}"
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing AI request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing AI request: {str(e)}",
        )

@router.post("/stream-audio")
async def stream_audio_response(
    text: str = Form(None),
    audio_file: UploadFile = File(None),
    audio_format: AudioFormat = Form(AudioFormat.MP3),
    max_tokens: int = Form(1000),
    temperature: float = Form(0.7),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Process an AI request and stream the audio response.
    This is useful for real-time audio playback in the client.
    """
    if ai_service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is not available. Check server logs for details.",
        )
    
    try:
        # Get company information
        if not current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not associated with any company",
            )
        
        db_company = company.get(db=db, id=current_user.company_id)
        if not db_company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found",
            )
        
        # Get company's AI agent settings
        db_settings = ai_agent_settings.get_by_company_id(db=db, company_id=current_user.company_id)
        if not db_settings:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI agent settings not found for company",
            )
        
        # Create request object
        request = AIRequest(
            text=text,
            audio_file=audio_file,
            audio_format=audio_format,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        if request.get_input_type() != InputType.AUDIO:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This endpoint only supports audio input",
            )
        
        # Process the request with company context and settings
        response = await ai_service.process_request(
            request=request,
            company=db_company,
            ai_settings=db_settings
        )
        
        if not response.audio_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate audio response",
            )
        
        # Decode base64 audio data
        audio_bytes = base64.b64decode(response.audio_data)
        
        # Create a file-like object from the bytes
        audio_stream = io.BytesIO(audio_bytes)
        
        # Determine content type based on audio format
        content_type = "audio/mpeg"
        if response.audio_format == AudioFormat.WAV:
            content_type = "audio/wav"
        elif response.audio_format == AudioFormat.OGG:
            content_type = "audio/ogg"
        elif response.audio_format == AudioFormat.WEBM:
            content_type = "audio/webm"
        
        # Log the request for analytics
        logger.info(
            f"Audio stream processed: user_id={current_user.id}, "
            f"processing_time={response.processing_time:.2f}s, model={response.model_used}"
        )
        
        # Return streaming response
        return StreamingResponse(
            audio_stream,
            media_type=content_type,
            headers={
                "Content-Disposition": f"attachment; filename=response.{response.audio_format}",
                "X-Processing-Time": str(response.processing_time),
                "X-Model-Used": response.model_used,
            }
        )
        
    except Exception as e:
        logger.error(f"Error streaming audio response: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error streaming audio response: {str(e)}",
        )

@router.post("/send-email", status_code=200)
async def send_email_api(
    request: SendEmailRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Send a plain text email to a recipient (Gmail/Outlook supported via API or SMTP).
    The sender will be the company's linked email by default, but can be overridden.
    """
    try:
        # Get company info
        if not current_user.company_id:
            raise HTTPException(status_code=400, detail="User is not associated with any company")
        db_company = company.get(db=db, id=current_user.company_id)
        if not db_company:
            raise HTTPException(status_code=400, detail="Company not found")
        
        # Determine which email service to use (Gmail or Outlook)
        gmail_credentials = getattr(db_company, 'gmail_box_credentials', None)
        outlook_credentials = getattr(db_company, 'outlook_box_credentials', None)
        
        # Use Gmail if available, otherwise use Outlook
        if gmail_credentials and db_company.gmail_box_email:
            # Use Gmail credentials
            from_email = request.from_email or db_company.gmail_box_email
            mail_username = request.mail_username or db_company.gmail_box_email
            mail_password = request.mail_password or db_company.gmail_box_app_password
            mail_from_name = db_company.gmail_box_username
            gmail_api_credentials = gmail_credentials
            outlook_api_credentials = None
        elif outlook_credentials and db_company.outlook_box_email:
            # Use Outlook credentials
            from_email = request.from_email or db_company.outlook_box_email
            mail_username = request.mail_username or db_company.outlook_box_email
            mail_password = request.mail_password  # Outlook doesn't use app password
            mail_from_name = db_company.outlook_box_username
            gmail_api_credentials = None
            outlook_api_credentials = outlook_credentials
        else:
            raise HTTPException(status_code=400, detail="No email credentials configured for this company")
        
        # Send the email and get the message ID
        sent_message_id = await send_plain_email(
            email_to=request.to,
            subject=request.subject,
            body=request.body,
            from_email=from_email,
            mail_username=mail_username,
            mail_password=mail_password,
            mail_from_name=mail_from_name,
            gmail_api_credentials=gmail_api_credentials,
            outlook_api_credentials=outlook_api_credentials,
            thread_id=request.thread_id,
            original_message_id=request.original_message_id
        )
        
        # Determine email provider based on credentials used
        email_provider = 'gmail' if gmail_api_credentials else 'outlook' if outlook_api_credentials else 'smtp'
        
        # Store the sent message in the chat table
        db_sent_message = Chat(
            company_id=current_user.company_id,
            channel_id=request.thread_id or f"manual-{int(time.time())}",
            message_id=sent_message_id if sent_message_id else f"manual-{int(time.time())}",
            from_email=from_email,
            to_email=extract_email_address(request.to),
            subject=request.subject,
            body_text=request.body,
            body_html=None,
            sent_at=datetime.now(timezone.utc),
            is_read=True,
            action_required=False,
            action_reason='',
            action_type='',
            urgency='',
            email_provider=email_provider
        )
        db.add(db_sent_message)
        db.commit()
        
        # Store manually sent email in channel context
        channel_context_service.store_message_in_context(db, db_sent_message)
        
        logger.info(f"Email sent and stored in chat table: message_id={sent_message_id}, to={request.to}, subject={request.subject}")
        
        return {
            "message": f"Email to {request.to} is being sent from {from_email}.",
            "message_id": sent_message_id,
            "chat_id": db_sent_message.id
        }
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


@router.post("/send-facebook", status_code=200)
async def send_facebook_message_api(
    request: SendFacebookMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Send a message via the connected Facebook Page (Messenger/IG Messaging).
    """
    try:
        if not current_user.company_id:
            raise HTTPException(status_code=400, detail="User is not associated with any company")
        db_company: Company = db.query(Company).filter(Company.id == current_user.company_id).first()
        if not db_company:
            raise HTTPException(status_code=404, detail="Company not found")

        # Resolve page token
        creds = getattr(db_company, 'facebook_box_credentials', None)
        if isinstance(creds, str):
            import json
            creds = json.loads(creds)
        page_access_token = creds.get('page_access_token') if isinstance(creds, dict) else None
        page_id = getattr(db_company, 'facebook_box_page_id', None)
        if not page_access_token or not page_id:
            raise HTTPException(status_code=400, detail="Facebook Page not connected")

        # Send message
        result = await facebook_auth_service.send_page_message(
            page_id=page_id,
            page_access_token=page_access_token,
            recipient_id=request.recipient_id,
            message=request.message
        )
        if not result:
            raise HTTPException(status_code=500, detail="Failed to send Facebook message")

        # Store in Chat
        chat = Chat(
            company_id=current_user.company_id,
            channel_id=request.thread_id or f"facebook-{request.recipient_id}",
            message_id=(result.get('message_id') if isinstance(result, dict) else None) or f"fb-{int(time.time())}",
            from_email=db_company.facebook_box_page_name or 'facebook',
            to_email=request.recipient_id,
            subject="Facebook Message",
            body_text=request.message,
            body_html=request.message,
            sent_at=datetime.now(timezone.utc),
            is_read=True,
            action_required=False,
            action_reason='',
            action_type='',
            urgency='',
            email_provider='facebook'
        )
        db.add(chat)
        db.commit()

        channel_context_service.store_message_in_context(db, chat)

        return {"message": "Facebook message sent", "chat_id": chat.id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send Facebook message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send Facebook message: {e}")


@router.post("/send-instagram", status_code=200)
async def send_instagram_message_api(
    request: SendInstagramMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Send an Instagram DM via the connected Facebook Page (Instagram Messaging API).
    """
    try:
        if not current_user.company_id:
            raise HTTPException(status_code=400, detail="User is not associated with any company")
        db_company: Company = db.query(Company).filter(Company.id == current_user.company_id).first()
        if not db_company:
            raise HTTPException(status_code=404, detail="Company not found")

        creds = getattr(db_company, 'facebook_box_credentials', None)
        if isinstance(creds, str):
            import json
            creds = json.loads(creds)
        page_access_token = creds.get('page_access_token') if isinstance(creds, dict) else None
        page_id = getattr(db_company, 'facebook_box_page_id', None) or getattr(db_company, 'instagram_page_id', None)
        if not page_access_token or not page_id:
            raise HTTPException(status_code=400, detail="Facebook Page not connected for Instagram messaging")

        # Send via page message API
        result = await facebook_auth_service.send_page_message(
            page_id=page_id,
            page_access_token=page_access_token,
            recipient_id=request.recipient_id,
            message=request.message
        )
        if not result:
            raise HTTPException(status_code=500, detail="Failed to send Instagram message")

        # Store in Chat
        chat = Chat(
            company_id=current_user.company_id,
            channel_id=request.thread_id or f"instagram-{request.recipient_id}",
            message_id=(result.get('message_id') if isinstance(result, dict) else None) or f"ig-{int(time.time())}",
            from_email=db_company.instagram_username or 'instagram',
            to_email=request.recipient_id,
            subject="Instagram Message",
            body_text=request.message,
            body_html=request.message,
            sent_at=datetime.now(timezone.utc),
            is_read=True,
            action_required=False,
            action_reason='',
            action_type='',
            urgency='',
            email_provider='instagram'
        )
        db.add(chat)
        db.commit()

        channel_context_service.store_message_in_context(db, chat)

        return {"message": "Instagram message sent", "chat_id": chat.id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send Instagram message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send Instagram message: {e}")