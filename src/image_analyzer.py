#!/usr/bin/env python3
"""
Image analysis module for PDF reader MCP server.
Provides OCR, basic image analysis, and optional vision model support.
"""

import logging
import os
import platform
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pytesseract
from PIL import Image

logger = logging.getLogger("pdf-reader-server")


def _find_tesseract_executable() -> Optional[str]:
    """
    Automatically find Tesseract executable on Windows.
    Checks common installation locations and PATH.
    
    Returns:
        Path to tesseract.exe if found, None otherwise
    """
    # First, check if tesseract is in PATH
    tesseract_path = shutil.which("tesseract")
    if tesseract_path:
        return tesseract_path
    
    # On Windows, check common installation locations
    if platform.system() == "Windows":
        common_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(os.getenv("USERNAME", "")),
            r"C:\ProgramData\chocolatey\bin\tesseract.exe",
        ]
        
        # Also check Chocolatey lib directory
        choco_lib = os.getenv("ChocolateyInstall", r"C:\ProgramData\chocolatey")
        choco_lib_path = os.path.join(choco_lib, "lib")
        if os.path.exists(choco_lib_path):
            try:
                for item in os.listdir(choco_lib_path):
                    if "tesseract" in item.lower():
                        tesseract_candidate = os.path.join(choco_lib_path, item, "tools", "tesseract.exe")
                        if os.path.exists(tesseract_candidate):
                            common_paths.append(tesseract_candidate)
            except (OSError, PermissionError):
                # Ignore permission errors when scanning Chocolatey directory
                pass
        
        for path in common_paths:
            if os.path.exists(path):
                logger.info(f"Found Tesseract at: {path}")
                return path
    
    return None


# Auto-configure Tesseract path if not already set
if not pytesseract.pytesseract.tesseract_cmd:
    tesseract_path = _find_tesseract_executable()
    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        logger.info(f"Auto-configured Tesseract path: {tesseract_path}")
    else:
        logger.warning("Tesseract not found. OCR functionality will be disabled.")

# Optional vision model imports (will be None if not available)
try:
    from transformers import BlipProcessor, BlipForConditionalGeneration
    import torch
    VISION_MODEL_AVAILABLE = True
except ImportError:
    VISION_MODEL_AVAILABLE = False
    logger.info("Vision model dependencies not available. OCR-only mode will be used.")


def analyze_image_ocr(image_path: str, ocr_language: str = "eng") -> Dict[str, Any]:
    """
    Extract text from image using OCR.
    
    Args:
        image_path: Path to the image file
        ocr_language: OCR language code (default: 'eng')
    
    Returns:
        Dictionary with OCR results
    """
    # Ensure Tesseract is configured (fallback in case auto-detection didn't run)
    if not pytesseract.pytesseract.tesseract_cmd or not os.path.exists(pytesseract.pytesseract.tesseract_cmd):
        tesseract_path = _find_tesseract_executable()
        if tesseract_path and os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            logger.info(f"Configured Tesseract path in OCR function: {tesseract_path}")
        else:
            logger.warning("Tesseract not found. OCR will be skipped.")
            return {
                "ocr_text": "",
                "has_text": False,
                "error": "Tesseract not installed or not in PATH"
            }
    
    # Verify Tesseract is actually working by checking version
    try:
        pytesseract.get_tesseract_version()
    except Exception as e:
        # If version check fails, try to re-detect
        tesseract_path = _find_tesseract_executable()
        if tesseract_path and os.path.exists(tesseract_path):
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            logger.info(f"Re-configured Tesseract path after version check failed: {tesseract_path}")
            # Try version check again
            try:
                pytesseract.get_tesseract_version()
            except Exception as e2:
                logger.warning(f"Tesseract version check failed: {e2}. OCR will be skipped.")
                return {
                    "ocr_text": "",
                    "has_text": False,
                    "error": f"Tesseract not working: {e2}"
                }
        else:
            logger.warning(f"Tesseract not found after version check failed: {e}")
            return {
                "ocr_text": "",
                "has_text": False,
                "error": f"Tesseract not working: {e}"
            }
    
    try:
        with Image.open(image_path) as img:
            # Skip very small images
            if img.width < 50 or img.height < 50:
                return {
                    "ocr_text": "",
                    "has_text": False,
                    "error": "Image too small for OCR"
                }
            
            # Perform OCR
            ocr_text = pytesseract.image_to_string(
                img,
                lang=ocr_language,
                config='--psm 6'  # Uniform block of text
            ).strip()
            
            return {
                "ocr_text": ocr_text,
                "has_text": bool(ocr_text),
                "word_count": len(ocr_text.split()) if ocr_text else 0,
                "character_count": len(ocr_text)
            }
    except Exception as e:
        logger.warning(f"OCR failed for {image_path}: {e}")
        return {
            "ocr_text": "",
            "has_text": False,
            "error": str(e)
        }


