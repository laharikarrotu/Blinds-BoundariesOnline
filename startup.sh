#!/bin/bash
cd /home/site/wwwroot

echo "=== Starting Blinds & Boundaries API ==="
echo "Current directory: $(pwd)"
echo "Files in current directory:"
ls -la

echo "=== Checking Python ==="
python --version
which python

echo "=== Checking for startup files ==="
if [ -f "startup.py" ]; then
    echo "✅ Found startup.py"
    echo "=== Starting FastAPI application with startup.py ==="
    python startup.py
elif [ -f "main.py" ]; then
    echo "✅ Found main.py"
    echo "=== Starting FastAPI application with main.py ==="
    python main.py
else
    echo "❌ No startup file found!"
    echo "Available files:"
    ls -la *.py
    exit 1
fi 