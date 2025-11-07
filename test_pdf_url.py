#!/usr/bin/env python3
"""
Test script for PDF reader MCP server with URL
"""
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import the functions directly from server module
# We need to import them before the @mcp.tool() decorator wraps them
import importlib.util
spec = importlib.util.spec_from_file_location("server_module", Path(__file__).parent / "src" / "server.py")
server_module = importlib.util.module_from_spec(spec)

# We'll call the functions through the mcp object's tool registry
# But actually, let's just import the raw functions by reading the source
# Or better: import the module and access the functions before decoration

# Actually, the simplest: import server and call the functions directly
# They should work even if decorated
import server

# Access the underlying functions from FastMCP FunctionTool wrappers
# FastMCP stores the function in the 'fn' attribute
read_pdf_text = server.read_pdf_text.fn
extract_pdf_images = server.extract_pdf_images.fn
read_pdf_with_ocr = server.read_pdf_with_ocr.fn
get_pdf_info = server.get_pdf_info.fn
analyze_pdf_structure = server.analyze_pdf_structure.fn

def test_pdf_url(url: str):
    """Test all PDF reader tools with a URL"""
    print("=" * 80)
    print(f"Testing PDF Reader MCP Server with URL:")
    print(f"{url}")
    print("=" * 80)
    
    # Test 1: Get PDF Info
    print("\n[1] Testing get_pdf_info...")
    try:
        result = get_pdf_info(url=url)
        if result.get("success"):
            print(f"OK Success! PDF has {result['document_stats']['total_pages']} pages")
            print(f"  Total images: {result['document_stats']['total_images']}")
            print(f"  File size: {result['file_info']['size_mb']} MB")
        else:
            print(f"X Failed: {result.get('error')}")
    except Exception as e:
        print(f"X Exception: {e}")
    
    # Test 2: Read PDF Text (first page only)
    print("\n[2] Testing read_pdf_text (first page)...")
    try:
        result = read_pdf_text(url=url, page_range={"start": 1, "end": 1})
        if result.get("success"):
            text = result.get("combined_text", "")
            print(f"OK Success! Extracted {len(text)} characters")
            print(f"  Preview: {text[:200]}...")
        else:
            print(f"X Failed: {result.get('error')}")
    except Exception as e:
        print(f"X Exception: {e}")
    
    # Test 3: Extract Images (first page, no analysis for speed)
    print("\n[3] Testing extract_pdf_images (first page, no analysis)...")
    try:
        result = extract_pdf_images(
            url=url,
            page_range={"start": 1, "end": 1},
            analyze_images=False
        )
        if result.get("success"):
            print(f"OK Success! Found {result['images_extracted']} images")
            if result['images_extracted'] > 0:
                img = result['images'][0]
                print(f"  First image: {img['width']}x{img['height']} pixels")
        else:
            print(f"X Failed: {result.get('error')}")
    except Exception as e:
        print(f"X Exception: {e}")
    
    # Test 4: Analyze PDF Structure
    print("\n[4] Testing analyze_pdf_structure...")
    try:
        result = analyze_pdf_structure(url=url)
        if result.get("success"):
            print(f"OK Success!")
            print(f"  Total pages: {result['document_structure']['total_pages']}")
            print(f"  Pages with text: {result['content_analysis']['pages_with_text']}")
            print(f"  Pages with images: {result['content_analysis']['pages_with_images']}")
        else:
            print(f"X Failed: {result.get('error')}")
    except Exception as e:
        print(f"X Exception: {e}")
    
    print("\n" + "=" * 80)
    print("Testing complete!")
    print("=" * 80)

if __name__ == "__main__":
    test_url = "https://canvas.instructure.com/files/12298~24243141/download?download_frd=1&verifier=1tnZYSNcH4OElgC1HWtM6C8rKmUlb03vamBFKOjS"
    test_pdf_url(test_url)

