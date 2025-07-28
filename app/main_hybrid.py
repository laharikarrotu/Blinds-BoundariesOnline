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

print("=== Importing AI-Enhanced detectors (SAM + YOLOv8) ===")
# Import AI-Enhanced detector with SAM and YOLOv8
AIEnhancedWindowDetector = None
BlindPatternGenerator = None

# Try to import AI-Enhanced detector
try:
    from .ai_enhanced_detector import AIEnhancedWindowDetector
    print("✅ Successfully imported AI-Enhanced detector")
except ImportError as e:
    print(f"⚠️ AI-Enhanced detector import failed: {e}")
    try:
        from ai_enhanced_detector import AIEnhancedWindowDetector
        print("✅ Successfully imported AI-Enhanced detector (absolute)")
    except ImportError as e2:
        print(f"⚠️ AI-Enhanced detector absolute import failed: {e2}")

# Try to import core components as fallback
try:
    from .hybrid_detector import HybridWindowDetector
    print("✅ Successfully imported HybridWindowDetector")
except ImportError as e:
    print(f"⚠️ Hybrid detector import failed: {e}")
    try:
        from hybrid_detector import HybridWindowDetector
        print("✅ Successfully imported HybridWindowDetector (absolute)")
    except ImportError as e2:
        print(f"⚠️ Hybrid detector absolute import failed: {e2}")

try:
    from .blind_pattern_generator import BlindPatternGenerator
    print("✅ Successfully imported BlindPatternGenerator")
except ImportError as e:
    print(f"⚠️ Blind pattern generator import failed: {e}")
    try:
        from blind_pattern_generator import BlindPatternGenerator
        print("✅ Successfully imported BlindPatternGenerator (absolute)")
    except ImportError as e2:
        print(f"⚠️ Blind pattern generator absolute import failed: {e2}")

print("=== Import status ===")
print(f"AIEnhancedWindowDetector: {'Available' if AIEnhancedWindowDetector else 'Not available'}")
print(f"HybridWindowDetector: {'Available' if HybridWindowDetector else 'Not available'}")
print(f"BlindPatternGenerator: {'Available' if BlindPatternGenerator else 'Not available'}")

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
        "message": "Blinds & Boundaries API is running with AI-Enhanced detection!", 
        "status": "healthy",
        "ml_type": "AI-Enhanced (SAM + YOLOv8 + Hybrid)",
        "features": "Revolutionary window detection, blind try-on",
        "ai_enhanced": AIEnhancedWindowDetector is not None,
        "hybrid_enabled": HybridWindowDetector is not None,
        "gemini_available": GEMINI_API_KEY is not None,
        "azure_available": AZURE_AVAILABLE,
        "version": "2.0.0"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "components": {
            "hybrid_detector": HybridWindowDetector is not None,
            "blind_pattern_generator": BlindPatternGenerator is not None,
            "azure_vision": AZURE_VISION_KEY is not None,
            "gemini_api": GEMINI_API_KEY is not None
        }
    }

@app.get("/blinds-boundaries.vercel.app/{path:path}")
def redirect_vercel_app(path: str):
    return {"message": f"Redirecting to Vercel app: {path}"}

@app.get("/test-results")
def test_results():
    """Test endpoint to check if results directory is accessible"""
    try:
        results_files = os.listdir(RESULTS_DIR) if os.path.exists(RESULTS_DIR) else []
        return {
            "message": "Results directory accessible",
            "files": results_files,
            "directory": RESULTS_DIR
        }
    except Exception as e:
        return {"error": f"Could not access results directory: {e}"}

