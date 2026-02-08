#!/usr/bin/env python3
"""
Example script for testing the Exercise Form Feedback API.

This script demonstrates how to use the API with both video files
and pre-extracted frames.
"""

import requests
import argparse
import base64
import sys
from pathlib import Path


def analyze_video(video_path: str, api_url: str = "http://localhost:8000/api/v1/analyze"):
    """
    Send video to API for analysis.

    Args:
        video_path: Path to video file
        api_url: API endpoint URL
    """
    if not Path(video_path).exists():
        print(f"Error: Video file not found: {video_path}")
        return

    print(f"Analyzing video: {video_path}")
    print(f"API URL: {api_url}\n")

    try:
        with open(video_path, "rb") as f:
            files = {"video": f}
            response = requests.post(api_url, files=files, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print("✓ Analysis successful!\n")
            print(f"\nFeedback:\n{result['feedback']}\n")
            print(f"Frames analyzed: {result['frames_analyzed']}")
            print(f"Timestamp: {result['timestamp']}")
        else:
            print(f"✗ Error {response.status_code}")
            print(f"Details: {response.json()}")

    except requests.exceptions.ConnectionError:
        print("✗ Error: Could not connect to API. Is the server running?")
    except requests.exceptions.Timeout:
        print("✗ Error: Request timed out. The video may be too large or the server is slow.")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def analyze_frames(frame_paths: list, api_url: str = "http://localhost:8000/api/v1/analyze"):
    """
    Send pre-extracted frames to API.

    Args:
        frame_paths: List of paths to frame image files
        api_url: API endpoint URL
    """
    print(f"Analyzing {len(frame_paths)} frames")
    print(f"API URL: {api_url}\n")

    # Encode frames as base64
    frames_base64 = []
    for path in frame_paths:
        if not Path(path).exists():
            print(f"Warning: Frame file not found: {path}")
            continue

        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')
            frames_base64.append(encoded)

    if not frames_base64:
        print("Error: No valid frame files found")
        return

    payload = {"frames": frames_base64}

    try:
        response = requests.post(api_url, json=payload, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print("✓ Analysis successful!\n")
            print(f"\nFeedback:\n{result['feedback']}\n")
            print(f"Frames analyzed: {result['frames_analyzed']}")
            print(f"Timestamp: {result['timestamp']}")
        else:
            print(f"✗ Error {response.status_code}")
            print(f"Details: {response.json()}")

    except requests.exceptions.ConnectionError:
        print("✗ Error: Could not connect to API. Is the server running?")
    except requests.exceptions.Timeout:
        print("✗ Error: Request timed out.")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test the Exercise Form Feedback API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a video file
  python scripts/test_request.py --video my_squat.mp4

  # Analyze with custom API URL
  python scripts/test_request.py --video my_squat.mp4 --url http://example.com/api/v1/analyze

  # Analyze pre-extracted frames
  python scripts/test_request.py --frames frame1.jpg frame2.jpg frame3.jpg frame4.jpg frame5.jpg
        """
    )

    parser.add_argument(
        '--video',
        type=str,
        help='Path to video file to analyze'
    )

    parser.add_argument(
        '--frames',
        type=str,
        nargs='+',
        help='Paths to frame image files (3-10 frames)'
    )

    parser.add_argument(
        '--url',
        type=str,
        default='http://localhost:8000/api/v1/analyze',
        help='API endpoint URL (default: http://localhost:8000/api/v1/analyze)'
    )

    args = parser.parse_args()

    if args.video:
        analyze_video(args.video, args.url)
    elif args.frames:
        analyze_frames(args.frames, args.url)
    else:
        parser.print_help()
        print("\nError: Either --video or --frames must be specified")
        sys.exit(1)


if __name__ == "__main__":
    main()
