print("=== Loading main_hybrid.py ===")

# Ensure python-multipart is available
try:
    import multipart
    print("✅ python-multipart is available")
except ImportError:
    print("⚠️ python-multipart not available, installing...")
    import subprocess
    import sys
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-multipart"])
        print("✅ python-multipart installed")
    except Exception as e:
        print(f"❌ Failed to install python-multipart: {e}")
        print("⚠️ Upload functionality may not work")

from fastapi import FastAPI, File, UploadFile, Query
import os
import shutil
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
import uuid
from PIL import Image
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

print("=== Importing hybrid_detector ===")
# Import the hybrid detector
from hybrid_detector import HybridWindowDetector
print("=== Successfully imported hybrid_detector ===")

app = FastAPI()

# Allow CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Create blinds directory if it doesn't exist
BLINDS_DIR = "blinds"
os.makedirs(BLINDS_DIR, exist_ok=True)

# Only mount the blinds folder if it exists and has content
if os.path.exists(BLINDS_DIR) and os.listdir(BLINDS_DIR):
    app.mount("/blinds", StaticFiles(directory=BLINDS_DIR), name="blinds")

# Load environment variables from .env file
load_dotenv()
AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_CONTAINER = os.getenv("AZURE_STORAGE_CONTAINER", "window-images")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Optional

# Check if Azure is configured
AZURE_AVAILABLE = AZURE_CONNECTION_STRING is not None

@app.get("/")
def read_root():
    return {
        "message": "Blinds & Boundaries API is running!", 
        "status": "healthy",
        "ml_type": "Hybrid (OpenCV + Gemini API)",
        "features": "Window detection, blind try-on",
        "gemini_available": GEMINI_API_KEY is not None,
        "azure_available": AZURE_AVAILABLE,
        "version": "1.1.0"  # Added version for deployment tracking
    }

@app.get("/health")
def health_check():
    import datetime
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "version": "1.1.0",
        "ml_type": "Hybrid (OpenCV + Gemini API)",
        "azure_available": AZURE_AVAILABLE,
        "gemini_available": GEMINI_API_KEY is not None,
        "directories": {
            "uploads": os.path.exists(UPLOAD_DIR),
            "masks": os.path.exists(MASK_DIR),
            "blinds": os.path.exists(BLINDS_DIR),
            "results": os.path.exists(RESULTS_DIR)
        }
    }

@app.get("/blinds-boundaries.vercel.app/{path:path}")
def redirect_vercel_app(path: str):
    """Redirect requests from the old Vercel domain to the root"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/", status_code=302)

@app.get("/blinds-boundaries.vercel.app/")
def redirect_vercel_app_root():
    """Redirect root requests from the old Vercel domain"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/", status_code=302)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MASK_DIR = "masks"
os.makedirs(MASK_DIR, exist_ok=True)

RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

