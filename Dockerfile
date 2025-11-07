FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
# Tesseract OCR and its dependencies
# libgl1 and libglib2.0-0 for image processing
# curl for health checks (optional)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY pyproject.toml .

# Set Python path to include src directory
ENV PYTHONPATH=/app:$PYTHONPATH

# Run the MCP server via stdio (FastMCP default)
# The server will read from stdin and write to stdout
CMD ["python", "src/server.py"]

