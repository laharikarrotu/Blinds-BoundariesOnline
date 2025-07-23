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

app = FastAPI()

# Allow CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the blinds folder at /blinds
app.mount("/blinds", StaticFiles(directory="blinds"), name="blinds")

# Load environment variables from .env file
load_dotenv()
AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_CONTAINER = os.getenv("AZURE_STORAGE_CONTAINER", "window-images")

@app.get("/")
def read_root():
    return {"message": "Blinds & Boundaries API is running!", "status": "healthy"}

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MASK_DIR = "masks"
os.makedirs(MASK_DIR, exist_ok=True)

BLINDS_DIR = "blinds"
os.makedirs(BLINDS_DIR, exist_ok=True)

RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

@app.get("/blinds-list")
def blinds_list():
    try:
        files = [f for f in os.listdir(BLINDS_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        return {"blinds": files}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to list blinds: {e}"})

def upload_to_azure_blob(file_path: str, blob_name: str) -> str:
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
    # Upload to Azure Blob Storage
    blob_url = upload_to_azure_blob(file_path, unique_filename)
    if blob_url:
        return {"message": "Image uploaded successfully!", "image_id": image_id, "url": blob_url}
    else:
        return JSONResponse(status_code=500, content={"error": "Failed to upload to Azure Blob Storage."})

@app.post("/detect-window")
def detect_window(image_id: str = Query(..., description="The image_id returned from /upload-image")):
    # For now, return a simple response indicating ML is not yet deployed
    return JSONResponse(
        status_code=503, 
        content={"error": "ML model not yet deployed. This is a placeholder endpoint."}
    )

@app.post("/try-on")
def try_on(
    image_id: str = Query(..., description="The image_id returned from /upload-image"),
    blind_name: str = Query(..., description="The filename of the blind texture in the blinds/ folder"),
    color: str = Query(None, description="Optional hex color to tint the blind texture (e.g., #FF0000)")
):
    # For now, return a simple response indicating ML is not yet deployed
    return JSONResponse(
        status_code=503, 
        content={"error": "ML model not yet deployed. This is a placeholder endpoint."}
    ) 