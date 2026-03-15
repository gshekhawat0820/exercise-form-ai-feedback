#!/bin/bash

# Stop all servers for Exercise Form Feedback AI

echo "🛑 Stopping servers..."

if [ -f ".pids" ]; then
    while read pid; do
        if ps -p $pid > /dev/null 2>&1; then
            echo "   Stopping process $pid..."
            kill $pid 2>/dev/null || true
        fi
    done < .pids
    rm .pids
    echo "✅ Servers stopped"
else
    echo "⚠️  No .pids file found. Servers may already be stopped."
    echo "   You can manually check and kill processes:"
    echo "   lsof -ti:8000 | xargs kill -9  # Backend"
    echo "   lsof -ti:3000 | xargs kill -9  # Frontend"
fi

# Clean up log files
if [ -f "backend.log" ]; then
    rm backend.log
fi

if [ -f "frontend.log" ]; then
    rm frontend.log
fi

echo "🧹 Cleaned up log files"
