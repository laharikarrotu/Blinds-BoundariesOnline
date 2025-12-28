"""API routes with dependency injection."""
from fastapi import APIRouter, File, UploadFile, Query, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
from pathlib import Path

# Import core modules first (these should always work)
from app.core.config import config
from app.core.logger import logger
from app.core.exceptions import AppException
from app.models.blind import BlindData, BlindType, Material
from app.cache.lru_cache import cache

# Initialize router immediately
router = APIRouter()

# Import services with error handling - don't fail module import if services fail
image_repo = None
storage_repo = None
detection_service = None
overlay_service = None

# Try importing repositories
try:
    from app.repositories.image_repository import ImageRepository
    from app.repositories.storage_repository import StorageRepository
    storage_repo = StorageRepository()
    # Pass storage_repo to ImageRepository for Azure integration
    image_repo = ImageRepository(storage_repo=storage_repo)
    logger.info("Repositories initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize repositories: {e}")
    import traceback
    traceback.print_exc()

# Try importing and initializing services (pass storage_repo for Azure integration)
try:
    from app.services.window_detection_service import WindowDetectionService
    detection_service = WindowDetectionService(storage_repo=storage_repo)
    logger.info("Window detection service initialized successfully")
except Exception as e:
    logger.warning(f"Detection service not available: {e}")
    detection_service = None

try:
    from app.services.blind_overlay_service import BlindOverlayService
    overlay_service = BlindOverlayService(storage_repo=storage_repo)
    logger.info("Blind overlay service initialized successfully")
except Exception as e:
    error_msg = str(e) if str(e) else repr(e)
    logger.error(f"Overlay service initialization failed: {error_msg}")
    import traceback
    logger.error(f"Traceback: {traceback.format_exc()}")
    overlay_service = None


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "components": {
            "detector": detection_service.detector is not None if detection_service else False,
            "cache": cache.size(),
            "azure_vision": config.azure_vision_available,
            "azure_storage": storage_repo.is_available() if storage_repo else False,
            "gemini_api": config.gemini_available
        }
    }


@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """Upload image endpoint with validation."""
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read file content
        content = await file.read()
        
        # Validate file size
        if len(content) > config.MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum of {config.MAX_IMAGE_SIZE / 1024 / 1024}MB"
            )
        
        # Save file
        image_id = image_repo.save_uploaded_file(content, file.filename)
        
        # Upload to Azure if available
        azure_url = None
        if storage_repo and storage_repo.is_available():
            image_data = image_repo.get_image_data(image_id)
            blob_name = f"uploads/{image_id}{Path(file.filename).suffix}"
            azure_url = storage_repo.upload_file(image_data.file_path, blob_name)
        
        logger.info(f"Image uploaded: {image_id} ({file.filename})")
        
        return {
            "message": "Image uploaded successfully",
            "image_id": image_id,
            "filename": file.filename,
            "azure_url": azure_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Upload failed")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/detect-window")
async def detect_window(image_id: str = Query(..., description="Image ID from upload")):
    """Detect window endpoint."""
    if not detection_service:
        raise HTTPException(status_code=503, detail="Detection service not available")
    try:
        # Get image data
        if not image_repo:
            raise HTTPException(status_code=503, detail="Image repository not available")
        image_data = image_repo.get_image_data(image_id)
        
        # Detect window
        mask_path = detection_service.detect_window(
            image_id,
            image_data.file_path
        )
        
        logger.info(f"Window detection completed for {image_id}")
        
        return {
            "message": "Window detection completed",
            "image_id": image_id,
            "mask_path": mask_path
        }
        
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.exception("Window detection failed")
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")


@router.post("/try-on")
async def try_on(
    image_id: str = Query(..., description="Image ID"),
    blind_name: Optional[str] = Query(None, description="Blind texture name"),
    blind_type: Optional[str] = Query(None, description="Blind type"),
    color: str = Query(..., description="Hex color"),
    material: str = Query("fabric", description="Material type"),
    mode: str = Query("texture", description="Mode: texture or generated")
):
    """Try-on endpoint with optimized processing."""
    try:
        # Create BlindData model
        blind_data = BlindData(
            mode=mode,
            color=color,
            blind_name=blind_name if mode == 'texture' else None,
            blind_type=BlindType(blind_type) if mode == 'generated' and blind_type else None,
            material=Material(material)
        )
        
        # Apply overlay
        if not overlay_service:
            raise HTTPException(status_code=503, detail="Overlay service not available")
        result_path = overlay_service.apply_blind_overlay(image_id, blind_data)
        
        logger.info(f"Try-on completed for {image_id}")
        
        # Determine result URL (Azure if available, otherwise local)
        if result_path.startswith("http"):
            # Already an Azure URL
            result_url = result_path
        else:
            # Local path, check if Azure URL exists
            result_filename = Path(result_path).name
            if storage_repo and storage_repo.is_available():
                azure_url = storage_repo.get_file_url(f"results/{result_filename}")
                result_url = azure_url if azure_url else f"/results/{result_filename}"
            else:
                result_url = f"/results/{result_filename}"
        
        return {
            "message": "Try-on completed successfully",
            "image_id": image_id,
            "result_path": result_path,
            "result_url": result_url
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AppException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        error_msg = str(e) if str(e) else repr(e) or "Unknown error"
        logger.exception(f"Try-on failed: {error_msg}")
        raise HTTPException(status_code=500, detail=f"Try-on failed: {error_msg}")


@router.get("/blinds-list")
@router.get("/blinds-list/")  # Also support trailing slash
async def blinds_list():
    """Get list of available blinds."""
    logger.info("Blinds-list endpoint called - Elite Architecture")
    try:
        from pathlib import Path
        
        blinds_dir = Path(config.BLINDS_DIR)
        
        # Ensure directory exists
        blinds_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Blinds directory: {blinds_dir}, exists: {blinds_dir.exists()}")
        
        if not blinds_dir.exists() or not any(blinds_dir.iterdir()):
            logger.info("Blinds directory is empty, returning empty list")
            return {
                "texture_blinds": [],
                "generated_patterns": [bt.value for bt in BlindType],
                "materials": [m.value for m in Material],
                "texture_count": 0,
                "pattern_count": len(BlindType),
                "mode": "elite"
            }
        
        texture_blinds = [
            f.name for f in blinds_dir.iterdir()
            if f.is_file() and f.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        ]
        
        logger.info(f"Found {len(texture_blinds)} texture blinds")
        
        return {
            "texture_blinds": texture_blinds,
            "generated_patterns": [bt.value for bt in BlindType],
            "materials": [m.value for m in Material],
            "texture_count": len(texture_blinds),
            "pattern_count": len(BlindType),
            "mode": "elite"
        }
        
    except Exception as e:
        logger.exception("Failed to list blinds")
        raise HTTPException(status_code=500, detail=f"Failed to list blinds: {str(e)}")

