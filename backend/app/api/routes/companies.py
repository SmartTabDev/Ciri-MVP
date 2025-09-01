from typing import Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body, UploadFile, File
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.crud.crud_company import company
from app.crud.crud_user import user
from app.crud.crud_channel_auto_reply_settings import channel_auto_reply_settings
from app.models.user import User
from app.schemas.company import Company, CompanyCreate, CompanyUpdate, CalendarResponse, CalendarCredentials
from app.schemas.channel_auto_reply_settings import ChannelAutoReplySettings, ChannelAutoReplySettingsCreate, ChannelAutoReplySettingsUpdate
from app.services.calendar_service import calendar_service
from app.services.gmail_auth_service import gmail_auth_service
from app.services.gmail_monitor_service import gmail_monitor_service
from googleapiclient.discovery import build
import asyncio
import re
from app.services.ai_service import SimpleAIService, filter_email_with_ai
from app.services.channel_context_service import channel_context_service
from app.models.chat import Chat
from bs4 import BeautifulSoup
from app.util import extract_email_address, remove_gmail_quote, clean_html_content
from app.models.company import Company as CompanyModel
import time
from app.core.config import settings

router = APIRouter()

def ensure_full_logo_url(logo_url: Optional[str]) -> Optional[str]:
    """Ensure logo_url is a full URL"""
    if not logo_url:
        return None
    if logo_url.startswith('http'):
        return logo_url
    return f"{settings.BACKEND_URL}{logo_url}"

@router.get("/", response_model=List[Company])
def read_companies(
    db: Session = Depends(get_db),
    skip: int = 0, 
    limit: int = 100,
) -> Any:
    """
    Retrieve companies.
    """
    companies = company.get_multi(db, skip=skip, limit=limit)
    return companies

@router.post("/", response_model=Company, status_code=status.HTTP_201_CREATED)
def create_company(
    *,
    db: Session = Depends(get_db),
    company_in: CompanyCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create new company.
    Required fields:
    - name: Company name
    - business_email: Company's business email
    - business_category: Company's business category
    - terms_of_service: Company's terms of service text
    Optional fields:
    - gmail_box_credentials: Company's Gmail box credentials (JSON)
    - calendar_credentials: Company's calendar credentials (JSON)
    - gmail_box_app_password: Company's Gmail app password (string)
    - outlook_box_credentials: Company's Outlook box credentials (JSON)
    - outlook_box_email: Company's Outlook email address
    - outlook_box_username: Company's Outlook username
    - instagram_credentials: Company's Instagram credentials (JSON)
    - instagram_username: Company's Instagram username
    - instagram_account_id: Company's Instagram account ID
    - instagram_page_id: Company's Instagram page ID
    - facebook_box_credentials: Company's Facebook credentials (JSON)
    - facebook_box_page_id: Company's Facebook page ID
    - facebook_box_page_name: Company's Facebook page name
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"[CREATE_COMPANY] Starting company creation for user {current_user.id}")
        logger.info(f"[CREATE_COMPANY] Company data received: {company_in.model_dump()}")
        
        # Check if user already has a company
        if current_user.company_id:
            logger.warning(f"[CREATE_COMPANY] User {current_user.id} already has company_id: {current_user.company_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has a company",
            )

        logger.info(f"[CREATE_COMPANY] Checking if company name '{company_in.name}' already exists")
        db_company = company.get_by_name(db, name=company_in.name)
        if db_company:
            logger.warning(f"[CREATE_COMPANY] Company with name '{company_in.name}' already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company with this name already exists",
            )
        
        logger.info(f"[CREATE_COMPANY] Checking if business email '{company_in.business_email}' already exists")
        db_company = company.get_by_business_email(db, email=company_in.business_email)
        if db_company:
            logger.warning(f"[CREATE_COMPANY] Company with business email '{company_in.business_email}' already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company with this business email already exists",
            )
        
        logger.info(f"[CREATE_COMPANY] All validations passed, creating company...")
        
        # Create company
        logger.info(f"[CREATE_COMPANY] Calling company.create() with data: {company_in.model_dump()}")
        db_company = company.create(db=db, obj_in=company_in)
        logger.info(f"[CREATE_COMPANY] Company created successfully with ID: {db_company.id}")
        
        # Update user's company_id
        logger.info(f"[CREATE_COMPANY] Updating user {current_user.id} with company_id: {db_company.id}")
        current_user.company_id = db_company.id
        db.add(current_user)
        db.commit()
        db.refresh(current_user)
        logger.info(f"[CREATE_COMPANY] User updated successfully")
        
        logger.info(f"[CREATE_COMPANY] Company creation completed successfully for user {current_user.id}")
        return db_company
        
    except HTTPException as http_ex:
        logger.error(f"[CREATE_COMPANY] HTTPException occurred: {http_ex.detail}")
        raise http_ex
    except Exception as e:
        logger.error(f"[CREATE_COMPANY] Unexpected error occurred: {str(e)}")
        logger.error(f"[CREATE_COMPANY] Error type: {type(e).__name__}")
        logger.error(f"[CREATE_COMPANY] Error details: {e}")
        import traceback
        logger.error(f"[CREATE_COMPANY] Full traceback: {traceback.format_exc()}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating company: {str(e)}"
        )

