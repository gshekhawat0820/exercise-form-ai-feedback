"""
Frame sampling service for extracting key frames from exercise videos.

This module provides functions to extract evenly distributed frames from videos
at strategic positions (0%, 25%, 50%, 75%, 100%) using OpenCV.
"""

from typing import List

import cv2
import numpy as np
from numpy.typing import NDArray


def sample_frames_from_video(video_path: str, num_frames: int = 5) -> List[NDArray[np.uint8]]:
    """
    Extract frames at fixed percentage positions through the video.

    Positions: 0%, 25%, 50%, 75%, 100% of total frames

    Args:
        video_path: Path to video file
        num_frames: Number of frames to extract (default: 5)

    Returns:
        List of numpy arrays representing RGB frames

    Raises:
        ValueError: If video cannot be opened or has insufficient frames
    """
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if total_frames < num_frames:
        cap.release()
        raise ValueError(f"Video has only {total_frames} frames, need at least {num_frames}")

    # Calculate frame positions: [0, 0.25, 0.5, 0.75, 1.0]
    # Use a slightly lower max position (98% instead of 100%) to avoid edge cases
    # where the last frame might not be readable due to codec issues
    positions = [i / (num_frames - 1) for i in range(num_frames)]

    # Cap the maximum position at 0.98 to avoid reading beyond available frames
    positions = [min(pos, 0.98) for pos in positions]
    frame_indices = [int(pos * (total_frames - 1)) for pos in positions]

    frames = []
    for idx in frame_indices:
        # Try to seek to the frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()

        # If we fail to read, try reading the previous frame
        if not ret and idx > 0:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx - 1)
            ret, frame = cap.read()

        if not ret:
            cap.release()
            raise ValueError(
                f"Failed to read frame at index {idx}. "
                f"Video might have codec issues or incorrect frame count. "
                f"Reported frames: {total_frames}, requested index: {idx}"
            )

        # Convert BGR (OpenCV) to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(frame_rgb)

    cap.release()
    return frames


def resize_frame(frame: NDArray[np.uint8], max_dimension: int = 1024) -> NDArray[np.uint8]:
    """
    Resize frame to fit within max_dimension while preserving aspect ratio.

    OpenAI's Vision API works best with images up to 1024px.

    Args:
        frame: Input frame as numpy array
        max_dimension: Maximum height or width in pixels

    Returns:
        Resized frame as numpy array
    """
    height, width = frame.shape[:2]

    if height <= max_dimension and width <= max_dimension:
        return frame

    scale = max_dimension / max(height, width)
    new_width = int(width * scale)
    new_height = int(height * scale)

    return cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_AREA)


def get_video_duration(video_path: str) -> float:
    """
    Get video duration in seconds.

    Args:
        video_path: Path to video file

    Returns:
        Duration in seconds

    Raises:
        ValueError: If video cannot be opened
    """
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)  # type: ignore[attr-defined]
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    cap.release()

    if fps == 0:
        raise ValueError("Video has invalid FPS (0)")

    duration = frame_count / fps
    return duration
