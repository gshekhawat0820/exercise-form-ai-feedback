"""
Tests for input validation utilities.
"""

from unittest.mock import Mock

import pytest
from fastapi import HTTPException, UploadFile

from app.utils.validators import validate_video_duration, validate_video_file


def test_validate_video_file_valid_mp4():
    """Test that valid MP4 files pass validation."""
    mock_file = Mock(spec=UploadFile)
    mock_file.filename = "test_video.mp4"
    mock_file.content_type = "video/mp4"

    # Should not raise
    validate_video_file(mock_file)


def test_validate_video_file_valid_mov():
    """Test that valid MOV files pass validation."""
    mock_file = Mock(spec=UploadFile)
    mock_file.filename = "test_video.MOV"
    mock_file.content_type = "video/quicktime"

    # Should not raise
    validate_video_file(mock_file)


def test_validate_video_file_invalid_extension():
    """Test that invalid file extensions raise 422."""
    mock_file = Mock(spec=UploadFile)
    mock_file.filename = "test_file.txt"
    mock_file.content_type = "text/plain"

    with pytest.raises(HTTPException) as exc_info:
        validate_video_file(mock_file)

    assert exc_info.value.status_code == 422
    assert "Unsupported video format" in exc_info.value.detail


def test_validate_video_file_invalid_mime_type():
    """Test that invalid MIME types raise 422."""
    mock_file = Mock(spec=UploadFile)
    mock_file.filename = "test_video.mp4"
    mock_file.content_type = "application/pdf"

    with pytest.raises(HTTPException) as exc_info:
        validate_video_file(mock_file)

    assert exc_info.value.status_code == 422
    assert "Invalid file type" in exc_info.value.detail


def test_validate_video_file_no_filename():
    """Test that missing filename raises 422."""
    mock_file = Mock(spec=UploadFile)
    mock_file.filename = None
    mock_file.content_type = "video/mp4"

    with pytest.raises(HTTPException) as exc_info:
        validate_video_file(mock_file)

    assert exc_info.value.status_code == 422


def test_validate_video_duration_valid():
    """Test that valid duration passes."""
    # Valid duration (between 5 and 30 seconds)
    validate_video_duration(15.0)


def test_validate_video_duration_too_short():
    """Test that duration < 5 seconds raises 422."""
    with pytest.raises(HTTPException) as exc_info:
        validate_video_duration(3.0)

    assert exc_info.value.status_code == 422
    assert "too short" in exc_info.value.detail.lower()


def test_validate_video_duration_too_long():
    """Test that duration > 30 seconds raises 413."""
    with pytest.raises(HTTPException) as exc_info:
        validate_video_duration(45.0)

    assert exc_info.value.status_code == 413
    assert "too long" in exc_info.value.detail.lower()


def test_validate_video_duration_at_minimum():
    """Test that exactly 5 seconds passes."""
    # Should not raise
    validate_video_duration(5.0)


def test_validate_video_duration_at_maximum():
    """Test that exactly 30 seconds passes."""
    # Should not raise
    validate_video_duration(30.0)
