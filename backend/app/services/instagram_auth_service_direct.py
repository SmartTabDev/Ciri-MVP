import logging
import requests
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from app.core.config import settings
import asyncio
from urllib.parse import urlencode
import secrets

logger = logging.getLogger(__name__)

class InstagramAuthService:
    def __init__(self):
        self.instagram_app_id = settings.INSTAGRAM_APP_ID
        self.instagram_app_secret = settings.INSTAGRAM_APP_SECRET
        self.instagram_redirect_uri = settings.INSTAGRAM_REDIRECT_URI

    def get_instagram_auth_url(self, state: str | None = None) -> str:
        base = "https://www.instagram.com/oauth/authorize"
        scopes = ",".join([
            "instagram_business_basic",
            "instagram_business_manage_comments",
            "instagram_business_manage_messages",
            "instagram_business_content_publish",
            "instagram_business_manage_insights"
        ])
        params = {
            "client_id": self.instagram_app_id,
            "redirect_uri": self.instagram_redirect_uri,          # MUST exactly match whitelisted URL
            "response_type": "code",
            "scope": scopes,                         # comma-separated works
            "state": state or secrets.token_urlsafe(16),
            "force_reauth" : True,
        }
        print(f"{base}?{urlencode(params)}")
        return f"{base}?{urlencode(params)}"

    async def exchange_instagram_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        """
        1) Exchange authorization code -> short-lived token (multipart/form-data to mirror curl -F)
        2) (Optional) Immediately exchange short-lived -> long-lived token
        """
        short_url = "https://api.instagram.com/oauth/access_token"

        # Data to send (same fields as your curl)
        payload = {
            "client_id": self.instagram_app_id,
            "client_secret": self.instagram_app_secret,
            "grant_type": "authorization_code",
            "redirect_uri": self.instagram_redirect_uri,  # must match EXACTLY
            "code": code,
        }

        try:
            # ---- Step 1: send as multipart/form-data (like curl -F) ----
            # Using requests in a thread so we don't block the event loop
            files = {k: (None, v) for k, v in payload.items()}  # (None, value) => form field
            resp = await asyncio.to_thread(
                requests.post,
                short_url,
                files=files,          # <- multipart/form-data
                timeout=20,
            )
            resp.raise_for_status()
            short = resp.json()  # {'access_token': '...', 'user_id': ...}

            access_token = short.get("access_token")
            logger.info("Instagram short-lived token : %s", access_token)

            if not access_token:
                logger.error("Instagram short-lived token missing: %s", short)
                return None

            # ---- Step 2 (optional): exchange for long-lived token ----
            # Comment out this whole block if you only need the short-lived token.
            long_url = "https://graph.instagram.com/access_token"
            long_resp = await asyncio.to_thread(
                requests.get,
                long_url,
                params={
                    "grant_type": "ig_exchange_token",
                    "client_secret": self.instagram_app_secret,
                    "access_token": access_token,
                },
                timeout=20,
            )
            long_resp.raise_for_status()
            long_token = long_resp.json()  # {'access_token': '...', 'token_type': 'bearer', 'expires_in': 5184000}

            logger.info("IG code exchange successful (short + long-lived).")
            return {"short_lived": short, "long_lived": long_token, "access_token": long_token.get("access_token",access_token)}

        except requests.RequestException as e:
            # Instagram errors often return JSON with 'error_message' or 'error_description'
            body = None
            try:
                body = resp.json() if 'resp' in locals() and resp is not None else None
            except Exception:
                pass
            logger.error("IG token exchange failed: %s | response=%s", e, body)
            return None
        
    def ig_exchange_short_to_long(short_token: str, app_secret: str) -> dict:
        r = requests.get(
            "https://graph.instagram.com/access_token",
            params={
                "grant_type": "ig_exchange_token",
                "client_secret": app_secret,
                "access_token": short_token,
            },
            timeout=20,
        )
        r.raise_for_status()
        return r.json()  # { access_token, token_type, expires_in }
 
    async def get_instagram_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Get Instagram user information using access token.
        """
        try:
            url = "https://graph.instagram.com/v23.0/me"
            params = {
                "fields": "id,username,account_type,name,profile_picture_url",
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

    async def get_instagram_page_user_info(self, access_token: str, page_id: str) -> Optional[Dict[str, Any]]:
        """
        Get Instagram page information using access token and page ID.
        """
        try:
            url = f"https://graph.facebook.com/{page_id}"
            params = {
                "fields": "id,name,username",
                "access_token": access_token
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            user_info = response.json()
            logger.info(f"Successfully retrieved Instagram user info: {user_info}")
            return user_info
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting Instagram user info: {str(e)}")
            return None
        
    async def get_instagram_user_accounts(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Get Instagram user accounts using access token.
        """
        try:
            url = "https://graph.facebook.com/me/accounts"
            params = {
                "fields": "connected_instagram_account,name,access_token",
                "access_token": access_token
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            user_accounts_info = response.json()
            logger.info(f"Successfully retrieved Instagram user accounts info: {user_accounts_info}")
            return user_accounts_info
            
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