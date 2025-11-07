# Quick Start Guide

Get the PDF Reader MCP server running and connected to Claude Code and Claude Desktop in minutes.

## Prerequisites

- ✅ Docker Desktop installed and running
- ✅ Node.js installed (any recent version)
- ✅ Claude Code installed
- ✅ Claude Desktop installed

## One-Command Setup

### Step 1: Build the Docker Image

```bash
cd mcp_pdf_reader
docker build -t mcp-pdf-reader-server .
```

### Step 2: Connect to Claude Code

**Windows:**
```powershell
claude mcp add --transport stdio --scope user pdf-reader -- node "C:\Users\YourName\Desktop\mcp-servers\mcp_pdf_reader\pdf-reader-docker-bridge.js"
```

**Mac/Linux:**
```bash
claude mcp add --transport stdio --scope user pdf-reader -- node "/path/to/mcp_pdf_reader/pdf-reader-docker-bridge.js"
```

### Step 3: Connect to Claude Desktop

Edit your Claude Desktop config file:

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`  
**Mac:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Linux:** `~/.config/Claude/claude_desktop_config.json`

Add:
```json
{
  "mcpServers": {
    "pdf-reader": {
      "command": "node",
      "args": [
        "/full/path/to/mcp_pdf_reader/pdf-reader-docker-bridge.js"
      ],
      "env": {}
    }
  }
}
```

Then restart Claude Desktop.

## Verify It's Working

### Claude Code
Ask: "Extract text from this PDF: [URL]"

### Claude Desktop
After restarting, ask: "What tools are available from the PDF reader?"

## Troubleshooting

- **Docker image not found?** Run: `docker build -t mcp-pdf-reader-server .`
- **Claude Code can't connect?** Run: `claude mcp list` to see connection status
- **Claude Desktop not working?** Check the bridge file path is absolute and correct
- **Docker not running?** Start Docker Desktop and verify with: `docker info`

## Next Steps

- See [CLAUDE_CODE_SETUP.md](./CLAUDE_CODE_SETUP.md) for detailed Claude Code setup
- See [CLAUDE_DESKTOP_SETUP.md](./CLAUDE_DESKTOP_SETUP.md) for detailed Claude Desktop setup
- See [SETUP_PROMPT.md](./SETUP_PROMPT.md) for platform-specific setup prompts