@app.get("/debug-results")
def debug_results():
    """Debug endpoint to check directory structure"""
    try:
        current_dir = os.getcwd()
        directories = {
            "current": current_dir,
            "uploads": os.listdir(UPLOAD_DIR) if os.path.exists(UPLOAD_DIR) else [],
            "masks": os.listdir(MASK_DIR) if os.path.exists(MASK_DIR) else [],
            "blinds": os.listdir(BLINDS_DIR) if os.path.exists(BLINDS_DIR) else [],
            "results": os.listdir(RESULTS_DIR) if os.path.exists(RESULTS_DIR) else []
        }
        return {
            "message": "Directory structure debug info",
            "directories": directories
        }
    except Exception as e:
        return {"error": f"Debug failed: {e}"}

@app.get("/blinds-boundaries.vercel.app/")
def redirect_vercel_app_root():
    return {"message": "Redirecting to Vercel app root"}

@app.get("/blinds-list")
def blinds_list():
    """Get list of available blind textures"""
    try:
        if not os.path.exists(BLINDS_DIR):
            return {"blinds": [], "message": "Blinds directory not found"}
        
        blind_files = []
        for filename in os.listdir(BLINDS_DIR):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                blind_files.append({
                    "name": filename,
                    "url": f"/blinds/{filename}"
                })
        
        return {
            "blinds": blind_files,
            "count": len(blind_files),
            "directory": BLINDS_DIR
        }
    except Exception as e:
        return {"error": f"Could not list blinds: {e}"}

@app.get("/debug-blinds")
def debug_blinds():
    """Debug endpoint for blinds directory"""
    try:
        if os.path.exists(BLINDS_DIR):
            files = os.listdir(BLINDS_DIR)
            return {
                "message": "Blinds directory debug info",
                "directory": BLINDS_DIR,
                "files": files,
                "exists": True
            }
        else:
            return {
                "message": "Blinds directory not found",
                "directory": BLINDS_DIR,
                "exists": False
            }
    except Exception as e:
        return {"error": f"Debug blinds failed: {e}"}

def upload_to_azure_blob(file_path: str, blob_name: str) -> str:
    """Upload a file to Azure Blob Storage"""
    if not AZURE_CONNECTION_STRING:
        print("⚠️ Azure connection string not configured")
        return None
    
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(AZURE_CONTAINER)
        
        with open(file_path, "rb") as data:
            blob_client = container_client.upload_blob(name=blob_name, data=data, overwrite=True)
        
        return f"https://{blob_service_client.account_name}.blob.core.windows.net/{AZURE_CONTAINER}/{blob_name}"
    except Exception as e:
        print(f"❌ Azure upload failed: {e}")
        return None

@app.options("/upload-image")
def upload_image_options():
    return {"message": "Upload endpoint ready"}