def analyze_image_basic(image_path: str) -> Dict[str, Any]:
    """
    Analyze basic image metadata and properties.
    
    Args:
        image_path: Path to the image file
    
    Returns:
        Dictionary with basic image information
    """
    try:
        with Image.open(image_path) as img:
            # Get image format
            img_format = img.format or "unknown"
            
            # Get color mode
            color_mode = img.mode
            
            # Get dimensions
            width, height = img.size
            
            # Initialize variables
            avg_color = None
            dominant_color_type = "unknown"
            is_likely_text = False
            is_colorful = False
            brightness = None
            is_bright = False
            is_dark = False
            dominant_hue = "unknown"
            
            # Analyze color distribution (basic)
            try:
                # Convert to RGB if needed for consistent processing
                if img.mode != "RGB":
                    img_rgb = img.convert("RGB")
                else:
                    img_rgb = img
                
                img_array = np.array(img_rgb)
                
                # For RGB images, get detailed color stats
                if len(img_array.shape) == 3:
                    # Calculate average color
                    avg_color = img_array.mean(axis=(0, 1)).tolist()
                    
                    # Get dominant colors using k-means-like approach (simplified)
                    # Reshape to list of pixels
                    pixels = img_array.reshape(-1, img_array.shape[2])
                    # Sample pixels for faster processing
                    sample_size = min(10000, len(pixels))
                    sample_indices = np.random.choice(len(pixels), sample_size, replace=False)
                    sample_pixels = pixels[sample_indices]
                    
                    # Calculate color variance to determine if image is colorful or monochromatic
                    color_variance = float(sample_pixels.std(axis=0).mean())
                    is_colorful = color_variance > 30
                    
                    # Get brightness
                    brightness = float(sample_pixels.mean())
                    is_bright = brightness > 180
                    is_dark = brightness < 75
                    
                    if img_array.shape[2] == 3:  # RGB
                        dominant_color_type = "color"
                        # Estimate dominant hue
                        hsv_pixels = sample_pixels.astype(np.float32) / 255.0
                        # Simple hue estimation (not true HSV, but good enough)
                        max_channel = np.argmax(hsv_pixels, axis=1)
                        red_dominant = np.sum(max_channel == 0) / len(max_channel)
                        green_dominant = np.sum(max_channel == 1) / len(max_channel)
                        blue_dominant = np.sum(max_channel == 2) / len(max_channel)
                        
                        dominant_hue = "red" if red_dominant > 0.4 else ("green" if green_dominant > 0.4 else ("blue" if blue_dominant > 0.4 else "mixed"))
                    elif img_array.shape[2] == 4:  # RGBA
                        dominant_color_type = "color_with_alpha"
                        dominant_hue = "mixed"
                    else:
                        dominant_color_type = "unknown"
                        dominant_hue = "unknown"
                else:  # Grayscale
                    avg_color = [float(img_array.mean())]
                    dominant_color_type = "grayscale"
                    is_colorful = False
                    brightness = float(img_array.mean())
                    is_bright = brightness > 180
                    is_dark = brightness < 75
                    dominant_hue = "grayscale"
                
                # Estimate if image is mostly text (high contrast, mostly black/white)
                if len(img_array.shape) == 2 or (len(img_array.shape) == 3 and img_array.shape[2] == 1):
                    # Grayscale
                    contrast = float(img_array.std())
                    is_likely_text = bool(contrast > 50 and float(img_array.mean()) < 128)
                else:
                    # Color - convert to grayscale for analysis
                    gray = np.dot(img_array[...,:3], [0.2989, 0.5870, 0.1140])
                    contrast = float(gray.std())
                    is_likely_text = bool(contrast > 50 and float(gray.mean()) < 128)
                
            except Exception as e:
                logger.warning(f"Error analyzing image colors: {e}")
                if avg_color is None:
                    avg_color = None
                if dominant_color_type == "unknown":
                    dominant_color_type = "unknown"
            
            # Get file size
            file_size = Path(image_path).stat().st_size
            
            result = {
                "dimensions": {
                    "width": width,
                    "height": height
                },
                "format": img_format,
                "color_mode": color_mode,
                "file_size_bytes": file_size,
                "file_size_kb": round(file_size / 1024, 2),
                "aspect_ratio": round(width / height, 2) if height > 0 else 0,
                "is_likely_text": is_likely_text,
                "dominant_color_type": dominant_color_type,
                "average_color_rgb": [int(c) for c in avg_color] if avg_color else None,
                "is_colorful": bool(is_colorful),
                "brightness": round(brightness, 1) if brightness is not None else None,
                "is_bright": bool(is_bright),
                "is_dark": bool(is_dark),
                "dominant_hue": dominant_hue
            }
            
            return result
            
    except Exception as e:
        logger.error(f"Error analyzing image basic info: {e}")
        return {
            "error": str(e)
        }


