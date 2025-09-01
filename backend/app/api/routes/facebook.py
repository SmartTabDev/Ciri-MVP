from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.db.session import get_db
from app.models.company import Company
from app.models.user import User
from app.services.facebook_auth_service import facebook_auth_service
from app.services.facebook_monitor_service import facebook_monitor_service
from app.api.deps import get_current_active_user
from app.schemas.facebook import (
    FacebookAuthResponse,
    FacebookAccountInfo,
    FacebookMessageResponse,
    FacebookAuthCallback,
    FacebookPagesResponse
)

router = APIRouter(prefix="", tags=["facebook"])

@router.get("/auth-url", response_model=FacebookAuthResponse)
async def get_facebook_auth_url(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get Facebook authorization URL for the current user's company.
    """
    try:
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        print(company.id)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Generate Facebook auth URL
        facebook_auth_url = facebook_auth_service.get_facebook_auth_url(
            state=f"company_{company.id}"
        )
        
        return FacebookAuthResponse(
            facebook_auth_url=facebook_auth_url,
            message="Connect your Facebook page for messaging and comments"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating auth URL: {str(e)}")

@router.post("/auth/callback", response_model=FacebookAccountInfo)
async def facebook_auth_callback(
    auth_data: FacebookAuthCallback,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Handle Facebook authorization callback and store credentials.
    """
    try:
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Exchange code for token
        token_data = await facebook_auth_service.exchange_facebook_code_for_token(auth_data.code)
        if not token_data:
            raise HTTPException(status_code=400, detail="Failed to exchange Facebook code for token")
        
        # Get user info
        user_info = await facebook_auth_service.get_facebook_user_info(token_data.get('access_token'))
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get Facebook user info")
        
        # Get Facebook pages
        pages_data = await facebook_auth_service.get_facebook_pages(token_data.get('access_token'))
        if not pages_data or not pages_data.get('data'):
            raise HTTPException(status_code=400, detail="No Facebook pages found")
        
        # Use the first page found (you could add logic to let user choose)
        page = pages_data['data'][0]
        
        # Store credentials
        company.facebook_box_credentials = {
            'access_token': token_data.get('access_token'),
            'expires_at': token_data.get('expires_at'),
            'user_id': user_info.get('id'),
            'page_id': page.get('id'),
            'page_name': page.get('name'),
            'page_access_token': page.get('access_token'),
            'category': page.get('category'),
            'fan_count': page.get('fan_count')
        }
        company.facebook_box_page_id = page.get('id')
        company.facebook_box_page_name = page.get('name')
        
        db.commit()
        
        return FacebookAccountInfo(
            page_id=company.facebook_box_page_id,
            page_name=company.facebook_box_page_name,
            connected=True,
            message="Facebook page connected successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing auth callback: {str(e)}")

@router.get("/account", response_model=FacebookAccountInfo)
async def get_facebook_account_info(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get Facebook account information for the current user's company.
    """
    try:
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        if not company.facebook_box_credentials:
            return FacebookAccountInfo(
                connected=False,
                message="No Facebook page connected"
            )
        
        return FacebookAccountInfo(
            page_id=company.facebook_box_page_id,
            page_name=company.facebook_box_page_name,
            connected=True,
            message="Facebook page is connected"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting account info: {str(e)}")

@router.get("/pages", response_model=FacebookPagesResponse)
async def get_facebook_pages(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get available Facebook pages for the current user.
    """
    try:
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        if not company.facebook_box_credentials:
            raise HTTPException(status_code=400, detail="No Facebook credentials found")
        
        credentials = company.facebook_box_credentials
        if isinstance(credentials, str):
            credentials = json.loads(credentials)
        
        # Get pages using the user access token
        pages_data = await facebook_auth_service.get_facebook_pages(credentials.get('access_token'))
        if not pages_data:
            return FacebookPagesResponse(pages=[])
        
        pages = []
        for page in pages_data.get('data', []):
            pages.append({
                'id': page.get('id'),
                'name': page.get('name'),
                'access_token': page.get('access_token'),
                'category': page.get('category'),
                'fan_count': page.get('fan_count')
            })
        
        return FacebookPagesResponse(pages=pages)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting pages: {str(e)}")

@router.delete("/disconnect")
async def disconnect_facebook_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Disconnect Facebook account from the company.
    """
    try:
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        # Clear Facebook credentials
        company.facebook_box_credentials = None
        company.facebook_box_page_id = None
        company.facebook_box_page_name = None
        
        db.commit()
        
        return {"message": "Facebook account disconnected successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error disconnecting account: {str(e)}")

@router.post("/refresh-token")
async def refresh_facebook_token(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Refresh Facebook access token.
    """
    try:
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        if not company.facebook_box_credentials:
            raise HTTPException(status_code=400, detail="No Facebook account connected")
        
        credentials = company.facebook_box_credentials
        if isinstance(credentials, str):
            credentials = json.loads(credentials)
        
        # Refresh token
        new_token_data = await facebook_auth_service.refresh_facebook_token(credentials.get('access_token'))
        if new_token_data:
            updated_credentials = {
                **credentials,
                'access_token': new_token_data.get('access_token'),
                'expires_at': new_token_data.get('expires_at', credentials.get('expires_at'))
            }
            company.facebook_box_credentials = updated_credentials
            db.commit()
            return {"message": "Token refreshed successfully"}
        
        raise HTTPException(status_code=400, detail="Could not refresh token")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refreshing token: {str(e)}")

@router.get("/messages", response_model=List[FacebookMessageResponse])
async def get_facebook_messages(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get recent Facebook messages for the company.
    """
    try:
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        if not company.facebook_box_credentials:
            raise HTTPException(status_code=400, detail="No Facebook account connected")
        
        # This would typically fetch from the database
        # For now, return empty list as messages are stored in the Chat table
        return []
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting messages: {str(e)}")

@router.post("/test-connection")
async def test_facebook_connection(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Test Facebook connection by polling for messages.
    """
    try:
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        if not company.facebook_box_credentials:
            raise HTTPException(status_code=400, detail="No Facebook account connected")
        
        # Test the connection by polling for messages
        return {await facebook_monitor_service.poll_facebook_messages(company.id)}
        
        return {"message": "Facebook connection test completed successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing connection: {str(e)}")
