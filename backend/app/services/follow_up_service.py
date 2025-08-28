import logging
from datetime import datetime, timedelta, timezone
from typing import List, Tuple
from sqlalchemy.orm import Session

from app.core.email import send_email, send_plain_email
from app.models.company import Company
from app.models.lead import Lead
from app.crud.crud_lead import lead
from app.services.ai_service import SimpleAIService

logger = logging.getLogger(__name__)

class FollowUpService:
    def __init__(self):
        """Initialize the follow-up service."""
        self.ai_service = SimpleAIService()

    async def send_follow_up_emails(self, db: Session) -> None:
        """
        Send follow-up emails to all leads based on their company's follow-up cycle.
        This should be called periodically (e.g., via a cron job).
        """
        try:
            # Get all companies with follow-up cycle set
            companies = db.query(Company).filter(Company.follow_up_cycle.isnot(None)).all()
            
            for company in companies:
                # Get all leads for this company
                leads = lead.get_by_company(db, company_id=company.id)
                
                for lead_obj in leads:
                    # Calculate if it's time to send a follow-up
                    if self._should_send_follow_up(lead_obj, company.follow_up_cycle):
                        await self._send_follow_up_email(lead_obj, company, db)
                        
        except Exception as e:
            logger.error(f"Error in send_follow_up_emails: {str(e)}")
            raise

    def _should_send_follow_up(self, lead: Lead, follow_up_cycle_ms: int) -> bool:
        """
        Determine if it's time to send a follow-up email to a lead.
        """
        # Convert milliseconds to days for easier comparison
        follow_up_cycle_days = follow_up_cycle_ms / (1000 * 60 * 60 * 24)
        
        # Calculate the time since the last follow-up or creation
        current_time = datetime.now(timezone.utc)
        reference_time = lead.follow_up_last_sent_at or lead.created_at
        time_since_last_follow_up = current_time - reference_time
        
        # Send follow-up if enough time has passed
        return time_since_last_follow_up.days >= follow_up_cycle_days

    async def _generate_email_content(self, lead: Lead, company: Company) -> Tuple[str, str]:
        """
        Generate email subject and body using AI, taking into account previous email context.
        """
        # Prepare the prompt for the AI
        prompt = f"""
        Generate a follow-up email for a lead named {lead.name} from {company.name}.
        Company type: {company.business_category}
        Company goal: {company.goal}
        
        Previous email context:
        {lead.email_context if lead.email_context else 'This is the first follow-up email.'}
        
        Please generate a professional and engaging follow-up email that:
        1. References previous communication if any
        2. Shows genuine interest in helping the lead
        3. Encourages response
        4. Maintains a professional yet friendly tone
        5. Aligns with the company's goal: {company.goal}
        
        Format the response as JSON with 'subject' and 'body' fields.
        The body should be in HTML format.
        """

        try:
            # Get AI response
            response = await self.ai_service.generate_text(prompt)
            
            # Parse the response to get subject and body
            # The AI should return a JSON string with subject and body
            import json
            email_content = json.loads(response)
            
            return email_content['subject'], email_content['body']
        except Exception as e:
            logger.error(f"Error generating email content: {str(e)}")
            # Fallback to default email if AI generation fails
            return self._get_default_email_content(lead, company)

    def _get_default_email_content(self, lead: Lead, company: Company) -> Tuple[str, str]:
        """Fallback method to generate default email content."""
        subject = f"Follow-up from {company.name}"
        body = f"""
        <html>
        <body>
            <p>Dear {lead.name},</p>
            <p>Thank you for your interest in {company.name}. We wanted to follow up with you and see if you have any questions or if there's anything we can help you with.</p>
            <p>We're here to assist you and would love to hear from you.</p>
            <p>Best regards,<br>The {company.name} Team</p>
        </body>
        </html>
        """
        return subject, body

    async def _send_follow_up_email(self, lead: Lead, company: Company, db: Session) -> None:
        """
        Send a follow-up email to a lead using Gmail or Outlook credentials.
        """
        try:
            # Generate email content using AI
            subject, body = await self._generate_email_content(lead, company)

            # Determine which email service to use
            gmail_credentials = getattr(company, 'gmail_box_credentials', None)
            outlook_credentials = getattr(company, 'outlook_box_credentials', None)
            
            if gmail_credentials and company.gmail_box_email:
                # Use Gmail credentials
                await send_plain_email(
                    email_to=lead.email,
                    subject=subject,
                    body=body,
                    from_email=company.gmail_box_email,
                    mail_username=company.gmail_box_email,
                    mail_password=company.gmail_box_app_password,
                    mail_from_name=company.gmail_box_username,
                    gmail_api_credentials=gmail_credentials,
                    outlook_api_credentials=None
                )
                logger.info(f"Follow-up email sent via Gmail to {lead.email} for company {company.name}")
                
            elif outlook_credentials and company.outlook_box_email:
                # Use Outlook credentials
                await send_plain_email(
                    email_to=lead.email,
                    subject=subject,
                    body=body,
                    from_email=company.outlook_box_email,
                    mail_username=company.outlook_box_email,
                    mail_password=None,  # Outlook doesn't use app password
                    mail_from_name=company.outlook_box_username,
                    gmail_api_credentials=None,
                    outlook_api_credentials=outlook_credentials
                )
                logger.info(f"Follow-up email sent via Outlook to {lead.email} for company {company.name}")
                
            else:
                raise Exception("No email credentials configured for this company")

            # Update the lead's email context and last sent timestamp
            lead.email_context = body  # Store the latest email content as context
            lead.follow_up_last_sent_at = datetime.now(timezone.utc)
            db.commit()

        except Exception as e:
            logger.error(f"Failed to send follow-up email to {lead.email}: {str(e)}")
            raise

follow_up_service = FollowUpService() 