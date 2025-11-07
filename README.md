# MCP PDF Reader Server

A powerful Model Context Protocol (MCP) server built with FastMCP that provides comprehensive PDF processing capabilities including text extraction, image extraction, OCR, and intelligent image analysis with natural language descriptions.

## Quick Start (Terminal Agent Prompts)

Use these prompts with a terminal agent (like Claude Code) to automatically set up the PDF Reader MCP server:

### Windows Setup Prompt

```markdown
I need to set up the PDF Reader MCP server. Please:

1. Clone the repository: git clone https://github.com/braedojabber/bestpdfmcp.git && cd bestpdfmcp
2. Build the Docker image: docker build -t mcp-pdf-reader-server .
3. Verify the image: docker images | grep mcp-pdf-reader-server
4. Configure Claude Code: claude mcp add --transport stdio --scope user pdf-reader -- node "C:\Users\Braedn Heney\Desktop\mcp-servers\mcp_pdf_reader\pdf-reader-docker-bridge.js"
5. Configure Claude Desktop: Edit %APPDATA%\Claude\claude_desktop_config.json and add:
   {
     "mcpServers": {
       "pdf-reader": {
         "command": "node",
         "args": ["C:\\Users\\Braedn Heney\\Desktop\\mcp-servers\\mcp_pdf_reader\\pdf-reader-docker-bridge.js"],
         "env": {}
       }
     }
   }
6. Configure Cursor: Edit %USERPROFILE%\.cursor\mcp.json and add:
   {
     "mcpServers": {
       "pdf-reader": {
         "command": "node",
         "args": ["C:\\Users\\Braedn Heney\\Desktop\\mcp-servers\\mcp_pdf_reader\\pdf-reader-docker-bridge.js"],
         "env": {}
       }
     }
   }
7. Verify: claude mcp list

Replace paths with actual locations. Docker Desktop and Node.js are installed.
```

### Mac Setup Prompt

```markdown
I need to set up the PDF Reader MCP server. Please:

1. Clone the repository: git clone https://github.com/braedojabber/bestpdfmcp.git && cd bestpdfmcp
2. Build the Docker image: docker build -t mcp-pdf-reader-server .
3. Verify the image: docker images | grep mcp-pdf-reader-server
4. Get absolute path: cd mcp_pdf_reader && realpath pdf-reader-docker-bridge.js
5. Configure Claude Code: claude mcp add --transport stdio --scope user pdf-reader -- node "[ABSOLUTE_PATH]"
6. Configure Claude Desktop: Edit ~/Library/Application Support/Claude/claude_desktop_config.json and add:
   {
     "mcpServers": {
       "pdf-reader": {
         "command": "node",
         "args": ["[ABSOLUTE_PATH]"],
         "env": {}
       }
     }
   }
7. Configure Cursor: Edit ~/.cursor/mcp.json and add:
   {
     "mcpServers": {
       "pdf-reader": {
         "command": "node",
         "args": ["[ABSOLUTE_PATH]"],
         "env": {}
       }
     }
   }
8. Verify: claude mcp list

Replace [ABSOLUTE_PATH] with the actual path from step 4. Docker Desktop and Node.js are installed.
```

### Linux Setup Prompt

```markdown
I need to set up the PDF Reader MCP server. Please:

1. Clone the repository: git clone https://github.com/braedojabber/bestpdfmcp.git && cd bestpdfmcp
2. Build the Docker image: docker build -t mcp-pdf-reader-server .
3. Verify the image: docker images | grep mcp-pdf-reader-server
4. Get absolute path: cd mcp_pdf_reader && realpath pdf-reader-docker-bridge.js
5. Configure Claude Code: claude mcp add --transport stdio --scope user pdf-reader -- node "[ABSOLUTE_PATH]"
6. Configure Claude Desktop: Edit ~/.config/Claude/claude_desktop_config.json and add:
   {
     "mcpServers": {
       "pdf-reader": {
         "command": "node",
         "args": ["[ABSOLUTE_PATH]"],
         "env": {}
       }
     }
   }
7. Configure Cursor: Edit ~/.cursor/mcp.json and add:
   {
     "mcpServers": {
       "pdf-reader": {
         "command": "node",
         "args": ["[ABSOLUTE_PATH]"],
         "env": {}
       }
     }
   }
8. Verify: claude mcp list

Replace [ABSOLUTE_PATH] with the actual path from step 4. Docker and Node.js are installed.
```

## Features

