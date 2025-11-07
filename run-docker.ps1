# PowerShell script to run the MCP PDF Reader server in Docker

# Build the image if it doesn't exist
$imageExists = docker images | Select-String "mcp-pdf-reader-server"
if (-not $imageExists) {
    Write-Host "Building Docker image..."
    docker build -t mcp-pdf-reader-server .
}

# Run the container interactively (for stdio communication)
Write-Host "Starting MCP PDF Reader server..."
docker run -it --rm mcp-pdf-reader-server python src/server.py


