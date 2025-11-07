#!/usr/bin/env python3

import json
import logging
import os
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import fitz  # PyMuPDF
import httpx
import pytesseract
from fastmcp import FastMCP
from PIL import Image

try:
    from .image_analyzer import analyze_image_hybrid
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from image_analyzer import analyze_image_hybrid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pdf-reader-server")

# Initialize FastMCP server
mcp = FastMCP("PDF Reader Server")

def download_pdf_from_url(url: str) -> bytes:
    """Download PDF from URL and return as bytes (synchronous)"""
    try:
        # Follow redirects (max 10 redirects)
        with httpx.Client(timeout=30.0, follow_redirects=True, max_redirects=10) as client:
            response = client.get(url)
            response.raise_for_status()
            
            # Validate content type
            content_type = response.headers.get("content-type", "").lower()
            if "pdf" not in content_type and not url.lower().endswith(".pdf"):
                logger.warning(f"URL may not be a PDF (Content-Type: {content_type})")
            
            return response.content
    except httpx.HTTPStatusError as e:
        raise Exception(f"HTTP error downloading PDF: {e.response.status_code} - {e.response.text}")
    except httpx.RequestError as e:
        raise Exception(f"Request error downloading PDF: {str(e)}")
    except Exception as e:
        raise Exception(f"Error downloading PDF from URL: {str(e)}")

def get_pdf_path_or_download(file_path: Optional[str] = None, url: Optional[str] = None) -> Tuple[Path, bool]:
    """
    Get PDF path from file_path or download from URL.
    Returns tuple of (path, is_temp_file)
    """
    if file_path and url:
        raise ValueError("Cannot specify both file_path and url. Use one or the other.")
    
    if url:
        # Download PDF and save to temp file (synchronous)
        pdf_bytes = download_pdf_from_url(url)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file.write(pdf_bytes)
        temp_file.close()
        return Path(temp_file.name), True
    elif file_path:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        if not path.suffix.lower() == '.pdf':
            raise ValueError(f"File is not a PDF: {file_path}")
        return path, False
    else:
        raise ValueError("Either file_path or url must be provided")

def validate_file_path(file_path: str) -> Path:
    """Validate that the file path exists and is a PDF"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    if not path.suffix.lower() == '.pdf':
        raise ValueError(f"File is not a PDF: {file_path}")
    return path

def get_page_range(doc: fitz.Document, page_range: Optional[Dict] = None) -> Tuple[int, int]:
    """Get validated page range for the document"""
    total_pages = len(doc)
    
    if page_range is None:
        return 0, total_pages - 1
    
    start = page_range.get('start', 1) - 1  # Convert to 0-based indexing
    end = page_range.get('end', total_pages) - 1
    
    start = max(0, min(start, total_pages - 1))
    end = max(start, min(end, total_pages - 1))
    
    return start, end

@mcp.tool()
def read_pdf_text(file_path: Optional[str] = None, url: Optional[str] = None, page_range: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Extract text content from a PDF file
    
    Args:
        file_path: Path to the PDF file to read (optional if url is provided)
        url: URL to download PDF from (optional if file_path is provided)
        page_range: Optional dict with 'start' and 'end' page numbers (1-indexed)
    
    Returns:
        Dictionary containing extracted text and metadata
    """
    temp_file = None
    try:
        path, is_temp = get_pdf_path_or_download(file_path, url)
        temp_file = path if is_temp else None
        
        with fitz.open(str(path)) as doc:
            start_page, end_page = get_page_range(doc, page_range)
            
            pages_text = []
            total_text = ""
            
            for page_num in range(start_page, end_page + 1):
                page = doc[page_num]
                page_text = page.get_text()
                pages_text.append({
                    "page_number": page_num + 1,
                    "text": page_text,
                    "word_count": len(page_text.split())
                })
                total_text += page_text + "\n"
            
            result = {
                "success": True,
                "file_path": str(path) if not is_temp else None,
                "url": url if url else None,
                "pages_processed": f"{start_page + 1}-{end_page + 1}",
                "total_pages": len(doc),
                "pages_text": pages_text,
                "combined_text": total_text.strip(),
                "total_word_count": len(total_text.split()),
                "total_character_count": len(total_text)
            }
            
            # Clean up temp file if created
            if temp_file and temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup temp file: {cleanup_error}")
            
            return result
            
    except Exception as e:
        logger.error(f"Error reading PDF text: {e}")
        # Clean up temp file on error
        if temp_file and temp_file.exists():
            try:
                temp_file.unlink()
            except:
                pass
        return {
            "success": False,
            "error": str(e),
            "file_path": file_path,
            "url": url if url else None
        }

