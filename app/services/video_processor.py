"""
Video processing service for encoding frames to base64.

This module provides functions to convert numpy array frames to base64-encoded
JPEG images for transmission to the OpenAI Vision API.
"""

import base64
import io

import numpy as np
from numpy.typing import NDArray
from PIL import Image


def encode_frame_to_base64(frame: NDArray[np.uint8], quality: int = 85) -> str:
    """
    Encode a numpy array frame as base64 JPEG.

    Args:
        frame: RGB numpy array
        quality: JPEG quality (1-100)

    Returns:
        Base64-encoded JPEG string
    """
    # Convert numpy array to PIL Image
    image = Image.fromarray(frame)

    # Save as JPEG to bytes buffer
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=quality)

    # Encode as base64
    encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return encoded
