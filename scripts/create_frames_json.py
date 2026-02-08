#!/usr/bin/env python3
"""
Create a JSON file with base64-encoded frames for testing.
"""

import base64
import json
import sys
from pathlib import Path


def create_frames_json(image_paths, output_file="frames_payload.json"):
    """Create JSON payload with base64-encoded frames."""

    frames = []
    for path in image_paths:
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode('utf-8')
            frames.append(encoded)
        print(f"✓ Encoded {Path(path).name}")

    payload = {"frames": frames}

    with open(output_file, "w") as f:
        json.dump(payload, f)

    print(f"\n✓ Created {output_file} with {len(frames)} frames")
    print(f"File size: {Path(output_file).stat().st_size / 1024:.1f} KB")
    print(f"\nYou can now test with:")
    print(f"  curl -X POST http://localhost:8000/api/v1/analyze \\")
    print(f"    -H 'Content-Type: application/json' \\")
    print(f"    -d @{output_file} | jq")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/create_frames_json.py <image1> <image2> ... [output.json]")
        print("\nExample:")
        print("  python scripts/create_frames_json.py extracted_frames/*.jpg")
        sys.exit(1)

    image_files = sys.argv[1:-1] if sys.argv[-1].endswith('.json') else sys.argv[1:]
    output_file = sys.argv[-1] if sys.argv[-1].endswith('.json') else "frames_payload.json"

    create_frames_json(image_files, output_file)
