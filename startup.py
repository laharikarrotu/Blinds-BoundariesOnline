import uvicorn
import sys
import os
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    # Add the app directory to the Python path
    app_path = os.path.join(os.path.dirname(__file__), 'app')
    sys.path.insert(0, app_path)
    logger.info(f"Added {app_path} to Python path")
    
    # Check if the app directory exists
    if not os.path.exists(app_path):
        logger.error(f"App directory {app_path} does not exist!")
        sys.exit(1)
    
    # Check if main_hybrid.py exists
    main_file = os.path.join(app_path, 'main_hybrid.py')
    if not os.path.exists(main_file):
        logger.error(f"main_hybrid.py not found at {main_file}")
        sys.exit(1)
    
    logger.info("Importing main_hybrid...")
    from main_hybrid import app
    logger.info("Successfully imported main_hybrid")
    
    # Create necessary directories
    directories = ['uploads', 'masks', 'blinds', 'results']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"Created/verified directory: {directory}")
    
    logger.info("Starting uvicorn server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    
except Exception as e:
    logger.error(f"Failed to start application: {e}")
    import traceback
    logger.error(traceback.format_exc())
    sys.exit(1) 