from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.chat import Chat
from app.schemas.notification import (
    NotificationReadResponse, 
    BulkNotificationUpdate,
    NotificationUpdate
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.put("/{message_id}/mark-read", response_model=NotificationReadResponse)
def mark_notification_as_read(
    *,
    db: Session = Depends(get_db),
    message_id: str,
    notification_update: NotificationUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Mark a notification as read/unread for a specific message.
    """
    # Find the chat message
    chat_message = db.query(Chat).filter(Chat.message_id == message_id).first()
    if not chat_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat message not found",
        )
    
    # Check if the current user has access to this chat
    if current_user.company_id != chat_message.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this chat",
        )
    
    # Update the notification_read status
    chat_message.notification_read = notification_update.notification_read
    db.add(chat_message)
    db.commit()
    db.refresh(chat_message)
    
    logger.info(f"Marked notification as {'read' if notification_update.notification_read else 'unread'} for message {message_id}")
    
    return NotificationReadResponse(
        success=True,
        message=f"Notification marked as {'read' if notification_update.notification_read else 'unread'}",
        notification_read=notification_update.notification_read
    )

@router.put("/bulk-mark-read", response_model=NotificationReadResponse)
def mark_multiple_notifications_as_read(
    *,
    db: Session = Depends(get_db),
    bulk_update: BulkNotificationUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Mark multiple notifications as read/unread for a list of message IDs.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any company",
        )
    
    # Find all chat messages for the given message IDs that belong to the user's company
    chat_messages = db.query(Chat).filter(
        Chat.message_id.in_(bulk_update.message_ids),
        Chat.company_id == current_user.company_id
    ).all()
    
    if not chat_messages:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No chat messages found for the provided message IDs",
        )
    
    # Update the notification_read status for all found messages
    updated_count = 0
    for chat_message in chat_messages:
        chat_message.notification_read = bulk_update.notification_read
        db.add(chat_message)
        updated_count += 1
    
    db.commit()
    
    logger.info(f"Marked {updated_count} notifications as {'read' if bulk_update.notification_read else 'unread'}")
    
    return NotificationReadResponse(
        success=True,
        message=f"Marked {updated_count} notifications as {'read' if bulk_update.notification_read else 'unread'}",
        notification_read=bulk_update.notification_read
    )

@router.get("/unread-count")
def get_unread_notifications_count(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get the count of unread notifications for the current user's company.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any company",
        )
    
    # Count unread notifications for the company
    unread_count = db.query(Chat).filter(
        Chat.company_id == current_user.company_id,
        Chat.notification_read == False
    ).count()
    
    return {
        "unread_count": unread_count,
        "company_id": current_user.company_id
    }

@router.get("/unread")
def get_unread_notifications(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    limit: int = 50,
) -> Any:
    """
    Get unread notifications for the current user's company.
    """
    if not current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not associated with any company",
        )
    
    # Get unread notifications for the company
    unread_notifications = db.query(Chat).filter(
        Chat.company_id == current_user.company_id,
        Chat.notification_read == False
    ).order_by(Chat.sent_at.desc()).limit(limit).all()
    
    # Format the response
    notifications = []
    for chat in unread_notifications:
        notifications.append({
            "message_id": chat.message_id,
            "channel_id": chat.channel_id,
            "from_email": chat.from_email,
            "subject": chat.subject,
            "sent_at": chat.sent_at.isoformat() if chat.sent_at else None,
            "action_required": chat.action_required or False,
            "action_reason": chat.action_reason or "",
            "action_type": chat.action_type or "",
            "urgency": chat.urgency or "",
            "notification_read": chat.notification_read
        })
    
    return {
        "notifications": notifications,
        "total_count": len(notifications)
    } 