# Global variables for vision model (lazy loading)
_vision_processor = None
_vision_model = None
_vision_model_loaded = False


def load_vision_model(model_name: str = "Salesforce/blip-image-captioning-base") -> bool:
    """
    Load vision model for image captioning.
    
    Args:
        model_name: Name of the vision model to load
    
    Returns:
        True if model loaded successfully, False otherwise
    """
    global _vision_processor, _vision_model, _vision_model_loaded
    
    if not VISION_MODEL_AVAILABLE:
        logger.warning("Vision model dependencies not available")
        return False
    
    if _vision_model_loaded:
        return True
    
    try:
        logger.info(f"Loading vision model: {model_name}")
        _vision_processor = BlipProcessor.from_pretrained(model_name)
        _vision_model = BlipForConditionalGeneration.from_pretrained(model_name)
        
        # Use CPU by default (can be changed to GPU if available)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _vision_model.to(device)
        _vision_model.eval()
        
        _vision_model_loaded = True
        logger.info(f"Vision model loaded successfully on {device}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to load vision model: {e}")
        return False


def analyze_image_vision(image_path: str, model_name: str = "Salesforce/blip-image-captioning-base") -> Dict[str, Any]:
    """
    Generate natural language description of image using vision model.
    
    Args:
        image_path: Path to the image file
        model_name: Name of the vision model to use
    
    Returns:
        Dictionary with vision model description
    """
    if not load_vision_model(model_name):
        return {
            "vision_description": "",
            "error": "Vision model not available"
        }
    
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if needed
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            # Process image
            inputs = _vision_processor(img, return_tensors="pt")
            
            # Generate caption
            device = "cuda" if torch.cuda.is_available() else "cpu"
            inputs = {k: v.to(device) for k, v in inputs.items()}
            
            with torch.no_grad():
                # Generate longer, more detailed captions
                out = _vision_model.generate(
                    **inputs, 
                    max_length=100,  # Increased for more detailed descriptions
                    num_beams=3,  # Better quality captions
                    early_stopping=True
                )
            
            caption = _vision_processor.decode(out[0], skip_special_tokens=True)
            
            return {
                "vision_description": caption,
                "has_description": bool(caption),
                "model_used": model_name
            }
            
    except Exception as e:
        logger.error(f"Vision model analysis failed for {image_path}: {e}")
        return {
            "vision_description": "",
            "error": str(e)
        }