@mcp.tool()
def extract_pdf_images(
    file_path: Optional[str] = None,
    url: Optional[str] = None,
    output_dir: Optional[str] = None,
    page_range: Optional[Dict] = None,
    analyze_images: bool = True,
    use_vision_model: bool = True,
    ocr_language: str = "eng"
) -> Dict[str, Any]:
    """
    Extract all images from a PDF file with optional image analysis
    
    Args:
        file_path: Path to the PDF file (optional if url is provided)
        url: URL to download PDF from (optional if file_path is provided)
        output_dir: Directory to save extracted images (optional, defaults to temp dir)
        page_range: Optional dict with 'start' and 'end' page numbers (1-indexed)
        analyze_images: Whether to analyze extracted images (default: True)
        use_vision_model: Whether to use vision model for image descriptions (default: True)
        ocr_language: OCR language code for text extraction from images (default: 'eng')
    
    Returns:
        Dictionary containing information about extracted images with analysis
    """
    temp_file = None
    try:
        path, is_temp = get_pdf_path_or_download(file_path, url)
        temp_file = path if is_temp else None
        
        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix="pdf_images_")
        else:
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        extracted_images = []
        
        with fitz.open(str(path)) as doc:
            start_page, end_page = get_page_range(doc, page_range)
            
            for page_num in range(start_page, end_page + 1):
                page = doc[page_num]
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    try:
                        # Get image data
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        # Skip if image is too small or has alpha channel issues
                        if pix.width < 10 or pix.height < 10:
                            pix = None
                            continue
                        
                        # Convert to PNG if needed
                        if pix.n - pix.alpha < 4:  # GRAY or RGB
                            img_data = pix.tobytes("png")
                        else:  # CMYK: convert to RGB first
                            pix1 = fitz.Pixmap(fitz.csRGB, pix)
                            img_data = pix1.tobytes("png")
                            pix1 = None
                        
                        # Save image
                        img_filename = f"page_{page_num + 1}_img_{img_index + 1}.png"
                        img_path = Path(output_dir) / img_filename
                        
                        with open(img_path, "wb") as img_file:
                            img_file.write(img_data)
                        
                        image_info = {
                            "page_number": page_num + 1,
                            "image_index": img_index + 1,
                            "filename": img_filename,
                            "path": str(img_path),
                            "width": pix.width,
                            "height": pix.height,
                            "size_bytes": len(img_data)
                        }
                        
                        # Analyze image if requested
                        if analyze_images:
                            try:
                                analysis = analyze_image_hybrid(
                                    str(img_path),
                                    use_vision=use_vision_model,
                                    ocr_language=ocr_language
                                )
                                image_info["analysis"] = analysis
                                image_info["description"] = analysis.get("description", "")
                            except Exception as analysis_error:
                                logger.warning(f"Image analysis failed for {img_path}: {analysis_error}")
                                image_info["analysis"] = {
                                    "error": str(analysis_error)
                                }
                                image_info["description"] = f"Image analysis failed: {str(analysis_error)}"
                        
                        extracted_images.append(image_info)
                        
                        pix = None
                        
                    except Exception as img_error:
                        logger.warning(f"Failed to extract image {img_index + 1} from page {page_num + 1}: {img_error}")
                        continue
        
        # Calculate summary statistics
        images_with_text = sum(1 for img in extracted_images if img.get("analysis", {}).get("analysis_summary", {}).get("has_text", False))
        images_analyzed = sum(1 for img in extracted_images if "analysis" in img)
        
        result = {
            "success": True,
            "file_path": str(path) if not is_temp else None,
            "url": url if url else None,
            "output_directory": output_dir,
            "pages_processed": f"{start_page + 1}-{end_page + 1}",
            "images_extracted": len(extracted_images),
            "images": extracted_images,
            "summary": {
                "total_images": len(extracted_images),
                "images_with_text": images_with_text,
                "images_analyzed": images_analyzed
            }
        }
        
        # Clean up temp file if created
        if temp_file and temp_file.exists():
            try:
                temp_file.unlink()
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temp file: {cleanup_error}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error extracting PDF images: {e}")
        # Clean up temp file on error
        if temp_file and temp_file.exists():
            try:
                temp_file.unlink()
            except:
                pass
        return {
            "success": False,
            "error": str(e),
            "file_path": file_path,
            "url": url if url else None
        }

