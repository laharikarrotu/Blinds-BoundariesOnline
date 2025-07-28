#!/bin/bash

# Install system dependencies for OpenCV
echo "Installing system dependencies for OpenCV..."

# Create symbolic links for missing OpenGL libraries
if [ ! -f /usr/lib/x86_64-linux-gnu/libGL.so.1 ]; then
    echo "Creating libGL.so.1 symbolic link..."
    ln -sf /usr/lib/x86_64-linux-gnu/libGL.so /usr/lib/x86_64-linux-gnu/libGL.so.1
fi

if [ ! -f /usr/lib/x86_64-linux-gnu/libGLU.so.1 ]; then
    echo "Creating libGLU.so.1 symbolic link..."
    ln -sf /usr/lib/x86_64-linux-gnu/libGLU.so /usr/lib/x86_64-linux-gnu/libGLU.so.1
fi

# Set environment variables to disable GUI features
export OPENCV_VIDEOIO_PRIORITY_MSMF=0
export OPENCV_VIDEOIO_DEBUG=1
export OPENCV_LOG_LEVEL=ERROR

echo "System dependencies configured successfully"
echo "Starting Python application..."

# Start the Python application
exec python main.py 