- **Text Extraction**: Extract text content from PDF pages
- **Image Extraction**: Extract all images from PDF files with intelligent analysis
- **OCR Capabilities**: Read text from images using Tesseract OCR (open source)
- **Image Analysis**: Analyze images with OCR, basic metadata, and optional vision model descriptions
- **URL Support**: Process PDFs from URLs in addition to local files
- **Comprehensive Analysis**: Get detailed PDF structure and metadata
- **Page Range Support**: Process specific page ranges
- **Multiple Languages**: OCR support for multiple languages
- **Configurable Vision Models**: Optional support for vision models (BLIP) for image descriptions

## Prerequisites

- **Docker Desktop** installed and running (recommended)
- **Node.js** installed (for the bridge script)
- **Claude Code**, **Claude Desktop**, or **Cursor** IDE

**Note:** With Docker, you don't need to install Python, Tesseract OCR, or any Python dependencies manually. Everything is included in the Docker image.

## Installation

### Docker (Recommended)

The easiest and most reliable way to run the PDF reader server is using Docker. The Docker image includes:
- Python 3.12
- Tesseract OCR with English language pack
- All Python dependencies (PyMuPDF, pytesseract, Pillow, transformers, torch, etc.)
- Vision model support (BLIP)

#### Step 1: Build the Docker Image

```bash
cd mcp_pdf_reader
docker build -t mcp-pdf-reader-server .
```

This will take several minutes the first time as it downloads all dependencies (~12.5GB image size).

#### Step 2: Verify the Image

```bash
docker images | grep mcp-pdf-reader-server
```

You should see the image listed.

#### Step 3: Test the Container

```bash
docker run --rm -i mcp-pdf-reader-server python -c "from src.server import mcp; print('OK')"
```

This should print "OK" if everything is working.

### Manual Setup (Alternative)

If you prefer not to use Docker, you can set up the server manually. See [Manual Setup Guide](#manual-setup-alternative) below.

## MCP Client Configuration

The PDF Reader MCP server uses **stdio transport** (not HTTP), so it requires a bridge script to run in Docker. The bridge script (`pdf-reader-docker-bridge.js`) handles communication between your MCP client and the Docker container.

### For Claude Code

**Quick Setup (CLI - Recommended):**

```bash
# Get the absolute path to the bridge script
cd mcp_pdf_reader
realpath pdf-reader-docker-bridge.js  # Mac/Linux
# or
Resolve-Path pdf-reader-docker-bridge.js  # Windows PowerShell

# Add the MCP server (replace [ABSOLUTE_PATH] with the path from above)
claude mcp add --transport stdio --scope user pdf-reader -- node "[ABSOLUTE_PATH]"

# Verify connection
claude mcp list
```

**Manual Configuration:**

Edit `~/.claude.json` (Mac/Linux) or `%USERPROFILE%\.claude.json` (Windows):

```json
{
  "mcpServers": {
    "pdf-reader": {
      "type": "stdio",
      "command": "node",
      "args": [
        "/full/path/to/mcp_pdf_reader/pdf-reader-docker-bridge.js"
      ],
      "env": {}
    }
  }
}
```

**See [docs/CLAUDE_CODE_SETUP.md](./docs/CLAUDE_CODE_SETUP.md) for detailed instructions.**

### For Claude Desktop

**Windows:**
Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pdf-reader": {
      "command": "node",
      "args": [
        "C:\\Users\\YourName\\Desktop\\mcp-servers\\mcp_pdf_reader\\pdf-reader-docker-bridge.js"
      ],
      "env": {}
    }
  }
}
```

**Mac:**
Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pdf-reader": {
      "command": "node",
      "args": [
        "/Users/YourName/Desktop/mcp-servers/mcp_pdf_reader/pdf-reader-docker-bridge.js"
      ],
      "env": {}
    }
  }
}
```

**Linux:**
Edit `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pdf-reader": {
      "command": "node",
      "args": [
        "/home/YourName/Desktop/mcp-servers/mcp_pdf_reader/pdf-reader-docker-bridge.js"
      ],
      "env": {}
    }
  }
}
```

**Important:** 
- Use absolute paths (full path to the bridge script)
- On Windows, use `\\` or `/` in paths
- Restart Claude Desktop after making changes

**See [docs/CLAUDE_DESKTOP_SETUP.md](./docs/CLAUDE_DESKTOP_SETUP.md) for detailed instructions.**

### For Cursor IDE

**Windows:**
Edit `%USERPROFILE%\.cursor\mcp.json`:

```json
{
  "mcpServers": {
    "pdf-reader": {
      "command": "node",
      "args": [
        "C:\\Users\\YourName\\Desktop\\mcp-servers\\mcp_pdf_reader\\pdf-reader-docker-bridge.js"
      ],
      "env": {}
    }
  }
}
```

**Mac/Linux:**
Edit `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "pdf-reader": {
      "command": "node",
      "args": [
        "/Users/YourName/Desktop/mcp-servers/mcp_pdf_reader/pdf-reader-docker-bridge.js"
      ],
      "env": {}
    }
  }
}
```

**Important:** 
- Use absolute paths
- Restart Cursor after making changes

## Testing the Setup

### Test Docker Container

```bash
docker run --rm -i mcp-pdf-reader-server python -c "from src.server import mcp; print('OK')"
```

### Test Bridge Script

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | node pdf-reader-docker-bridge.js
```

### Test in Claude Code

Ask: "Extract text from this PDF: https://example.com/sample.pdf"

### Test in Claude Desktop

After restarting, ask: "What tools are available from the PDF reader?"

### Test in Cursor

After restarting, ask: "Get information about this PDF: [URL]"

## Available Tools

### 1. `read_pdf_text`
Extract text content from PDF pages.

**Parameters:**
- `file_path` (string, optional): Path to the PDF file (required if url not provided)
- `url` (string, optional): URL to download PDF from (required if file_path not provided)
- `page_range` (object, optional): Dict with `start` and `end` page numbers

**Example:**
```json
{
  "url": "https://example.com/document.pdf",
  "page_range": {"start": 1, "end": 5}
}
```

### 2. `extract_pdf_images`
Extract all images from a PDF file with optional intelligent analysis.

**Parameters:**
- `file_path` (string, optional): Path to the PDF file (required if url not provided)
- `url` (string, optional): URL to download PDF from (required if file_path not provided)
- `output_dir` (string, optional): Directory to save images
- `page_range` (object, optional): Page range to process
- `analyze_images` (boolean, optional): Whether to analyze extracted images (default: true)
- `use_vision_model` (boolean, optional): Whether to use vision model for image descriptions (default: true)
- `ocr_language` (string, optional): OCR language code for text extraction from images (default: "eng")

**Example:**
```json
{
  "url": "https://example.com/document.pdf",
  "analyze_images": true,
  "use_vision_model": true,
  "ocr_language": "eng"
}
```

### 3. `read_pdf_with_ocr`
Extract text from both regular text and images using OCR.

**Parameters:**
- `file_path` (string, optional): Path to the PDF file (required if url not provided)
- `url` (string, optional): URL to download PDF from (required if file_path not provided)
- `page_range` (object, optional): Page range to process
- `ocr_language` (string, optional): OCR language code (default: "eng")

**Example:**
```json
{
  "url": "https://example.com/document.pdf",
  "ocr_language": "eng",
  "page_range": {"start": 1, "end": 10}
}
```

### 4. `get_pdf_info`
Get comprehensive metadata and statistics about a PDF.

**Parameters:**
- `file_path` (string, optional): Path to the PDF file (required if url not provided)
- `url` (string, optional): URL to download PDF from (required if file_path not provided)

**Example:**
```json
{
  "url": "https://example.com/document.pdf"
}
```

### 5. `analyze_pdf_structure`
Analyze the structure and content distribution of a PDF.

**Parameters:**
- `file_path` (string, optional): Path to the PDF file (required if url not provided)
- `url` (string, optional): URL to download PDF from (required if file_path not provided)

**Example:**
```json
{
  "url": "https://example.com/document.pdf"
}
```

## Documentation

- [Quick Start Guide](./docs/QUICK_START.md) - Get started in minutes
- [Claude Code Setup](./docs/CLAUDE_CODE_SETUP.md) - Detailed Claude Code configuration
- [Claude Desktop Setup](./docs/CLAUDE_DESKTOP_SETUP.md) - Detailed Claude Desktop configuration
- [Setup Prompts](./docs/SETUP_PROMPT.md) - Platform-specific setup prompts

**Using Claude Code to set up?** Copy the prompt from [SETUP_PROMPT.md](./docs/SETUP_PROMPT.md) and paste it into Claude Code for automated setup.

## Troubleshooting

### Docker Issues

**Docker image not found:**
```bash
docker build -t mcp-pdf-reader-server .
```

**Docker not running:**
- Start Docker Desktop
- Verify with: `docker info`

**Container fails to start:**
```bash
docker run --rm -i mcp-pdf-reader-server python -c "from src.server import mcp; print('OK')"
```

### Bridge Script Issues

**Node.js not found:**
```bash
node --version
```

**Bridge script not found:**
- Verify the absolute path is correct
- Use `realpath` (Mac/Linux) or `Resolve-Path` (Windows) to get the correct path

**Bridge script errors:**
- Check Docker is running: `docker info`
- Test Docker image: `docker images | grep mcp-pdf-reader-server`

### MCP Client Issues

**Claude Code:**
- Run: `claude mcp list` to see connection status
- Check the path in `~/.claude.json` is absolute

**Claude Desktop:**
- Check JSON syntax is valid
- Ensure absolute path is used
- Restart Claude Desktop completely

**Cursor:**
- Check JSON syntax in `~/.cursor/mcp.json`
- Ensure absolute path is used
- Restart Cursor completely

### Common Errors

**"Tesseract not found":**
- This shouldn't happen with Docker (Tesseract is pre-installed)
- If using manual setup, install Tesseract OCR

**"Docker spawn error":**
- Ensure Docker Desktop is running
- Verify Docker is accessible: `docker info`

**"Connection refused":**
- The server uses stdio, not HTTP
- Ensure you're using the bridge script, not trying to connect directly

## Manual Setup (Alternative)

If you prefer not to use Docker, you can set up the server manually:

### Prerequisites

- Python 3.12+
- Tesseract OCR installed
- Node.js (for the bridge script is not needed in manual mode)

### Installation Steps

1. **Install Tesseract OCR:**

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-eng
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
- Download from: https://github.com/UB-Mannheim/tesseract/wiki
- Install and add to PATH

2. **Install Python Dependencies:**

```bash
pip install -r requirements.txt
```

3. **Run the Server:**

```bash
python src/server.py
```

4. **Configure MCP Clients:**

For manual setup, you can configure MCP clients to run Python directly instead of using the Docker bridge:

**Claude Desktop:**
```json
{
  "mcpServers": {
    "pdf-reader": {
      "command": "python",
      "args": ["/path/to/mcp_pdf_reader/src/server.py"],
      "env": {}
    }
  }
}
```

**Cursor:**
```json
{
  "mcpServers": {
    "pdf-reader": {
      "command": "python",
      "args": ["/path/to/mcp_pdf_reader/src/server.py"],
      "env": {}
    }
  }
}
```

**Note:** Docker is still recommended as it includes all dependencies and ensures consistent behavior across platforms.

## Performance Considerations

### OCR Performance
- OCR processing can be slow for large images
- Consider processing smaller page ranges for faster results
- Images smaller than 50x50 pixels are automatically skipped

### Memory Usage
- Large PDFs with many images may consume significant memory
- The server processes pages sequentially to manage memory usage
- Extracted images are saved to disk to reduce memory pressure

### Optimization Tips
1. **Use page ranges** for large documents
2. **Specify output directories** for image extraction to avoid temp file buildup
3. **Choose appropriate OCR languages** to improve accuracy and speed
4. **Docker image size:** The image is ~12.5GB due to PyTorch and vision models. This is normal and expected.

## Advanced Features

### Image Analysis

The `extract_pdf_images` tool includes intelligent image analysis:

1. **OCR Text Extraction**: Automatically extracts text from images using Tesseract OCR
2. **Basic Image Analysis**: Analyzes dimensions, format, color mode, and estimates if image contains text
3. **Vision Model Descriptions**: Uses BLIP vision model to generate natural language descriptions of images (enabled by default)

### URL Support

All tools support both local file paths and URLs:
- Use `file_path` for local PDF files
- Use `url` for PDFs accessible via HTTP/HTTPS
- The server automatically downloads PDFs from URLs to temporary files
- Temporary files are cleaned up after processing

### Supported OCR Languages

- `eng` - English
- `fra` - French
- `deu` - German
- `spa` - Spanish
- `eng+fra` - Multiple languages

## Dependencies

### Included in Docker Image

- **fastmcp**: Modern MCP server framework
- **PyMuPDF**: Fast PDF processing and rendering
- **pytesseract**: Python wrapper for Tesseract OCR
- **Pillow**: Image processing library
- **httpx**: HTTP client for URL downloads
- **numpy**: Numerical operations for image analysis
- **transformers**: For vision models (BLIP image captioning)
- **torch**: For vision model inference
- **tesseract-ocr**: System OCR engine (pre-installed in Docker)

See `requirements.txt` for the complete list.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details.
