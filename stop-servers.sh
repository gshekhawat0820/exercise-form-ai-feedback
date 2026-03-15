#!/bin/bash

# Stop all Docker containers for Exercise Form Feedback AI

echo "🛑 Stopping Docker containers..."

# Check if Docker Compose is available
if docker compose version &> /dev/null; then
    docker compose down
elif command -v docker-compose &> /dev/null; then
    docker-compose down
else
    echo "❌ Docker Compose is not available"
    exit 1
fi

echo ""
echo "✅ Docker containers stopped"
echo ""
echo "💡 To remove all data and start fresh:"
echo "   docker compose down -v  # Remove volumes"
echo "   docker system prune     # Clean up unused Docker resources"
echo ""
