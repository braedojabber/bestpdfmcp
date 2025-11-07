#!/bin/bash
# Simple script to run the MCP PDF Reader server in Docker

# Build the image if it doesn't exist
if ! docker images | grep -q "mcp-pdf-reader-server"; then
    echo "Building Docker image..."
    docker build -t mcp-pdf-reader-server .
fi

# Run the container interactively (for stdio communication)
echo "Starting MCP PDF Reader server..."
docker run -it --rm mcp-pdf-reader-server python src/server.py


