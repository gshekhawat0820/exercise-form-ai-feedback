"""
Input validation utilities for video files and durations.

This module provides validation functions for uploaded video files
to ensure they meet format and duration requirements.
"""

from fastapi import HTTPException, UploadFile
from app.core.config import settings


def validate_video_file(file: UploadFile) -> None:
    """
    Validate uploaded video file format and MIME type.

    Args:
        file: The uploaded file object

    Raises:
        HTTPException: 422 if file extension or MIME type is invalid
    """
    # Check file extension
    allowed_extensions = [".mp4", ".mov", ".avi"]

    if not file.filename:
        raise HTTPException(
            status_code=422,
            detail="Filename is required"
        )

    file_ext = f".{file.filename.lower().split('.')[-1]}"

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=422,
            detail=f"Unsupported video format. Allowed: {', '.join(allowed_extensions)}"
        )

    # Check MIME type
    if file.content_type and not file.content_type.startswith("video/"):
        raise HTTPException(
            status_code=422,
            detail="Invalid file type. Must be a video file."
        )


def validate_video_duration(duration_seconds: float) -> None:
    """
    Validate video duration is within acceptable range.

    Args:
        duration_seconds: Duration of the video in seconds

    Raises:
        HTTPException: 422 if too short, 413 if too long
    """
    if duration_seconds < settings.min_video_duration_sec:
        raise HTTPException(
            status_code=422,
            detail=f"Video too short. Minimum: {settings.min_video_duration_sec} seconds"
        )

    if duration_seconds > settings.max_video_duration_sec:
        raise HTTPException(
            status_code=413,
            detail=f"Video too long. Maximum: {settings.max_video_duration_sec} seconds"
        )
