#!/bin/bash

# Quick start script for Exercise Form Feedback AI
# This script starts both the backend and frontend servers

set -e

echo "🚀 Exercise Form Feedback AI - Quick Start"
echo "=========================================="
echo ""

# Check if we're in the project root
if [ ! -f "requirements.txt" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check Python backend
echo "📋 Checking Python backend..."
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Please run:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please create one with your OPENAI_API_KEY"
    exit 1
fi

# Check Node.js frontend
echo "📋 Checking Node.js frontend..."
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

if [ ! -f "frontend/.env.local" ]; then
    echo "📝 Creating frontend .env.local file..."
    cp frontend/.env.local.example frontend/.env.local
fi

# Start backend in background
echo ""
echo "🔧 Starting FastAPI backend on http://localhost:8000..."
source venv/bin/activate
uvicorn app.main:app --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Wait for backend to start
echo "⏳ Waiting for backend to be ready..."
sleep 3

# Start frontend
echo ""
echo "🎨 Starting Next.js frontend on http://localhost:3000..."
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "   Frontend PID: $FRONTEND_PID"

# Save PIDs to file for easy cleanup
echo "$BACKEND_PID" > .pids
echo "$FRONTEND_PID" >> .pids

echo ""
echo "✅ Both servers are starting!"
echo ""
echo "📍 URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📄 Logs:"
echo "   Backend: tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "🛑 To stop both servers, run: ./stop-servers.sh"
echo "   Or press Ctrl+C and run: kill $BACKEND_PID $FRONTEND_PID"
echo ""

# Keep script running
wait
