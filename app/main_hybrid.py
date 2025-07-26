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
import cv2
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

print("=== Importing hybrid_detector ===")
# Import the hybrid detector
from hybrid_detector import HybridWindowDetector
from blind_pattern_generator import BlindPatternGenerator
print("=== Successfully imported hybrid_detector and blind_pattern_generator ===")

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

# Create other required directories
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

MASK_DIR = "masks"
os.makedirs(MASK_DIR, exist_ok=True)

RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

# Only mount the blinds folder if it exists and has content
if os.path.exists(BLINDS_DIR) and os.listdir(BLINDS_DIR):
    app.mount("/blinds", StaticFiles(directory=BLINDS_DIR), name="blinds")

# Mount results directory for serving generated images
if os.path.exists(RESULTS_DIR):
    app.mount("/results", StaticFiles(directory=RESULTS_DIR), name="results")

# Load environment variables from .env file
load_dotenv()
AZURE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
AZURE_CONTAINER = os.getenv("AZURE_STORAGE_CONTAINER", "window-images")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Optional

# Azure Computer Vision credentials
AZURE_VISION_KEY = os.getenv("AZURE_VISION_KEY")
AZURE_VISION_ENDPOINT = os.getenv("AZURE_VISION_ENDPOINT")

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

@app.get("/test-results")
def test_results():
    """Test endpoint to verify results directory is accessible"""
    try:
        if not os.path.exists(RESULTS_DIR):
            return {"error": "Results directory does not exist"}
        
        # Create a test file
        test_filename = "test.txt"
        test_path = os.path.join(RESULTS_DIR, test_filename)
        with open(test_path, "w") as f:
            f.write("Test file created successfully")
        
        # Check if we can read it back
        with open(test_path, "r") as f:
            content = f.read()
        
        return {
            "message": "Results directory is working",
            "test_file_created": test_filename,
            "test_content": content,
            "results_dir": RESULTS_DIR,
            "exists": True
        }
    except Exception as e:
        return {"error": f"Error testing results directory: {e}"}

@app.get("/debug-results")
def debug_results():
    """Debug endpoint to check results directory"""
    try:
        if not os.path.exists(RESULTS_DIR):
            return {"error": "Results directory does not exist"}
        
        files = os.listdir(RESULTS_DIR)
        return {
            "results_dir": RESULTS_DIR,
            "exists": True,
            "file_count": len(files),
            "files": files[:10],  # Show first 10 files
            "total_files": len(files)
        }
    except Exception as e:
        return {"error": f"Error accessing results directory: {e}"}

