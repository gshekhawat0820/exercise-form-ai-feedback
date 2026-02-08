"""
API routes for exercise form feedback analysis.

This module provides the main POST /analyze endpoint that accepts
either video files or pre-extracted frames and returns AI-generated
exercise form feedback.
"""

import logging
import tempfile
import os
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, Request

from app.models.schemas import FramesRequest, AnalyzeResponse, ErrorResponse
from app.services.frame_sampler import sample_frames_from_video, resize_frame, get_video_duration
from app.services.video_processor import encode_frame_to_base64
from app.services.llm_analyzer import call_openai_vision_api
from app.utils.validators import validate_video_file, validate_video_duration
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    responses={
        413: {"model": ErrorResponse, "description": "Payload too large"},
        422: {"model": ErrorResponse, "description": "Unprocessable entity"},
        429: {"model": ErrorResponse, "description": "Too many requests"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
        503: {"model": ErrorResponse, "description": "Service unavailable"}
    },
    summary="Analyze exercise form from video or frames",
    description="Accepts either a video file upload or pre-extracted base64 frames and returns AI-generated form feedback"
)
async def analyze_exercise(
    request: Request,
    video: Optional[UploadFile] = File(None, description="Video file (MP4, MOV, or AVI)")
) -> AnalyzeResponse:
    """
    Analyze exercise form from video or frames.

    Accepts two input methods:
    1. Video file upload (multipart/form-data): `video` field
    2. Pre-extracted frames (JSON): `frames` array of base64-encoded images

    The endpoint will:
    - Extract 5 key frames from the video (or use provided frames)
    - Send frames to OpenAI GPT-4o Vision API for analysis
    - Automatically detect the exercise type
    - Return personalized form feedback

    Args:
        request: FastAPI request object
        video: Uploaded video file (optional)

    Returns:
        AnalyzeResponse with feedback, detected exercise, frames analyzed, and timestamp

    Raises:
        HTTPException: Various error codes for validation failures and processing errors
    """
    frames_base64 = []
    frames_analyzed = 0
    temp_file_path = None
    frames_request = None

    try:
        # Check if this is a JSON request (frames) or file upload (video)
        content_type = request.headers.get("content-type", "")

        if video is not None:
            # Option A: Video file upload (multipart/form-data)
            logger.info(f"Processing video file: {video.filename}")

            # Validate video file
            validate_video_file(video)

            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_file:
                temp_file_path = temp_file.name
                content = await video.read()

                # Check file size
                file_size_mb = len(content) / (1024 * 1024)
                if file_size_mb > settings.max_video_size_mb:
                    raise HTTPException(
                        status_code=413,
                        detail=f"Video too large. Maximum size: {settings.max_video_size_mb}MB"
                    )

                temp_file.write(content)

            # Get and validate duration
            try:
                duration = get_video_duration(temp_file_path)
                validate_video_duration(duration)
            except ValueError as e:
                raise HTTPException(
                    status_code=422,
                    detail=f"Unable to process video: {str(e)}"
                )

            # Extract frames
            try:
                frames = sample_frames_from_video(temp_file_path, num_frames=settings.frame_count)
                frames_analyzed = len(frames)
            except ValueError as e:
                raise HTTPException(
                    status_code=422,
                    detail=f"Frame extraction failed: {str(e)}"
                )

            # Resize and encode frames
            for frame in frames:
                resized_frame = resize_frame(frame, max_dimension=1024)
                encoded = encode_frame_to_base64(resized_frame, quality=85)
                frames_base64.append(encoded)

        elif "application/json" in content_type:
            # Option B: Pre-extracted frames (JSON)
            try:
                body = await request.json()
                frames_request = FramesRequest(**body)
                frames_base64 = frames_request.frames
                frames_analyzed = len(frames_base64)
                logger.info(f"Processing {frames_analyzed} pre-extracted frames")
            except Exception as e:
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid JSON body: {str(e)}"
                )

        else:
            # Neither input provided
            raise HTTPException(
                status_code=422,
                detail="Either 'video' file or 'frames' JSON array must be provided"
            )

        # Call LLM for analysis
        logger.info(f"Analyzing {frames_analyzed} frames with LLM")
        feedback = await call_openai_vision_api(frames_base64, model=settings.model_name)

        # Return response
        return AnalyzeResponse(
            feedback=feedback,
            exercise_detected="detected",  # Placeholder - will be extracted from feedback
            frames_analyzed=frames_analyzed,
            timestamp=datetime.utcnow()
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise

    except Exception as e:
        # Catch any unexpected errors
        logger.exception(f"Unexpected error during analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during analysis: {e}"
        )

    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                logger.debug(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file: {e}")
