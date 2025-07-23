#!/bin/bash
cd /home/site/wwwroot

echo "=== Starting Blinds & Boundaries API ==="
echo "Current directory: $(pwd)"
echo "Files in current directory:"
ls -la

echo "=== Checking Python ==="
python --version
which python

echo "=== Testing minimal startup first ==="
if [ -f "test_startup.py" ]; then
    echo "Running minimal test..."
    python test_startup.py
else
    echo "test_startup.py not found, running main startup..."
    python startup.py
fi 