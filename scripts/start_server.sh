#!/bin/bash
# Start Blinds & Boundaries API server

echo "=== Starting Blinds & Boundaries API ==="

# Kill any existing process on port 8000
echo "Checking for processes on port 8000..."
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "⚠️ Found process on port 8000, killing it..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    sleep 2
    echo "✅ Port 8000 cleared"
else
    echo "✅ Port 8000 is free"
fi

# Start the server
echo ""
echo "Starting server on port 8000..."
cd "$(dirname "$0")/.."
python3 main.py

