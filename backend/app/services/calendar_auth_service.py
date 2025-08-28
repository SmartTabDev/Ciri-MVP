import logging
from typing import Optional
from sqlalchemy.orm import Session
from pathlib import Path
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from app.models.company import Company

logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class CalendarAuthService:
    def __init__(self):
        """Initialize the calendar auth service."""
        self.token_dir = Path("tokens")
        self.token_dir.mkdir(exist_ok=True)

    def _get_token_path(self, company_id: int) -> Path:
        """Get the path for a company's token file."""
        return self.token_dir / f"token_{company_id}.json"

    def get_auth_url(self, company: Company) -> str:
        """
        Get the authorization URL for Google Calendar OAuth.
        
        Args:
            company: Company model instance with calendar credentials
            
        Returns:
            Authorization URL for the user to visit
        """
        if not company.calendar_credentials:
            raise ValueError("Company has no calendar credentials")

        try:
            # Create flow instance for web application
            flow = Flow.from_client_config(
                company.calendar_credentials,
                SCOPES,
                redirect_uri=company.calendar_credentials['web']['redirect_uris'][0]
            )

            # Get authorization URL
            auth_url, _ = flow.authorization_url(
                access_type='offline',  # This is required to get a refresh token
                prompt='consent',       # This forces the consent screen to appear
                include_granted_scopes='true'
            )
            
            return auth_url
        except Exception as e:
            logger.error(f"Error generating auth URL for company {company.id}: {str(e)}")
            raise ValueError(f"Failed to generate authorization URL: {str(e)}")

    def handle_auth_callback(
        self,
        db: Session,
        company: Company,
        auth_code: str
    ) -> None:
        """
        Handle the OAuth callback and store the credentials.
        
        Args:
            db: Database session
            company: Company model instance
            auth_code: Authorization code from the callback
        """
        if not company.calendar_credentials:
            raise ValueError("Company has no calendar credentials")

        try:
            # Create flow instance for web application
            flow = Flow.from_client_config(
                company.calendar_credentials,
                SCOPES,
                redirect_uri=company.calendar_credentials['web']['redirect_uris'][0]
            )

            # Exchange auth code for credentials
            flow.fetch_token(code=auth_code)

            # Get credentials
            creds = flow.credentials

            # Save the credentials to token file
            token_path = self._get_token_path(company.id)
            try:
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
                logger.info(f"Successfully saved token for company {company.id}")
            except Exception as e:
                logger.error(f"Error saving token file for company {company.id}: {str(e)}")
                raise ValueError(f"Failed to save credentials: {str(e)}")

        except Exception as e:
            logger.error(f"Error handling auth callback for company {company.id}: {str(e)}")
            raise ValueError(f"Failed to complete authentication: {str(e)}")

    def revoke_access(self, company: Company) -> None:
        """
        Revoke calendar access for a company.
        
        Args:
            company: Company model instance
        """
        try:
            # Remove token file
            token_path = self._get_token_path(company.id)
            if token_path.exists():
                token_path.unlink()
                logger.info(f"Removed token file for company {company.id}")

            # Clear calendar credentials from company
            company.calendar_credentials = None
            db.add(company)
            db.commit()
            logger.info(f"Cleared calendar credentials for company {company.id}")

        except Exception as e:
            logger.error(f"Error revoking access for company {company.id}: {str(e)}")
            raise ValueError(f"Failed to revoke access: {str(e)}")

# Create a singleton instance
calendar_auth_service = CalendarAuthService() 