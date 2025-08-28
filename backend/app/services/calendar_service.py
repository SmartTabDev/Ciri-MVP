import logging
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import pytz
from pathlib import Path
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from app.models.company import Company
from app.schemas.company import CalendarEvent, CalendarResponse

logger = logging.getLogger(__name__)

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class CalendarService:
    def __init__(self):
        """Initialize the calendar service."""
        self.token_dir = Path("tokens")
        self.token_dir.mkdir(exist_ok=True)

    def _get_token_path(self, company_id: int) -> Path:
        """Get the path for a company's token file."""
        return self.token_dir / f"token_{company_id}.json"

    def _get_credentials(self, company: Company) -> Optional[Credentials]:
        """Get credentials for a specific company."""
        if not company.calendar_credentials:
            logger.warning(f"No calendar credentials found for company {company.id}")
            return None

        try:
            token_path = self._get_token_path(company.id)
            creds = None

            # Try to load existing token
            if token_path.exists():
                try:
                    creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
                except Exception as e:
                    logger.error(f"Error loading token file for company {company.id}: {str(e)}")
                    # Remove invalid token file
                    token_path.unlink(missing_ok=True)

            # If no valid credentials, return None
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                    except Exception as e:
                        logger.error(f"Error refreshing token for company {company.id}: {str(e)}")
                        # Remove invalid token file
                        token_path.unlink(missing_ok=True)
                        return None
                else:
                    return None

            return creds
        except Exception as e:
            logger.error(f"Error getting credentials for company {company.id}: {str(e)}")
            return None

    async def get_company_calendar_events(
        self,
        db: Session,
        company: Company,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        max_results: int = 10
    ) -> CalendarResponse:
        """
        Get calendar events for a company using their Google Calendar.
        
        Args:
            db: Database session
            company: Company model instance
            start_time: Start time for events (defaults to now)
            end_time: End time for events (defaults to 7 days from now)
            max_results: Maximum number of events to return
            
        Returns:
            CalendarResponse containing events and next page token
        """
        try:
            # Get credentials for this company
            credentials = self._get_credentials(company)
            if not credentials:
                logger.error(f"No valid credentials found for company {company.id}")
                return CalendarResponse(events=[], next_page_token=None)

            # Set default time range if not provided
            if not start_time:
                start_time = datetime.now(pytz.UTC)
            if not end_time:
                end_time = start_time + timedelta(days=7)

            # Ensure times are in UTC
            if start_time.tzinfo is None:
                start_time = pytz.UTC.localize(start_time)
            if end_time.tzinfo is None:
                end_time = pytz.UTC.localize(end_time)

            # Create Google Calendar API service
            service = build('calendar', 'v3', credentials=credentials)

            # Get events
            events_result = service.events().list(
                calendarId='primary',
                timeMin=start_time.isoformat(),
                timeMax=end_time.isoformat(),
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            events = []
            for event in events_result.get('items', []):
                try:
                    # Parse start and end times
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    end = event['end'].get('dateTime', event['end'].get('date'))

                    calendar_event = CalendarEvent(
                        id=event['id'],
                        summary=event.get('summary', ''),
                        start=datetime.fromisoformat(start.replace('Z', '+00:00')),
                        end=datetime.fromisoformat(end.replace('Z', '+00:00')),
                        description=event.get('description', ''),
                        location=event.get('location', '')
                    )
                    events.append(calendar_event)
                except Exception as e:
                    logger.error(f"Error processing event {event.get('id')}: {str(e)}")
                    continue

            return CalendarResponse(
                events=events,
                next_page_token=events_result.get('nextPageToken')
            )

        except Exception as e:
            logger.error(f"Error accessing calendar for company {company.id}: {str(e)}")
            return CalendarResponse(events=[], next_page_token=None)

    def cleanup_old_tokens(self, max_age_days: int = 30) -> None:
        """Clean up old token files."""
        try:
            current_time = datetime.now()
            for token_file in self.token_dir.glob("token_*.json"):
                try:
                    file_age = current_time - datetime.fromtimestamp(token_file.stat().st_mtime)
                    if file_age.days > max_age_days:
                        token_file.unlink()
                        logger.info(f"Removed old token file: {token_file}")
                except Exception as e:
                    logger.error(f"Error processing token file {token_file}: {str(e)}")
        except Exception as e:
            logger.error(f"Error cleaning up old tokens: {str(e)}")

# Create a singleton instance
calendar_service = CalendarService() 