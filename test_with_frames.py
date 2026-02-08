#!/usr/bin/env python3
"""
Quick test script for analyzing frames.
"""

import base64
import requests
from pathlib import Path


def analyze_frames_from_images(image_paths, api_url="http://localhost:8000/api/v1/analyze"):
    """
    Load images from disk, encode as base64, and send to API.

    Args:
        image_paths: List of paths to image files
        api_url: API endpoint URL
    """
    print(f"Loading {len(image_paths)} images...")

    frames_base64 = []
    for path in image_paths:
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')
            frames_base64.append(encoded)
        print(f"  ✓ Loaded {Path(path).name}")

    print(f"\nSending {len(frames_base64)} frames to API...")

    payload = {"frames": frames_base64}
    response = requests.post(api_url, json=payload, timeout=30)

    if response.status_code == 200:
        result = response.json()
        print("\n" + "="*50)
        print("✓ Analysis Successful!")
        print("="*50)
        print(f"\nFeedback:\n{result['feedback']}\n")
        print(f"Frames analyzed: {result['frames_analyzed']}")
        print(f"Timestamp: {result['timestamp']}")
        print("="*50)
    else:
        print(f"\n✗ Error {response.status_code}")
        print(f"Details: {response.json()}")


if __name__ == "__main__":
    # Example: Test with extracted frames
    frames_dir = Path("extracted_frames")

    if not frames_dir.exists():
        print("Please extract frames first:")
        print("  python scripts/extract_frames.py tests/fixtures/sample_squat.mp4")
        exit(1)

    # Get all JPEG files in order
    frame_files = sorted(frames_dir.glob("*.jpg"))

    if not frame_files:
        print(f"No frames found in {frames_dir}/")
        exit(1)

    print(f"Found {len(frame_files)} frames in {frames_dir}/\n")
    analyze_frames_from_images(frame_files)
