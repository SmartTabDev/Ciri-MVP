from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.db.session import get_db
from app.models.company import Company
from app.models.user import User
from app.services.instagram_auth_service import instagram_auth_service
from app.services.instagram_monitor_service import instagram_monitor_service
from app.api.deps import get_current_active_user
from app.schemas.instagram import (
    InstagramAuthResponse,
    InstagramAccountInfo,
    InstagramMessageResponse,
    InstagramAuthCallback
)

router = APIRouter(prefix="/instagram", tags=["instagram"])

@router.get("/auth-url", response_model=InstagramAuthResponse)
async def get_instagram_auth_url(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get Instagram authorization URL for the current user's company.
    """
    try:
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Generate Instagram Basic Display API auth URL
        instagram_auth_url = instagram_auth_service.get_instagram_auth_url(
            state=f"company_{company.id}"
        )
        
        return InstagramAuthResponse(
            instagram_auth_url=instagram_auth_url,
            message="Instagram Basic Display API authorization URL generated"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating auth URL: {str(e)}")

@router.post("/auth/callback", response_model=InstagramAccountInfo)
async def instagram_auth_callback(
    auth_data: InstagramAuthCallback,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Handle Instagram authorization callback and store credentials.
    """
    try:
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Handle Instagram Basic Display API callback
        token_data = await instagram_auth_service.exchange_instagram_code_for_token(auth_data.code)
        if not token_data:
            raise HTTPException(status_code=400, detail="Failed to exchange Instagram code for token")
        
        # Get user info
        user_info = await instagram_auth_service.get_instagram_user_info(token_data.get('access_token'))
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get Instagram user info")
        
        # Store credentials
        company.instagram_credentials = {
            'access_token': token_data.get('access_token'),
            'refresh_token': token_data.get('refresh_token'),
            'expires_at': token_data.get('expires_at'),
            'user_id': user_info.get('id'),
            'username': user_info.get('username'),
            'account_type': user_info.get('account_type')
        }
        company.instagram_username = user_info.get('username')
        company.instagram_account_id = user_info.get('id')
        
        db.commit()
        
        return InstagramAccountInfo(
            account_id=company.instagram_account_id,
            username=company.instagram_username,
            page_id=company.instagram_page_id,
            connected=True,
            message="Instagram account connected successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing auth callback: {str(e)}")

@router.get("/account", response_model=InstagramAccountInfo)
async def get_instagram_account_info(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get Instagram account information for the current user's company.
    """
    try:
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        if not company.instagram_credentials:
            return InstagramAccountInfo(
                connected=False,
                message="No Instagram account connected"
            )
        
        return InstagramAccountInfo(
            account_id=company.instagram_account_id,
            username=company.instagram_username,
            page_id=company.instagram_page_id,
            connected=True,
            message="Instagram account is connected"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting account info: {str(e)}")

@router.delete("/disconnect")
async def disconnect_instagram_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Disconnect Instagram account from the company.
    """
    try:
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Clear Instagram credentials
        company.instagram_credentials = None
        company.instagram_account_id = None
        company.instagram_username = None
        company.instagram_page_id = None
        
        db.commit()
        
        return {"message": "Instagram account disconnected successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error disconnecting account: {str(e)}")

@router.post("/refresh-token")
async def refresh_instagram_token(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Refresh Instagram access token.
    """
    try:
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        if not company.instagram_credentials:
            raise HTTPException(status_code=400, detail="No Instagram account connected")
        
        # Refresh token
        new_token_data = await instagram_auth_service.refresh_instagram_token(
            company.instagram_credentials.get('refresh_token')
        )
        
        if not new_token_data:
            raise HTTPException(status_code=400, detail="Failed to refresh token")
        
        # Update credentials
        company.instagram_credentials.update({
            'access_token': new_token_data.get('access_token'),
            'expires_at': new_token_data.get('expires_at')
        })
        
        db.commit()
        
        return {"message": "Instagram token refreshed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing token: {str(e)}")

@router.get("/messages", response_model=InstagramMessageResponse)
async def get_instagram_messages(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get Instagram messages for the current user's company.
    """
    try:
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        if not company.instagram_credentials:
            raise HTTPException(status_code=400, detail="No Instagram account connected")
        
        # Get messages from Instagram
        messages = await instagram_monitor_service.get_instagram_messages(
            company.instagram_credentials,
            limit=limit
        )
        
        return InstagramMessageResponse(
            messages=messages,
            count=len(messages),
            message="Instagram messages retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting messages: {str(e)}")

@router.post("/test-connection")
async def test_instagram_connection(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Test Instagram connection by attempting to get user info.
    """
    try:
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        if not company.instagram_credentials:
            raise HTTPException(status_code=400, detail="No Instagram account connected")
        
        # Test connection by getting user info
        user_info = await instagram_auth_service.get_instagram_user_info(
            company.instagram_credentials.get('access_token')
        )
        
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info - connection may be invalid")
        
        return {
            "connected": True,
            "username": user_info.get('username'),
            "user_id": user_info.get('id'),
            "message": "Instagram connection is working"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing connection: {str(e)}") 