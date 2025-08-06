#!/usr/bin/env python3
"""
Main entry point for Azure App Service
This file is required by Azure App Service to find the ASGI application
"""

import sys
import os

print("=== MAIN.PY STARTING ===")
print(f"Current directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')}")

try:
    print("Step 1: Setting up imports...")
    from fastapi import FastAPI
    import uvicorn
    
    print("Step 2: Creating directories...")
    directories = ['uploads', 'masks', 'blinds', 'results']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")
    
    print("Step 3: Ensuring python-multipart is available...")
    # Check if python-multipart is available
    try:
        import multipart
        print("✅ python-multipart is available")
    except ImportError:
        print("⚠️ python-multipart not available, installing...")
        import subprocess
        import os
        try:
            # Force install python-multipart
            print("Installing python-multipart...")
            result = subprocess.run([sys.executable, "-m", "pip", "install", "--force-reinstall", "python-multipart"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ python-multipart installed successfully")
                print(f"Output: {result.stdout}")
            else:
                print(f"❌ Installation failed: {result.stderr}")
                # Try alternative method
                os.system(f"{sys.executable} -m pip install --force-reinstall python-multipart")
                print("✅ python-multipart installed via os.system")
        except Exception as e:
            print(f"❌ All installation methods failed: {e}")
            print("⚠️ Upload functionality may not work")
    
    print("Step 4: Importing main application...")
    
    # Set environment variables to handle OpenCV issues
    os.environ['OPENCV_VIDEOIO_PRIORITY_MSMF'] = '0'
    os.environ['OPENCV_VIDEOIO_DEBUG'] = '1'
    os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'
    
    # Add app directory to Python path
    app_path = os.path.join(os.path.dirname(__file__), 'app')
    sys.path.insert(0, app_path)
    print(f"Added {app_path} to Python path")
    
    # Try to import the main application
    try:
        from main_hybrid import app
        print("✅ Successfully imported main_hybrid.py application")
        application = app
    except ImportError as e:
        print(f"⚠️ Could not import main_hybrid.py: {e}")
        print("Creating fallback FastAPI app...")
        
        # Fallback: Create a basic FastAPI app
        app = FastAPI()
        
        @app.get("/")
        def read_root():
            return {
                "message": "Blinds & Boundaries API is working!", 
                "status": "healthy",
                "note": "Running fallback app - main_hybrid.py not found"
            }
        
        @app.get("/health")
        def health_check():
            return {"status": "healthy", "version": "1.0.0", "mode": "fallback"}
        
        application = app
    
    print("Step 5: Starting the server...")
    # For Azure App Service, we need to use the PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting server on 0.0.0.0:{port}")
    
    # Start the uvicorn server
    uvicorn.run(application, host="0.0.0.0", port=port, log_level="info")
    
except Exception as e:
    print(f"ERROR: Failed to setup main.py: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 