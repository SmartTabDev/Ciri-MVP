from enum import Enum
from typing import Optional, Union
from pydantic import BaseModel, Field, validator
from fastapi import UploadFile

class InputType(str, Enum):
    TEXT = "text"
    AUDIO = "audio"

class AudioFormat(str, Enum):
    MP3 = "mp3"
    WAV = "wav"
    OGG = "ogg"
    WEBM = "webm"

class VoiceType(str, Enum):
    ALLOY = "alloy"
    ASH = "ash"
    CORAL = "coral"
    ECHO = "echo"
    FABLE = "fable"
    ONYX = "onyx"
    NOVA = "nova"
    SAGE = "sage"
    SHIMMER = "shimmer"

class AIRequest(BaseModel):
    """Request model for the AI API"""
    # Either text or audio_file must be provided
    text: Optional[str] = Field(None, min_length=1, max_length=4000)
    audio_file: Optional[UploadFile] = None
    audio_format: Optional[AudioFormat] = AudioFormat.MP3
    
    # Optional parameters
    max_tokens: Optional[int] = Field(1000, ge=1, le=4000)
    temperature: Optional[float] = Field(0.7, ge=0, le=1.0)
    
    @validator('text', 'audio_file')
    def validate_input(cls, v, values):
        # Ensure at least one of text or audio_file is provided
        if 'text' in values and values['text'] is None and 'audio_file' in values and values['audio_file'] is None:
            raise ValueError("Either text or audio_file must be provided")
        return v
    
    def get_input_type(self) -> InputType:
        """Determine the input type based on the provided data"""
        if self.audio_file is not None:
            return InputType.AUDIO
        return InputType.TEXT

class AIResponse(BaseModel):
    """Response model for the AI API"""
    text: Optional[str] = None
    audio_data: Optional[str] = None
    audio_format: Optional[AudioFormat] = None
    input_type: InputType
    output_type: InputType
    processing_time: float
    model_used: str