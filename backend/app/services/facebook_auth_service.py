import logging,anyio
import requests
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from app.core.config import settings

logger = logging.getLogger(__name__)

class FacebookAuthService:
    def __init__(self):
        self.facebook_app_id = settings.FACEBOOK_APP_ID
        self.facebook_app_secret = settings.FACEBOOK_APP_SECRET
        self.facebook_redirect_uri = settings.FACEBOOK_REDIRECT_URI

    def get_facebook_auth_url(self, state: str = None) -> str:
        """
        Generate Facebook authorization URL for Facebook Pages and Messenger.
        """
        base_url = "https://www.facebook.com/v18.0/dialog/oauth"
        params = {
            "client_id": self.facebook_app_id,
            "redirect_uri": self.facebook_redirect_uri,
            "scope": "pages_show_list,pages_read_engagement,pages_manage_posts,pages_messaging,pages_manage_metadata",
            "response_type": "code",
            "state": state or "facebook_auth"
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"

    async def exchange_facebook_code_for_token(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Exchange Facebook authorization code for access token.
        """
        try:
            url = "https://graph.facebook.com/v18.0/oauth/access_token"
            params = {
                "client_id": self.facebook_app_id,
                "client_secret": self.facebook_app_secret,
                "redirect_uri": self.facebook_redirect_uri,
                "code": code
            }
            
            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()
            
            token_data = response.json()
            logger.info(f"Successfully exchanged Facebook code for token")
            return token_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error exchanging Facebook code for token: {str(e)}")
            return None
    
    async def get_facebook_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Get Facebook user information using access token.
        Stays async, but executes blocking `requests.get` in a worker thread.
        """
        try:
            url = "https://graph.facebook.com/me"
            params = {
                "fields": "id,name,email",
                "access_token": access_token
            }

            def _do_request():
                r = requests.get(url, params=params, timeout=20)
                r.raise_for_status()
                return r.json()

            user_info = await anyio.to_thread.run_sync(_do_request)
            logger.info(f"Successfully retrieved Facebook user info: {user_info.get('name')}")
            return user_info

        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting Facebook user info: {str(e)}")
            return None

    async def get_facebook_pages(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Get Facebook pages that the user manages.
        """
        try:
            url = "https://graph.facebook.com/me/accounts"
            params = {
                "access_token": access_token,
                "fields": "id,name,access_token,category,fan_count"
            }
            
            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()
            
            pages_data = response.json()
            logger.info(f"Found {len(pages_data.get('data', []))} Facebook pages")
            return pages_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting Facebook pages: {str(e)}")
            return None

    async def get_page_messages(self, page_id: str, page_access_token: str, limit: int = 10) -> Optional[Dict[str, Any]]:
        """
        Get messages from a Facebook page (requires pages_messaging permission).
        """
        try:
            url = f"https://graph.facebook.com/v18.0/{page_id}/conversations"
            params = {
                "access_token": page_access_token,
                "fields": "id,participants,messages{id,message,from,created_time}",
                "limit": limit
            }
            
            response = requests.get(url, params=params, timeout=20)
            if response.status_code == 200:
                conversations_data = response.json()
                logger.info(f"Retrieved {len(conversations_data.get('data', []))} conversations")
                return conversations_data
            else:
                logger.warning(f"Could not retrieve page messages: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting Facebook page messages: {str(e)}")
            return None

    async def get_page_posts(self, page_id: str, page_access_token: str, limit: int = 10) -> Optional[Dict[str, Any]]:
        """
        Get posts from a Facebook page.
        """
        try:
            url = f"https://graph.facebook.com/v18.0/{page_id}/posts"
            params = {
                "access_token": page_access_token,
                "fields": "id,message,created_time,comments{id,message,from,created_time}",
                "limit": limit
            }
            
            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()
            
            posts_data = response.json()
            logger.info(f"Retrieved {len(posts_data.get('data', []))} posts")
            return posts_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting Facebook page posts: {str(e)}")
            return None

    async def refresh_facebook_token(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        Refresh Facebook access token.
        """
        try:
            url = "https://graph.facebook.com/v18.0/oauth/access_token"
            params = {
                "grant_type": "fb_exchange_token",
                "client_id": self.facebook_app_id,
                "client_secret": self.facebook_app_secret,
                "fb_exchange_token": access_token
            }
            
            response = requests.get(url, params=params, timeout=20)
            response.raise_for_status()
            
            token_data = response.json()
            logger.info("Successfully refreshed Facebook token")
            return token_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error refreshing Facebook token: {str(e)}")
            return None

    async def send_page_message(self, page_id: str, page_access_token: str, recipient_id: str, message: str) -> Optional[Dict[str, Any]]:
        """
        Send a message from a Facebook page (requires pages_messaging permission).
        """
        try:
            url = f"https://graph.facebook.com/v18.0/{page_id}/messages"
            data = {
                "recipient": {"id": recipient_id},
                "message": {"text": message},
                "access_token": page_access_token
            }
            
            response = requests.post(url, json=data, timeout=20)
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Successfully sent Facebook message to {recipient_id}")
                return result
            else:
                logger.warning(f"Could not send Facebook message: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending Facebook message: {str(e)}")
            return None

# Create a singleton instance
facebook_auth_service = FacebookAuthService()
