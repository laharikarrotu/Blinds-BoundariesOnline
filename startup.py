import uvicorn
import sys
import os

print("=== Python Startup Script Starting ===")

try:
    print("Step 1: Setting up Python path...")
    current_dir = os.path.dirname(__file__)
    print(f"Current directory: {current_dir}")
    print(f"Files in current directory: {os.listdir(current_dir)}")
    
    # Try to find main_hybrid.py in different possible locations
    possible_paths = [
        os.path.join(current_dir, 'main_hybrid.py'),  # Flattened structure
        os.path.join(current_dir, 'app', 'main_hybrid.py'),  # Directory structure
    ]
    
    main_file = None
    for path in possible_paths:
        if os.path.exists(path):
            main_file = path
            print(f"✅ Found main_hybrid.py at: {path}")
            break
    
    if main_file is None:
        print("❌ main_hybrid.py not found in any expected location!")
        print("Searched in:")
        for path in possible_paths:
            print(f"  - {path}")
        print("Available files:")
        for file in os.listdir(current_dir):
            print(f"  - {file}")
        sys.exit(1)
    
    # If main_hybrid.py is in app directory, add it to Python path
    if 'app' in main_file:
        app_path = os.path.join(current_dir, 'app')
        sys.path.insert(0, app_path)
        print(f"Added {app_path} to Python path")
    
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