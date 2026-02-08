"""
Pydantic models for API request and response schemas.

This module defines the data models for API inputs and outputs,
providing validation and serialization.
"""

from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, field_validator
import base64


class FramesRequest(BaseModel):
    """Request model for pre-extracted frames input."""

    frames: List[str] = Field(
        ...,
        min_length=3,
        max_length=10,
        description="Array of 3-10 base64-encoded JPEG images"
    )

    @field_validator('frames')
    @classmethod
    def validate_base64(cls, v: List[str]) -> List[str]:
        """Validate that each frame is valid base64."""
        for i, frame in enumerate(v):
            try:
                # Attempt to decode to verify it's valid base64
                base64.b64decode(frame, validate=True)
            except Exception as e:
                raise ValueError(f"Frame {i} is not valid base64: {str(e)}")
        return v


class AnalyzeResponse(BaseModel):
    """Success response model for exercise analysis."""

    feedback: str = Field(
        ...,
        description="Personalized form feedback from the LLM"
    )
    frames_analyzed: int = Field(
        ...,
        description="Number of frames that were analyzed"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp of the analysis"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "feedback": "I can see you're performing a squat. You're doing a good job keeping your chest up and maintaining balance throughout the movement. One thing to focus on is your knee alignment - make sure your knees track over your toes rather than caving inward.",
                "frames_analyzed": 5,
                "timestamp": "2026-02-07T15:30:00Z"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(
        ...,
        description="Error type or category"
    )
    detail: str = Field(
        ...,
        description="Detailed error message"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Video too large",
                "detail": "Maximum size: 50MB, maximum duration: 30 seconds"
            }
        }
