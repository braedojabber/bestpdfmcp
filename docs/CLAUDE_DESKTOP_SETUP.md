# Claude Desktop Setup Guide

This guide shows you how to connect the PDF Reader MCP server to Claude Desktop using Docker.

## Prerequisites

- Docker Desktop installed and running
- Node.js installed (for the bridge script)
- Claude Desktop installed

## Step 1: Build the Docker Image

First, build the Docker image:

```bash
cd mcp_pdf_reader
docker build -t mcp-pdf-reader-server .
```

Verify the image was created:
```bash
docker images | grep mcp-pdf-reader-server
```

## Step 2: Locate Claude Desktop Config File

The config file location depends on your operating system:

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```
Typically: `C:\Users\YourName\AppData\Roaming\Claude\claude_desktop_config.json`

**Mac:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

## Step 3: Edit Configuration File

Open the config file in a text editor and add the PDF Reader MCP server configuration.

### Windows Configuration

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

**Important:** Replace `C:\\Users\\YourName\\Desktop\\mcp-servers\\mcp_pdf_reader\\pdf-reader-docker-bridge.js` with your actual file path!

### Mac Configuration

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

**Important:** Replace `/Users/YourName/Desktop/mcp-servers/mcp_pdf_reader/pdf-reader-docker-bridge.js` with your actual file path!

### Linux Configuration

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

**Important:** Replace `/home/YourName/Desktop/mcp-servers/mcp_pdf_reader/pdf-reader-docker-bridge.js` with your actual file path!

## Step 4: Get the Absolute Path

You need to use the absolute (full) path to the bridge script. Here's how to find it:

### Windows (PowerShell)

```powershell
Resolve-Path ".\pdf-reader-docker-bridge.js"
```

Or manually:
```powershell
cd "C:\Users\YourName\Desktop\mcp-servers\mcp_pdf_reader"
$PWD.Path + "\pdf-reader-docker-bridge.js"
```

### Mac/Linux

```bash
cd /path/to/mcp_pdf_reader
realpath pdf-reader-docker-bridge.js
```

Or manually:
```bash
cd /path/to/mcp_pdf_reader
pwd
# Then append: /pdf-reader-docker-bridge.js
```

## Step 5: Restart Claude Desktop

After editing the configuration file:

1. **Save the file**
2. **Completely quit Claude Desktop** (not just close the window)
3. **Restart Claude Desktop**

The MCP server should now be connected.

## Step 6: Verify Connection

After restarting Claude Desktop, you can test the connection by asking:

- "What tools are available from the PDF reader?"
- "Extract text from this PDF: [URL]"
- "Get information about this PDF: [URL]"

If the server is connected, Claude should be able to use the PDF reader tools.

## Complete Configuration Example

If you already have other MCP servers configured, your file might look like this:

```json
{
  "mcpServers": {
    "canvas-mcp": {
      "command": "node",
      "args": [
        "C:\\Users\\YourName\\Desktop\\mcp-servers\\canvas\\canvas-mcp-bridge.js"
      ],
      "env": {
        "MCP_URL": "http://localhost:8000/mcp"
      }
    },
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

## Troubleshooting

### Server Not Appearing

1. **Check the config file location:**
   - Make sure you're editing the correct file
   - The path varies by operating system (see Step 2)

2. **Verify JSON syntax:**
   - Use a JSON validator to check for syntax errors
   - Make sure all quotes are properly escaped (Windows paths need `\\`)

3. **Check file path:**
   - The path must be absolute (full path), not relative
   - On Windows, use `\\` or `/` (both work)
   - Make sure the bridge script file exists at that location

### Docker Not Running

1. **Start Docker Desktop:**
   - Open Docker Desktop application
   - Wait for it to fully start (whale icon should be steady)

2. **Verify Docker is running:**
   ```bash
   docker info
   ```

3. **Check Docker image exists:**
   ```bash
   docker images | grep mcp-pdf-reader-server
   ```
   If not found, build it: `docker build -t mcp-pdf-reader-server .`

### Bridge Script Errors

1. **Verify Node.js is installed:**
   ```bash
   node --version
   ```

2. **Test bridge script manually:**
   ```bash
   # Windows PowerShell
   echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | node pdf-reader-docker-bridge.js
   
   # Mac/Linux
   echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | node pdf-reader-docker-bridge.js
   ```

3. **Check file permissions:**
   - Make sure the bridge script is executable (Mac/Linux): `chmod +x pdf-reader-docker-bridge.js`
   - Make sure you have read permissions

### Claude Desktop Not Loading Server

1. **Check Claude Desktop logs:**
   - Look for error messages in the console
   - On Mac: `~/Library/Logs/Claude/`
   - On Windows: Check Event Viewer or Claude Desktop logs

2. **Verify JSON is valid:**
   - Use a JSON validator
   - Common issues: missing commas, unescaped quotes, trailing commas

3. **Try a minimal config:**
   - Start with just the pdf-reader server
   - If that works, add other servers one by one

### Path Issues

**Windows:**
- Use forward slashes `/` or escaped backslashes `\\`
- Example: `C:/Users/Name/path.js` or `C:\\Users\\Name\\path.js`
- Avoid: `C:\Users\Name\path.js` (unescaped backslashes)

**Mac/Linux:**
- Use forward slashes `/`
- Make sure the path starts with `/` (absolute path)
- Example: `/Users/Name/path.js`

## Testing the Setup

### Test 1: Check Docker Image

```bash
docker images | grep mcp-pdf-reader-server
```

Should show the image.

### Test 2: Test Docker Container

```bash
docker run --rm -i mcp-pdf-reader-server python -c "from src.server import mcp; print('OK')"
```

Should print "OK".

### Test 3: Test Bridge Script

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | node pdf-reader-docker-bridge.js
```

Should return a JSON-RPC response (may take a moment as Docker starts).

### Test 4: Test in Claude Desktop

After restarting Claude Desktop, ask:
- "What MCP tools are available?"
- "Extract text from this PDF: https://example.com/sample.pdf"

## Additional Resources

- [PDF Reader MCP Server README](../README.md)
- [Claude Code Setup Guide](./CLAUDE_CODE_SETUP.md)
- [Quick Start Guide](./QUICK_START.md)
- [Official Claude Desktop MCP Documentation](https://claude.ai/docs/mcp)

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify Docker is running: `docker info`
3. Check Docker image exists: `docker images | grep mcp-pdf-reader-server`
4. Test bridge script manually (see Testing section)
5. Check Claude Desktop logs for error messages
6. Review the [official Claude Desktop MCP documentation](https://claude.ai/docs/mcp) for the latest information