@router.get("/{id}", response_model=Company)
def read_company(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get company by ID.
    """
    db_company = company.get(db=db, id=id)
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Ensure logo_url is a full URL
    if db_company.logo_url:
        db_company.logo_url = ensure_full_logo_url(db_company.logo_url)
    
    return db_company

@router.put("/{id}", response_model=Company)
def update_company(
    *,
    db: Session = Depends(get_db),
    id: int,
    company_in: CompanyUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update a company.
    All fields are optional for updates.
    """
    db_company = company.get(db=db, id=id)
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Check if name is being updated and already exists
    if company_in.name and company_in.name != db_company.name:
        existing_company = company.get_by_name(db, name=company_in.name)
        if existing_company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company with this name already exists",
            )
    
    # Check if business email is being updated and already exists
    if company_in.business_email and company_in.business_email != db_company.business_email:
        existing_company = company.get_by_business_email(db, email=company_in.business_email)
        if existing_company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company with this business email already exists",
            )
    
    updated_company = company.update(db=db, db_obj=db_company, obj_in=company_in)
    
    # Ensure logo_url is a full URL
    if updated_company.logo_url:
        updated_company.logo_url = ensure_full_logo_url(updated_company.logo_url)
    
    return updated_company

@router.delete("/{id}", response_model=Company)
def delete_company(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a company.
    """
    db_company = company.get(db=db, id=id)
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Check if user owns this company
    if current_user.company_id != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this company",
        )
    
    # Remove company_id from user
    user.update(db=db, db_obj=current_user, obj_in={"company_id": None})
    
    # Delete company
    return company.remove(db=db, id=id)

@router.get("/{id}/events", response_model=CalendarResponse)
async def get_company_calendar_events(
    *,
    db: Session = Depends(get_db),
    id: int,
    start_date: datetime = Query(..., description="Start date for events"),
    end_date: datetime = Query(..., description="End date for events"),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get calendar events for a company.
    """
    db_company = company.get(db=db, id=id)
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Check if user has access to this company
    if current_user.company_id != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this company's calendar",
        )
    
    # Check if company has calendar credentials
    if not db_company.calendar_credentials:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company has no calendar credentials configured",
        )
    
    return await calendar_service.get_company_calendar_events(
        db=db,
        company=db_company,
        start_time=start_date,
        end_time=end_date
    )