@app.get("/blinds-list")
def blinds_list():
    try:
        if not os.path.exists(BLINDS_DIR):
            return {"blinds": [], "message": "Blinds directory not found"}
        
        files = [f for f in os.listdir(BLINDS_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        return {"blinds": files, "count": len(files)}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to list blinds: {e}"})

def upload_to_azure_blob(file_path: str, blob_name: str) -> str:
    if not AZURE_AVAILABLE:
        print("Azure Blob Storage not configured, skipping upload")
        return None
    
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(AZURE_CONTAINER)
        with open(file_path, "rb") as data:
            container_client.upload_blob(name=blob_name, data=data, overwrite=True)
        blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{AZURE_CONTAINER}/{blob_name}"
        return blob_url
    except Exception as e:
        print(f"Azure upload error: {e}")
        return None

@app.options("/upload-image")
def upload_image_options():
    """Handle CORS preflight requests for upload endpoint"""
    from fastapi.responses import Response
    response = Response()
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

@app.post("/upload-image")
def upload_image(file: UploadFile = File(...)):
    print(f"Upload request received for file: {file.filename}")
    try:
        # Basic validation for image files
        if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
            return JSONResponse(status_code=400, content={"error": "Only .jpg, .jpeg, .png files are allowed."})
        
        # Generate a unique filename
        ext = os.path.splitext(file.filename)[1]
        image_id = str(uuid.uuid4())
        unique_filename = f"{image_id}{ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        print(f"Saving file to: {file_path}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Upload to Azure Blob Storage (optional)
        blob_url = upload_to_azure_blob(file_path, unique_filename)
        response = {"message": "Image uploaded successfully!", "image_id": image_id}
        if blob_url:
            response["url"] = blob_url
        
        print(f"Upload successful: {image_id}")
        return response
    except Exception as e:
        print(f"Upload error: {e}")
        return JSONResponse(status_code=500, content={"error": f"Upload failed: {str(e)}"})

@app.post("/detect-window")
def detect_window(image_id: str = Query(..., description="The image_id returned from /upload-image")):
    # Find the image file in uploads directory
    image_file = None
    for fname in os.listdir(UPLOAD_DIR):
        if fname.startswith(image_id):
            image_file = os.path.join(UPLOAD_DIR, fname)
            break
    if not image_file or not os.path.exists(image_file):
        return JSONResponse(status_code=404, content={"error": "Image not found for the given image_id."})
    
    # Prepare mask filename
    mask_filename = f"mask_{image_id}.png"
    mask_path = os.path.join(MASK_DIR, mask_filename)
    
    # Run hybrid window detection (OpenCV + Gemini API)
    try:
        detector = HybridWindowDetector(gemini_api_key=GEMINI_API_KEY)
        detector.detect_window(image_file, mask_path)
        print(f"✅ Hybrid window detection completed")
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Window detection failed: {e}"})
    
    # Upload mask to Azure (optional)
    mask_url = upload_to_azure_blob(mask_path, mask_filename)
    response = {
        "message": "Window mask generated successfully using hybrid detection!", 
        "method": "Hybrid (OpenCV + Gemini API)",
        "gemini_used": GEMINI_API_KEY is not None
    }
    if mask_url:
        response["mask_url"] = mask_url
    return response

@app.post("/try-on")
def try_on(
    image_id: str = Query(..., description="The image_id returned from /upload-image"),
    blind_name: str = Query(..., description="The filename of the blind texture in the blinds/ folder"),
    color: str = Query(None, description="Optional hex color to tint the blind texture (e.g., #FF0000)")
):
    print(f"Try-on request: image_id={image_id}, blind_name={blind_name}, color={color}")
    
    # Find the image file
    image_file = None
    for fname in os.listdir(UPLOAD_DIR):
        if fname.startswith(image_id):
            image_file = os.path.join(UPLOAD_DIR, fname)
            break
    if not image_file or not os.path.exists(image_file):
        print(f"Image not found: {image_file}")
        return JSONResponse(status_code=404, content={"error": "Image not found for the given image_id."})
    
    print(f"Found image file: {image_file}")
    
    # Find the mask file
    mask_filename = f"mask_{image_id}.png"
    mask_path = os.path.join(MASK_DIR, mask_filename)
    if not os.path.exists(mask_path):
        print(f"Mask not found: {mask_path}")
        return JSONResponse(status_code=404, content={"error": "Mask not found. Please run /detect-window first."})
    
    print(f"Found mask file: {mask_path}")
    
    # Find the blind texture
    blind_path = os.path.join(BLINDS_DIR, blind_name)
    print(f"Looking for blind at: {blind_path}")
    print(f"BLINDS_DIR exists: {os.path.exists(BLINDS_DIR)}")
    if os.path.exists(BLINDS_DIR):
        print(f"BLINDS_DIR contents: {os.listdir(BLINDS_DIR)}")
    
    if not os.path.exists(blind_path):
        # List available blinds to help user
        try:
            available_blinds = [f for f in os.listdir(BLINDS_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
            print(f"Available blinds: {available_blinds}")
            return JSONResponse(
                status_code=404, 
                content={
                    "error": f"Blind texture '{blind_name}' not found in blinds/ folder.",
                    "available_blinds": available_blinds,
                    "searched_path": blind_path
                }
            )
        except Exception as e:
            print(f"Error listing blinds: {e}")
            return JSONResponse(status_code=404, content={"error": f"Blind texture '{blind_name}' not found in blinds/ folder."})
    
    print(f"Found blind file: {blind_path}")
    
    # Load images
    try:
        orig_img = Image.open(image_file).convert("RGB").resize((320, 320))
        mask_img = Image.open(mask_path).convert("L").resize((320, 320))
        blind_img = Image.open(blind_path).convert("RGB").resize((320, 320))
        print("All images loaded successfully")
    except Exception as e:
        print(f"Error loading images: {e}")
        return JSONResponse(status_code=500, content={"error": f"Failed to load images: {e}"})
    
    # Optionally tint the blind texture
    if color:
        try:
            color_rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            color_layer = Image.new("RGB", blind_img.size, color_rgb)
            blind_img = Image.blend(blind_img, color_layer, alpha=0.5)
        except Exception as e:
            return JSONResponse(status_code=400, content={"error": f"Invalid color format: {e}"})
    
    # Apply the blind texture to the window area using the mask
    try:
        mask_np = np.array(mask_img)
        mask_bin = (mask_np > 128).astype(np.uint8) * 255
        mask_img_bin = Image.fromarray(mask_bin)
        result_img = orig_img.copy()
        
        # Make the blinds more visible by blending with original
        # Convert to numpy arrays for processing
        orig_np = np.array(orig_img)
        blind_np = np.array(blind_img)
        mask_np_bin = np.array(mask_img_bin)
        
        # Create a more visible blend
        alpha = 0.7  # Blend factor - blinds will be 70% visible
        result_np = orig_np.copy().astype(float)
        
        # Apply mask to each channel
        for i in range(3):  # RGB channels
            blind_channel = blind_np[:, :, i].astype(float)
            mask_channel = mask_np_bin.astype(float) / 255.0
            
            # Blend: result = original * (1 - mask * alpha) + blind * mask * alpha
            result_np[:, :, i] = result_np[:, :, i] * (1 - mask_channel * alpha) + blind_channel * mask_channel * alpha
        
        # Convert back to PIL Image
        result_img = Image.fromarray(result_np.astype(np.uint8))
        
        print(f"Try-on completed. Result saved with mask area: {np.count_nonzero(mask_np_bin)} pixels")
    except Exception as e:
        print(f"Error during image processing: {e}")
        return JSONResponse(status_code=500, content={"error": f"Image processing failed: {e}"})
    
    # Save and upload result
    try:
        result_filename = f"tryon_{image_id}_{os.path.splitext(blind_name)[0]}.png"
        result_path = os.path.join(RESULTS_DIR, result_filename)
        result_img.save(result_path)
        print(f"Result saved to: {result_path}")
    except Exception as e:
        print(f"Error saving result: {e}")
        return JSONResponse(status_code=500, content={"error": f"Failed to save result: {e}"})
    
    # Upload to Azure (optional)
    result_url = upload_to_azure_blob(result_path, result_filename)
    response = {
        "message": "Try-on result generated successfully!", 
        "method": "Hybrid (OpenCV + Gemini API) + PIL"
    }
    if result_url:
        response["result_url"] = result_url
    return response 

# For local development
if __name__ == "__main__":
    import uvicorn
    print("Starting local development server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info") 