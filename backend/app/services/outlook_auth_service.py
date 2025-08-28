import requests
import json
import logging
import urllib3
import ssl
from typing import Dict, Any, Optional
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3.poolmanager import PoolManager
from app.core.config import settings

# Disable SSL warnings for development (remove in production)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

class CustomHTTPAdapter(HTTPAdapter):
    """Custom HTTP adapter with SSL configuration"""
    
    def init_poolmanager(self, connections, maxsize, block=False):
        """Initialize pool manager with custom SSL context"""
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        self.poolmanager = PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_version=ssl.PROTOCOL_TLSv1_2,
            ssl_context=ctx
        )

class OutlookAuthService:
    """Service for handling Microsoft Outlook OAuth authentication"""
    
    def __init__(self):
        self.client_id = settings.OUTLOOK_CLIENT_ID
        self.client_secret = settings.OUTLOOK_CLIENT_SECRET
        self.redirect_uri = settings.OUTLOOK_OAUTH_REDIRECT_URI
        self.token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        self.userinfo_url = "https://graph.microsoft.com/v1.0/me"
        
        # Create a session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        # Try different adapter configurations
        try:
            # First try with standard adapter
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)
            self.session.verify = True
        except Exception as e:
            logger.warning(f"Standard adapter failed, using custom SSL adapter: {str(e)}")
            # Fallback to custom adapter with relaxed SSL settings
            adapter = CustomHTTPAdapter(max_retries=retry_strategy)
            self.session.mount("http://", adapter)
            self.session.mount("https://", adapter)
            self.session.verify = False
        
        # Configure timeout
        self.session.timeout = (10, 30)  # (connect_timeout, read_timeout)
    
    def _make_request_with_fallback(self, method: str, url: str, **kwargs):
        """Make request with SSL fallback mechanism"""
        try:
            # First attempt with standard SSL verification
            response = self.session.request(method, url, **kwargs)
            return response
        except (requests.exceptions.SSLError, ssl.SSLError) as e:
            logger.warning(f"SSL error with standard settings, trying with relaxed SSL: {str(e)}")
            
            # Create a new session with relaxed SSL settings
            fallback_session = requests.Session()
            fallback_session.verify = False
            fallback_session.timeout = (10, 30)
            
            # Add retry strategy to fallback session
            retry_strategy = Retry(
                total=2,
                backoff_factor=1,
                status_forcelist=[429, 500, 502, 503, 504],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            fallback_session.mount("http://", adapter)
            fallback_session.mount("https://", adapter)
            
            try:
                response = fallback_session.request(method, url, **kwargs)
                return response
            except Exception as fallback_error:
                logger.error(f"Fallback request also failed: {str(fallback_error)}")
                raise fallback_error
    
    def get_auth_url(self, state: str = None) -> str:
        """Generate the OAuth authorization URL"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": "openid email profile User.Read Mail.Read Mail.Send Mail.ReadWrite offline_access",
            "response_mode": "query",
            "state": state or "",
            "access_type": "offline",  # Request refresh token
            "prompt": "consent",       # Force consent screen to ensure refresh token
        }
        
        url = "https://login.microsoftonline.com/common/oauth2/v2.0/authorize"
        query_string = "&".join([f"{k}={requests.utils.quote(str(v))}" for k, v in params.items()])
        return f"{url}?{query_string}"
    
    def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access and refresh tokens"""
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "grant_type": "authorization_code",
        }
        
        try:
            response = self._make_request_with_fallback("POST", self.token_url, data=data)
            if not response.ok:
                logger.error(f"Failed to exchange code for tokens: {response.status_code} - {response.text}")
                raise Exception(f"Failed to exchange code for tokens: {response.status_code}")
            
            tokens = response.json()
            logger.info(f"Token exchange successful. Available tokens: {list(tokens.keys())}")
            
            # Log token details (without exposing sensitive data)
            if 'access_token' in tokens:
                logger.info(f"Access token received (length: {len(tokens['access_token'])})")
            if 'refresh_token' in tokens:
                logger.info(f"Refresh token received (length: {len(tokens['refresh_token'])})")
            else:
                logger.warning("No refresh token received from Microsoft OAuth")
            
            return tokens
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL error during token exchange: {str(e)}")
            raise Exception(f"SSL connection error: {str(e)}")
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout during token exchange: {str(e)}")
            raise Exception(f"Request timeout: {str(e)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error during token exchange: {str(e)}")
            raise Exception(f"Network error: {str(e)}")
    
    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from Microsoft Graph API"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        try:
            logger.info(f"Making request to Microsoft Graph API: {self.userinfo_url}")
            logger.info(f"Access token length: {len(access_token)}")
            
            response = self._make_request_with_fallback("GET", self.userinfo_url, headers=headers)
            
            if not response.ok:
                logger.error(f"Failed to get user info: {response.status_code} - {response.text}")
                
                # Log additional debugging information
                if response.status_code == 403:
                    logger.error("403 Forbidden - This usually means insufficient permissions or invalid scopes")
                    logger.error("Required scopes: User.Read, openid, email, profile")
                    logger.error(f"Response headers: {dict(response.headers)}")
                
                raise Exception(f"Failed to get user info: {response.status_code}")
            
            user_data = response.json()
            logger.info(f"Successfully retrieved user info: {user_data.get('displayName', 'Unknown')} ({user_data.get('mail', user_data.get('userPrincipalName', 'No email'))})")
            return user_data
            
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL error during user info request: {str(e)}")
            raise Exception(f"SSL connection error: {str(e)}")
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout during user info request: {str(e)}")
            raise Exception(f"Request timeout: {str(e)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error during user info request: {str(e)}")
            raise Exception(f"Network error: {str(e)}")
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh the access token using the refresh token"""
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }
        
        try:
            response = self._make_request_with_fallback("POST", self.token_url, data=data)
            if not response.ok:
                logger.error(f"Failed to refresh token: {response.status_code} - {response.text}")
                raise Exception(f"Failed to refresh token: {response.status_code}")
            
            return response.json()
        except requests.exceptions.SSLError as e:
            logger.error(f"SSL error during token refresh: {str(e)}")
            raise Exception(f"SSL connection error: {str(e)}")
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout during token refresh: {str(e)}")
            raise Exception(f"Request timeout: {str(e)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error during token refresh: {str(e)}")
            raise Exception(f"Network error: {str(e)}")

# Create a singleton instance
outlook_auth_service = OutlookAuthService() 