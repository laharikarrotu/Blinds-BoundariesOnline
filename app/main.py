"""Main entry point using elite architecture."""
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Set environment variables for OpenCV (fix libGL.so.1 error on Azure)
os.environ['OPENCV_VIDEOIO_PRIORITY_MSMF'] = '0'
os.environ['OPENCV_VIDEOIO_DEBUG'] = '1'
os.environ['OPENCV_LOG_LEVEL'] = 'ERROR'
# Disable OpenGL/GLX to prevent libGL.so.1 errors on Azure App Service
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['DISPLAY'] = ''
os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '0'

# Create required directories
from app.core.config import config
from pathlib import Path

for directory in [config.UPLOAD_DIR, config.MASK_DIR, config.BLINDS_DIR, config.RESULTS_DIR]:
    Path(directory).mkdir(exist_ok=True)

# Import and run the application
try:
    from app.api.main import app
    from app.core.logger import logger
    
    if __name__ == "__main__":
        import uvicorn
        logger.info("Starting elite architecture server...")
        uvicorn.run(
            app,
            host=config.HOST,
            port=config.PORT,
            log_level="info"
        )
except ImportError as e:
    print(f"Error importing application: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