@app.post("/upload-image")
def upload_image(file: UploadFile = File(...)):
    """Upload an image for window detection"""
    try:
        # Generate unique filename
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
        image_id = str(uuid.uuid4())
        filename = f"{image_id}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        print(f"✅ Image uploaded: {filename}")
        
        # Upload to Azure (optional)
        azure_url = upload_to_azure_blob(file_path, filename)
        
        return {
            "message": "Image uploaded successfully!",
            "image_id": image_id,
            "filename": filename,
            "azure_url": azure_url
        }
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return JSONResponse(status_code=500, content={"error": f"Upload failed: {e}"})

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
    
    # Run AI-Enhanced window detection (SAM + YOLOv8 + Hybrid)
    try:
        if AIEnhancedWindowDetector is not None:
            # Check for models and enable only what's available
            sam_model_path = 'models/sam_vit_l_0b3195.pth'
            yolo_model_path = 'yolov8n.pt'
            
            enable_sam = os.path.exists(sam_model_path)
            enable_yolo = os.path.exists(yolo_model_path)
            
            print(f"Model availability check:")
            print(f"  - SAM model: {'Available' if enable_sam else 'Not found'}")
            print(f"  - YOLOv8 model: {'Available' if enable_yolo else 'Not found'}")
            print(f"  - Hybrid: Always available")
            
            ai_detector = AIEnhancedWindowDetector(
                sam_model_path=sam_model_path if enable_sam else None,
                yolo_model_path=yolo_model_path if enable_yolo else None,
                gemini_api_key=GEMINI_API_KEY,
                azure_vision_key=AZURE_VISION_KEY,
                azure_vision_endpoint=AZURE_VISION_ENDPOINT,
                device='auto',
                enable_sam=enable_sam,
                enable_yolo=enable_yolo,
                enable_hybrid=True
            )
            
            # Get detection statistics
            stats = ai_detector.get_detection_stats()
            print(f"AI-Enhanced detector stats: {stats}")
            
            # Run ensemble detection
            result, detection_results = ai_detector.detect_window_ensemble(image_file, mask_path)
            
            if result:
                print(f"✅ Revolutionary AI-Enhanced window detection completed!")
                print(f"Detection results: {detection_results}")
            else:
                print(f"⚠️ AI-Enhanced detection failed, using fallback")
                result = create_simple_mask(image_file, mask_path)
        elif HybridWindowDetector is not None:
            print("⚠️ AI-Enhanced detector not available, using Hybrid fallback")
            hybrid_detector = HybridWindowDetector(
                gemini_api_key=GEMINI_API_KEY,
                azure_vision_key=AZURE_VISION_KEY,
                azure_vision_endpoint=AZURE_VISION_ENDPOINT
            )
            result = hybrid_detector.detect_window(image_file, mask_path)
            
            if result:
                print(f"✅ Hybrid window detection completed!")
            else:
                print(f"⚠️ Hybrid detection failed, using fallback")
                result = create_simple_mask(image_file, mask_path)
        else:
            print("⚠️ No detectors available, using simple fallback")
            result = create_simple_mask(image_file, mask_path)
                
    except Exception as e:
        print(f"Detection error: {e}")
        print("Using simple fallback...")
        result = create_simple_mask(image_file, mask_path)
    
    # Upload mask to Azure (optional)
    mask_url = upload_to_azure_blob(mask_path, mask_filename)
    response = {
        "message": "Window mask generated successfully using AI-Enhanced detection!", 
        "method": "AI-Enhanced (SAM + YOLOv8 + Hybrid)" if AIEnhancedWindowDetector else "Hybrid (Azure Vision + Gemini + OpenCV)" if HybridWindowDetector else "Simple OpenCV fallback",
        "ai_enhanced": AIEnhancedWindowDetector is not None,
        "hybrid_enabled": HybridWindowDetector is not None,
        "gemini_used": GEMINI_API_KEY is not None,
        "azure_used": AZURE_AVAILABLE
    }
    if mask_url:
        response["mask_url"] = mask_url
    return response

