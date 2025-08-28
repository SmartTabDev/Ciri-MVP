import logging
import asyncio
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import requests
from email.mime.text import MIMEText
import base64
import re
import urllib3
import ssl
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

from app.core.config import settings
from app.services.outlook_auth_service import outlook_auth_service

logger = logging.getLogger(__name__)

# Configure urllib3 to be less strict about SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CustomHTTPAdapter(HTTPAdapter):
    """Custom HTTP adapter with relaxed SSL context for Outlook API"""
    
    def init_poolmanager(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = context
        return super().init_poolmanager(*args, **kwargs)
    
    def proxy_manager_for(self, *args, **kwargs):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = context
        return super().proxy_manager_for(*args, **kwargs)

def create_outlook_session():
    """Create a requests session with robust SSL handling for Outlook API"""
    session = requests.Session()
    
    # Configure retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    
    # Add custom adapter with relaxed SSL
    adapter = CustomHTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    
    return session

def is_valid_jwt_token(token: str) -> bool:
    """
    Basic JWT token validation - checks if token has the correct format.
    JWT tokens should have 3 parts separated by dots: header.payload.signature
    """
    if not token:
        return False
    
    # Check if token has the correct JWT format (3 parts separated by dots)
    parts = token.split('.')
    if len(parts) != 3:
        return False
    
    # Check if all parts are non-empty
    for part in parts:
        if not part:
            return False
    
    return True

class OutlookEmailService:
    """Service for sending emails via Microsoft Graph API"""
    
    def __init__(self):
        self.base_url = "https://graph.microsoft.com/v1.0"
    
    async def _retry_outlook_api_call(self, func, max_retries=3, delay=1):
        """Retry Outlook API calls with exponential backoff - handles SSL, timeout, and connection errors"""
        for attempt in range(max_retries):
            try:
                return await func()
            except (requests.exceptions.SSLError, requests.exceptions.Timeout, requests.exceptions.RequestException) as e:
                if "EOF occurred in violation of protocol" in str(e) or "SSL" in str(e) or "timeout" in str(e).lower():
                    if attempt < max_retries - 1:
                        logging.warning(f"Outlook API connection error, retrying in {delay}s (attempt {attempt + 1}/{max_retries}): {str(e)}")
                        await asyncio.sleep(delay)
                        delay *= 2  # Exponential backoff
                        continue
                raise e
            except Exception as e:
                raise e
        return None
    
    async def send_email_via_outlook_api(
        self,
        email_to: str,
        subject: str,
        body: str,
        from_email: str,
        credentials_data: dict,
        thread_id: str = None,
        original_message_id: str = None
    ) -> str:
        """
        Send an email using Microsoft Graph API and return the message ID.
        
        Args:
            email_to: Recipient email address
            subject: Email subject
            body: Email body (plain text)
            from_email: Sender email address
            credentials_data: Outlook OAuth2 credentials data
            thread_id: Thread ID to reply to (optional)
            original_message_id: Original message ID to reply to (optional)
            
        Returns:
            str: The message ID of the sent email
        """
        
        async def retry_outlook_api_call(func, max_retries=3, delay=1):
            """Retry Outlook API calls with exponential backoff"""
            for attempt in range(max_retries):
                try:
                    return await func()
                except Exception as e:
                    if "EOF occurred in violation of protocol" in str(e) or "SSL" in str(e):
                        if attempt < max_retries - 1:
                            logging.warning(f"Outlook API SSL error, retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
                            await asyncio.sleep(delay)
                            delay *= 2  # Exponential backoff
                            continue
                    raise e
            return None
        
        try:
            # Check if access token is expired and refresh if needed
            access_token = credentials_data.get("access_token")
            refresh_token = credentials_data.get("refresh_token")
            
            if not access_token:
                raise Exception("No access token provided")
            
            # If we have a refresh token, try to refresh the access token
            if refresh_token:
                try:
                    refreshed_tokens = outlook_auth_service.refresh_access_token(refresh_token)
                    access_token = refreshed_tokens["access_token"]
                    # Update the credentials data with new tokens
                    credentials_data.update(refreshed_tokens)
                except Exception as e:
                    logging.warning(f"Failed to refresh Outlook token: {str(e)}")
                    # Continue with existing token
            
            # Prepare the email message
            message_data = {
                "message": {
                    "subject": subject,
                    "body": {
                        "contentType": "Text",
                        "content": body
                    },
                    "toRecipients": [
                        {
                            "emailAddress": {
                                "address": email_to
                            }
                        }
                    ]
                }
            }
            
            # If this is a reply, add proper headers
            if thread_id and original_message_id:
                # Generate a new Message-ID for this reply
                new_message_id = f"<{uuid.uuid4()}@{from_email.split('@')[1]}>"
                message_data["message"]["internetMessageId"] = new_message_id
                # Add conversationId for threading (thread_id parameter is the conversationId for Outlook)
                message_data["message"]["conversationId"] = thread_id
                # Threading is handled automatically by the API based on conversationId
                
                logging.info(f"Sending email via Outlook API to {email_to} with conversationId: {thread_id}")
            else:
                # For new messages, generate a new Message-ID
                new_message_id = f"<{uuid.uuid4()}@{from_email.split('@')[1]}>"
                message_data["message"]["internetMessageId"] = new_message_id
                
                logging.info(f"Sending new email via Outlook API to {email_to}")
            
            # Send the message
            async def send_message():
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                # Use robust session with SSL handling
                session = create_outlook_session()
                
                try:
                    response = session.post(
                        f"{self.base_url}/me/sendMail",
                        json=message_data,
                        headers=headers,
                        timeout=30
                    )
                except requests.exceptions.SSLError as ssl_error:
                    logger.warning(f"SSL error with Outlook API, trying with fallback: {ssl_error}")
                    # Fallback to regular session if SSL fails
                    response = requests.post(
                        f"{self.base_url}/me/sendMail",
                        json=message_data,
                        headers=headers,
                        timeout=30,
                        verify=False
                    )
                except requests.exceptions.Timeout as timeout_error:
                    logger.error(f"Timeout error with Outlook API: {timeout_error}")
                    raise Exception(f"Timeout connecting to Outlook API: {timeout_error}")
                except requests.exceptions.RequestException as req_error:
                    logger.error(f"Request error with Outlook API: {req_error}")
                    raise Exception(f"Failed to connect to Outlook API: {req_error}")
                
                if not response.ok:
                    raise Exception(f"Outlook API error: {response.status_code} - {response.text}")
                
                return response
            
            sent_response = await self._retry_outlook_api_call(send_message)
            
            if not sent_response:
                raise Exception("Failed to send email after all retry attempts")
            
            # Get the real message ID by polling for the sent message
            # Microsoft Graph API doesn't return message ID immediately from sendMail
            # We need to search for the message we just sent
            real_message_id = await self._get_sent_message_id(
                credentials_data, 
                email_to, 
                subject, 
                from_email
            )
            
            if real_message_id:
                logging.info(f"Email sent via Outlook API successfully to {email_to} with real message ID: {real_message_id}")
                return real_message_id
            else:
                # Fallback to generated ID if we can't find the real one
                message_id = f"outlook-{uuid.uuid4()}"
                logging.warning(f"Could not find real message ID, using generated ID: {message_id}")
                return message_id
            
        except Exception as e:
            error_msg = f"Failed to send email via Outlook API: {str(e)}"
            logging.error(error_msg)
            raise Exception(error_msg)
    
    async def get_user_messages(
        self,
        credentials_data: dict,
        max_results: int = 10,
        query: str = "isRead eq false"
    ):
        """
        Get user messages from Outlook using Microsoft Graph API.
        
        Args:
            credentials_data: Outlook OAuth2 credentials data
            max_results: Maximum number of messages to retrieve
            query: OData query filter
            
        Returns:
            tuple: (List of message objects, Whether tokens were refreshed)
        """
        tokens_refreshed = False
        try:
            # Check if access token is expired and refresh if needed
            access_token = credentials_data.get("access_token")
            refresh_token = credentials_data.get("refresh_token")
            
            if not access_token:
                raise Exception("No access token provided")
            
            # Validate JWT token format
            if not is_valid_jwt_token(access_token):
                logger.warning("Invalid JWT token format detected, attempting to refresh")
                if refresh_token:
                    try:
                        refreshed_tokens = outlook_auth_service.refresh_access_token(refresh_token)
                        access_token = refreshed_tokens["access_token"]
                        # Update the credentials data with new tokens
                        credentials_data.update(refreshed_tokens)
                        tokens_refreshed = True
                        logger.info("Successfully refreshed Outlook access token")
                    except Exception as e:
                        logger.error(f"Failed to refresh invalid Outlook token: {str(e)}")
                        raise Exception("Invalid access token and failed to refresh")
                else:
                    raise Exception("Invalid access token and no refresh token available")
            
            # If we have a refresh token, try to refresh the access token
            elif refresh_token:
                try:
                    refreshed_tokens = outlook_auth_service.refresh_access_token(refresh_token)
                    access_token = refreshed_tokens["access_token"]
                    # Update the credentials data with new tokens
                    credentials_data.update(refreshed_tokens)
                    tokens_refreshed = True
                    logger.info("Successfully refreshed Outlook access token")
                except Exception as e:
                    logger.warning(f"Failed to refresh Outlook token: {str(e)}")
                    # Continue with existing token
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Build the API URL with query parameters
            url = f"{self.base_url}/me/messages"
            params = {
                "$top": max_results,
                "$select": "id,subject,from,receivedDateTime,body,isRead,conversationId,internetMessageId",
                "$orderby": "receivedDateTime desc"
            }
            
            if query:
                params["$filter"] = query
            
            # Use robust session with SSL handling
            session = create_outlook_session()
            
            try:
                response = session.get(url, headers=headers, params=params, timeout=30)
            except requests.exceptions.SSLError as ssl_error:
                logger.warning(f"SSL error with Outlook API, trying with fallback: {ssl_error}")
                # Fallback to regular session if SSL fails
                response = requests.get(url, headers=headers, params=params, timeout=30, verify=False)
            except requests.exceptions.Timeout as timeout_error:
                logger.error(f"Timeout error with Outlook API: {timeout_error}")
                raise Exception(f"Timeout connecting to Outlook API: {timeout_error}")
            except requests.exceptions.RequestException as req_error:
                logger.error(f"Request error with Outlook API: {req_error}")
                raise Exception(f"Failed to connect to Outlook API: {req_error}")
            
            if not response.ok:
                raise Exception(f"Outlook API error: {response.status_code} - {response.text}")
            
            data = response.json()
            return data.get("value", []), tokens_refreshed
            
        except Exception as e:
            error_msg = f"Failed to get messages from Outlook API: {str(e)}"
            logging.error(error_msg)
            raise Exception(error_msg)
    
    async def get_message_details(
        self,
        message_id: str,
        credentials_data: dict
    ) -> dict:
        """
        Get detailed information about a specific message.
        
        Args:
            message_id: The message ID
            credentials_data: Outlook OAuth2 credentials data
            
        Returns:
            dict: Message details
        """
        try:
            # Check if access token is expired and refresh if needed
            access_token = credentials_data.get("access_token")
            refresh_token = credentials_data.get("refresh_token")
            
            if not access_token:
                raise Exception("No access token provided")
            
            # Validate JWT token format
            if not is_valid_jwt_token(access_token):
                logger.warning("Invalid JWT token format detected, attempting to refresh")
                if refresh_token:
                    try:
                        refreshed_tokens = outlook_auth_service.refresh_access_token(refresh_token)
                        access_token = refreshed_tokens["access_token"]
                        # Update the credentials data with new tokens
                        credentials_data.update(refreshed_tokens)
                        logger.info("Successfully refreshed Outlook access token")
                    except Exception as e:
                        logger.error(f"Failed to refresh invalid Outlook token: {str(e)}")
                        raise Exception("Invalid access token and failed to refresh")
                else:
                    raise Exception("Invalid access token and no refresh token available")
            
            # If we have a refresh token, try to refresh the access token
            elif refresh_token:
                try:
                    refreshed_tokens = outlook_auth_service.refresh_access_token(refresh_token)
                    access_token = refreshed_tokens["access_token"]
                    # Update the credentials data with new tokens
                    credentials_data.update(refreshed_tokens)
                    logger.info("Successfully refreshed Outlook access token")
                except Exception as e:
                    logger.warning(f"Failed to refresh Outlook token: {str(e)}")
                    # Continue with existing token
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            url = f"{self.base_url}/me/messages/{message_id}"
            params = {
                "$select": "id,subject,from,toRecipients,receivedDateTime,body,isRead,conversationId,internetMessageId"
            }
            
            # Use robust session with SSL handling
            session = create_outlook_session()
            
            try:
                response = session.get(url, headers=headers, params=params, timeout=30)
            except requests.exceptions.SSLError as ssl_error:
                logger.warning(f"SSL error with Outlook API, trying with fallback: {ssl_error}")
                # Fallback to regular session if SSL fails
                response = requests.get(url, headers=headers, params=params, timeout=30, verify=False)
            except requests.exceptions.Timeout as timeout_error:
                logger.error(f"Timeout error with Outlook API: {timeout_error}")
                raise Exception(f"Timeout connecting to Outlook API: {timeout_error}")
            except requests.exceptions.RequestException as req_error:
                logger.error(f"Request error with Outlook API: {req_error}")
                raise Exception(f"Failed to connect to Outlook API: {req_error}")
            
            if not response.ok:
                raise Exception(f"Outlook API error: {response.status_code} - {response.text}")
            
            return response.json()
            
        except Exception as e:
            error_msg = f"Failed to get message details from Outlook API: {str(e)}"
            logging.error(error_msg)
            raise Exception(error_msg)

    async def reply_to_message_via_outlook_api(
        self,
        message_id: str,
        reply_body: str,
        credentials_data: dict,
        from_email: str = None
    ) -> str:
        """
        Reply to a specific message using Microsoft Graph API reply endpoint.
        
        Args:
            message_id: The ID of the message to reply to
            reply_body: The reply content
            credentials_data: Outlook OAuth2 credentials data
            from_email: Sender email address (optional, used for getting real message ID)
            
        Returns:
            str: The message ID of the sent reply
        """
        
        async def retry_outlook_api_call(func, max_retries=3, delay=1):
            """Retry Outlook API calls with exponential backoff"""
            for attempt in range(max_retries):
                try:
                    return await func()
                except Exception as e:
                    if "EOF occurred in violation of protocol" in str(e) or "SSL" in str(e):
                        if attempt < max_retries - 1:
                            logging.warning(f"Outlook API SSL error, retrying in {delay}s (attempt {attempt + 1}/{max_retries})")
                            await asyncio.sleep(delay)
                            delay *= 2  # Exponential backoff
                            continue
                    raise e
            return None
        
        try:
            # Check if access token is expired and refresh if needed
            access_token = credentials_data.get("access_token")
            refresh_token = credentials_data.get("refresh_token")
            
            if not access_token:
                raise Exception("No access token provided")
            
            # If we have a refresh token, try to refresh the access token
            if refresh_token:
                try:
                    refreshed_tokens = outlook_auth_service.refresh_access_token(refresh_token)
                    access_token = refreshed_tokens["access_token"]
                    # Update the credentials data with new tokens
                    credentials_data.update(refreshed_tokens)
                except Exception as e:
                    logging.warning(f"Failed to refresh Outlook token: {str(e)}")
                    # Continue with existing token
            
            # Prepare the reply data
            reply_data = {
                "comment": reply_body
            }
            
            logging.info(f"Replying to Outlook message {message_id} with content: {reply_body[:50]}...")
            
            # Send the reply using the reply endpoint
            async def send_reply():
                headers = {
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                }
                
                # Use robust session with SSL handling
                session = create_outlook_session()
                
                try:
                    response = session.post(
                        f"{self.base_url}/me/messages/{message_id}/reply",
                        json=reply_data,
                        headers=headers,
                        timeout=30
                    )
                except requests.exceptions.SSLError as ssl_error:
                    logger.warning(f"SSL error with Outlook API, trying with fallback: {ssl_error}")
                    # Fallback to regular session if SSL fails
                    response = requests.post(
                        f"{self.base_url}/me/messages/{message_id}/reply",
                        json=reply_data,
                        headers=headers,
                        timeout=30,
                        verify=False
                    )
                except requests.exceptions.Timeout as timeout_error:
                    logger.error(f"Timeout error with Outlook API: {timeout_error}")
                    raise Exception(f"Timeout connecting to Outlook API: {timeout_error}")
                except requests.exceptions.RequestException as req_error:
                    logger.error(f"Request error with Outlook API: {req_error}")
                    raise Exception(f"Failed to connect to Outlook API: {req_error}")
                
                if not response.ok:
                    raise Exception(f"Outlook API error: {response.status_code} - {response.text}")
                
                return response
            
            sent_response = await self._retry_outlook_api_call(send_reply)
            
            if not sent_response:
                raise Exception("Failed to send reply after all retry attempts")
            
            # Get the real message ID of the reply by polling for the sent message
            # The reply endpoint doesn't return a message ID, so we need to find it
            real_reply_message_id = await self._get_reply_message_id(
                credentials_data,
                message_id,  # Original message ID
                reply_body,
                from_email
            )
            
            if real_reply_message_id:
                logging.info(f"Reply sent via Outlook API successfully to message {message_id} with real reply ID: {real_reply_message_id}")
                return real_reply_message_id
            else:
                # Fallback to generated ID if we can't find the real one
                reply_message_id = f"reply-{message_id}-{uuid.uuid4()}"
                logging.warning(f"Could not find real reply message ID, using generated ID: {reply_message_id}")
                return reply_message_id
            
        except Exception as e:
            error_msg = f"Failed to reply to message via Outlook API: {str(e)}"
            logging.error(error_msg)
            raise Exception(error_msg)

    async def _get_sent_message_id(
        self,
        credentials_data: dict,
        email_to: str,
        subject: str,
        from_email: str,
        max_attempts: int = 5,
        delay_seconds: int = 2
    ) -> str:
        """
        Get the real message ID of a sent message by polling the sent items folder.
        
        Args:
            credentials_data: Outlook OAuth2 credentials data
            email_to: Recipient email address
            subject: Email subject
            from_email: Sender email address
            max_attempts: Maximum number of polling attempts
            delay_seconds: Delay between polling attempts
            
        Returns:
            str: The real message ID if found, None otherwise
        """
        try:
            access_token = credentials_data.get("access_token")
            if not access_token:
                return None
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Use robust session with SSL handling
            session = create_outlook_session()
            
            # Poll for the sent message
            for attempt in range(max_attempts):
                try:
                    # Search for the message in sent items
                    # Use a filter to find the message we just sent
                    query_params = {
                        "$top": 10,
                        "$select": "id,subject,toRecipients,from,receivedDateTime",
                        "$filter": f"subject eq '{subject}' and from/emailAddress/address eq '{from_email}'",
                        "$orderby": "receivedDateTime desc"
                    }
                    
                    response = session.get(
                        f"{self.base_url}/me/mailFolders/SentItems/messages",
                        headers=headers,
                        params=query_params,
                        timeout=30
                    )
                    
                    if response.ok:
                        messages = response.json().get('value', [])
                        
                        # Look for the most recent message that matches our criteria
                        for message in messages:
                            to_recipients = message.get('toRecipients', [])
                            if any(recipient.get('emailAddress', {}).get('address') == email_to for recipient in to_recipients):
                                message_id = message.get('id')
                                if message_id:
                                    logging.info(f"Found real message ID: {message_id} after {attempt + 1} attempts")
                                    return message_id
                    
                    # Wait before next attempt
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(delay_seconds)
                        
                except Exception as e:
                    logging.warning(f"Error polling for sent message (attempt {attempt + 1}): {e}")
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(delay_seconds)
            
            logging.warning(f"Could not find real message ID after {max_attempts} attempts")
            return None
            
        except Exception as e:
            logging.error(f"Error in _get_sent_message_id: {e}")
            return None
    
    async def _get_reply_message_id(
        self,
        credentials_data: dict,
        original_message_id: str,
        reply_body: str,
        from_email: str,
        max_attempts: int = 5,
        delay_seconds: int = 2
    ) -> str:
        """
        Get the real message ID of a reply by polling the sent items folder.
        
        Args:
            credentials_data: Outlook OAuth2 credentials data
            original_message_id: ID of the original message being replied to
            reply_body: Content of the reply
            from_email: Sender email address
            max_attempts: Maximum number of polling attempts
            delay_seconds: Delay between polling attempts
            
        Returns:
            str: The real message ID if found, None otherwise
        """
        try:
            access_token = credentials_data.get("access_token")
            if not access_token:
                return None
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Use robust session with SSL handling
            session = create_outlook_session()
            
            # Poll for the reply message
            for attempt in range(max_attempts):
                try:
                    # Search for the reply in sent items
                    # Look for recent messages from the sender
                    query_params = {
                        "$top": 10,
                        "$select": "id,subject,body,from,receivedDateTime,conversationId",
                        "$filter": f"from/emailAddress/address eq '{from_email}'",
                        "$orderby": "receivedDateTime desc"
                    }
                    
                    response = session.get(
                        f"{self.base_url}/me/mailFolders/SentItems/messages",
                        headers=headers,
                        params=query_params,
                        timeout=30
                    )
                    
                    if response.ok:
                        messages = response.json().get('value', [])
                        
                        # Look for the most recent message that could be our reply
                        for message in messages:
                            # Check if this message contains our reply content
                            message_body = message.get('body', {}).get('content', '')
                            if reply_body in message_body:
                                message_id = message.get('id')
                                if message_id:
                                    logging.info(f"Found real reply message ID: {message_id} after {attempt + 1} attempts")
                                    return message_id
                    
                    # Wait before next attempt
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(delay_seconds)
                        
                except Exception as e:
                    logging.warning(f"Error polling for reply message (attempt {attempt + 1}): {e}")
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(delay_seconds)
            
            logging.warning(f"Could not find real reply message ID after {max_attempts} attempts")
            return None
            
        except Exception as e:
            logging.error(f"Error in _get_reply_message_id: {e}")
            return None

# Create a singleton instance
outlook_email_service = OutlookEmailService()
