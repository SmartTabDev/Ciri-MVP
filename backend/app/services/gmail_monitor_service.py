import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from pathlib import Path
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import sys
import asyncio
sys.path.append('.')  # Ensure main.py can be imported
try:
    from main import company_email_ws_clients
except ImportError:
    company_email_ws_clients = None

from app.models.company import Company
from app.db.session import SessionLocal
from app.core.config import settings
from app.core.ws_clients import company_email_ws_clients
from app.core.broadcast import broadcast_new_email
from app.services.ai_service import SimpleAIService, filter_email_with_ai
import base64
from email.mime.text import MIMEText
from app.core.email import send_plain_email
from app.models.chat import Chat
from app.crud.crud_channel_auto_reply_settings import channel_auto_reply_settings
from app.services.channel_context_service import channel_context_service
from bs4 import BeautifulSoup
from app.util import extract_email_address, remove_gmail_quote, clean_html_content
import re

logger = logging.getLogger(__name__)

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify',
]


def should_reply_to_email(sender: str, content: str, settings, company_gmail_box_email: str = None) -> bool:
    """
    Check if an email should be replied to based on filtering criteria.
    
    Args:
        sender: Email sender address
        content: Email content
        settings: Application settings
        company_gmail_box_email: Company's Gmail box email address
    
    Returns:
        bool: True if email should be replied to, False otherwise
    """
    # Don't reply if email content contains an unsubscribe link
    if 'unsubscribe' in content.lower():
        return False
    
    # Don't reply if sender address contains 'no-reply' or 'noreply'
    if 'no-reply' in sender.lower() or 'noreply' in sender.lower():
        return False
    
    # Don't reply if email is from settings.MAIL_FROM
    if settings.MAIL_FROM and settings.MAIL_FROM.lower() in sender.lower():
        return False
    
    # Don't reply if email is from company's own Gmail box email
    if company_gmail_box_email and company_gmail_box_email.lower() in sender.lower():
        return False
    
    return True

def extract_message_id_from_headers(headers: list) -> str:
    """
    Extract the Message-ID from email headers.
    
    Args:
        headers: List of email headers from Gmail API
        
    Returns:
        str: The Message-ID value, or None if not found
    """
    for header in headers:
        if header.get('name', '').lower() == 'message-id':
            return header.get('value', '')
    return None