@mcp.tool()
def read_pdf_with_ocr(file_path: Optional[str] = None, url: Optional[str] = None, page_range: Optional[Dict] = None, ocr_language: str = "eng") -> Dict[str, Any]:
    """
    Extract text from PDF including OCR text from images
    
    Args:
        file_path: Path to the PDF file (optional if url is provided)
        url: URL to download PDF from (optional if file_path is provided)
        page_range: Optional dict with 'start' and 'end' page numbers (1-indexed)
        ocr_language: OCR language code (default: 'eng')
    
    Returns:
        Dictionary containing extracted text from both text and images
    """
    temp_file = None
    try:
        path, is_temp = get_pdf_path_or_download(file_path, url)
        temp_file = path if is_temp else None
        
        with fitz.open(str(path)) as doc:
            start_page, end_page = get_page_range(doc, page_range)
            
            pages_data = []
            total_text = ""
            total_ocr_text = ""
            
            for page_num in range(start_page, end_page + 1):
                page = doc[page_num]
                
                # Extract regular text
                page_text = page.get_text()
                
                # Extract and OCR images
                image_texts = []
                image_list = page.get_images()
                
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        # Skip very small images
                        if pix.width < 50 or pix.height < 50:
                            pix = None
                            continue
                        
                        # Convert to PIL Image for OCR
                        if pix.n - pix.alpha < 4:  # GRAY or RGB
                            img_data = pix.tobytes("png")
                        else:  # CMYK: convert to RGB first
                            pix1 = fitz.Pixmap(fitz.csRGB, pix)
                            img_data = pix1.tobytes("png")
                            pix1 = None
                        
                        # Perform OCR
                        with Image.open(BytesIO(img_data)) as pil_image:
                            ocr_text = pytesseract.image_to_string(
                                pil_image, 
                                lang=ocr_language,
                                config='--psm 6'  # Uniform block of text
                            ).strip()
                            
                            if ocr_text:
                                image_texts.append({
                                    "image_index": img_index + 1,
                                    "ocr_text": ocr_text,
                                    "confidence": "high" if len(ocr_text) > 10 else "low"
                                })
                        
                        pix = None
                        
                    except Exception as ocr_error:
                        logger.warning(f"OCR failed for image {img_index + 1} on page {page_num + 1}: {ocr_error}")
                        continue
                
                # Combine all OCR text from this page
                page_ocr_text = "\n".join([img["ocr_text"] for img in image_texts])
                
                page_data = {
                    "page_number": page_num + 1,
                    "text": page_text,
                    "ocr_text": page_ocr_text,
                    "images_with_text": image_texts,
                    "combined_text": f"{page_text}\n{page_ocr_text}".strip(),
                    "text_word_count": len(page_text.split()),
                    "ocr_word_count": len(page_ocr_text.split())
                }
                
                pages_data.append(page_data)
                total_text += page_text + "\n"
                total_ocr_text += page_ocr_text + "\n"
            
            combined_all_text = f"{total_text}\n{total_ocr_text}".strip()
            
            result = {
                "success": True,
                "file_path": str(path) if not is_temp else None,
                "url": url if url else None,
                "pages_processed": f"{start_page + 1}-{end_page + 1}",
                "total_pages": len(doc),
                "ocr_language": ocr_language,
                "pages_data": pages_data,
                "summary": {
                    "total_text_word_count": len(total_text.split()),
                    "total_ocr_word_count": len(total_ocr_text.split()),
                    "combined_word_count": len(combined_all_text.split()),
                    "combined_character_count": len(combined_all_text),
                    "images_processed": sum(len(p["images_with_text"]) for p in pages_data)
                },
                "combined_text": total_text.strip(),
                "combined_ocr_text": total_ocr_text.strip(),
                "all_text_combined": combined_all_text
            }
            
            # Clean up temp file if created
            if temp_file and temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup temp file: {cleanup_error}")
            
            return result
            
    except Exception as e:
        logger.error(f"Error reading PDF with OCR: {e}")
        # Clean up temp file on error
        if temp_file and temp_file.exists():
            try:
                temp_file.unlink()
            except:
                pass
        return {
            "success": False,
            "error": str(e),
            "file_path": file_path,
            "url": url if url else None
        }

