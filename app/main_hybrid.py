print("=== Loading main_hybrid.py ===")

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
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

@app.post("/upload-image")
def upload_image(file: UploadFile = File(...)):
    # Basic validation for image files
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        return JSONResponse(status_code=400, content={"error": "Only .jpg, .jpeg, .png files are allowed."})
    # Generate a unique filename
    ext = os.path.splitext(file.filename)[1]
    image_id = str(uuid.uuid4())
    unique_filename = f"{image_id}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    # Upload to Azure Blob Storage (optional)
    blob_url = upload_to_azure_blob(file_path, unique_filename)
    response = {"message": "Image uploaded successfully!", "image_id": image_id}
    if blob_url:
        response["url"] = blob_url
    return response

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
    # Find the image file
    image_file = None
    for fname in os.listdir(UPLOAD_DIR):
        if fname.startswith(image_id):
            image_file = os.path.join(UPLOAD_DIR, fname)
            break
    if not image_file or not os.path.exists(image_file):
        return JSONResponse(status_code=404, content={"error": "Image not found for the given image_id."})
    
    # Find the mask file
    mask_filename = f"mask_{image_id}.png"
    mask_path = os.path.join(MASK_DIR, mask_filename)
    if not os.path.exists(mask_path):
        return JSONResponse(status_code=404, content={"error": "Mask not found. Please run /detect-window first."})
    
    # Find the blind texture
    blind_path = os.path.join(BLINDS_DIR, blind_name)
    if not os.path.exists(blind_path):
        # List available blinds to help user
        try:
            available_blinds = [f for f in os.listdir(BLINDS_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
            return JSONResponse(
                status_code=404, 
                content={
                    "error": f"Blind texture '{blind_name}' not found in blinds/ folder.",
                    "available_blinds": available_blinds
                }
            )
        except Exception:
            return JSONResponse(status_code=404, content={"error": f"Blind texture '{blind_name}' not found in blinds/ folder."})
    
    # Load images
    orig_img = Image.open(image_file).convert("RGB").resize((320, 320))
    mask_img = Image.open(mask_path).convert("L").resize((320, 320))
    blind_img = Image.open(blind_path).convert("RGB").resize((320, 320))
    
    # Optionally tint the blind texture
    if color:
        try:
            color_rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
            color_layer = Image.new("RGB", blind_img.size, color_rgb)
            blind_img = Image.blend(blind_img, color_layer, alpha=0.5)
        except Exception as e:
            return JSONResponse(status_code=400, content={"error": f"Invalid color format: {e}"})
    
    # Apply the blind texture to the window area using the mask
    mask_np = np.array(mask_img)
    mask_bin = (mask_np > 128).astype(np.uint8) * 255
    mask_img_bin = Image.fromarray(mask_bin)
    result_img = orig_img.copy()
    # Composite: where mask is white, use blind_img; else use orig_img
    result_img.paste(blind_img, (0, 0), mask_img_bin)
    
    # Save and upload result
    result_filename = f"tryon_{image_id}_{os.path.splitext(blind_name)[0]}.png"
    result_path = os.path.join(RESULTS_DIR, result_filename)
    result_img.save(result_path)
    
    # Upload to Azure (optional)
    result_url = upload_to_azure_blob(result_path, result_filename)
    response = {
        "message": "Try-on result generated successfully!", 
        "method": "Hybrid (OpenCV + Gemini API) + PIL"
    }
    if result_url:
        response["result_url"] = result_url
    return response 