class GmailMonitorService:
    def __init__(self):
        self.token_dir = Path("tokens")
        self.token_dir.mkdir(exist_ok=True)
        self.last_seen_message_ids = {}  # company_id -> last seen Gmail message ID

    def _get_token_path(self, company_id: int) -> Path:
        return self.token_dir / f"gmail_token_{company_id}.json"

    def _get_credentials(self, company: Company, db: Session = None) -> Optional[Credentials]:
        creds_data = company.gmail_box_credentials
        if not creds_data:
            logger.warning(f"No Gmail credentials found for company {company.id}")
            return None
        client_id = settings.GOOGLE_CLIENT_ID
        client_secret = settings.GOOGLE_CLIENT_SECRET
        token_uri = "https://oauth2.googleapis.com/token"
        scopes = SCOPES
        creds = Credentials(
            creds_data["access_token"],
            refresh_token=creds_data.get("refresh_token"),
            token_uri=token_uri,
            client_id=client_id,
            client_secret=client_secret,
            scopes=scopes,
        )
        # Refresh if needed
        if not creds.valid and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Update DB with new access_token if possible
                if db is not None:
                    company.gmail_box_credentials["access_token"] = creds.token
                    db.add(company)
                    db.commit()
            except Exception as e:
                # Detect invalid_grant error (token revoked/expired)
                if hasattr(e, 'args') and any('invalid_grant' in str(arg) for arg in e.args):
                    logger.error(f"Gmail refresh token for company {company.id} is invalid or revoked. User must re-authenticate.")
                    if db is not None:
                        # Mark credentials as invalid (set to None or add a flag)
                        company.gmail_box_credentials = None
                        db.add(company)
                        db.commit()
                    # Optionally, return a special value to indicate re-auth is needed
                    return 'REAUTH_NEEDED'
                logger.error(f"Error refreshing Gmail token for company {company.id}: {str(e)}")
                return None
        return creds

    async def poll_new_emails(self, db: Session):
        print("[DEBUG] poll_new_emails called")
        logger.info("[DEBUG] poll_new_emails called")
        companies = db.query(Company).filter(Company.gmail_box_credentials.isnot(None)).all()
        print(f"[DEBUG] Found {len(companies)} companies with Gmail credentials")
        for company in companies:
            print(f"[DEBUG] Polling company {company.id} - {company.name}")
            logger.info(f"[DEBUG] Polling company {company.id} - {company.name}")
            creds = self._get_credentials(company, db)
            if creds == 'REAUTH_NEEDED':
                # Optionally, notify user/admin here (e.g., send alert, log, etc.)
                logger.warning(f"Company {company.id} ({company.name}) must reconnect their Gmail account.")
                print(f"[DEBUG] Company {company.id} needs re-authentication")
                continue
            if not creds:
                print(f"[DEBUG] No credentials for company {company.id}")
                continue
            try:
                service = build('gmail', 'v1', credentials=creds)
                results = service.users().messages().list(userId='me', maxResults=5, q='is:inbox').execute()
                messages = results.get('messages', [])
                print(f"[DEBUG] Found {len(messages)} total messages in inbox for company {company.id}")
                last_seen_id = self.last_seen_message_ids.get(company.id)
                print(f"[DEBUG] Last seen message ID for company {company.id}: {last_seen_id}")
                new_messages = []
                for msg in messages:
                    if msg['id'] == last_seen_id:
                        print(f"[DEBUG] Reached last seen message ID, stopping at: {last_seen_id}")
                        break
                    
                    # Get message details to check sender and content
                    msg_detail = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
                    headers = msg_detail.get('payload', {}).get('headers', [])
                    sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), None)
                    print(f"[DEBUG] Processing message {msg['id']} from: {sender}")
                    
                    # Get message content for filtering
                    def get_body_parts(payload):
                        text = None
                        html = None
                        if 'parts' in payload:
                            for part in payload['parts']:
                                if part.get('mimeType') == 'text/plain' and 'data' in part.get('body', {}):
                                    import base64
                                    text = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                                elif part.get('mimeType') == 'text/html' and 'data' in part.get('body', {}):
                                    import base64
                                    html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                                    print(f"[DEBUG] Processing part: {base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')}")
                            for part in payload['parts']:
                                t, h = get_body_parts(part)
                                if t and not text:
                                    text = t
                                if h and not html:
                                    html = h
                        else:
                            if payload.get('mimeType') == 'text/plain' and 'data' in payload.get('body', {}):
                                import base64
                                text = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
                            elif payload.get('mimeType') == 'text/html' and 'data' in payload.get('body', {}):
                                import base64
                                html = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
                        return text, html
                    
                    text_body, html_body = get_body_parts(msg_detail.get('payload', {}))
                    main_content = text_body or html_body or ''
                    print(f"[DEBUG] Message {msg['id']} content length: {len(main_content)}")
                    
                    # Apply filtering rules
                    # 1. Skip if email content contains an unsubscribe link
                    if 'unsubscribe' in main_content.lower():
                        print(f"[DEBUG] Skipping message {msg['id']} - contains unsubscribe link")
                        continue
                    
                    # 2. Skip if sender address contains 'no-reply' or 'noreply'
                    if sender and ('no-reply' in sender.lower() or 'noreply' in sender.lower()):
                        print(f"[DEBUG] Skipping message {msg['id']} - no-reply sender: {sender}")
                        continue
                    
                    # 3. Skip if email is from settings.MAIL_FROM
                    if sender and settings.MAIL_FROM and settings.MAIL_FROM.lower() in extract_email_address(sender).lower():
                        print(f"[DEBUG] Skipping message {msg['id']} - from settings.MAIL_FROM: {sender}")
                        continue
                    
                    # 4. Skip if message is sent by the company's own Gmail box email
                    if sender and company.gmail_box_email:
                        sender_email = extract_email_address(sender)
                        if company.gmail_box_email.lower() in sender_email.lower():
                            print(f"[DEBUG] Skipping message {msg['id']} - sent by company itself: {sender}")
                            continue  # Skip messages sent by the company itself
                    
                    print(f"[DEBUG] Message {msg['id']} passed all filters, adding to new_messages")
                    new_messages.append(msg)
                if new_messages:
                    print(f"[DEBUG] New messages found for company {company.id}: {[m['id'] for m in new_messages]}")
                    self.last_seen_message_ids[company.id] = new_messages[0]['id']
                for msg in reversed(new_messages):  # Oldest first
                    print(f"[DEBUG] Processing new message: {msg['id']}")
                    msg_detail = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
                    thread_id = msg_detail.get('threadId')
                    print(f"[DEBUG] Thread ID: {thread_id}")
                    thread = service.users().threads().get(userId='me', id=thread_id, format='full').execute()
                    thread_messages = thread.get('messages', [])
                    print(f"[DEBUG] Thread has {len(thread_messages)} messages")
                    bodies = []
                    # Use the last message in the thread for top-level fields
                    last_msg = thread_messages[-1] if thread_messages else msg_detail
                    headers = last_msg.get('payload', {}).get('headers', [])
                    subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '(No Subject)')
                    sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), '(Unknown)')
                    date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
                    print(f"[DEBUG] Thread subject: {subject}, sender: {sender}")
                    # Store all incoming messages and collect the latest incoming per thread
                    latest_incoming_msg = None
                    latest_incoming_date = None
                    has_new_messages = False  # Track if this thread has new messages
                    
                    for m in thread_messages:
                        print(f"[DEBUG] Processing thread message: {m.get('id')}")
                        headers = m.get('payload', {}).get('headers', [])
                        sender = extract_email_address(next((h['value'] for h in headers if h['name'].lower() == 'from'), None))
                        date_str = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
                        label_ids = m.get('labelIds', [])
                        is_read = 'UNREAD' not in label_ids
                        
                        # Extract the actual Message-ID from headers for proper threading
                        message_id_from_headers = extract_message_id_from_headers(headers)
                        print(f"[DEBUG] Thread message {m.get('id')} from: {sender}, read: {is_read}, Message-ID: {message_id_from_headers}")
                        def get_body_parts(payload):
                            text = None
                            html = None
                            if 'parts' in payload:
                                for part in payload['parts']:
                                    if part.get('mimeType') == 'text/plain' and 'data' in part.get('body', {}):
                                        import base64
                                        text = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                                    elif part.get('mimeType') == 'text/html' and 'data' in part.get('body', {}):
                                        import base64
                                        html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                                for part in payload['parts']:
                                    t, h = get_body_parts(part)
                                    if t and not text:
                                        text = t
                                    if h and not html:
                                        html = h
                            else:
                                if payload.get('mimeType') == 'text/plain' and 'data' in payload.get('body', {}):
                                    import base64
                                    text = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
                                elif payload.get('mimeType') == 'text/html' and 'data' in payload.get('body', {}):
                                    import base64
                                    html = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
                            return text, html
                        text_body, html_body = get_body_parts(m.get('payload', {}))
                        main_content = text_body or html_body or ''

                        # Remove HTML parts with 'gmail_quote gmail_quote_container' class
                        if html_body:
                            html_body = remove_gmail_quote(html_body)
                            html_body = clean_html_content(html_body)
                            print(f"[DEBUG] Cleaned HTML content: {html_body}")
                        print(f"[DEBUG] Thread message {m.get('id')} content length: {len(main_content)}")
                        # Use shared AI filter
                        ai_filter_result = await filter_email_with_ai(sender, main_content)
                        print(f"[DEBUG] AI filter result for message {m.get('id')}: {ai_filter_result}")
                        if not ai_filter_result:
                            print(f"[DEBUG] Skipping message {m.get('id')} - failed AI filter")
                            continue
                        # Store incoming message in chat table if not already present
                        db_msg = db.query(Chat).filter_by(message_id=m.get('id')).first()
                        # Ensure sender is not the company's own Gmail box email
                        sender_email = extract_email_address(sender)
                        if not db_msg and sender_email.lower() != company.gmail_box_email.lower():
                            print(f"[DEBUG] Message {m.get('id')} not in database and not sent by company, storing...")
                            has_new_messages = True  # This is a new message
                            # Use timezone-aware datetime for sent_at
                            sent_at = None
                            try:
                                sent_at = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z') if date_str else datetime.now(timezone.utc)
                            except Exception:
                                sent_at = datetime.now(timezone.utc)
                            
                            # Analyze message for action requirement before storing
                            ai_service = SimpleAIService()
                            action_analysis = await ai_service.analyze_message_for_action_requirement(
                                sender=sender,
                                content=main_content,
                                company_goals=company.business_category,
                                company_category=company.business_category,
                                company_id=company.id
                            )
                            
                            action_required = action_analysis.get('action_required', False)
                            action_reason = action_analysis.get('reason', '')
                            action_type = action_analysis.get('action_type', 'none')
                            urgency = action_analysis.get('urgency', 'none')
                            
                            print(f"[DEBUG] Action analysis for message {m.get('id')}: action_required={action_required}, type={action_type}, urgency={urgency}")
                            
                            db_msg = Chat(
                                company_id=company.id,
                                channel_id=thread_id,  # Gmail thread_id becomes channel_id
                                message_id=m.get('id'),
                                from_email=sender_email,
                                to_email=company.gmail_box_email if hasattr(company, 'gmail_box_email') else None,
                                subject=subject,
                                body_text=main_content,
                                body_html=html_body,
                                sent_at=sent_at,
                                is_read=is_read,
                                action_required=action_required,
                                action_reason=action_reason,
                                action_type=action_type,
                                urgency=urgency,
                                email_provider='gmail'
                            )
                            db.add(db_msg)
                            db.commit()
                            
                            # Store message in channel context
                            channel_context_service.store_message_in_context(db, db_msg)
                            
                            print(f"[DEBUG] Stored message {m.get('id')} in database with action_required={action_required}")
                            # Add new incoming message to bodies
                            bodies.append({
                                'from': sender, 
                                'date': date_str, 
                                'content': main_content, 
                                'html': html_body, 
                                'read': is_read,
                                'message_id': m.get('id'),
                                'action_required': action_required,
                                'action_reason': action_reason,
                                'action_type': action_type,
                                'urgency': urgency
                            })
                        else:
                            print(f"[DEBUG] Message {m.get('id')} already in database")
                        # Track the latest incoming message in this thread
                        if db_msg and (not latest_incoming_date or db_msg.sent_at > latest_incoming_date):
                            latest_incoming_msg = db_msg
                            latest_incoming_date = db_msg.sent_at
                            print(f"[DEBUG] Updated latest incoming message: {db_msg.id} from {db_msg.from_email}, Message-ID: {message_id_from_headers}")
                    
                    # Only send AI reply if no outgoing message exists for this thread after the latest incoming
                    if latest_incoming_msg:
                        print(f"[DEBUG] Checking if should send AI reply for message {latest_incoming_msg.id}")
                        # Check if this incoming message has already been replied to
                        if not latest_incoming_msg.replied:
                            print(f"[DEBUG] Message {latest_incoming_msg.id} not replied yet")
                            
                            # Check if action is required - if so, skip AI reply
                            if latest_incoming_msg.action_required:
                                print(f"[DEBUG] Action required for message {latest_incoming_msg.id}, skipping AI reply")
                                logger.info(f"Action required for message {latest_incoming_msg.id}, skipping AI reply")
                            else:
                                # Check channel auto-reply settings
                                channel_settings = channel_auto_reply_settings.get_by_channel_id(db, channel_id=thread_id)
                                if channel_settings and not channel_settings.enable_auto_reply:
                                    print(f"[DEBUG] Auto-reply disabled for channel {thread_id}, skipping AI reply")
                                    logger.info(f"Auto-reply disabled for channel {thread_id}, skipping AI reply")
                                else:
                                    # Check for outgoing messages (messages sent by the company)
                                    last_outgoing = db.query(Chat).filter_by(
                                        company_id=company.id, 
                                        channel_id=thread_id,
                                        from_email=company.gmail_box_email
                                    ).order_by(Chat.sent_at.desc()).first()
                                    
                                    # Ensure last_outgoing is not None before accessing sent_at
                                    should_reply = not last_outgoing or (last_outgoing and last_outgoing.sent_at < latest_incoming_msg.sent_at)
                                    print(f"[DEBUG] Should reply: {should_reply}, last_outgoing: {last_outgoing.id if last_outgoing else None}")
                                    if should_reply:
                                        print(f"[DEBUG] Preparing to send AI reply")
                                        # Additional filtering: Check if we should reply to this email
                                        reply_filter_result = should_reply_to_email(latest_incoming_msg.from_email, latest_incoming_msg.body_text, settings, company.gmail_box_email)
                                        print(f"[DEBUG] Reply filter result: {reply_filter_result}")
                                        if not reply_filter_result:
                                            logger.info(f"Skipping AI reply for email from {latest_incoming_msg.from_email} due to filtering criteria")
                                            print(f"[DEBUG] Skipping AI reply due to filtering criteria")
                                        else:
                                            ai_service = SimpleAIService()
                                            company_goal = getattr(company, 'goal', '')
                                            company_category = getattr(company, 'business_category', '')
                                            
                                            # Use the generate_email_reply method instead of generate_free_text
                                            print(f"[DEBUG] Generating AI email reply for message from: {latest_incoming_msg.from_email}")
                                            reply_text = await ai_service.generate_email_reply(
                                                sender=latest_incoming_msg.from_email,
                                                content=latest_incoming_msg.body_text,
                                                company_id=company.id,
                                                channel_id=thread_id
                                            )
                                            print(f"[DEBUG] Generated AI email reply length: {len(reply_text)}")
                                            try:
                                                # Try to use Gmail API if OAuth2 credentials are available
                                                print(f"[DEBUG] Sending email to: {latest_incoming_msg.from_email}")
                                                # Use the Message-ID from headers for proper threading
                                                original_message_id = message_id_from_headers if message_id_from_headers else latest_incoming_msg.message_id
                                                
                                                # Determine which email service to use for auto-reply
                                                gmail_credentials = getattr(company, 'gmail_box_credentials', None)
                                                outlook_credentials = getattr(company, 'outlook_box_credentials', None)
                                                
                                                if gmail_credentials and company.gmail_box_email:
                                                    # Use Gmail for auto-reply
                                                    sent_message_id = await send_plain_email(
                                                        email_to=latest_incoming_msg.from_email,
                                                        subject=latest_incoming_msg.subject,
                                                        body=reply_text,
                                                        from_email=company.gmail_box_email,
                                                        mail_username=company.gmail_box_email,
                                                        mail_password=company.gmail_box_app_password,
                                                        mail_from_name=company.gmail_box_username,
                                                        gmail_api_credentials=gmail_credentials,
                                                        outlook_api_credentials=None,
                                                        thread_id=thread_id,
                                                        original_message_id=original_message_id
                                                    )
                                                elif outlook_credentials and company.outlook_box_email:
                                                    # Use Outlook for auto-reply
                                                    sent_message_id = await send_plain_email(
                                                        email_to=latest_incoming_msg.from_email,
                                                        subject=latest_incoming_msg.subject,
                                                        body=reply_text,
                                                        from_email=company.outlook_box_email,
                                                        mail_username=company.outlook_box_email,
                                                        mail_password=None,  # Outlook doesn't use app password
                                                        mail_from_name=company.outlook_box_username,
                                                        gmail_api_credentials=None,
                                                        outlook_api_credentials=outlook_credentials,
                                                        thread_id=thread_id,
                                                        original_message_id=original_message_id
                                                    )
                                                else:
                                                    # Fall back to Gmail if no Outlook credentials
                                                    sent_message_id = await send_plain_email(
                                                        email_to=latest_incoming_msg.from_email,
                                                        subject=latest_incoming_msg.subject,
                                                        body=reply_text,
                                                        from_email=getattr(company, 'gmail_box_email', None),
                                                        mail_username=getattr(company, 'gmail_box_email', None),
                                                        mail_password=getattr(company, 'gmail_box_app_password', None),
                                                        mail_from_name=getattr(company, 'gmail_box_username', None),
                                                        gmail_api_credentials=getattr(company, 'gmail_box_credentials', None),
                                                        outlook_api_credentials=None,
                                                        thread_id=thread_id,
                                                        original_message_id=original_message_id
                                                    )
                                                print(f"[DEBUG] Email sent successfully, message ID: {sent_message_id}")
                                                # Mark the incoming message as replied to
                                                latest_incoming_msg.replied = True
                                                db.add(latest_incoming_msg)
                                                # Store outgoing message in chat table
                                                db_reply = Chat(
                                                    company_id=company.id,
                                                    channel_id=thread_id,
                                                    message_id=sent_message_id if sent_message_id else f'reply-{latest_incoming_msg.message_id}',  # Use the actual sent message ID
                                                    from_email=company.gmail_box_email if hasattr(company, 'gmail_box_email') else None,
                                                    email_provider='gmail',
                                                    to_email=extract_email_address(latest_incoming_msg.from_email),
                                                    subject=latest_incoming_msg.subject,
                                                    body_text=reply_text,
                                                    body_html=None,
                                                    sent_at=datetime.now(timezone.utc),
                                                    is_read=True,
                                                    action_required=False,
                                                    action_reason='',
                                                    action_type='',
                                                    urgency=''
                                                )
                                                db.add(db_reply)
                                                db.commit()
                                                
                                                # Store AI reply in channel context
                                                channel_context_service.store_message_in_context(db, db_reply)
                                                
                                                print(f"[DEBUG] Stored AI reply in database with ID: {sent_message_id}")
                                                # Add the replied message to bodies array for frontend
                                                bodies.append({
                                                    'from': db_reply.from_email,
                                                    'date': db_reply.sent_at.isoformat(),
                                                    'content': db_reply.body_text,
                                                    'html': None,
                                                    'read': True,
                                                    'message_id': sent_message_id,  # Include the actual sent message ID
                                                    'action_required': False,
                                                    'action_reason': '',
                                                    'action_type': '',
                                                    'urgency': ''
                                                })
                                            except Exception as e:
                                                logger.error(f"Failed to send or broadcast AI reply: {str(e)}")
                                                print(f"[DEBUG] Error sending AI reply: {str(e)}")
                                                # Rollback the replied flag if sending failed
                                                db.rollback()
                        else:
                            print(f"[DEBUG] Message {latest_incoming_msg.id} already replied")
                    else:
                        print(f"[DEBUG] No latest incoming message found")
                    
                    # Only broadcast if there were new messages in this thread
                    if has_new_messages:
                        print(f"[DEBUG] Broadcasting new email data to frontend")
                        
                        # Get auto-reply settings for this channel
                        channel_settings = channel_auto_reply_settings.get_by_channel_id(db, channel_id=thread_id)
                        enable_auto_reply = channel_settings.enable_auto_reply if channel_settings else True
                        
                        # Get all messages for this thread
                        thread_messages = db.query(Chat).filter(
                            Chat.channel_id == thread_id,
                            Chat.company_id == company.id
                        ).order_by(Chat.sent_at.asc()).all()
                        
                        bodies = []
                        has_new_messages = False
                        seen_message_ids = set() # Track message IDs already processed
                        
                        for msg in thread_messages:
                            # Check if this is a new message (not previously seen)
                            if msg.message_id not in seen_message_ids:
                                has_new_messages = True
                                seen_message_ids.add(msg.message_id)
                            
                            bodies.append({
                                'from': msg.from_email, 
                                'date': msg.sent_at.isoformat(), 
                                'content': msg.body_text, 
                                'html': msg.body_html, 
                                'read': msg.is_read,
                                'notification_read': msg.notification_read,
                                'message_id': msg.message_id,
                                'action_required': msg.action_required or False,
                                'action_reason': msg.action_reason or '',
                                'action_type': msg.action_type or '',
                                'urgency': msg.urgency or ''
                            })
                        
                        email_data = {
                            'id': msg['id'],
                            'thread_id': thread_id,  # Keep for frontend compatibility
                            'channel_id': thread_id,  # Add channel_id for clarity
                            'subject': subject,
                            'from': sender,
                            'date': date,
                            'bodies': bodies,
                            'enable_auto_reply': enable_auto_reply,
                            'email_provider': 'gmail'
                        }
                        print(f"[DEBUG] Broadcasting new email for company {company.id}: {email_data}")
                        logger.info(f"[DEBUG] Broadcasting new email for company {company.id}: {email_data}")
                        print(f"[DEBUG] broadcast_new_email function: {broadcast_new_email}")
                        print(f"[DEBUG] company_email_ws_clients: {company_email_ws_clients}")
                        await broadcast_new_email(company_email_ws_clients, company.id, email_data)
                    else:
                        print(f"[DEBUG] No new messages to broadcast")

            except Exception as e:
                print(f"[DEBUG] Error polling Gmail for company {company.id}: {e}")
                logger.error(f"Error polling Gmail for company {company.id}: {str(e)}")

gmail_monitor_service = GmailMonitorService() 

# Function to remove HTML parts with specific class

def remove_gmail_quote(html_content: str) -> str:
    soup = BeautifulSoup(html_content, 'html.parser')
    for quote in soup.find_all(class_='gmail_quote gmail_quote_container'):
        quote.decompose()  # Remove the element from the tree
    return str(soup) 