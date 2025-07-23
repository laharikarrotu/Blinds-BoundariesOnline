#!/usr/bin/env python3
import sys
import os

print("=== MINIMAL TEST STARTUP ===")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print(f"Files in current directory: {os.listdir('.')}")

try:
    print("Testing basic imports...")
    import fastapi
    print("✅ FastAPI imported successfully")
    
    import uvicorn
    print("✅ Uvicorn imported successfully")
    
    import cv2
    print("✅ OpenCV imported successfully")
    
    import numpy
    print("✅ NumPy imported successfully")
    
    from PIL import Image
    print("✅ PIL imported successfully")
    
    print("=== Creating minimal FastAPI app ===")
    from fastapi import FastAPI
    
    app = FastAPI()
    
    @app.get("/")
    def read_root():
        return {"message": "Test API is working!", "status": "healthy"}
    
    @app.get("/health")
    def health_check():
        return {"status": "healthy", "test": True}
    
    print("=== Starting minimal server ===")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 