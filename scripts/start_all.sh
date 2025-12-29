#!/bin/bash
# Start both backend and frontend for local testing

echo "=== Starting Blinds & Boundaries Application ==="
echo ""

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

# Kill any existing process on port 8000
echo "1. Checking backend port 8000..."
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "   ⚠️ Found process on port 8000, killing it..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    sleep 2
    echo "   ✅ Port 8000 cleared"
else
    echo "   ✅ Port 8000 is free"
fi

# Check if frontend dependencies are installed
echo ""
echo "2. Checking frontend dependencies..."
cd "$PROJECT_ROOT/frontend"
if [ ! -d "node_modules" ]; then
    echo "   ⚠️ node_modules not found, installing dependencies..."
    pnpm install
    if [ $? -ne 0 ]; then
        echo "   ❌ Failed to install dependencies"
        exit 1
    fi
    echo "   ✅ Dependencies installed"
else
    echo "   ✅ Dependencies already installed"
fi

# Start backend in background
echo ""
echo "3. Starting backend server (port 8000)..."
cd "$PROJECT_ROOT"
python3 main.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "   ✅ Backend started (PID: $BACKEND_PID)"
echo "   📝 Logs: tail -f backend.log"

# Wait for backend to start
echo ""
echo "4. Waiting for backend to start..."
sleep 5

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ Backend is responding!"
else
    echo "   ⚠️ Backend may still be starting... (check backend.log)"
fi

# Start frontend
echo ""
echo "5. Starting frontend (port 5173)..."
cd "$PROJECT_ROOT/frontend"
pnpm dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   ✅ Frontend started (PID: $FRONTEND_PID)"
echo "   📝 Logs: tail -f frontend.log"

# Summary
echo ""
echo "=========================================="
echo "✅ Application Started!"
echo "=========================================="
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""
echo "Backend PID:  $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "To stop:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "To view logs:"
echo "  tail -f backend.log"
echo "  tail -f frontend.log"
echo ""
echo "Opening frontend in browser..."
sleep 3
open http://localhost:5173 2>/dev/null || xdg-open http://localhost:5173 2>/dev/null || echo "Please open http://localhost:5173 in your browser"

