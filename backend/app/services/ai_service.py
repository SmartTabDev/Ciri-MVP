import time
import base64
import logging
import asyncio
from typing import Optional, Tuple, Dict, Any
import tempfile
import os
from fastapi import UploadFile
from datetime import datetime, timedelta
import json
import pytz

from app.schemas.ai import InputType, AudioFormat, VoiceType, AIRequest, AIResponse
from app.core.config import settings
from app.models.company import Company
from app.models.ai_agent_settings import AIAgentSettings
from app.services.calendar_service import calendar_service

logger = logging.getLogger(__name__)

class SimpleAIService:
    def __init__(self):
        """Initialize the OpenAI service."""
        try:
            import openai
            self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
            self.tts_model = "tts-1"
            self.chat_model = "gpt-4o-mini"
            self.transcription_model = "whisper-1"
            logger.info(f"OpenAI service initialized with models: {self.chat_model}, {self.tts_model}, {self.transcription_model}")
        except ImportError:
            logger.error("OpenAI package not installed. Run 'pip install openai'")
            raise ImportError("OpenAI package not installed. Run 'pip install openai'")
        except Exception as e:
            logger.error(f"Error initializing OpenAI service: {str(e)}")
            raise
    
    async def process_request(self, request: AIRequest, company: Company, ai_settings: AIAgentSettings) -> AIResponse:
        """
        Process an AI request and return the appropriate response.
        
        Args:
            request: The AI request containing text or audio file
            company: The company model instance for calendar context
            ai_settings: The AI agent settings for the company
            
        Returns:
            AIResponse: The AI response with text or audio data
        """
        start_time = time.time()
        input_type = request.get_input_type()
        
        # Step 1: Extract or transcribe text from input
        if input_type == InputType.AUDIO:
            text = await self._transcribe_audio(request.audio_file, request.audio_format)
        else:
            text = request.text

        # Step 2: Get calendar context using the user's query
        calendar_context = await self._get_calendar_context(company, text)

        # Step 3: Generate AI response text with calendar context
        ai_response_text, model_used = await self._generate_ai_response(
            text, 
            calendar_context, 
            request.max_tokens, 
            request.temperature, 
            ai_settings.dialect, 
            company.name, 
            ai_settings.goal,
            company.business_category,
            company.terms_of_service
        )

        # Step 4: Determine output type (match input type)
        output_type = input_type
        
        # Step 5: Convert response to audio if needed
        audio_data = None
        audio_format = None
        
        if output_type == InputType.AUDIO:
            audio_data, audio_format = await self._text_to_speech(ai_response_text, ai_settings.voice_type)
        
        processing_time = time.time() - start_time
        
        # Return the response
        return AIResponse(
            text=ai_response_text if output_type == InputType.TEXT else None,
            audio_data=audio_data,
            audio_format=audio_format,
            input_type=input_type,
            output_type=output_type,
            processing_time=processing_time,
            model_used=model_used
        )
    
    async def _transcribe_audio(self, audio_file: UploadFile, audio_format: AudioFormat) -> str:
        """
        Transcribe audio to text using OpenAI Whisper.
        
        Args:
            audio_file: The uploaded audio file
            audio_format: Format of the audio data
            
        Returns:
            Transcribed text
        """
        try:
            # Save uploaded file to temporary file
            with tempfile.NamedTemporaryFile(suffix=f".{audio_format}", delete=False) as temp_file:
                content = await audio_file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            try:
                # Transcribe with OpenAI Whisper
                with open(temp_file_path, "rb") as audio_file:
                    transcription = self.client.audio.transcriptions.create(
                        model=self.transcription_model,
                        file=audio_file
                    )
                return transcription.text
            finally:
                # Clean up temp file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return f"Error transcribing audio: {str(e)}"
    
    async def _get_calendar_context(self, company: Company, user_query: str) -> str:
        """
        Get calendar context for the company.
        
        Args:
            company: Company model instance
            user_query: The user's original query text
            
        Returns:
            Calendar context as a string
        """
        try:
            # Get current date in UTC
            current_date = datetime.now(pytz.UTC)
            
            # First, use AI to determine appropriate time range based on user's query
            time_range_prompt = (
                f"Current date is {current_date.strftime('%Y-%m-%d')}. "
                f"Based on this user query: '{user_query}', determine the appropriate time range for calendar events. "
                "Return the response in JSON format with 'start_time' and 'end_time' in ISO format. "
                "For example: {\"start_time\": \"2024-03-20T00:00:00Z\", \"end_time\": \"2024-03-27T23:59:59Z\"}. "
                "If no specific time range is mentioned, default to the next 7 days from the current date. "
                "Consider natural language time references like 'today', 'tomorrow', 'next week', etc. "
                "Make sure to use the current date as the reference point for all time calculations."
            )
            
            time_range_response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that determines time ranges for calendar queries. Always use the provided current date as the reference point."},
                    {"role": "user", "content": time_range_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            try:
                time_range = json.loads(time_range_response.choices[0].message.content)
                start_time = datetime.fromisoformat(time_range["start_time"].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(time_range["end_time"].replace('Z', '+00:00'))
            except (json.JSONDecodeError, KeyError, ValueError):
                # Fallback to default time range if AI response is invalid
                start_time = current_date
                end_time = start_time + timedelta(days=7)
            
            # Get calendar events for the determined time range
            calendar_response = await calendar_service.get_company_calendar_events(
                None,  # No DB session needed as we're using stored credentials
                company,
                start_time=start_time,
                end_time=end_time,
                max_results=5  # Limit to 5 upcoming events
            )
            
            if not calendar_response.events:
                return "No upcoming calendar events found."
            
            # Format calendar events into a context string
            context = "Upcoming calendar events:\n"
            for event in calendar_response.events:
                context += f"- {event.summary} on {event.start.strftime('%Y-%m-%d %H:%M')}"
                if event.location:
                    context += f" at {event.location}"
                context += "\n"
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting calendar context: {str(e)}")
            return "Unable to fetch calendar events."
    
    async def _generate_ai_response(
        self, 
        text: str,
        calendar_context: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        dialect: str = "Southern dialect",
        company_name: str = "",
        goal: str = "Book appointments and collect customer emails",
        business_category: str = "",
        terms_of_service: str = ""
    ) -> Tuple[str, str]:
        """
        Generate AI response from text using OpenAI.
        
        Args:
            text: The input text
            calendar_context: Calendar context to include in the prompt
            max_tokens: Maximum tokens for the response
            temperature: Temperature for response generation
            dialect: The dialect to use for the response
            company_name: The name of the company
            goal: The goal for the AI agent
            business_category: The company's business category
            terms_of_service: The company's terms of service
            
        Returns:
            Tuple containing the AI response text and model used
        """
        try:
            # Create system message with calendar context, dialect, company name, and business details
            system_message = (
                f"You are a professional and engaging AI receptionist for {company_name}, "
                f"a {business_category} business. "
                "Always respond in Norwegian (Bokmål), keeping your responses concise, professional, and friendly. "
                "Be efficient in your communication while maintaining a warm and approachable tone. "
                f"Your primary goal is to: {goal}. "
                "You have access to the company's calendar information to help answer questions about scheduling and events. "
                f"Here is the current calendar context:\n{calendar_context}\n\n"
                f"Company Terms of Service:\n{terms_of_service}\n\n"
                "Important: When a customer shows interest in booking an appointment or using our services, "
                "always ask for their email address. This is necessary for: "
                "1. Sending appointment confirmations "
                "2. Following up on their inquiries "
                "3. Sending important updates about their service "
                "4. Maintaining communication records "
                "Ask for their email in a natural way, for example: "
                "'For å sende deg bekreftelse og viktige oppdateringer, trenger jeg e-postadressen din. Kan du dele den med meg?'"
            )
            
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": text}
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content, self.chat_model
            
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return f"Error generating AI response: {str(e)}", self.chat_model
    
    async def _text_to_speech(self, text: str, voice: VoiceType = VoiceType.ALLOY) -> Tuple[str, AudioFormat]:
        """
        Convert text to speech using OpenAI TTS.
        
        Args:
            text: The text to convert
            voice: The voice to use for TTS
            
        Returns:
            Tuple containing base64 encoded audio data and format
        """
        try:
            response = self.client.audio.speech.create(
                model=self.tts_model,
                voice=voice,
                input=text
            )
            
            # Convert audio to base64
            audio_data = base64.b64encode(response.content).decode('utf-8')
            
            return audio_data, AudioFormat.MP3
            
        except Exception as e:
            logger.error(f"Error converting text to speech: {str(e)}")
            raise

    async def generate_text(self, prompt: str) -> str:
        """
        Generate text using OpenAI's chat completion.
        
        Args:
            prompt: The prompt to generate text from
            
        Returns:
            Generated text response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates professional email content."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating text: {str(e)}")
            raise

    async def generate_free_text(self, prompt: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates professional email replies."},
                    {"role": "user", "content": prompt}
                ]
                # Do NOT set response_format here!
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating free text: {str(e)}")
            raise

    async def generate_email_reply(self, sender: str, content: str, company_id: int, channel_id: str) -> str:
        """
        Generate an email reply using AI based on the incoming message and company context.
        
        Args:
            sender: The email sender
            content: The email content
            company_id: The company ID
            channel_id: The channel ID for context
            
        Returns:
            str: The generated email reply
        """
        try:
            # Get company information from database
            from app.db.session import SessionLocal
            from app.models.company import Company
            from app.models.company_context import CompanyContext
            from app.services.channel_context_service import channel_context_service
            
            db = SessionLocal()
            try:
                # Get company details
                company = db.query(Company).filter(Company.id == company_id).first()
                if not company:
                    logger.error(f"Company not found for ID: {company_id}")
                    return "Takk for din henvendelse. Vi vil svare deg så snart som mulig."
                
                # Get company context
                company_context = db.query(CompanyContext).filter(CompanyContext.company_id == company_id).first()
                
                # Get channel context
                channel_context = channel_context_service.get_channel_context(db, company_id, channel_id)
                
                # Prepare context information - only company info and company context
                company_goal = getattr(company, 'goal', '')
                company_category = getattr(company, 'business_category', '')
                terms_of_service = getattr(company, 'terms_of_service', '')
                text_context = company_context.text_context if company_context else ''
                flow_context = company_context.flow_context if company_context else ''
                
                
                prompt = f"""
                Don't show your name.
                Company name is {company.name}, Company category is {company_category}, phone number is {company.phone_numbers}, Company goal is {company.goal}, Terms of service is {company.terms_of_service}
                
                Please reference below context when generating the email reply.

                Chat History: {channel_context}
                Text Context: {text_context}
                Flow Instructions: {flow_context}
                
                Reply to the following email in a professional, helpful, and friendly manner.
                Sender email: {sender}
                Email content: {content}
                
                Generate a professional email reply in Norwegian (Bokmål). Keep it concise, relevant, and helpful.
                The reply should be appropriate for the business context and address the sender's inquiry professionally.
                Use the provided company context to personalize the response appropriately.
                """

                print(f"[DEBUG] Prompt length: {prompt}")
                
                response = self.client.chat.completions.create(
                    model=self.chat_model,
                    messages=[
                        {"role": "system", "content": prompt},
                        {"role": "user", "content": content}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                
                return response.choices[0].message.content
                
            finally:
                db.close()
            
        except Exception as e:
            logger.error(f"Error generating email reply: {str(e)}")
            # Return a fallback reply if AI generation fails
            return f"Takk for din henvendelse. Vi vil svare deg så snart som mulig. Med vennlig hilsen, {company_category if 'company_category' in locals() else 'teamet'}."

    async def analyze_message_for_action_requirement(self, sender: str, content: str, company_goals: str, company_category: str, company_id: int = None) -> Dict[str, Any]:
        """
        Analyze incoming message to determine if it requires human action.
        Includes text context and flow context in the analysis.
        Returns a dictionary with action_required flag and reason.
        """
        try:
            # Get company context if company_id is provided
            text_context = ""
            flow_context = ""
            
            if company_id:
                from app.db.session import SessionLocal
                from app.models.company_context import CompanyContext
                
                db = SessionLocal()
                try:
                    company_context = db.query(CompanyContext).filter(CompanyContext.company_id == company_id).first()
                    if company_context:
                        text_context = company_context.text_context or ""
                        flow_context = company_context.flow_context or ""
                finally:
                    db.close()
            
            prompt = f"""
            You are an AI agent that analyzes incoming messages to determine if human action is required.
            
            IMPORTANT: You can send messages to users automatically, so sending messages does NOT require human action.
            
            Company Information:
            - Category: {company_category}
            - Goals: {company_goals}
            - Text Context: {text_context}
            - Flow Context: {flow_context}
            
            Message Details:
            - From: {sender}
            - Content: {content}
            
            ANALYSIS RULES:
            1. FIRST, check if there are conflicts between the company text context and flow context (contradictory instructions).
            2. If conflicts are detected, return action_required: true with reason explaining the conflict that needs human resolution.
            3. If no conflicts, check if the company text context or flow context contains specific instructions for handling this type of request.
            4. If specific instructions exist, follow them and return action_required: false (no human action needed).
            5. If no specific instructions exist, then check if the request requires human action for any of these reasons:
               - Refund requests or payment issues
               - Complaints or disputes
               - Special requests that cannot be handled by AI
               - Urgent matters requiring immediate attention
               - Requests for human contact or callback
            6. If the request requires human action (except sending messages), return action_required: true.
            
            Return JSON with this structure:
            {{
                "action_required": true/false,
                "reason": "explain why action is required or not. If conflicts exist, specify: 'There is conflict between text context and flow context for [specific issue], resolve this'. If following context instructions, mention which context and what instruction.",
                "action_type": "appointment|refund|complaint|technical|legal|conflict|other|none",
                "urgency": "low|medium|high|none"
            }}
            """
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo-0125",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=400,
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return {
                "action_required": result.get("action_required", False),
                "reason": result.get("reason", ""),
                "action_type": result.get("action_type", "none"),
                "urgency": result.get("urgency", "none")
            }
            
        except Exception as e:
            print(f"Error analyzing message for action requirement: {str(e)}")
            # Default to no action required if AI fails
            return {
                "action_required": False,
                "reason": "AI analysis failed, defaulting to no action required",
                "action_type": "none",
                "urgency": "none"
            }
# Shared async function to filter emails using AI
async def filter_email_with_ai(sender: str, content: str) -> bool:    
    if 'unsubscribe' in content.lower():
        return False
    
    # Don't reply if sender address contains 'no-reply' or 'noreply'
    if 'no-reply' in sender.lower() or 'noreply' in sender.lower():
        return False
    
    # Don't reply if email is from settings.MAIL_FROM
    if settings.MAIL_FROM and settings.MAIL_FROM.lower() in sender.lower():
        return False

    return True