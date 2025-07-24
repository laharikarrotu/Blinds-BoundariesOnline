import uvicorn
import sys
import os

print("=== Python Startup Script Starting ===")

try:
    print("Step 1: Setting up Python path...")
    # Add the app directory to the Python path
    app_path = os.path.join(os.path.dirname(__file__), 'app')
    sys.path.insert(0, app_path)
    print(f"Added {app_path} to Python path")
    
    # Check if the app directory exists
    if not os.path.exists(app_path):
        print(f"ERROR: App directory {app_path} does not exist!")
        sys.exit(1)
    
    # Check if main_hybrid.py exists
    main_file = os.path.join(app_path, 'main_hybrid.py')
    if not os.path.exists(main_file):
        print(f"ERROR: main_hybrid.py not found at {main_file}")
        sys.exit(1)
    
    print("Step 2: Importing main_hybrid...")
    # Import with explicit path to avoid linter issues
    import importlib.util
    spec = importlib.util.spec_from_file_location("main_hybrid", main_file)
    main_hybrid = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main_hybrid)
    app = main_hybrid.app  # type: ignore
    print("Successfully imported main_hybrid")
    
    print("Step 3: Creating necessary directories...")
    # Create necessary directories
    directories = ['uploads', 'masks', 'blinds', 'results']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created/verified directory: {directory}")
    
    print("Step 4: Starting uvicorn server...")
    
    # For Azure App Service, we need to use the PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    print(f"Server will start on 0.0.0.0:{port}")
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
    
except Exception as e:
    print(f"ERROR: Failed to start application: {e}")
    import traceback
    print("Full traceback:")
    print(traceback.format_exc())
    sys.exit(1) 