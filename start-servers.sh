#!/bin/bash

# Quick start script for Exercise Form Feedback AI using Docker
# This script starts both the backend and frontend servers using Docker Compose

set -e

echo "🚀 Exercise Form Feedback AI - Docker Quick Start"
echo "================================================="
echo ""

# Check if we're in the project root
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker from https://docker.com"
    exit 1
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null && ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not available. Please install Docker Compose"
    exit 1
fi

# Check for environment file
if [ ! -f ".env.docker" ]; then
    echo "📝 Creating .env.docker from template..."
    if [ -f ".env.docker.example" ]; then
        cp .env.docker.example .env.docker
        echo "⚠️  Please edit .env.docker and add your OPENAI_API_KEY"
        echo ""
        read -p "Press Enter after you've updated .env.docker with your API key..."
    else
        echo "❌ .env.docker.example not found. Creating a minimal .env.docker file..."
        echo "OPENAI_API_KEY=your-key-here" > .env.docker
        echo "⚠️  Please edit .env.docker and add your OPENAI_API_KEY"
        exit 1
    fi
fi

# Verify OPENAI_API_KEY is set
if grep -q "your-key-here" .env.docker || grep -q "sk-your-key-here" .env.docker; then
    echo "⚠️  Warning: .env.docker still contains placeholder API key"
    echo "   Please edit .env.docker and add your real OPENAI_API_KEY"
    exit 1
fi

echo "🐳 Starting Docker containers..."
echo ""

# Use docker compose (new) or docker-compose (legacy)
if docker compose version &> /dev/null; then
    docker compose --env-file .env.docker up --build -d
else
    docker-compose --env-file .env.docker up --build -d
fi

echo ""
echo "✅ Docker containers are starting!"
echo ""
echo "📍 URLs:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📄 View logs:"
echo "   All services: docker compose logs -f"
echo "   Backend only: docker compose logs -f backend"
echo "   Frontend only: docker compose logs -f frontend"
echo ""
echo "🛑 To stop all services, run: ./stop-servers.sh"
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5
echo "✅ Services should be ready now!"
echo ""

# Keep script running
wait