@router.post("/{id}/gmail/auth", response_model=dict)
def initiate_gmail_auth(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Initiate Gmail OAuth for a company and return the Google consent URL.
    Only accessible by users associated with the company.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with any company",
        )
    if current_user.company_id != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this company",
        )
    db_company = company.get(db=db, id=id)
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    try:
        auth_url = gmail_auth_service.get_auth_url(db_company)
        return {"auth_url": auth_url}
    except ValueError as e:
        if "no Gmail credentials" in str(e):
            raise HTTPException(status_code=400, detail="No Gmail credentials configured for this company")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}/gmail/callback")
def handle_gmail_callback(
    *,
    db: Session = Depends(get_db),
    id: int,
    code: str,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Handle Gmail OAuth callback and store credentials for the company.
    Only accessible by users associated with the company.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with any company",
        )
    if current_user.company_id != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this company",
        )
    db_company = company.get(db=db, id=id)
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    try:
        gmail_auth_service.handle_auth_callback(db, db_company, code)
        return {"success": True}
    except ValueError as e:
        if "no Gmail credentials" in str(e):
            raise HTTPException(status_code=400, detail="No Gmail credentials configured for this company")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{id}/gmail/channels", response_model=dict)
async def get_company_gmail_channels(
    *,
    db: Session = Depends(get_db),
    id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(30, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get paginated Gmail channels (subjects and content) for a company, only those created after the company's creation date.
    Only accessible by users associated with the company.
    Now: Only fetch page_size messages for the requested page, then filter by company.created_at.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with any company",
        )
    if current_user.company_id != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this company",
        )
    db_company = company.get(db=db, id=id)
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    # creds = gmail_monitor_service._get_credentials(db_company, db)
    # if not creds:
    #     raise HTTPException(status_code=400, detail="No Gmail credentials configured for this company")
    try:
        # Fetch emails from database instead of Gmail API
        from sqlalchemy import func
        
        # Get all chat messages for this company, grouped by channel_id
        chat_messages = db.query(Chat).filter(
            Chat.company_id == id
        ).order_by(Chat.sent_at.desc()).all()
        
        # Group messages by channel_id
        channel_groups = {}
        
        for chat_msg in chat_messages:
            channel_id = chat_msg.channel_id
            
            # Skip if we already processed this channel
            if channel_id in channel_groups:
                continue
            
            # Get all messages for this channel
            channel_messages = db.query(Chat).filter(
                Chat.company_id == id,
                Chat.channel_id == channel_id
            ).order_by(Chat.sent_at.asc()).all()
            
            bodies = []
            channel_should_include = False
            
            for msg in channel_messages:
                # Use shared AI filter
                if await filter_email_with_ai(msg.from_email, msg.body_text):
                    channel_should_include = True
                
                # Add message to bodies
                bodies.append({
                    'from': msg.from_email, 
                    'date': msg.sent_at.isoformat(), 
                    'content': msg.body_text, 
                    'html': msg.body_html, 
                    'read': msg.is_read,
                    'notification_read': msg.notification_read,
                    'message_id': msg.message_id,
                    'action_required': msg.action_required or False,
                    'action_reason': msg.action_reason or '',
                    'action_type': msg.action_type or '',
                    'urgency': msg.urgency or ''
                })
            
            if not channel_should_include:
                continue
            
            # Get channel metadata from the first message
            first_msg = channel_messages[0] if channel_messages else None
            if not first_msg:
                continue
        
            # Get auto-reply settings for this channel
            channel_settings = channel_auto_reply_settings.get_by_channel_id(db, channel_id=channel_id)
            enable_auto_reply = channel_settings.enable_auto_reply if channel_settings else True
            
            # Determine email provider from the first message
            email_provider = first_msg.email_provider or 'unknown'
            
            channel_groups[channel_id] = {
                'id': channel_id,  # Use channel_id as the channel ID
                'thread_id': channel_id,  # Keep for frontend compatibility
                'channel': first_msg.subject,
                'from': first_msg.from_email,
                'date': first_msg.sent_at.isoformat(),
                'bodies': bodies,
                'read': first_msg.is_read,
                'enable_auto_reply': enable_auto_reply,
                'email_provider': email_provider,  # Add email provider information
            }
        
        # Convert to list and sort by date descending
        result = list(channel_groups.values())
        result.sort(key=lambda x: x['date'], reverse=True)
        
        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_result = result[start_idx:end_idx]
        
        has_more = end_idx < len(result)
        
        return {
            'channels': paginated_result,
            'total': len(result),
            'page': page,
            'page_size': page_size,
            'has_more': has_more
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch Gmail channels: {str(e)}")

@router.put("/chats/{chat_id}/mark-as-read")
def mark_chat_as_read(
    *,
    db: Session = Depends(get_db),
    chat_id: str,
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """
    Mark all chat messages with the same channel_id as read.
    """
    # Get all messages with the same channel_id
    db_chats = db.query(Chat).filter(Chat.channel_id == chat_id).all()
    if not db_chats:
        raise HTTPException(status_code=404, detail="Chat messages not found")
    
    # Check if the current user has access to these chats
    if current_user.company_id != db_chats[0].company_id:
        raise HTTPException(status_code=403, detail="Not enough permissions to mark these chats as read")
    
    # Mark all messages as read in the database
    for db_chat in db_chats:
        db_chat.is_read = True
        db.add(db_chat)
    
    db.commit()
    
    # Call Gmail API to mark all messages in the thread as read
    try:
        company = db.query(CompanyModel).filter(CompanyModel.id == current_user.company_id).first()
        if company and company.gmail_box_credentials:
            creds = gmail_monitor_service._get_credentials(company, db)
            if creds:
                service = build('gmail', 'v1', credentials=creds)
                # Remove the UNREAD label from all Gmail messages in the thread
                for db_chat in db_chats:
                    try:
                        service.users().messages().modify(
                            userId='me',
                            id=db_chat.message_id,
                            body={'removeLabelIds': ['UNREAD']}
                        ).execute()
                        print(f"[DEBUG] Marked Gmail message {db_chat.message_id} as read")
                    except Exception as e:
                        print(f"[DEBUG] Error marking Gmail message {db_chat.message_id} as read: {str(e)}")
                        # Continue with other messages even if one fails
    except Exception as e:
        print(f"[DEBUG] Error accessing Gmail API: {str(e)}")
        # Continue even if Gmail API call fails
    
    return {"success": True, "message": f"Marked {len(db_chats)} chat messages as read"}


@router.post("/chats/{message_id}/send-feedback")
def send_feedback(
    *,
    db: Session = Depends(get_db),
    message_id: str,
    feedback: str = Body(..., embed=True),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """
    Add feedback to a chat message by message_id.
    """
    chat = db.query(Chat).filter(Chat.message_id == message_id).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat message not found")
    
    # Update the chat message with feedback
    chat.feedback = feedback
    db.add(chat)
    db.commit()
    
    # Store feedback in channel context
    channel_context_service.store_feedback_in_context(
        db=db,
        message_id=message_id,
        feedback=feedback,
        user_id=current_user.id
    )
    
    return {"success": True, "message": "Feedback added"}


@router.post("/channels/{channel_id}/disable-auto-reply", response_model=ChannelAutoReplySettings)
def disable_channel_auto_reply(
    *,
    db: Session = Depends(get_db),
    channel_id: str,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Disable auto-reply for a specific channel.
    This will set enable_auto_reply to False for the given channel_id.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with any company",
        )
    
    # Update or create settings to disable auto-reply
    settings_update = ChannelAutoReplySettingsUpdate(enable_auto_reply=False)
    settings = channel_auto_reply_settings.update_by_channel_id(
        db, 
        channel_id=channel_id, 
        obj_in=settings_update
    )
    
    return settings


@router.post("/channels/{channel_id}/enable-auto-reply", response_model=ChannelAutoReplySettings)
def enable_channel_auto_reply(
    *,
    db: Session = Depends(get_db),
    channel_id: str,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Enable auto-reply for a specific channel.
    This will set enable_auto_reply to True for the given channel_id.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with any company",
        )
    
    # Update or create settings to enable auto-reply
    settings_update = ChannelAutoReplySettingsUpdate(enable_auto_reply=True)
    settings = channel_auto_reply_settings.update_by_channel_id(
        db, 
        channel_id=channel_id, 
        obj_in=settings_update
    )
    
    return settings


@router.get("/channels/{channel_id}/context")
def get_channel_context(
    *,
    db: Session = Depends(get_db),
    channel_id: str,
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """
    Get the full context for a specific channel.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with any company",
        )
    
    context_data = channel_context_service.get_channel_context(
        db=db,
        channel_id=channel_id,
        company_id=current_user.company_id
    )
    
    if not context_data:
        return {"context": None, "message": "No context found for this channel"}
    
    return {"context": context_data}


@router.get("/channels/contexts")
def get_all_channel_contexts(
    *,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """
    Get all channel contexts for the current user's company.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with any company",
        )
    
    contexts = channel_context_service.get_all_contexts_for_company(
        db=db,
        company_id=current_user.company_id,
        skip=skip,
        limit=limit
    )
    
    return {"contexts": contexts, "total": len(contexts)}


@router.post("/channels/sync-contexts")
def sync_existing_chat_messages(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """
    Sync existing chat messages to channel context (for migration).
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with any company",
        )
    
    synced_count = channel_context_service.sync_existing_chat_messages(
        db=db,
        company_id=current_user.company_id
    )
    
    return {
        "success": True,
        "message": f"Synced {synced_count} chat messages to channel context",
        "synced_count": synced_count
    }


@router.post("/{id}/logo", response_model=dict)
def upload_company_logo(
    *,
    db: Session = Depends(get_db),
    id: int,
    logo: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Upload a company logo.
    Only accessible by users associated with the company.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with any company",
        )
    if current_user.company_id != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to upload logo for this company",
        )
    
    db_company = company.get(db=db, id=id)
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Validate file type
    if not logo.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    # Validate file size (5MB limit)
    if logo.size > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 5MB"
        )
    
    try:
        # For now, we'll store the file in a local directory
        # In production, you'd want to use a cloud storage service like AWS S3
        import os
        from pathlib import Path
        
        # Create uploads directory if it doesn't exist
        upload_dir = Path("uploads/logos")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_extension = Path(logo.filename).suffix
        filename = f"company_{id}_logo_{int(time.time())}{file_extension}"
        file_path = upload_dir / filename
        
        # Save the file
        with open(file_path, "wb") as buffer:
            content = logo.file.read()
            buffer.write(content)
        
        # Generate URL for the uploaded file
        logo_url = f"{settings.BACKEND_URL}/uploads/logos/{filename}"
        
        # Update company with logo URL
        company_update = CompanyUpdate(logo_url=logo_url)
        updated_company = company.update(db=db, db_obj=db_company, obj_in=company_update)
        
        return {
            "success": True,
            "logo_url": ensure_full_logo_url(logo_url),
            "message": "Logo uploaded successfully"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error uploading logo: {str(e)}"
        )


@router.get("/{id}/logo", response_model=dict)
def get_company_logo(
    *,
    db: Session = Depends(get_db),
    id: int,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get company logo URL.
    Only accessible by users associated with the company.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with any company",
        )
    if current_user.company_id != id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access logo for this company",
        )
    
    db_company = company.get(db=db, id=id)
    if not db_company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Ensure logo_url is a full URL
    logo_url = ensure_full_logo_url(db_company.logo_url)
    
    return {
        "logo_url": logo_url,
        "success": True
    }

@router.get("/test-logging")
def test_logging():
    """Test endpoint to verify logging is working"""
    import logging
    logger = logging.getLogger(__name__)
    logger.info("[TEST] This is a test log message")
    logger.warning("[TEST] This is a test warning message")
    logger.error("[TEST] This is a test error message")
    return {"message": "Logging test completed", "check": "app.log file and console output"}

