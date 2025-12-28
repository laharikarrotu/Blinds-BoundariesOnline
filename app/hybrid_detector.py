print("=== Loading hybrid_detector.py ===")

# Disable OpenGL/GLX before importing cv2 (fixes Azure App Service libGL.so.1 error)
import os
os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '0'
os.environ['OPENCV_IO_ENABLE_OPENEXR'] = '0'
# Disable GUI backends that require libGL
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['DISPLAY'] = ''

try:
    import cv2
    # Test if cv2 works (some operations may still fail)
    cv2.setNumThreads(1)  # Reduce threading issues
    print("✅ OpenCV imported successfully")
except Exception as e:
    print(f"⚠️ OpenCV import warning: {e}")
    cv2 = None

import numpy as np
from PIL import Image
import requests
import json
import base64
import time  # For retry delays
from io import BytesIO

# Try importing logger for better error handling
try:
    from app.core.logger import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

print("=== Successfully imported all modules in hybrid_detector ===")

class HybridWindowDetector:
    """
    AI-Enhanced Hybrid approach: Azure Computer Vision + Gemini API + OpenCV fallback
    Focus on: AI-powered window detection for maximum accuracy
    """
    
    def __init__(self, gemini_api_key=None, azure_vision_key=None, azure_vision_endpoint=None):
        try:
            self.gemini_api_key = gemini_api_key
            self.gemini_available = gemini_api_key is not None
            
            # Azure Computer Vision setup
            self.azure_vision_key = azure_vision_key
            self.azure_vision_endpoint = azure_vision_endpoint
            self.azure_vision_available = azure_vision_key is not None and azure_vision_endpoint is not None
            
            print(f"✅ AI-Enhanced Hybrid Window Detector initialized")
            print(f"   - Azure Computer Vision: {'Available' if self.azure_vision_available else 'Not configured'}")
            print(f"   - Gemini API: {'Available' if self.gemini_available else 'Not configured'}")
            print(f"   - OpenCV: Always available (FREE fallback)")
        except Exception as e:
            print(f"⚠️ Warning: Error initializing Hybrid Window Detector: {e}")
            self.gemini_api_key = None
            self.gemini_available = False
            self.azure_vision_available = False
    
    def detect_windows_azure_vision(self, image_path, mask_save_path):
        """
        Azure Computer Vision AI-based window detection (MOST ACCURATE)
        Enhanced with:
        - Retry logic for reliability
        - Better error handling
        - Multiple detection strategies
        - Caching support
        """
        if not self.azure_vision_available:
            return None, "Azure Computer Vision not configured"
        
        try:
            # Try optimized service first (if available)
            try:
                from app.services.azure_vision_optimized import AzureVisionOptimized
                optimized_service = AzureVisionOptimized(
                    self.azure_vision_key,
                    self.azure_vision_endpoint
                )
                result, success = optimized_service.detect_windows_with_segmentation(
                    image_path,
                    mask_save_path
                )
                if success and result:
                    return result, True
            except (ImportError, Exception) as e:
                logger.debug(f"Optimized service not available, using standard method: {e}")
            
            # Fallback to standard method with improvements
            # Read image file
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
            
            # Try v4.0 API first (newer, better), fallback to v3.2
            api_versions = ['v4.0', 'v3.2']
            last_error = None
            
            for api_version in api_versions:
                try:
                    # Azure Computer Vision API endpoint
                    vision_url = f"{self.azure_vision_endpoint}/vision/{api_version}/analyze"
                    
                    # Enhanced parameters for better detection
                    params = {
                        'visualFeatures': 'Objects,Description,Tags',  # Added Tags for better detection
                        'language': 'en',
                        'model-version': 'latest',
                        'details': 'Landmarks'  # Get more details
                    }
                    
                    headers = {
                        'Content-Type': 'application/octet-stream',
                        'Ocp-Apim-Subscription-Key': self.azure_vision_key
                    }
                    
                    # Make API call with timeout
                    response = requests.post(
                        vision_url,
                        params=params,
                        headers=headers,
                        data=image_data,
                        timeout=30  # Add timeout
                    )
                    
                    if response.status_code == 200:
                        break  # Success, use this version
                    elif response.status_code == 401:  # Unauthorized - API key issue
                        error_detail = response.text[:200] if response.text else "No error details"
                        last_error = f"API {api_version} authentication failed (401): Check AZURE_VISION_KEY. Error: {error_detail}"
                        print(f"  ❌ Azure Computer Vision 401 Error: Invalid API key or endpoint")
                        print(f"     Endpoint: {self.azure_vision_endpoint}")
                        print(f"     Key present: {'Yes' if self.azure_vision_key else 'No'}")
                        print(f"     Key length: {len(self.azure_vision_key) if self.azure_vision_key else 0} characters")
                        # Don't try next version if auth failed - it will fail for all versions
                        return None, last_error
                    elif response.status_code == 429:  # Rate limit
                        import time
                        time.sleep(2)  # Wait before retry
                        continue
                    else:
                        error_detail = response.text[:200] if response.text else "No error details"
                        last_error = f"API {api_version} error {response.status_code}: {error_detail}"
                        print(f"  ⚠️ Azure Computer Vision {response.status_code}: {error_detail}")
                        continue  # Try next version
                        
                except requests.exceptions.RequestException as e:
                    last_error = str(e)
                    continue  # Try next version
            
            if response.status_code != 200:
                return None, f"Azure Computer Vision API error: {last_error or response.status_code}"
            
            if response.status_code == 200:
                result = response.json()
                
                # Load image for mask creation (use PIL instead of cv2 to avoid libGL.so.1)
                from PIL import Image as PILImage
                pil_image = PILImage.open(image_path)
                image_width, image_height = pil_image.size
                mask = np.zeros((image_height, image_width), dtype=np.uint8)
                
                # Look for window-related objects
                window_objects = []
                for obj in result.get('objects', []):
                    # Check if object is window-related
                    object_name = obj.get('object', '').lower()
                    if any(keyword in object_name for keyword in ['window', 'glass', 'pane', 'frame']):
                        window_objects.append(obj)
                
                # If no specific window objects found, look for rectangular objects
                if not window_objects:
                    for obj in result.get('objects', []):
                        # Check for large rectangular objects (likely windows)
                        bbox = obj.get('rectangle', {})
                        if bbox:
                            x = bbox.get('x', 0)
                            y = bbox.get('y', 0)
                            w = bbox.get('w', 0)
                            h = bbox.get('h', 0)
                            
                            # Check if it's a reasonable size for a window
                            area = w * h
                            image_area = image_width * image_height
                            if area > image_area * 0.1:  # At least 10% of image
                                window_objects.append(obj)
                
                # Create mask from detected windows
                for obj in window_objects:
                    bbox = obj.get('rectangle', {})
                    if bbox:
                        x = bbox.get('x', 0)
                        y = bbox.get('y', 0)
                        w = bbox.get('w', 0)
                        h = bbox.get('h', 0)
                        
                        # Adaptive padding based on object size for better coverage
                        padding = max(10, min(w, h) * 0.1)  # 10% of smaller dimension, min 10px
                        x = max(0, int(x - padding))
                        y = max(0, int(y - padding))
                        w = min(image_width - x, int(w + 2 * padding))
                        h = min(image_height - y, int(h + 2 * padding))
                        
                        # Fill rectangle in mask (using numpy instead of cv2.rectangle)
                        mask[y:y+h, x:x+w] = 255
                
                # If no objects detected, try semantic analysis
                if np.count_nonzero(mask) < 1000:
                    # Use description to find windows
                    description = result.get('description', {})
                    captions = description.get('captions', [])
                    
                    for caption in captions:
                        text = caption.get('text', '').lower()
                        if 'window' in text or 'glass' in text:
                            # Create a center-based mask if window is mentioned
                            center_x, center_y = image_width // 2, image_height // 2
                            mask_size = min(image_width, image_height) // 2
                            x1 = center_x - mask_size//2
                            y1 = center_y - mask_size//2
                            x2 = center_x + mask_size//2
                            y2 = center_y + mask_size//2
                            # Fill rectangle in mask (using numpy instead of cv2.rectangle)
                            mask[y1:y2, x1:x2] = 255
                            break
                
                # Apply realistic blending preparation
                # Convert mask shape to match image dimensions
                image_shape = (image_height, image_width, 3)  # (height, width, channels)
                final_mask = self._prepare_realistic_mask(mask, image_shape)
                
                # Resize to 320x320 using PIL (avoids cv2 and libGL.so.1)
                mask_image = PILImage.fromarray(final_mask.astype(np.uint8))
                mask_resized = mask_image.resize((320, 320), PILImage.LANCZOS)
                mask_resized.save(mask_save_path)
                
                # Convert back to numpy for counting
                mask_resized_array = np.array(mask_resized)
                
                print(f"Azure Computer Vision detected {len(window_objects)} window objects")
                return mask_save_path, np.count_nonzero(mask_resized_array) > 1000
                
            else:
                return None, f"Azure Computer Vision API error: {response.status_code}"
                
        except Exception as e:
            return None, f"Azure Computer Vision detection error: {e}"
    
    def detect_windows_opencv(self, image_path, mask_save_path):
        """
        Enhanced OpenCV-based window detection (FREE) - Focus on 4 critical improvements
        Returns: (mask_path or None, window_found: bool, error_message: str or None)
        """
        if cv2 is None:
            return None, False, "OpenCV not available (libGL.so.1 missing)"
        
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise Exception("Could not load image")
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # IMPROVEMENT 1: Better Edge Detection
            # Use multiple edge detection methods for better results
            edges_combined = self._enhanced_edge_detection(gray)
            
            # IMPROVEMENT 2: Grid Pattern Recognition
            # Detect window frames and grid lines
            window_frames, grid_lines = self._detect_window_grid(gray, edges_combined)
            
            # IMPROVEMENT 3: Full Window Coverage
            # Create mask for the entire window area (including frame)
            full_window_mask = self._create_glass_mask(gray, window_frames, grid_lines)
            
            # IMPROVEMENT 4: Realistic Blending Preparation
            # Prepare mask for realistic blind application
            final_mask = self._prepare_realistic_mask(full_window_mask, image.shape)
            
            # Resize to 320x320 for consistency
            mask_resized = cv2.resize(final_mask, (320, 320))
            
            # Save the mask
            cv2.imwrite(mask_save_path, mask_resized)
            
            print(f"Enhanced window detection completed. Mask saved: {mask_save_path}")
            print(f"Mask size: {mask_resized.shape}, Non-zero pixels: {np.count_nonzero(mask_resized)}")
            
            window_found = np.count_nonzero(mask_resized) > 1000
            return mask_save_path, window_found, None
            
        except Exception as e:
            error_msg = str(e)
            print(f"Enhanced OpenCV detection error: {e}")
            
            # Check if it's the libGL.so.1 error
            if 'libGL' in error_msg or 'libGL.so' in error_msg:
                return None, False, f"OpenCV requires libGL.so.1 (not available on Azure App Service): {error_msg}"
            
            # Try to create a simple fallback mask if cv2 is available
            if cv2 is not None:
                try:
                    fallback_mask = np.zeros((320, 320), dtype=np.uint8)
                    cv2.rectangle(fallback_mask, (80, 80), (240, 240), 255, -1)
                    cv2.imwrite(mask_save_path, fallback_mask)
                    return mask_save_path, False, None
                except Exception as e2:
                    return None, False, f"OpenCV fallback failed: {e2}"
            
            return None, False, f"OpenCV error: {error_msg}"
    
    def _enhanced_edge_detection(self, gray):
        """
        IMPROVEMENT 1: Better Edge Detection
        Uses multiple methods to detect window edges more accurately
        """
        # Method 1: Adaptive Canny with different thresholds
        edges1 = cv2.Canny(gray, 30, 100)
        edges2 = cv2.Canny(gray, 50, 150)
        edges3 = cv2.Canny(gray, 20, 80)
        
        # Method 2: Sobel edge detection
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        sobel_edges = np.sqrt(sobelx**2 + sobely**2)
        sobel_edges = np.uint8(sobel_edges / sobel_edges.max() * 255)
        
        # Method 3: Laplacian edge detection
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        laplacian_edges = np.uint8(np.absolute(laplacian))
        
        # Combine all edge detection methods
        edges_combined = cv2.bitwise_or(edges1, edges2)
        edges_combined = cv2.bitwise_or(edges_combined, edges3)
        edges_combined = cv2.bitwise_or(edges_combined, sobel_edges)
        edges_combined = cv2.bitwise_or(edges_combined, laplacian_edges)
        
        # Clean up edges with morphological operations
        kernel = np.ones((2, 2), np.uint8)
        edges_combined = cv2.morphologyEx(edges_combined, cv2.MORPH_CLOSE, kernel)
        
        return edges_combined
    
    def _detect_window_grid(self, gray, edges):
        """
        IMPROVEMENT 2: Grid Pattern Recognition
        Detects window frames and grid lines for multi-pane windows
        """
        # Find horizontal and vertical lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
        
        # Detect horizontal lines
        horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel)
        horizontal_lines = cv2.dilate(horizontal_lines, horizontal_kernel, iterations=2)
        
        # Detect vertical lines
        vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel)
        vertical_lines = cv2.dilate(vertical_lines, vertical_kernel, iterations=2)
        
        # Combine horizontal and vertical lines
        grid_lines = cv2.bitwise_or(horizontal_lines, vertical_lines)
        
        # Find window frame (outer boundary)
        # Use HoughLinesP to detect strong lines
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=50, maxLineGap=10)
        
        window_frames = np.zeros_like(gray)
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(window_frames, (x1, y1), (x2, y2), 255, 2)
        
        return window_frames, grid_lines
    
    def _create_glass_mask(self, gray, window_frames, grid_lines):
        """
        IMPROVEMENT 3: Full Window Coverage
        Creates mask for the entire window area (including frame)
        """
        # Create initial mask from window frames
        frame_mask = window_frames.copy()
        
        # Dilate frame mask to include the entire window area
        kernel = np.ones((10, 10), np.uint8)
        frame_mask = cv2.dilate(frame_mask, kernel, iterations=5)
        
        # Find contours in frame mask
        contours, _ = cv2.findContours(frame_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Create full window mask
        full_window_mask = np.zeros_like(gray)
        
        if contours:
            # Find the largest contour (main window area)
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Fill the entire window area (including frame)
            cv2.fillPoly(full_window_mask, [largest_contour], 255)
        
        # If no frames detected, try alternative approach for full window detection
        if np.count_nonzero(full_window_mask) < 1000:
            # Use edge detection to find window boundaries
            edges = cv2.Canny(gray, 30, 100)
            
            # Find contours from edges
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Find the largest rectangular contour (likely the window)
            largest_area = 0
            best_contour = None
            
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > largest_area and area > 5000:  # Minimum area threshold
                    # Check if it's roughly rectangular
                    x, y, w, h = cv2.boundingRect(contour)
                    aspect_ratio = w / h
                    if 0.3 < aspect_ratio < 5.0:  # Reasonable aspect ratio for windows
                        largest_area = area
                        best_contour = contour
            
            if best_contour is not None:
                # Fill the entire window area
                cv2.fillPoly(full_window_mask, [best_contour], 255)
        
        return full_window_mask
    
    def _prepare_realistic_mask(self, glass_mask, image_shape):
        """
        IMPROVEMENT 4: Realistic Blending Preparation
        Prepares mask for realistic blind application with proper edges
        Uses scipy instead of cv2 to avoid libGL.so.1 dependency
        """
        from scipy import ndimage
        
        # Apply Gaussian blur to create soft edges for realistic blending (using scipy)
        blurred_mask = ndimage.gaussian_filter(glass_mask.astype(float), sigma=1.5)
        
        # Normalize to 0-255 range
        mask_min = blurred_mask.min()
        mask_max = blurred_mask.max()
        if mask_max > mask_min:
            normalized_mask = ((blurred_mask - mask_min) / (mask_max - mask_min) * 255).astype(np.uint8)
        else:
            normalized_mask = blurred_mask.astype(np.uint8)
        
        # Apply slight erosion to avoid bleeding into frame areas (using scipy)
        kernel = np.ones((2, 2), dtype=np.uint8)
        final_mask = ndimage.binary_erosion(normalized_mask > 0, structure=kernel).astype(np.uint8) * 255
        
        return final_mask
    
    def detect_windows_gemini(self, image_path, mask_save_path):
        """
        Enhanced Gemini API-based window detection (more accurate)
        Returns: (mask_path or None, window_found: bool, error_message: str or None)
        """
        if not self.gemini_available:
            return None, False, "Gemini API not configured"
        
        try:
            # Read and encode image
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Enhanced prompt for full window coverage
            prompt = """
            Analyze this image and identify all windows. 
            For each window, identify the ENTIRE window area (including frame) that should be covered by blinds.
            
            Return a JSON response in this format:
            {
                "windows": [
                    {
                        "full_window": {"x": 0, "y": 0, "width": 100, "height": 100}
                    }
                ]
            }
            
            The full_window should cover the entire window area including the frame, not just individual panes.
            Only return the JSON, no other text.
            """
            
            # Prepare Gemini API request
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent?key={self.gemini_api_key}"
            
            payload = {
                "contents": [{
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_data
                            }
                        }
                    ]
                }]
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            # Make API call
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                content = result['candidates'][0]['content']['parts'][0]['text']
                
                # Parse JSON response
                try:
                    windows_data = json.loads(content)
                    windows = windows_data.get('windows', [])
                    
                    # Create enhanced mask from Gemini results (using PIL instead of OpenCV)
                    from PIL import Image as PILImage
                    pil_image = PILImage.open(image_path)
                    image_width, image_height = pil_image.size
                    mask = np.zeros((image_height, image_width), dtype=np.uint8)
                    
                    for window in windows:
                        # Add full window area to mask
                        full_window = window.get('full_window', {})
                        if full_window:
                            x, y, w, h = full_window['x'], full_window['y'], full_window['width'], full_window['height']
                            # Fill rectangle in mask (using numpy instead of cv2.rectangle)
                            mask[y:y+h, x:x+w] = 255
                    
                    # Apply realistic blending preparation
                    image_shape = (image_height, image_width, 3)  # (height, width, channels)
                    final_mask = self._prepare_realistic_mask(mask, image_shape)
                    
                    # Resize to 320x320 using PIL (avoids cv2 and libGL.so.1)
                    mask_image = PILImage.fromarray(final_mask.astype(np.uint8))
                    mask_resized = mask_image.resize((320, 320), PILImage.LANCZOS)
                    mask_resized.save(mask_save_path)
                    
                    # Convert back to numpy for counting
                    mask_resized_array = np.array(mask_resized)
                    
                    return mask_save_path, len(windows) > 0, None
                    
                except json.JSONDecodeError:
                    return None, False, "Failed to parse Gemini response"
            else:
                return None, False, f"Gemini API error: {response.status_code}"
                
        except Exception as e:
            error_msg = str(e)
            # Check if it's the libGL.so.1 error
            if 'libGL' in error_msg or 'libGL.so' in error_msg:
                return None, False, f"OpenCV requires libGL.so.1 (not available on Azure App Service): {error_msg}"
            return None, False, f"Gemini detection error: {e}"
    
    def detect_window(self, image_path, mask_save_path):
        """
        Main detection method - tries Azure Computer Vision first (AI), then Gemini, then OpenCV fallback
        """
        print("🔍 Starting AI-enhanced hybrid window detection...")
        
        # Try Azure Computer Vision first (MOST ACCURATE - AI)
        if self.azure_vision_available:
            print("  1. Trying Azure Computer Vision (AI - MOST ACCURATE)...")
            try:
                azure_result, azure_status = self.detect_windows_azure_vision(image_path, mask_save_path)
                
                if azure_result:
                    print("  ✅ Azure Computer Vision found window - using AI result")
                    return azure_result
                else:
                    print(f"  ⚠️ Azure Computer Vision failed: {azure_status}")
            except Exception as e:
                error_msg = str(e)
                if 'libGL' in error_msg or 'libGL.so' in error_msg:
                    print(f"  ⚠️ Azure Computer Vision error (libGL): {error_msg}")
                else:
                    print(f"  ⚠️ Azure Computer Vision error: {error_msg}")
        
        # Try Gemini API second (AI)
        if self.gemini_available:
            print("  2. Azure Computer Vision didn't find window - trying Gemini API (AI)...")
            try:
                gemini_result, gemini_status, gemini_error = self.detect_windows_gemini(image_path, mask_save_path)
                
                if gemini_result:
                    print("  ✅ Gemini found window - using AI result")
                    return gemini_result
                else:
                    print(f"  ⚠️ Gemini failed: {gemini_status}")
            except ValueError:
                # Handle old return format (2 values) for backward compatibility
                try:
                    gemini_result, gemini_status = self.detect_windows_gemini(image_path, mask_save_path)
                    if gemini_result:
                        print("  ✅ Gemini found window - using AI result")
                        return gemini_result
                    else:
                        print(f"  ⚠️ Gemini failed: {gemini_status}")
                except Exception as e:
                    error_msg = str(e)
                    if 'libGL' in error_msg or 'libGL.so' in error_msg:
                        print(f"  ⚠️ Gemini error (libGL): {error_msg}")
                    else:
                        print(f"  ⚠️ Gemini error: {error_msg}")
            except Exception as e:
                error_msg = str(e)
                if 'libGL' in error_msg or 'libGL.so' in error_msg:
                    print(f"  ⚠️ Gemini error (libGL): {error_msg}")
                else:
                    print(f"  ⚠️ Gemini error: {error_msg}")
        
        # Try enhanced OpenCV as fallback (FREE)
        if cv2 is not None:
            print("  3. AI methods didn't find window - trying enhanced OpenCV (FREE)...")
            opencv_result, window_found, error_msg = self.detect_windows_opencv(image_path, mask_save_path)
            
            if opencv_result and window_found:
                print("  ✅ Enhanced OpenCV found window - using result (FREE)")
                return opencv_result
            elif opencv_result:
                # OpenCV ran but didn't find window - use result anyway
                print("  📋 Using enhanced OpenCV result as final fallback")
                return opencv_result
            else:
                print(f"  ⚠️ OpenCV fallback failed: {error_msg}")
        else:
            print("  ⚠️ OpenCV not available (libGL.so.1 missing on Azure App Service)")
        
        # If all methods failed, create a simple fallback mask
        print("  ⚠️ All detection methods failed - creating fallback mask...")
        try:
            from PIL import Image as PILImage
            import numpy as np
            
            # Load image to get dimensions
            pil_image = PILImage.open(image_path)
            image_width, image_height = pil_image.size
            
            # Create a simple center rectangle mask
            mask = np.zeros((image_height, image_width), dtype=np.uint8)
            x1, y1 = image_width // 4, image_height // 4
            x2, y2 = 3 * image_width // 4, 3 * image_height // 4
            mask[y1:y2, x1:x2] = 255
            
            # Resize to 320x320
            mask_image = PILImage.fromarray(mask)
            mask_resized = mask_image.resize((320, 320), PILImage.LANCZOS)
            mask_resized.save(mask_save_path)
            
            print(f"  ✅ Fallback mask created and saved to {mask_save_path}")
            return mask_save_path
        except Exception as fallback_error:
            error_msg = f"All window detection methods failed and fallback mask creation also failed: {fallback_error}"
            print(f"  ❌ {error_msg}")
            raise Exception(error_msg) 