def analyze_image_hybrid(
    image_path: str,
    use_vision: bool = False,
    ocr_language: str = "eng",
    vision_model_name: str = "Salesforce/blip-image-captioning-base"
) -> Dict[str, Any]:
    """
    Perform hybrid image analysis combining OCR, basic analysis, and optional vision model.
    
    Args:
        image_path: Path to the image file
        use_vision: Whether to use vision model for description
        ocr_language: OCR language code
        vision_model_name: Name of vision model to use
    
    Returns:
        Dictionary with complete analysis results
    """
    # Run OCR
    ocr_result = analyze_image_ocr(image_path, ocr_language)
    
    # Run basic analysis
    basic_info = analyze_image_basic(image_path)
    
    # Run vision model if requested
    vision_result = {}
    if use_vision:
        vision_result = analyze_image_vision(image_path, vision_model_name)
    
    # Combine into natural language description (detailed, like direct image upload)
    description_parts = []
    
    # Start with visual characteristics
    if "dimensions" in basic_info:
        dims = basic_info["dimensions"]
        aspect_ratio = basic_info.get("aspect_ratio", 0)
        if aspect_ratio > 2.0:
            orientation_desc = "wide, panoramic"
        elif aspect_ratio < 0.6:
            orientation_desc = "tall, portrait-oriented"
        else:
            orientation_desc = "standard"
        description_parts.append(f"This is a {orientation_desc} image ({dims['width']}x{dims['height']} pixels)")
    
    # Add color and visual characteristics
    if "dominant_hue" in basic_info and basic_info["dominant_hue"] != "unknown":
        hue = basic_info["dominant_hue"]
        if hue != "grayscale" and hue != "mixed":
            description_parts.append(f"The image has a {hue}-dominant color palette")
        elif hue == "grayscale":
            description_parts.append("The image is grayscale")
    
    if "is_colorful" in basic_info:
        if basic_info["is_colorful"]:
            description_parts.append("The image is colorful with varied hues")
        else:
            description_parts.append("The image has a more monochromatic or muted color scheme")
    
    if "brightness" in basic_info and basic_info["brightness"] is not None:
        brightness = basic_info["brightness"]
        if basic_info.get("is_bright", False):
            description_parts.append("The image is bright and well-lit")
        elif basic_info.get("is_dark", False):
            description_parts.append("The image is dark or dimly lit")
        else:
            description_parts.append(f"The image has moderate brightness (average: {brightness:.0f}/255)")
    
    # Add content type analysis
    if basic_info.get("is_likely_text", False):
        description_parts.append("The image appears to contain primarily text content")
    else:
        description_parts.append("The image appears to be a visual/graphical element rather than text-based")
    
    # Add OCR text if found
    if ocr_result.get("has_text"):
        ocr_text = ocr_result.get("ocr_text", "")
        if ocr_text:
            # Truncate long OCR text in description
            if len(ocr_text) > 200:
                ocr_preview = ocr_text[:200] + "..."
            else:
                ocr_preview = ocr_text
            description_parts.append(f"The image contains the following text: \"{ocr_preview}\"")
    
    # Add vision model description if available (this is the key part for detailed content description)
    if use_vision and vision_result.get("has_description"):
        vision_desc = vision_result.get("vision_description", "")
        if vision_desc:
            description_parts.append(f"Content description: {vision_desc}")
    elif use_vision and vision_result.get("error"):
        # Vision model failed, but we tried
        description_parts.append("(Vision model analysis was requested but unavailable)")
    
    # Combine all parts into a natural flowing description
    if description_parts:
        description = ". ".join(description_parts) + "."
    else:
        description = "Image analysis completed. This appears to be a visual image with the dimensions and color characteristics described above."
    
    return {
        "ocr_text": ocr_result.get("ocr_text", ""),
        "basic_info": basic_info,
        "vision_description": vision_result.get("vision_description", "") if use_vision else None,
        "description": description,
        "analysis_summary": {
            "has_text": ocr_result.get("has_text", False),
            "has_vision_description": vision_result.get("has_description", False) if use_vision else False,
            "is_likely_text": basic_info.get("is_likely_text", False)
        }
    }