@mcp.tool()
def get_pdf_info(file_path: Optional[str] = None, url: Optional[str] = None) -> Dict[str, Any]:
    """
    Get metadata and information about a PDF file
    
    Args:
        file_path: Path to the PDF file (optional if url is provided)
        url: URL to download PDF from (optional if file_path is provided)
    
    Returns:
        Dictionary containing PDF metadata and statistics
    """
    temp_file = None
    try:
        path, is_temp = get_pdf_path_or_download(file_path, url)
        temp_file = path if is_temp else None
        
        with fitz.open(str(path)) as doc:
            # Get basic document info
            metadata = doc.metadata
            
            # Count images across all pages
            total_images = 0
            page_info = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                images_on_page = len(page.get_images())
                total_images += images_on_page
                
                page_info.append({
                    "page_number": page_num + 1,
                    "images_count": images_on_page,
                    "text_length": len(page.get_text()),
                    "has_text": bool(page.get_text().strip()),
                    "page_width": page.rect.width,
                    "page_height": page.rect.height
                })
            
            file_stats = path.stat()
            
            result = {
                "success": True,
                "file_path": str(path) if not is_temp else None,
                "url": url if url else None,
                "file_info": {
                    "size_bytes": file_stats.st_size,
                    "size_mb": round(file_stats.st_size / (1024 * 1024), 2),
                    "created": file_stats.st_ctime,
                    "modified": file_stats.st_mtime
                },
                "pdf_metadata": {
                    "title": metadata.get("title", ""),
                    "author": metadata.get("author", ""),
                    "subject": metadata.get("subject", ""),
                    "creator": metadata.get("creator", ""),
                    "producer": metadata.get("producer", ""),
                    "creation_date": metadata.get("creationDate", ""),
                    "modification_date": metadata.get("modDate", "")
                },
                "document_stats": {
                    "total_pages": len(doc),
                    "total_images": total_images,
                    "pages_with_text": sum(1 for p in page_info if p["has_text"]),
                    "pages_with_images": sum(1 for p in page_info if p["images_count"] > 0),
                    "is_encrypted": doc.needs_pass,
                    "can_extract_text": not doc.is_closed
                },
                "page_details": page_info
            }
        
        # Clean up temp file if created (after document is closed)
        if temp_file and temp_file.exists():
            try:
                import time
                time.sleep(0.1)  # Brief delay to ensure file is released
                temp_file.unlink()
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup temp file: {cleanup_error}")
        
        return result
            
    except Exception as e:
        logger.error(f"Error getting PDF info: {e}")
        # Clean up temp file on error
        if temp_file and temp_file.exists():
            try:
                temp_file.unlink()
            except:
                pass
        return {
            "success": False,
            "error": str(e),
            "file_path": file_path,
            "url": url if url else None
        }

