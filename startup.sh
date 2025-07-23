#!/bin/bash
cd /home/site/wwwroot

echo "=== Starting Blinds & Boundaries API ==="
echo "Current directory: $(pwd)"
echo "Files in current directory:"
ls -la

echo "=== Checking Python ==="
python --version
which python

echo "=== Starting FastAPI application ==="
# Start the FastAPI app with uvicorn
uvicorn main:application --host 0.0.0.0 --port 8000 