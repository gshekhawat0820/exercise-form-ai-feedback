"""
LLM analyzer service for exercise form feedback using OpenAI Vision API.

This module provides functions to call OpenAI's GPT-4o Vision model with
retry logic and extract exercise information from the response.
"""

import logging
import re
from typing import List
from fastapi import HTTPException
from openai import AsyncOpenAI
import openai
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.prompts import SYSTEM_PROMPT, USER_PROMPT

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = AsyncOpenAI(api_key=settings.openai_api_key)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def call_openai_vision_api(
    frames_base64: List[str],
    model: str = "gpt-4o"
) -> str:
    """
    Call OpenAI Vision API with retry logic.

    Retries up to 3 times with exponential backoff on transient errors.

    Args:
        frames_base64: List of base64-encoded JPEG images
        model: OpenAI model name

    Returns:
        Feedback text from the LLM including exercise detection

    Raises:
        HTTPException: 429 for rate limits, 503 for API errors, 500 for other errors
    """
    try:
        # Build messages with system prompt, user prompt, and images
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": USER_PROMPT},
                    *[
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{frame}"}
                        }
                        for frame in frames_base64
                    ]
                ]
            }
        ]

        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=300,
            temperature=0.7
        )

        feedback = response.choices[0].message.content

        if not feedback:
            raise ValueError("Empty response from LLM")

        return feedback

    except openai.RateLimitError as e:
        logger.warning(f"Rate limit hit: {e}")
        raise HTTPException(status_code=429, detail="API rate limit exceeded")

    except openai.APIError as e:
        logger.error(f"OpenAI API error: {e}")
        raise HTTPException(status_code=503, detail="LLM service temporarily unavailable")

    except Exception as e:
        logger.exception(f"Unexpected error calling LLM: {e}")
        raise HTTPException(status_code=500, detail="Error analyzing video")