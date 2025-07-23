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
    
    print("Step 2: Creating FastAPI app...")
    app = FastAPI()
    
    @app.get("/")
    def read_root():
        return {"message": "Blinds & Boundaries API is working!", "status": "healthy"}
    
    @app.get("/health")
    def health_check():
        return {"status": "healthy", "version": "1.0.0"}
    
    print("Step 3: Creating directories...")
    directories = ['uploads', 'masks', 'blinds', 'results']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")
    
    print("Step 4: Setting up for Azure...")
    # This is what Azure App Service looks for
    application = app
    
    print("=== MAIN.PY SUCCESSFULLY LOADED ===")
    
except Exception as e:
    print(f"ERROR: Failed to setup main.py: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 