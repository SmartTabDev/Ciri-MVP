from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, case, extract
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
import json

from app.api.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.chat import Chat
from app.models.company import Company
from app.models.channel_context import ChannelContext

router = APIRouter()

class DateRangeRequest(BaseModel):
    startDate: str
    endDate: str

class AnalyticsResponse(BaseModel):
    success: bool
    data: dict

@router.post("/ai-handled-requests", response_model=AnalyticsResponse)
async def get_ai_handled_requests(
    request: DateRangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Get the count of AI-handled requests (auto-replied messages), average response time, 
    human escalation rate, and customer satisfaction for a given date range.
    
    Customer satisfaction is calculated by analyzing feedback from channel-context data
    where users have provided feedback on AI responses.
    """
    try:
        # Validate user has company access
        if not current_user.company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not associated with any company"
            )

        # Get company information to identify company email addresses
        company = db.query(Company).filter(Company.id == current_user.company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company not found"
            )

        # Parse date range
        try:
            start_date = datetime.fromisoformat(request.startDate.replace('Z', '+00:00'))
            end_date = datetime.fromisoformat(request.endDate.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use ISO 8601 format (e.g., 2024-01-01T00:00:00.000Z)"
            )

        if start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Start date must be before end date"
            )

        # Build company email filter
        company_emails = []
        if company.gmail_box_email:
            company_emails.append(company.gmail_box_email)
        if company.outlook_box_email:
            company_emails.append(company.outlook_box_email)
        if company.business_email:
            company_emails.append(company.business_email)

        if not company_emails:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No email addresses configured for this company"
            )

        # Count AI-handled requests (outgoing messages sent by the company)
        ai_handled_requests = db.query(func.count(Chat.id)).filter(
            and_(
                Chat.company_id == current_user.company_id,
                Chat.sent_at >= start_date,
                Chat.sent_at <= end_date,
                # Filter for outgoing messages (from company email)
                or_(*[Chat.from_email == email for email in company_emails])
            )
        ).scalar()

        # Calculate average response time using a simpler approach
        # First, get all threads with both incoming and outgoing messages
        threads_with_responses = db.query(Chat.channel_id).filter(
            and_(
                Chat.company_id == current_user.company_id,
                Chat.sent_at >= start_date,
                Chat.sent_at <= end_date,
                Chat.channel_id.isnot(None)
            )
        ).group_by(Chat.channel_id).having(
            and_(
                func.count(case((or_(*[Chat.from_email == email for email in company_emails]), 1))) > 0,
                func.count(case((~or_(*[Chat.from_email == email for email in company_emails]), 1))) > 0
            )
        ).subquery()

        # Calculate response times for these threads
        response_times = []
        for thread_result in db.query(threads_with_responses.c.channel_id).all():
            channel_id = thread_result[0]
            
            # Get first incoming message time
            first_incoming = db.query(func.min(Chat.sent_at)).filter(
                and_(
                    Chat.channel_id == channel_id,
                    ~or_(*[Chat.from_email == email for email in company_emails])
                )
            ).scalar()
            
            # Get first outgoing message time
            first_outgoing = db.query(func.min(Chat.sent_at)).filter(
                and_(
                    Chat.channel_id == channel_id,
                    or_(*[Chat.from_email == email for email in company_emails])
                )
            ).scalar()
            
            if first_incoming and first_outgoing and first_outgoing > first_incoming:
                response_time_seconds = (first_outgoing - first_incoming).total_seconds()
                if response_time_seconds > 0:
                    response_times.append(response_time_seconds)

        # Calculate average response time
        if response_times:
            avg_response_time_seconds = sum(response_times) / len(response_times)
            avg_response_time_minutes = avg_response_time_seconds / 60
            # Format the time for display
            if avg_response_time_minutes < 1:
                avg_response_time_formatted = f"{int(avg_response_time_seconds)}s"
            elif avg_response_time_minutes < 60:
                avg_response_time_formatted = f"{avg_response_time_minutes:.1f}m"
            else:
                hours = int(avg_response_time_minutes // 60)
                remaining_minutes = avg_response_time_minutes % 60
                avg_response_time_formatted = f"{hours}h {int(remaining_minutes)}m"
        else:
            avg_response_time_formatted = "0s"

        # Calculate human escalation rate
        # Count total requests (incoming messages) in the date range
        total_requests = db.query(func.count(Chat.id)).filter(
            and_(
                Chat.company_id == current_user.company_id,
                Chat.sent_at >= start_date,
                Chat.sent_at <= end_date,
                # Filter for incoming messages (not from company email)
                ~or_(*[Chat.from_email == email for email in company_emails])
            )
        ).scalar()

        # Count escalated requests (messages that require human action)
        escalated_requests = db.query(func.count(Chat.id)).filter(
            and_(
                Chat.company_id == current_user.company_id,
                Chat.sent_at >= start_date,
                Chat.sent_at <= end_date,
                # Filter for incoming messages (not from company email)
                ~or_(*[Chat.from_email == email for email in company_emails]),
                # Filter for messages that require human action
                Chat.action_required == True
            )
        ).scalar()

        # Calculate human escalation rate percentage
        if total_requests > 0:
            human_escalation_rate = round((escalated_requests / total_requests) * 100, 1)
        else:
            human_escalation_rate = 0.0

        # Calculate customer satisfaction from channel context chat history
        # Get all channel contexts for the company in the date range
        channel_contexts = db.query(ChannelContext).filter(
            and_(
                ChannelContext.company_id == current_user.company_id,
                ChannelContext.last_updated >= start_date,
                ChannelContext.last_updated <= end_date
            )
        ).all()

        # Analyze chat history for customer satisfaction indicators
        satisfaction_scores = []
        total_conversations = 0
        
        for context in channel_contexts:
            if context.channel_context:
                try:
                    context_data = json.loads(context.channel_context)
                    messages = context_data.get("messages", [])
                    
                    if len(messages) > 0:
                        total_conversations += 1
                        
                        # Analyze conversation patterns for satisfaction indicators
                        satisfaction_score = analyze_conversation_satisfaction(messages, company_emails)
                        if satisfaction_score is not None:
                            satisfaction_scores.append(satisfaction_score)
                            
                except json.JSONDecodeError:
                    continue

        # Calculate average customer satisfaction
        if satisfaction_scores:
            customer_satisfaction = round(sum(satisfaction_scores) / len(satisfaction_scores), 1)
        else:
            customer_satisfaction = 0.0

        # Calculate percentage change by comparing with previous period
        period_duration = end_date - start_date
        previous_start = start_date - period_duration
        previous_end = start_date

        previous_requests = db.query(func.count(Chat.id)).filter(
            and_(
                Chat.company_id == current_user.company_id,
                Chat.sent_at >= previous_start,
                Chat.sent_at <= previous_end,
                # Filter for outgoing messages (from company email)
                or_(*[Chat.from_email == email for email in company_emails])
            )
        ).scalar()

        # Calculate percentage change
        if previous_requests > 0:
            percentage_change = ((ai_handled_requests - previous_requests) / previous_requests) * 100
        else:
            percentage_change = 0.0

        return AnalyticsResponse(
            success=True,
            data={
                "aiHandledRequests": ai_handled_requests,
                "percentageChange": round(percentage_change, 1),
                "averageResponseTime": avg_response_time_formatted,
                "humanEscalationRate": human_escalation_rate,
                "customerSatisfaction": customer_satisfaction,
                "dateRange": {
                    "startDate": request.startDate,
                    "endDate": request.endDate
                }
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

def analyze_conversation_satisfaction(messages: list, company_emails: list) -> float:
    """
    Analyze conversation patterns to determine customer satisfaction score (0-100)
    Based on factors like response quality, conversation flow, resolution patterns, etc.
    """
    if not messages:
        return None
    
    score = 50.0  # Neutral starting point
    
    # Count messages from company vs customer
    company_messages = []
    customer_messages = []
    
    for message in messages:
        from_email = message.get("from_email", "")
        if from_email in company_emails:
            company_messages.append(message)
        else:
            customer_messages.append(message)
    
    # Factor 1: Response time (faster responses = higher satisfaction)
    if len(company_messages) > 0 and len(customer_messages) > 0:
        # Calculate average response time
        response_times = []
        for i, customer_msg in enumerate(customer_messages):
            if i < len(company_messages):
                # Find the next company response after this customer message
                customer_time = datetime.fromisoformat(customer_msg.get("timestamp", "").replace('Z', '+00:00'))
                company_time = datetime.fromisoformat(company_messages[i].get("timestamp", "").replace('Z', '+00:00'))
                
                if company_time > customer_time:
                    response_time_minutes = (company_time - customer_time).total_seconds() / 60
                    response_times.append(response_time_minutes)
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            # Score based on response time: < 5 min = +20, < 15 min = +10, < 30 min = +5, > 60 min = -10
            if avg_response_time < 5:
                score += 20
            elif avg_response_time < 15:
                score += 10
            elif avg_response_time < 30:
                score += 5
            elif avg_response_time > 60:
                score -= 10
    
    # Factor 2: Conversation resolution (shorter conversations = higher satisfaction)
    total_messages = len(messages)
    if total_messages <= 4:  # Quick resolution
        score += 15
    elif total_messages <= 8:  # Moderate resolution
        score += 5
    elif total_messages > 12:  # Long conversation, might indicate issues
        score -= 10
    
    # Factor 3: Response quality indicators
    for company_msg in company_messages:
        content = company_msg.get("content", "").lower()
        
        # Positive indicators in company responses
        positive_indicators = ["thank you", "appreciate", "glad to help", "happy to assist", "welcome", "pleasure"]
        for indicator in positive_indicators:
            if indicator in content:
                score += 2
        
        # Professional indicators
        professional_indicators = ["please", "kindly", "regards", "best regards", "sincerely"]
        for indicator in professional_indicators:
            if indicator in content:
                score += 1
    
    # Factor 4: Customer engagement (if customer sends follow-up messages, it might indicate satisfaction)
    if len(customer_messages) > 1:
        # Check if customer sent follow-up messages after company response
        follow_up_count = 0
        for i, customer_msg in enumerate(customer_messages[1:], 1):
            if i < len(company_messages):
                follow_up_count += 1
        
        if follow_up_count > 0:
            score += 5  # Customer engaged in conversation
    
    # Factor 5: Action required (if no action required, higher satisfaction)
    action_required_count = sum(1 for msg in messages if msg.get("action_required", False))
    if action_required_count == 0:
        score += 10  # No escalation needed
    elif action_required_count > 2:
        score -= 15  # Multiple escalations indicate issues
    
    # Factor 6: Conversation ending patterns
    if len(messages) > 0:
        last_message = messages[-1]
        last_content = last_message.get("content", "").lower()
        
        # Positive ending indicators
        positive_endings = ["thank you", "thanks", "appreciate", "great", "perfect", "excellent"]
        for ending in positive_endings:
            if ending in last_content:
                score += 10
                break
        
        # Negative ending indicators
        negative_endings = ["frustrated", "disappointed", "unhappy", "dissatisfied", "angry"]
        for ending in negative_endings:
            if ending in last_content:
                score -= 15
                break
    
    return max(0, min(100, score))

def analyze_feedback_satisfaction(feedback_data: dict) -> float:
    """
    Analyze structured feedback data to determine satisfaction score (0-100)
    """
    score = 50.0  # Neutral starting point
    
    # Analyze friendliness feedback
    friendliness = feedback_data.get("friendliness", "").lower()
    if friendliness:
        if any(word in friendliness for word in ["good", "great", "excellent", "perfect", "love", "amazing"]):
            score += 20
        elif any(word in friendliness for word in ["bad", "terrible", "awful", "hate", "dislike", "rude"]):
            score -= 20
        elif any(word in friendliness for word in ["okay", "fine", "acceptable", "decent"]):
            score += 5
    
    # Analyze length feedback
    length = feedback_data.get("length", "").lower()
    if length:
        if any(word in length for word in ["perfect", "good", "appropriate", "right"]):
            score += 15
        elif any(word in length for word in ["too long", "too short", "brief", "verbose"]):
            score -= 10
    
    # Analyze emoji feedback
    emoji = feedback_data.get("emoji", "").lower()
    if emoji:
        if any(word in emoji for word in ["good", "perfect", "love", "appropriate"]):
            score += 10
        elif any(word in emoji for word in ["too much", "less", "stop", "annoying"]):
            score -= 10
    
    # Analyze other feedback
    other = feedback_data.get("other", "").lower()
    if other:
        if any(word in other for word in ["good", "great", "excellent", "perfect", "love", "amazing", "helpful"]):
            score += 15
        elif any(word in other for word in ["bad", "terrible", "awful", "hate", "dislike", "useless", "unhelpful"]):
            score -= 15
    
    return max(0, min(100, score))

def analyze_text_satisfaction(text: str) -> float:
    """
    Analyze plain text feedback to determine satisfaction score (0-100)
    """
    text_lower = text.lower()
    score = 50.0  # Neutral starting point
    
    # Positive indicators
    positive_words = ["good", "great", "excellent", "perfect", "love", "amazing", "helpful", "satisfied", "happy", "pleased"]
    for word in positive_words:
        if word in text_lower:
            score += 10
    
    # Negative indicators
    negative_words = ["bad", "terrible", "awful", "hate", "dislike", "useless", "unhelpful", "dissatisfied", "unhappy", "disappointed"]
    for word in negative_words:
        if word in text_lower:
            score -= 10
    
    # Neutral indicators
    neutral_words = ["okay", "fine", "acceptable", "decent", "average"]
    for word in neutral_words:
        if word in text_lower:
            score += 2
    
    return max(0, min(100, score)) 