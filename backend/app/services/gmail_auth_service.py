import logging
from typing import Optional
from sqlalchemy.orm import Session
from pathlib import Path
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

from app.models.company import Company

logger = logging.getLogger(__name__)

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
]

class GmailAuthService:
    def __init__(self):
        self.token_dir = Path("tokens")
        self.token_dir.mkdir(exist_ok=True)

    def _get_token_path(self, company_id: int) -> Path:
        return self.token_dir / f"gmail_token_{company_id}.json"

    def get_auth_url(self, company: Company) -> str:
        if not company.gmail_box_credentials:
            raise ValueError("Company has no Gmail credentials config (client_id, etc.)")
        try:
            flow = Flow.from_client_config(
                company.gmail_box_credentials,
                SCOPES,
                redirect_uri=company.gmail_box_credentials['web']['redirect_uris'][0]
            )
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                prompt='consent',
                include_granted_scopes='true'
            )
            return auth_url
        except Exception as e:
            logger.error(f"Error generating Gmail auth URL for company {company.id}: {str(e)}")
            raise ValueError(f"Failed to generate Gmail authorization URL: {str(e)}")

    def handle_auth_callback(self, db: Session, company: Company, auth_code: str) -> None:
        if not company.gmail_box_credentials:
            raise ValueError("Company has no Gmail credentials config (client_id, etc.)")
        try:
            flow = Flow.from_client_config(
                company.gmail_box_credentials,
                SCOPES,
                redirect_uri=company.gmail_box_credentials['web']['redirect_uris'][0]
            )
            flow.fetch_token(code=auth_code)
            creds = flow.credentials
            token_path = self._get_token_path(company.id)
            try:
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
                logger.info(f"Successfully saved Gmail token for company {company.id}")
            except Exception as e:
                logger.error(f"Error saving Gmail token file for company {company.id}: {str(e)}")
                raise ValueError(f"Failed to save Gmail credentials: {str(e)}")
        except Exception as e:
            logger.error(f"Error handling Gmail auth callback for company {company.id}: {str(e)}")
            raise ValueError(f"Failed to complete Gmail authentication: {str(e)}")

gmail_auth_service = GmailAuthService() 