# Exercise Form Feedback API

An LLM-based exercise form feedback system that analyzes exercise videos using computer vision and provides personalized coaching feedback.

## Features

- **Video Analysis**: Upload exercise videos (5-30 seconds, MP4/MOV/AVI format)
- **Frame Extraction**: Automatically extracts 5 key frames at strategic positions (0%, 25%, 50%, 75%, 100%)
- **AI-Powered Feedback**: Uses OpenAI GPT-4o Vision API to detect exercises and provide form feedback
- **Dual Input Methods**: Supports both video file upload and pre-extracted base64-encoded frames
- **RESTful API**: Built with FastAPI for high performance and automatic documentation

## What This System Does

1. Accepts exercise videos or pre-extracted frames
2. Extracts representative frames from videos
3. Sends frames to OpenAI's GPT-4o Vision model
4. LLM automatically detects the exercise type
5. Returns personalized form feedback with detected exercise and metadata

## Prerequisites

- **Python 3.10 or higher**
- **OpenAI API key** (with GPT-4o access)

## Installation

### 1. Clone the repository

```bash
cd future-applied-ai
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
```

### 3. Activate virtual environment

**On macOS/Linux:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

## Configuration

Environment variables in `.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `MODEL_NAME` | OpenAI model to use | `gpt-4o` |
| `MAX_VIDEO_SIZE_MB` | Maximum video file size | `50` |
| `MAX_VIDEO_DURATION_SEC` | Maximum video duration | `30` |
| `MIN_VIDEO_DURATION_SEC` | Minimum video duration | `5` |
| `FRAME_COUNT` | Number of frames to extract | `5` |
| `LOG_LEVEL` | Logging level | `INFO` |

## Running the Server

Start the development server:

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy"
}
```

#### Analyze Exercise Video
```http
POST /api/v1/analyze
```

**Option 1: Video File Upload (multipart/form-data)**

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -F "video=@path/to/squat_video.mp4"
```

**Option 2: Pre-extracted Frames (JSON)**

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "frames": ["base64_encoded_frame_1", "base64_encoded_frame_2", ...]
  }'
```

**Success Response (200 OK):**
```json
{
  "feedback": "I can see you're performing a squat. You're doing a good job keeping your chest up and maintaining balance throughout the movement. One thing to focus on is your knee alignment...",
  "exercise_detected": "squat",
  "frames_analyzed": 5,
  "timestamp": "2026-02-07T15:30:00Z"
}
```

**Error Responses:**
- `413 Payload Too Large` - File exceeds size/duration limits
- `422 Unprocessable Entity` - Invalid file format or processing failure
- `429 Too Many Requests` - API rate limit exceeded
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - LLM API unavailable

## Usage Examples

### Python Script

```python
import requests

def analyze_video(video_path: str):
    """Send video to API for analysis."""
    url = "http://localhost:8000/api/v1/analyze"

    with open(video_path, "rb") as f:
        files = {"video": f}
        response = requests.post(url, files=files)

    if response.status_code == 200:
        result = response.json()
        print(f"Exercise detected: {result['exercise_detected']}")
        print(f"Feedback: {result['feedback']}")
        print(f"Frames analyzed: {result['frames_analyzed']}")
    else:
        print(f"Error: {response.status_code}")
        print(response.json())

if __name__ == "__main__":
    analyze_video("my_squat_video.mp4")
```

### cURL

```bash
# Analyze a video file
curl -X POST http://localhost:8000/api/v1/analyze \
  -F "video=@squat_video.mp4" \
  | jq
```

## Testing

Run the test suite:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Performance & Cost

### Expected Performance
- **Frame extraction time**: 1-3 seconds
- **LLM API call time**: 2-5 seconds
- **Total request time**: 3-8 seconds

### Estimated Costs (OpenAI GPT-4o)
- **Input tokens per request**: ~2000-3000 tokens (5 images + text prompt)
- **Output tokens per request**: ~100-300 tokens (feedback text)
- **Approximate cost per request**: $0.01-0.03 USD

## Project Structure

```
future-applied-ai/
├── .env.example              # Environment variable template
├── .gitignore               # Git ignore rules
├── README.md                # This file
├── requirements.txt         # Python dependencies
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py       # API endpoint definitions
│   ├── services/
│   │   ├── __init__.py
│   │   ├── video_processor.py    # Video decoding and frame extraction
│   │   ├── frame_sampler.py      # Frame sampling logic
│   │   └── llm_analyzer.py       # OpenAI LLM integration
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py      # Pydantic request/response models
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py       # Application settings and configuration
│   │   └── prompts.py      # LLM prompt templates
│   └── utils/
│       ├── __init__.py
│       └── validators.py   # Input validation utilities
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_validators.py
│   ├── test_frame_sampler.py
│   ├── test_video_processor.py
│   ├── test_llm_analyzer.py
│   ├── conftest.py         # Pytest configuration
│   └── fixtures/
│       └── sample_squat.mp4    # Sample test video
└── scripts/
    └── test_request.py     # Example usage script
```

## Troubleshooting

### Video Format Not Supported
- Ensure video is in MP4, MOV, or AVI format
- Try converting to MP4 H.264 codec (most compatible)

### OpenCV Cannot Decode Video
- Install codec support: `brew install ffmpeg` (macOS) or `apt-get install ffmpeg` (Linux)
- Check video file is not corrupted

### OpenAI API Rate Limit
- Wait and retry after a few seconds
- Consider implementing request queuing for high-load scenarios
- Check your OpenAI API tier limits

### Dependencies Installation Fails
- Ensure Python 3.10+ is installed: `python --version`
- Try upgrading pip: `pip install --upgrade pip`
- On macOS with M1/M2, you may need to install Rosetta for some packages

## License

This project is for educational and demonstration purposes.

## Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [OpenAI GPT-4o](https://openai.com/)
- [OpenCV](https://opencv.org/)
