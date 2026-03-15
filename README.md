# Exercise Form Feedback AI

An LLM-based exercise form feedback system that analyzes exercise videos using computer vision and provides personalized coaching feedback.

## Features

- **Video Analysis**: Upload exercise videos (5-30 seconds, MP4/MOV/AVI format)
- **Frame Extraction**: Automatically extracts 5 key frames at strategic positions
- **AI-Powered Feedback**: Uses OpenAI GPT-4o Vision API for form analysis
- **Modern Web Interface**: Next.js frontend with drag-and-drop upload
- **RESTful API**: FastAPI backend with automatic documentation

## Tech Stack

**Backend:** FastAPI, OpenAI GPT-4o, OpenCV, Python 3.9+  
**Frontend:** Next.js 15, React 18, TypeScript, Tailwind CSS

## Quick Start

### 1. Clone and setup backend

```bash
git clone git@github.com:gshekhawat0820/exercise-form-ai-feedback.git
cd exercise-form-ai-feedback/backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Setup frontend

```bash
cd ../frontend
npm install
cp .env.local.example .env.local
```

### 3. Run both servers

From project root:
```bash
./start-servers.sh
```

Or manually:
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

Then visit **http://localhost:3000**

## Configuration

**Backend** (`backend/.env`):
```bash
OPENAI_API_KEY=sk-your-key-here
MODEL_NAME=gpt-4o
MAX_VIDEO_SIZE_MB=50
MAX_VIDEO_DURATION_SEC=30
MIN_VIDEO_DURATION_SEC=5
FRAME_COUNT=5
```

**Frontend** (`frontend/.env.local`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```
- Frontend UI on `http://localhost:3000`

To stop both servers:

```bash
./stop-servers.sh
```

### Run Backend Only

Start the FastAPI development server:

```bash
source venv/bin/activate
uvicorn app.main:app --port 8000
```

The API will be available at `http://localhost:8000`

### Run Frontend Only

```bash
cd frontend
## API Endpoints

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- `GET /health` - Health check
- `POST /api/v1/analyze` - Analyze video (multipart/form-data with video file)

### Example Request

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -F "video=@squat.mp4"
```

### Example Response

```json
{
  "feedback": "I can see you're performing a squat. Good job keeping your chest up...",
  "frames_analyzed": 5,
  "timestamp": "2026-03-15T10:30:00Z"
}
```

## Testing

```bash
cd backend
source venv/bin/activate
pytest tests/ -v --cov
```

## Project Structure

```
exercise-form-ai-feedback/
├── backend/                 # Python FastAPI backend
│   ├── app/                # Application code
│   ├── tests/              # Backend tests
│   ├── scripts/            # Utility scripts
│   ├── requirements.txt    # Python dependencies
│   ├── .env               # Environment config
│   └── venv/              # Virtual environment
├── frontend/               # Next.js frontend
│   ├── app/               # Pages and layouts
│   ├── components/        # React components
│   ├── lib/               # Utilities and API client
│   └── package.json       # Node dependencies
├── README.md
├── KEY_LEARNINGS.md
└── start-servers.sh       # Quick start script
```

## Development Notes

See [KEY_LEARNINGS.md](KEY_LEARNINGS.md) for implementation insights and edge cases discovered during development.