@app.get("/blinds-boundaries.vercel.app/")
def redirect_vercel_app_root():
    """Redirect root requests from the old Vercel domain"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/", status_code=302)

@app.get("/blinds-list")
def blinds_list():
    try:
        # Get pre-made blind textures
        texture_blinds = []
        if os.path.exists(BLINDS_DIR):
            texture_blinds = [f for f in os.listdir(BLINDS_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
        
        # Get available generated patterns
        pattern_generator = BlindPatternGenerator()
        generated_patterns = pattern_generator.get_available_patterns()
        materials = pattern_generator.get_available_materials()
        
        return {
            "texture_blinds": texture_blinds,
            "generated_patterns": generated_patterns,
            "materials": materials,
            "texture_count": len(texture_blinds),
            "pattern_count": len(generated_patterns)
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Failed to list blinds: {e}"})

@app.get("/debug-blinds")
def debug_blinds():
    """Debug endpoint to check blind directory status"""
    try:
        return {
            "blinds_dir_exists": os.path.exists(BLINDS_DIR),
            "blinds_dir_path": os.path.abspath(BLINDS_DIR),
            "blinds_dir_contents": os.listdir(BLINDS_DIR) if os.path.exists(BLINDS_DIR) else [],
            "current_working_dir": os.getcwd(),
            "all_directories": [d for d in os.listdir(".") if os.path.isdir(d)]
        }
    except Exception as e:
        return {"error": str(e)}

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
    
    # Run AI-enhanced hybrid window detection (Azure Computer Vision + Gemini API + OpenCV)
    try:
        detector = HybridWindowDetector(
            gemini_api_key=GEMINI_API_KEY,
            azure_vision_key=AZURE_VISION_KEY,
            azure_vision_endpoint=AZURE_VISION_ENDPOINT
        )
        detector.detect_window(image_file, mask_path)
        print(f"✅ AI-enhanced hybrid window detection completed")
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
    blind_name: str = Query(None, description="The filename of the blind texture in the blinds/ folder (for texture mode)"),
    blind_type: str = Query(None, description="The type of blind pattern to generate (for generated mode)"),
    color: str = Query(..., description="Hex color for the blinds (e.g., #FF0000)"),
    material: str = Query("fabric", description="Material type for generated blinds (fabric, wood, metal, plastic)"),
    mode: str = Query("texture", description="Mode: 'texture' for pre-made textures, 'generated' for custom patterns")
):
    print(f"Try-on request: image_id={image_id}, mode={mode}, blind_name={blind_name}, blind_type={blind_type}, color={color}, material={material}")
    
    try:
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
        
        # Load original image and mask
        try:
            orig_img = Image.open(image_file).convert("RGB").resize((320, 320))
            mask_img = Image.open(mask_path).convert("L").resize((320, 320))
            print("Original image and mask loaded successfully")
        except Exception as e:
            print(f"Error loading images: {e}")
            return JSONResponse(status_code=500, content={"error": f"Failed to load images: {e}"})
        
        # Get blind image based on mode
        if mode == "texture":
            # Use pre-made texture
            if not blind_name:
                return JSONResponse(status_code=400, content={"error": "blind_name is required for texture mode"})
            
            blind_path = os.path.join(BLINDS_DIR, blind_name)
            print(f"Looking for blind texture at: {blind_path}")
            
            if not os.path.exists(blind_path):
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
            
            print(f"Found blind texture: {blind_path}")
            blind_img = Image.open(blind_path).convert("RGB").resize((320, 320))
            
            # Optionally tint the blind texture
            if color:
                try:
                    color_rgb = tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
                    color_layer = Image.new("RGB", blind_img.size, color_rgb)
                    blind_img = Image.blend(blind_img, color_layer, alpha=0.5)
                    print(f"Applied color tint: {color}")
                except Exception as e:
                    print(f"Error applying color tint: {e}")
                    return JSONResponse(status_code=400, content={"error": f"Invalid color format: {e}"})
        
        elif mode == "generated":
            # Generate custom blind pattern
            if not blind_type:
                return JSONResponse(status_code=400, content={"error": "blind_type is required for generated mode"})
            
            try:
                pattern_generator = BlindPatternGenerator()
                blind_img = pattern_generator.generate_blind_pattern(
                    blind_type=blind_type,
                    color=color,
                    width=320,
                    height=320,
                    material=material
                )
                print(f"Generated blind pattern: {blind_type}, color: {color}, material: {material}")
            except Exception as e:
                print(f"Error generating blind pattern: {e}")
                return JSONResponse(status_code=500, content={"error": f"Failed to generate blind pattern: {e}"})
        
        else:
            return JSONResponse(status_code=400, content={"error": f"Invalid mode: {mode}. Use 'texture' or 'generated'"})
        
        # Apply the blind texture to the window area using the mask
        try:
            mask_np = np.array(mask_img)
            mask_bin = (mask_np > 128).astype(np.uint8) * 255
            mask_img_bin = Image.fromarray(mask_bin)
            result_img = orig_img.copy()
            
            # IMPROVED BLENDING: Make blinds look more realistic
            # Convert to numpy arrays for processing
            orig_np = np.array(orig_img)
            blind_np = np.array(blind_img)
            mask_np_bin = np.array(mask_img_bin)
            
            # Create realistic blind effect
            result_np = orig_np.copy().astype(float)
            
            # Apply realistic blending with proper mask handling
            for i in range(3):  # RGB channels
                blind_channel = blind_np[:, :, i].astype(float)
                mask_channel = mask_np_bin.astype(float) / 255.0
                
                # Enhanced blending formula for realistic blinds
                # Use different blend factors for different areas
                blend_factor = 0.8  # Stronger blind visibility
                
                # Apply blinds with realistic lighting
                result_np[:, :, i] = (
                    orig_np[:, :, i] * (1 - mask_channel * blend_factor) + 
                    blind_channel * mask_channel * blend_factor
                )
            
            # Add subtle shadow effect to make blinds look installed
            shadow_mask = cv2.GaussianBlur(mask_np_bin.astype(np.float32) / 255.0, (5, 5), 0)
            shadow_intensity = 0.1
            
            for i in range(3):
                result_np[:, :, i] = result_np[:, :, i] * (1 - shadow_mask * shadow_intensity)
            
            # Convert back to PIL Image
            result_img = Image.fromarray(np.clip(result_np, 0, 255).astype(np.uint8))
            
            print(f"Enhanced try-on completed. Result saved with mask area: {np.count_nonzero(mask_np_bin)} pixels")
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
        result_url = None
        try:
            result_url = upload_to_azure_blob(result_path, result_filename)
            print(f"Azure upload result: {result_url}")
        except Exception as e:
            print(f"Azure upload failed: {e}")
            # Continue without Azure upload
        
        # Prepare response
        response = {
            "message": "Try-on result generated successfully!", 
            "method": "Hybrid (OpenCV + Gemini API) + PIL",
            "result_filename": result_filename,
            "local_path": result_path
        }
        
        # Always provide a result URL - either Azure or direct
        if result_url:
            response["result_url"] = result_url
            print(f"Using Azure result URL: {result_url}")
        else:
            # If Azure upload failed, provide a direct URL to the result image
            base_url = "https://blinds-boundaries-api-dbewbmh4bjdsc6ht.canadacentral-01.azurewebsites.net"
            response["result_url"] = f"{base_url}/results/{result_filename}"
            print(f"Using direct result URL: {response['result_url']}")
        
        print(f"Try-on completed successfully. Response: {response}")
        return response
        
    except Exception as e:
        print(f"Unexpected error in try-on: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": f"Unexpected error: {e}"})

# For local development
if __name__ == "__main__":
    import uvicorn
    print("Starting local development server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info") 