#!/usr/bin/env python3
"""
Script to extract frames from a video and save as images.
"""

from pathlib import Path
import sys
import cv2


def extract_frames(video_path: str, output_dir: str = "extracted_frames", num_frames: int = 5):
    """Extract frames from video and save as JPEG images."""

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video {video_path}")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Total frames in video: {total_frames}")

    # Calculate frame positions
    positions = [i / (num_frames - 1) for i in range(num_frames)]
    positions = [min(pos, 0.98) for pos in positions]  # Cap at 98%
    frame_indices = [int(pos * (total_frames - 1)) for pos in positions]

    print(f"Extracting frames at indices: {frame_indices}")

    saved_files = []
    for i, idx in enumerate(frame_indices):
        cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
        ret, frame = cap.read()

        if not ret:
            print(f"Warning: Could not read frame {idx}")
            continue

        # Save as JPEG
        output_file = output_path / f"frame_{i+1:02d}_at_{int(positions[i]*100):02d}pct.jpg"
        cv2.imwrite(str(output_file), frame)
        saved_files.append(str(output_file))
        print(f"  ✓ Saved {output_file}")

    cap.release()
    print(f"\n✓ Extracted {len(saved_files)} frames to {output_dir}/")
    print("\nYou can now analyze these frames with:")
    print(f"python scripts/test_request.py --frames {' '.join(saved_files)}")

    return saved_files


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/extract_frames.py <video_path> [output_dir] [num_frames]")
        print("\nExample:")
        print("  python scripts/extract_frames.py tests/fixtures/sample_squat.mp4")
        print("  python scripts/extract_frames.py tests/fixtures/sample_squat.mp4 my_frames 5")
        sys.exit(1)

    video_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "extracted_frames"
    num_frames = int(sys.argv[3]) if len(sys.argv) > 3 else 5

    extract_frames(video_path, output_dir, num_frames)
