import uvicorn
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from main_hybrid import app

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 