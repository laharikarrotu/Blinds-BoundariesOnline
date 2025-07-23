#!/usr/bin/env python3
"""
Main entry point for Azure App Service
This file is required by Azure App Service to find the ASGI application
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

try:
    # Import the FastAPI app from main_hybrid
    from main_hybrid import app
    
    # Create necessary directories
    directories = ['uploads', 'masks', 'blinds', 'results']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    # This is what Azure App Service looks for
    application = app
    
except Exception as e:
    print(f"ERROR: Failed to import main_hybrid: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 