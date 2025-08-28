import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from dateutil import parser

from app.core.config import settings
from app.models.chat import Chat
from app.models.company import Company
from app.services.outlook_email_service import outlook_email_service
from app.services.ai_service import SimpleAIService, filter_email_with_ai
from app.services.channel_context_service import channel_context_service
from app.crud.crud_channel_auto_reply_settings import channel_auto_reply_settings
from app.core.email import send_plain_email
from app.util import extract_email_address, clean_html_content
from app.core.broadcast import broadcast_new_email
from app.core.ws_clients import company_email_ws_clients

logger = logging.getLogger(__name__)

def should_reply_to_outlook_email(sender: str, content: str, settings, company_outlook_box_email: str = None) -> bool:
    """Check if we should reply to this Outlook email based on filtering rules."""
    try:
        # 1. Skip if email content contains an unsubscribe link
        if 'unsubscribe' in content.lower():
            print(f"[DEBUG] Skipping Outlook email - contains unsubscribe link")
            return False
        
        # 2. Skip if sender address contains 'no-reply' or 'noreply'
        if sender and ('no-reply' in sender.lower() or 'noreply' in sender.lower()):
            print(f"[DEBUG] Skipping Outlook email - no-reply sender: {sender}")
            return False
        
        # 3. Skip if email is from settings.MAIL_FROM
        if sender and settings.MAIL_FROM and settings.MAIL_FROM.lower() in extract_email_address(sender).lower():
            print(f"[DEBUG] Skipping Outlook email - from settings.MAIL_FROM: {sender}")
            return False
        
        # 4. Skip if message is sent by the company's own Outlook box email
        if sender and company_outlook_box_email:
            sender_email = extract_email_address(sender)
            if company_outlook_box_email.lower() in sender_email.lower():
                print(f"[DEBUG] Skipping Outlook email - sent by company itself: {sender}")
                return False
        
        return True
    except Exception as e:
        print(f"[DEBUG] Error in should_reply_to_outlook_email: {e}")
        return False

def parse_outlook_message_content(msg_detail: dict) -> Tuple[str, str]:
    """
    Parse Outlook message content to extract text and HTML parts.
    Similar to Gmail's get_body_parts function.
    
    Returns:
        Tuple[str, str]: (text_content, html_content)
    """
    try:
        body = msg_detail.get('body', {})
        content = body.get('content', '') if body else ''
        content_type = body.get('contentType', 'text')
        
        text_content = None
        html_content = None
        
        if content_type == 'html':
            html_content = content
            # Clean HTML content
            html_content = clean_html_content(html_content)
            # Remove Outlook-specific quotes if needed
            html_content = remove_outlook_quotes(html_content)
            # Extract text from HTML as fallback
            text_content = extract_text_from_html(html_content)
        else:
            text_content = content
        
        return text_content or '', html_content or ''
        
    except Exception as e:
        print(f"[DEBUG] Error parsing Outlook message content: {e}")
        return '', ''

def remove_outlook_quotes(html_content: str) -> str:
    """
    Remove Outlook-specific quote patterns from HTML content.
    Similar to Gmail's remove_gmail_quote function.
    """
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove common Outlook quote patterns
        # Remove elements with specific Outlook quote classes
        for quote in soup.find_all(class_=lambda x: x and 'quote' in x.lower()):
            quote.decompose()
        
        # Remove elements with specific Outlook signature patterns
        for sig in soup.find_all(class_=lambda x: x and 'signature' in x.lower()):
            sig.decompose()
        
        # Remove elements with specific Outlook reply patterns
        for reply in soup.find_all(class_=lambda x: x and 'reply' in x.lower()):
            reply.decompose()
        
        return str(soup)
    except Exception as e:
        print(f"[DEBUG] Error removing Outlook quotes: {e}")
        return html_content

def extract_text_from_html(html_content: str) -> str:
    """
    Extract plain text from HTML content.
    """
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text(separator=' ', strip=True)
    except Exception as e:
        print(f"[DEBUG] Error extracting text from HTML: {e}")
        return html_content