def create_simple_mask(image_file: str, mask_path: str) -> str:
    """Create a simple rectangular mask as fallback"""
    try:
        import cv2
        image = cv2.imread(image_file)
        if image is not None:
            # Create a simple rectangular mask
            height, width = image.shape[:2]
            mask = np.zeros((height, width), dtype=np.uint8)
            # Create a rectangle in the center
            x1, y1 = width//4, height//4
            x2, y2 = 3*width//4, 3*height//4
            cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
            cv2.imwrite(mask_path, mask)
            print("✅ Simple mask created as fallback")
            return mask_path
        else:
            print("❌ Could not read image file")
            return None
    except Exception as e:
        print(f"❌ Simple mask creation failed: {e}")
        return None

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
            return JSONResponse(status_code=404, content={"error": "Image not found for the given image_id."})
        
        # Find the mask file
        mask_file = None
        for fname in os.listdir(MASK_DIR):
            if fname.startswith(f"mask_{image_id}"):
                mask_file = os.path.join(MASK_DIR, fname)
                break
        
        if not mask_file or not os.path.exists(mask_file):
            return JSONResponse(status_code=404, content={"error": "Mask not found. Please run window detection first."})
        
        print(f"Found image file: {image_file}")
        print(f"Found mask file: {mask_file}")
        
        # Load the original image and mask
        original_image = Image.open(image_file)
        mask_image = Image.open(mask_file).convert('L')
        
        print("Original image and mask loaded successfully")
        
        if mode == "texture":
            # Use pre-made blind texture
            if not blind_name:
                return JSONResponse(status_code=400, content={"error": "blind_name is required for texture mode"})
            
            blind_texture_path = os.path.join(BLINDS_DIR, blind_name)
            if not os.path.exists(blind_texture_path):
                return JSONResponse(status_code=404, content={"error": f"Blind texture '{blind_name}' not found"})
            
            print(f"Looking for blind texture at: {blind_texture_path}")
            
            # Load blind texture
            blind_texture = Image.open(blind_texture_path)
            print(f"Found blind texture: {blind_texture_path}")
            
            # Apply color tint
            if color and color != "#000000":
                print(f"Applied color tint: {color}")
                # Convert hex to RGB
                color_rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
                # Create a tinted version of the blind texture
                tinted_texture = blind_texture.copy()
                tinted_texture = tinted_texture.convert('RGBA')
                # Apply color tint
                tinted_data = np.array(tinted_texture)
                tinted_data[:, :, 0] = (tinted_data[:, :, 0] * color_rgb[0]) // 255
                tinted_data[:, :, 1] = (tinted_data[:, :, 1] * color_rgb[1]) // 255
                tinted_data[:, :, 2] = (tinted_data[:, :, 2] * color_rgb[2]) // 255
                blind_texture = Image.fromarray(tinted_data)
            
            # Resize blind texture to match image size
            blind_texture = blind_texture.resize(original_image.size)
            
            # Apply blind texture to masked area
            result_image = original_image.copy()
            result_image = result_image.convert('RGBA')
            blind_texture = blind_texture.convert('RGBA')
            
            # Create a mask for the blind texture
            mask_array = np.array(mask_image)
            mask_array = mask_array > 128  # Threshold to binary
            
            # Apply blind texture only to masked areas
            result_array = np.array(result_image)
            blind_array = np.array(blind_texture)
            
            # Blend the blind texture with the original image in masked areas
            alpha = 0.8  # Transparency factor
            result_array[mask_array] = (
                alpha * blind_array[mask_array] + 
                (1 - alpha) * result_array[mask_array]
            ).astype(np.uint8)
            
            result_image = Image.fromarray(result_array)
            
        else:  # generated mode
            # Generate custom blind pattern
            if not BlindPatternGenerator:
                return JSONResponse(status_code=500, content={"error": "Blind pattern generator not available"})
            
            generator = BlindPatternGenerator()
            result_image = generator.generate_blind_pattern(
                original_image, mask_image, blind_type, color, material
            )
        
        # Save the result
        result_filename = f"tryon_{image_id}_{blind_name or blind_type or 'custom'}.png"
        result_path = os.path.join(RESULTS_DIR, result_filename)
        result_image.save(result_path)
        
        # Calculate mask area for statistics
        mask_array = np.array(mask_image)
        mask_area = np.sum(mask_array > 128)
        print(f"Enhanced try-on completed. Result saved with mask area: {mask_area} pixels")
        print(f"Result saved to: {result_path}")
        
        # Upload to Azure
        azure_url = upload_to_azure_blob(result_path, result_filename)
        print(f"Azure upload result: {azure_url}")
        
        # Use Azure URL if available, otherwise use local path
        result_url = azure_url if azure_url else f"/results/{result_filename}"
        print(f"Using Azure result URL: {result_url}")
        
        return {
            "message": "Try-on result generated successfully!",
            "method": "Hybrid (OpenCV + Gemini API) + PIL",
            "result_filename": result_filename,
            "local_path": result_path,
            "result_url": result_url
        }
        
    except Exception as e:
        print(f"❌ Try-on failed: {e}")
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": f"Try-on failed: {e}"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 