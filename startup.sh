#!/bin/bash
cd /home/site/wwwroot

echo "=== Starting Blinds & Boundaries API ==="
echo "Current directory: $(pwd)"
echo "Files in current directory:"
ls -la

echo "=== Checking Python ==="
python --version
which python

echo "=== Starting Python application ==="
python startup.py 