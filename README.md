# Exercise Form Feedback AI

An LLM-based exercise form feedback system that analyzes exercise videos using computer vision and provides personalized coaching feedback.

## Features

- **Video Analysis**: Upload exercise videos (5-30 seconds, MP4/MOV/AVI format)
- **Frame Extraction**: Automatically extracts 5 key frames at strategic positions
- **AI-Powered Feedback**: Uses OpenAI GPT-4o Vision API for form analysis
- **Modern Web Interface**: Next.js frontend with drag-and-drop upload
- **RESTful API**: FastAPI backend with automatic documentation
- **Docker Deployment**: Fully containerized with docker-compose

## Tech Stack

**Backend:** FastAPI, OpenAI GPT-4o, OpenCV, Python 3.9+  
**Frontend:** Next.js 15, React 18, TypeScript, Tailwind CSS  
**Deployment:** Docker, Docker Compose

## Quick Start

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose installed
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### Setup and Run

1. **Clone the repository:**

```bash
git clone git@github.com:gshekhawat0820/exercise-form-ai-feedback.git
cd exercise-form-ai-feedback
```

2. **Add your OpenAI API key:**

```bash
cp .env.docker.example .env.docker
# Edit .env.docker and replace 'your-key-here' with your actual OpenAI API key
```

3. **Start the application:**

```bash
./start-servers.sh
```

That's it! The application will build and start automatically.

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Stop the Application

```bash
./stop-servers.sh
```

## Configuration

All configuration is handled through `.env.docker`:

```bash
OPENAI_API_KEY=sk-your-key-here
MODEL_NAME=gpt-4o
MAX_VIDEO_SIZE_MB=50
MAX_VIDEO_DURATION_SEC=30
MIN_VIDEO_DURATION_SEC=5
FRAME_COUNT=5
```

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

Run backend tests:

```bash
cd backend
pytest tests/ -v --cov
```

## Project Structure

```
exercise-form-ai-feedback/
├── backend/                 # Python FastAPI backend
│   ├── app/                # Application code
│   ├── tests/              # Backend tests
│   ├── Dockerfile          # Backend Docker image
│   └── requirements.txt    # Python dependencies
├── frontend/               # Next.js frontend
│   ├── app/               # Pages and layouts
│   ├── components/        # React components
│   ├── lib/               # Utilities and API client
│   ├── Dockerfile         # Frontend Docker image
│   └── package.json       # Node dependencies
├── docker-compose.yml      # Docker orchestration
├── .env.docker            # Environment variables
├── start-servers.sh       # Start script
├── stop-servers.sh        # Stop script
├── README.md
└── KEY_LEARNINGS.md
```

## Development Notes

See [KEY_LEARNINGS.md](KEY_LEARNINGS.md) for implementation insights and edge cases discovered during development.

## Production Considerations

This project demonstrates core AI engineering capabilities with a working MVP. For production deployment, the following enhancements would be implemented:

**Security & Authentication**
- API key authentication for backend endpoints
- Rate limiting (e.g., 10 requests/min per IP) to prevent abuse
- CORS origins configured via `FRONTEND_URL` environment variable
- Input sanitization for malicious file uploads

**Scalability & Performance**
- Async job queue (Celery + Redis) for video processing to handle concurrent uploads
- Result caching (hash-based) to reduce redundant API calls and costs
- CDN integration for static assets
- Horizontal scaling with load balancing

**Observability & Monitoring**
- Structured logging with correlation IDs for request tracking
- Metrics collection (Prometheus) for latency, error rates, and API costs
- Alerting for service degradation or rate limit issues
- Distributed tracing for debugging

**Cost Optimization**
- Video deduplication via content hashing
- Frame compression before sending to OpenAI
- Configurable quality settings based on use case
- Usage analytics and per-user cost tracking

Current focus is on demonstrating full-stack AI integration, proper error handling, and deployment automation.