@mcp.tool()
def analyze_pdf_structure(file_path: Optional[str] = None, url: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze PDF structure including pages, images, and text blocks
    
    Args:
        file_path: Path to the PDF file (optional if url is provided)
        url: URL to download PDF from (optional if file_path is provided)
    
    Returns:
        Dictionary containing detailed structural analysis
    """
    temp_file = None
    try:
        path, is_temp = get_pdf_path_or_download(file_path, url)
        temp_file = path if is_temp else None
        
        with fitz.open(str(path)) as doc:
            structure_analysis = {
                "document_structure": {
                    "total_pages": len(doc),
                    "is_encrypted": doc.needs_pass,
                    "pdf_version": doc.pdf_version() if hasattr(doc, 'pdf_version') else "unknown"
                },
                "content_analysis": {
                    "pages_with_text": 0,
                    "pages_with_images": 0,
                    "pages_text_only": 0,
                    "pages_images_only": 0,
                    "pages_mixed_content": 0,
                    "total_text_blocks": 0,
                    "total_images": 0
                },
                "page_details": []
            }
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Get text blocks
                text_blocks = page.get_text("dict")["blocks"]
                text_block_count = len([block for block in text_blocks if "lines" in block])
                
                # Get images
                images = page.get_images()
                image_count = len(images)
                
                # Get text
                page_text = page.get_text().strip()
                has_text = bool(page_text)
                has_images = image_count > 0
                
                # Categorize page content
                if has_text and has_images:
                    content_type = "mixed"
                    structure_analysis["content_analysis"]["pages_mixed_content"] += 1
                elif has_text:
                    content_type = "text_only"
                    structure_analysis["content_analysis"]["pages_text_only"] += 1
                elif has_images:
                    content_type = "images_only"
                    structure_analysis["content_analysis"]["pages_images_only"] += 1
                else:
                    content_type = "empty"
                
                if has_text:
                    structure_analysis["content_analysis"]["pages_with_text"] += 1
                if has_images:
                    structure_analysis["content_analysis"]["pages_with_images"] += 1
                
                structure_analysis["content_analysis"]["total_text_blocks"] += text_block_count
                structure_analysis["content_analysis"]["total_images"] += image_count
                
                page_detail = {
                    "page_number": page_num + 1,
                    "content_type": content_type,
                    "text_blocks": text_block_count,
                    "image_count": image_count,
                    "text_length": len(page_text),
                    "dimensions": {
                        "width": page.rect.width,
                        "height": page.rect.height
                    },
                    "rotation": page.rotation
                }
                
                structure_analysis["page_details"].append(page_detail)
            
            # Add summary statistics
            structure_analysis["summary"] = {
                "content_distribution": {
                    "text_only_pages": structure_analysis["content_analysis"]["pages_text_only"],
                    "images_only_pages": structure_analysis["content_analysis"]["pages_images_only"],
                    "mixed_content_pages": structure_analysis["content_analysis"]["pages_mixed_content"],
                    "empty_pages": len(doc) - sum([
                        structure_analysis["content_analysis"]["pages_text_only"],
                        structure_analysis["content_analysis"]["pages_images_only"],
                        structure_analysis["content_analysis"]["pages_mixed_content"]
                    ])
                },
                "avg_images_per_page": round(structure_analysis["content_analysis"]["total_images"] / len(doc), 2),
                "avg_text_blocks_per_page": round(structure_analysis["content_analysis"]["total_text_blocks"] / len(doc), 2)
            }
            
            result = {
                "success": True,
                "file_path": str(path) if not is_temp else None,
                "url": url if url else None,
                **structure_analysis
            }
            
            # Clean up temp file if created
            if temp_file and temp_file.exists():
                try:
                    temp_file.unlink()
                except Exception as cleanup_error:
                    logger.warning(f"Failed to cleanup temp file: {cleanup_error}")
            
            return result
            
    except Exception as e:
        logger.error(f"Error analyzing PDF structure: {e}")
        # Clean up temp file on error
        if temp_file and temp_file.exists():
            try:
                temp_file.unlink()
            except:
                pass
        return {
            "success": False,
            "error": str(e),
            "file_path": file_path,
            "url": url if url else None
        }

if __name__ == "__main__":
    mcp.run()