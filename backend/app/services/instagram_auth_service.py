import logging
import requests
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from app.core.config import settings

logger = logging.getLogger(__name__)

class InstagramAuthService:
    def __init__(self):
        self.instagram_app_id = settings.INSTAGRAM_APP_ID
        self.instagram_app_secret = settings.INSTAGRAM_APP_SECRET
        self.instagram_redirect_uri = settings.INSTAGRAM_REDIRECT_URI

    def get_instagram_auth_url(self, state: str = None) -> str:
        """
        Generate Instagram Basic Display API authorization URL.
        """
        base_url = "https://api.instagram.com/oauth/authorize"
        params = {
            "client_id": self.instagram_app_id,
            "redirect_uri": self.instagram_redirect_uri,
            "scope": "user_profile,user_media",
            "response_type": "code",
            "state": state or "instagram_auth"
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"

    async def exchange_instagram_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Exchange Instagram authorization code for access token.
        """
        try:
            url = "https://api.instagram.com/oauth/access_token"
            data = {
                "client_id": self.instagram_app_id,
                "client_secret": self.instagram_app_secret,
                "grant_type": "authorization_code",
                "redirect_uri": self.instagram_redirect_uri,
                "code": code
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            logger.info(f"Successfully exchanged Instagram code for token")
            return token_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error exchanging Instagram code for token: {str(e)}")
            return None

    async def get_instagram_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Get Instagram user information using access token.
        """
        try:
            url = "https://graph.instagram.com/me"
            params = {
                "fields": "id,username,account_type",
                "access_token": access_token
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            user_info = response.json()
            logger.info(f"Successfully retrieved Instagram user info: {user_info.get('username')}")
            return user_info
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting Instagram user info: {str(e)}")
            return None

    async def refresh_instagram_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Refresh Instagram access token using refresh token.
        """
        try:
            url = "https://graph.instagram.com/refresh_access_token"
            params = {
                "grant_type": "ig_refresh_token",
                "access_token": refresh_token
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            token_data = response.json()
            logger.info("Successfully refreshed Instagram token")
            return token_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error refreshing Instagram token: {str(e)}")
            return None

# Create a singleton instance
instagram_auth_service = InstagramAuthService() 