class OutlookMonitorService:
    def __init__(self):
        self.last_seen_message_ids = {}  # company_id -> last seen Outlook message ID

    async def poll_new_emails(self, db: Session):
        """Poll for new emails from Outlook for all companies with Outlook credentials."""
        print("[DEBUG] poll_new_outlook_emails called")
        logger.info("[DEBUG] poll_new_outlook_emails called")
        
        companies = db.query(Company).filter(Company.outlook_box_credentials.isnot(None)).all()
        print(f"[DEBUG] Found {len(companies)} companies with Outlook credentials")
        
        for company in companies:
            print(f"[DEBUG] Polling Outlook for company {company.id} - {company.name}")
            logger.info(f"[DEBUG] Polling Outlook for company {company.id} - {company.name}")
            
            try:
                # Get messages from Outlook API
                messages, tokens_refreshed = await outlook_email_service.get_user_messages(
                    credentials_data=company.outlook_box_credentials,
                    max_results=10,
                    query="isRead eq false"
                )
                
                # Save refreshed tokens back to database if they were refreshed
                if tokens_refreshed:
                    try:
                        from app.crud.crud_company import company as company_crud
                        company_crud.update(
                            db=db,
                            db_obj=company,
                            obj_in={"outlook_box_credentials": company.outlook_box_credentials}
                        )
                        logger.info(f"Updated Outlook credentials for company {company.id}")
                    except Exception as e:
                        logger.warning(f"Failed to update Outlook credentials for company {company.id}: {str(e)}")
                
                print(f"[DEBUG] Found {len(messages)} unread messages in Outlook for company {company.id}")
                
                last_seen_id = self.last_seen_message_ids.get(company.id)
                print(f"[DEBUG] Last seen message ID for company {company.id}: {last_seen_id}")
                
                new_messages = []
                for msg in messages:
                    if msg['id'] == last_seen_id:
                        print(f"[DEBUG] Reached last seen message ID, stopping at: {last_seen_id}")
                        break
                    
                    # Get detailed message information
                    msg_detail = await outlook_email_service.get_message_details(
                        message_id=msg['id'],
                        credentials_data=company.outlook_box_credentials
                    )
                    
                    sender = msg_detail.get('from', {}).get('emailAddress', {}).get('address', '')
                    subject = msg_detail.get('subject', '(No Subject)')
                    received_date = msg_detail.get('receivedDateTime', '')
                    is_read = msg_detail.get('isRead', False)
                    conversation_id = msg_detail.get('conversationId', msg['id'])
                    
                    print(f"[DEBUG] Processing Outlook message {msg['id']} from: {sender}")
                    
                    # Get message content
                    text_content, html_content = parse_outlook_message_content(msg_detail)
                    
                    print(f"[DEBUG] Outlook message {msg['id']} content length: {len(text_content)}")
                    
                    # Apply filtering rules
                    if not should_reply_to_outlook_email(sender, text_content, settings, company.outlook_box_email):
                        print(f"[DEBUG] Skipping Outlook message {msg['id']} - failed filtering rules")
                        continue
                    
                    print(f"[DEBUG] Outlook message {msg['id']} passed all filters, adding to new_messages")
                    new_messages.append({
                        'id': msg['id'],
                        'detail': msg_detail,
                        'sender': sender,
                        'subject': subject,
                        'content': text_content, # Store text content
                        'received_date': received_date,
                        'is_read': is_read,
                        'conversation_id': conversation_id
                    })
                
                if new_messages:
                    print(f"[DEBUG] New Outlook messages found for company {company.id}: {[m['id'] for m in new_messages]}")
                    self.last_seen_message_ids[company.id] = new_messages[0]['id']
                
                # Process new messages
                for msg_data in reversed(new_messages):  # Oldest first
                    await self._process_outlook_message(msg_data, company, db)
                    
            except Exception as e:
                print(f"[DEBUG] Error polling Outlook for company {company.id}: {e}")
                logger.error(f"Error polling Outlook for company {company.id}: {str(e)}")

    async def _process_outlook_message(self, msg_data: dict, company: Company, db: Session):
        """Process a single Outlook message."""
        try:
            msg_id = msg_data['id']
            msg_detail = msg_data['detail']
            sender = msg_data['sender']
            subject = msg_data['subject']
            content = msg_data['content']  # This is now text_content
            received_date = msg_data['received_date']
            is_read = msg_data['is_read']
            conversation_id = msg_data['conversation_id']
            
            print(f"[DEBUG] Processing new Outlook message: {msg_id}")
            
            # Parse received date
            sent_at = None
            try:
                sent_at = parser.parse(received_date) if received_date else datetime.now(timezone.utc)
            except Exception:
                sent_at = datetime.now(timezone.utc)
            
            # Use shared AI filter
            ai_filter_result = await filter_email_with_ai(sender, content)
            print(f"[DEBUG] AI filter result for Outlook message {msg_id}: {ai_filter_result}")
            
            if not ai_filter_result:
                print(f"[DEBUG] Skipping Outlook message {msg_id} - failed AI filter")
                return
            
            # Store incoming message in chat table if not already present
            db_msg = db.query(Chat).filter_by(message_id=msg_id).first()
            sender_email = extract_email_address(sender)
            
            if not db_msg and sender_email.lower() != company.outlook_box_email.lower():
                print(f"[DEBUG] Outlook message {msg_id} not in database and not sent by company, storing...")
                
                # Parse content again to get both text and HTML
                text_content, html_content = parse_outlook_message_content(msg_detail)
                
                # Analyze message for action requirement
                ai_service = SimpleAIService()
                action_analysis = await ai_service.analyze_message_for_action_requirement(
                    sender=sender,
                    content=text_content,  # Use text content for analysis
                    company_goals=company.business_category,
                    company_category=company.business_category,
                    company_id=company.id
                )
                
                action_required = action_analysis.get('action_required', False)
                action_reason = action_analysis.get('reason', '')
                action_type = action_analysis.get('action_type', 'none')
                urgency = action_analysis.get('urgency', 'none')
                
                print(f"[DEBUG] Action analysis for Outlook message {msg_id}: action_required={action_required}, type={action_type}, urgency={urgency}")
                
                db_msg = Chat(
                    company_id=company.id,
                    channel_id=conversation_id,  # Outlook conversationId becomes channel_id
                    message_id=msg_id,
                    from_email=sender_email,
                    to_email=company.outlook_box_email,
                    subject=subject,
                    body_text=text_content,  # Store text content
                    body_html=html_content,  # Store HTML content
                    sent_at=sent_at,
                    is_read=is_read,
                    action_required=action_required,
                    action_reason=action_reason,
                    action_type=action_type,
                    urgency=urgency,
                    email_provider='outlook'
                )
                db.add(db_msg)
                db.commit()
                
                # Store message in channel context
                channel_context_service.store_message_in_context(db, db_msg)
                
                print(f"[DEBUG] Stored Outlook message {msg_id} in database with action_required={action_required}")
                
                # Check for auto-reply settings and send reply if needed
                auto_reply_data = await self._handle_outlook_auto_reply(msg_data, company, db)
                
                # Broadcast new email to frontend (including auto-reply if sent)
                await self._broadcast_outlook_email(msg_data, company, db, auto_reply_data)
                
        except Exception as e:
            print(f"[DEBUG] Error processing Outlook message {msg_data.get('id', 'unknown')}: {e}")
            logger.error(f"Error processing Outlook message: {str(e)}")

    async def _handle_outlook_auto_reply(self, msg_data: dict, company: Company, db: Session):
        """Handle auto-reply for Outlook messages."""
        try:
            # Get auto-reply settings for this channel
            channel_settings = channel_auto_reply_settings.get_by_channel_id(db, channel_id=msg_data['conversation_id'])
            enable_auto_reply = channel_settings.enable_auto_reply if channel_settings else True
            
            if not enable_auto_reply:
                print(f"[DEBUG] Auto-reply disabled for Outlook thread {msg_data['conversation_id']}")
                return
            
            # Generate AI reply using text content
            ai_service = SimpleAIService()
            reply_text = await ai_service.generate_email_reply(
                sender=msg_data['sender'],
                content=msg_data['content'],  # Use text content for reply generation
                company_id=company.id,
                channel_id=msg_data["conversation_id"]
            )
            
            if reply_text:
                print(f"[DEBUG] Sending auto-reply to Outlook message {msg_data['id']}")
                
                # Send reply via Outlook API using reply endpoint
                from app.services.outlook_email_service import outlook_email_service
                
                try:
                    # Try to use the proper reply endpoint first
                    sent_message_id = await outlook_email_service.reply_to_message_via_outlook_api(
                        message_id=msg_data['id'],
                        reply_body=reply_text,
                        credentials_data=company.outlook_box_credentials,
                        from_email=company.outlook_box_email
                    )
                    print(f"[DEBUG] Outlook auto-reply sent via reply endpoint, message ID: {sent_message_id}")
                except Exception as reply_error:
                    print(f"[DEBUG] Reply endpoint failed, falling back to send email: {reply_error}")
                    # Fallback to sending a new email if reply endpoint fails
                    sent_message_id = await send_plain_email(
                        email_to=msg_data['sender'],
                        subject=f"Re: {msg_data['subject']}",
                        body=reply_text,
                        from_email=company.outlook_box_email,
                        mail_username=company.outlook_box_email,
                        mail_password=company.outlook_box_password,  # Use Outlook password for SMTP fallback
                        mail_from_name=company.outlook_box_username,
                        gmail_api_credentials=None,
                        outlook_api_credentials=company.outlook_box_credentials,
                        thread_id=msg_data['conversation_id'],
                        original_message_id=msg_data['id']
                    )
                
                print(f"[DEBUG] Outlook auto-reply sent successfully, message ID: {sent_message_id}")
                
                # Store outgoing auto-reply message in chat table
                from app.models.chat import Chat
                from app.services.channel_context_service import channel_context_service
                from datetime import datetime, timezone
                
                db_reply = Chat(
                    company_id=company.id,
                    channel_id=msg_data['conversation_id'],
                    message_id=sent_message_id if sent_message_id else f'reply-{msg_data["id"]}',
                    from_email=company.outlook_box_email,
                    email_provider='outlook',
                    to_email=msg_data['sender'],
                    subject=f"Re: {msg_data['subject']}",
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
                
                print(f"[DEBUG] Stored Outlook auto-reply in database with ID: {sent_message_id}")
                
                # Return the reply data for broadcasting
                return {
                    'from': company.outlook_box_email,
                    'date': datetime.now(timezone.utc).isoformat(),
                    'content': reply_text,
                    'html': None,
                    'read': True,
                    'message_id': sent_message_id,
                    'action_required': False,
                    'action_reason': '',
                    'action_type': '',
                    'urgency': ''
                }
                
        except Exception as e:
            print(f"[DEBUG] Error handling Outlook auto-reply: {e}")
            logger.error(f"Error handling Outlook auto-reply: {str(e)}")
            return None

    async def _broadcast_outlook_email(self, msg_data: dict, company: Company, db: Session, auto_reply_data: dict = None):
        """Broadcast new Outlook email to frontend."""
        try:
            # Get auto-reply settings for this channel
            channel_settings = channel_auto_reply_settings.get_by_channel_id(db, channel_id=msg_data['conversation_id'])
            enable_auto_reply = channel_settings.enable_auto_reply if channel_settings else True
            
            # Parse content to get both text and HTML for broadcast
            text_content, html_content = parse_outlook_message_content(msg_data['detail'])
            
            # Prepare bodies array with incoming message
            bodies = [{
                'from': msg_data['sender'], 
                'date': msg_data['received_date'], 
                'content': text_content,  # Use text content
                'html': html_content,  # Include HTML content
                'read': msg_data['is_read'], 
                'notification_read': False,  # New messages start as unread notifications
                'message_id': msg_data['id'], 
                'action_required': False, 
                'action_reason': '', 
                'action_type': '', 
                'urgency': ''
            }]
            
            # Add auto-reply message to bodies if it was sent
            if auto_reply_data:
                bodies.append(auto_reply_data)
            
            # Broadcast new email to WebSocket clients
            email_data = {
                'id': msg_data['id'],
                'thread_id': msg_data['conversation_id'],  # Keep for frontend compatibility
                'channel_id': msg_data['conversation_id'],  # Add channel_id for clarity
                'subject': msg_data['subject'],
                'from': msg_data['sender'],
                'date': msg_data['received_date'],
                'bodies': bodies,  # Include both incoming and auto-reply messages
                'enable_auto_reply': enable_auto_reply,
                'email_provider': 'outlook'
            }
            
            await broadcast_new_email(company_email_ws_clients, company.id, email_data)
            
        except Exception as e:
            print(f"[DEBUG] Error broadcasting Outlook email: {e}")
            logger.error(f"Error broadcasting Outlook email: {str(e)}")

# Create a singleton instance
outlook_monitor_service = OutlookMonitorService()
