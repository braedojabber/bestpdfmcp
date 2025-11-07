# Claude Code Setup Guide

This guide shows you how to connect the PDF Reader MCP server to Claude Code IDE using Docker.

## Prerequisites

- Docker Desktop installed and running
- Node.js installed (for the bridge script)
- Claude Code installed

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

## Step 2: Add MCP Server via CLI (Recommended)

Claude Code uses a CLI-based approach for managing MCP servers. This is the recommended and official method.

### Add Server to User Scope (Global)

Add the server to your user configuration so it's available across all projects:

**Windows:**
```powershell
claude mcp add --transport stdio --scope user pdf-reader -- node "C:\Users\YourName\Desktop\mcp-servers\mcp_pdf_reader\pdf-reader-docker-bridge.js"
```

**Mac:**
```bash
claude mcp add --transport stdio --scope user pdf-reader -- node "/Users/YourName/Desktop/mcp-servers/mcp_pdf_reader/pdf-reader-docker-bridge.js"
```

**Linux:**
```bash
claude mcp add --transport stdio --scope user pdf-reader -- node "/home/YourName/Desktop/mcp-servers/mcp_pdf_reader/pdf-reader-docker-bridge.js"
```

**Important:** Replace the path with your actual file location!

This will:
- Add the server to your user configuration (`~/.claude.json` on Mac/Linux, `%USERPROFILE%\.claude.json` on Windows)
- Make it available globally across all Claude Code sessions
- Automatically verify the connection

### Add Server to Project Scope (Local)

If you only want the server available in the mcp_pdf_reader project directory:

```bash
cd mcp_pdf_reader
claude mcp add --transport stdio --scope local pdf-reader -- node "./pdf-reader-docker-bridge.js"
```

This will:
- Add the server to the project's `.claude.json` file
- Make it available only when working in this directory
- Can be committed to version control for team sharing

## Step 3: Verify Connection

Check that the server is connected:

```bash
claude mcp list
```

You should see:
```
pdf-reader: stdio (Node.js bridge) - ✓ Connected
```

## Method 2: Manual JSON Configuration (Alternative)

If you prefer to manually edit the configuration files, you can add the server configuration directly.

### User Scope Configuration

**Windows:** Edit `%USERPROFILE%\.claude.json`  
**Mac/Linux:** Edit `~/.claude.json`

```json
{
  "mcpServers": {
    "pdf-reader": {
      "type": "stdio",
      "command": "node",
      "args": [
        "C:\\Users\\YourName\\Desktop\\mcp-servers\\mcp_pdf_reader\\pdf-reader-docker-bridge.js"
      ],
      "env": {}
    }
  }
}
```

**Important:** Update the path to match your actual file location!

### Local/Project Scope Configuration

Create or edit `.claude.json` in your project directory:

```json
{
  "mcpServers": {
    "pdf-reader": {
      "type": "stdio",
      "command": "node",
      "args": [
        "./pdf-reader-docker-bridge.js"
      ],
      "env": {}
    }
  }
}
```

**Note**: The CLI method is recommended as it automatically validates the configuration and verifies the connection.

## Testing the Connection

### Method 1: Check MCP Status via CLI

Use the CLI to verify the connection:

```bash
claude mcp list
```

You should see:
```
Checking MCP server health...

pdf-reader: stdio (Node.js bridge) - ✓ Connected
```

### Method 2: Test in Claude Code

Try asking Claude Code to:
- "Extract text from this PDF: https://example.com/document.pdf"
- "Get information about this PDF: [URL]"
- "Extract images from this PDF: [URL]"

If the MCP server is connected, Claude Code should be able to use the PDF reader tools.

### Method 3: View MCP Details

Get detailed information about your MCP servers:

```bash
claude mcp view
```

This shows all configured servers with their status and capabilities.

## Managing MCP Servers

### Remove a Server

To remove the pdf-reader server:

```bash
# Remove from user scope
claude mcp remove --scope user pdf-reader

# Remove from local scope
claude mcp remove --scope local pdf-reader
```

### Update Server Configuration

To update the server configuration:

```bash
# Remove old configuration
claude mcp remove --scope user pdf-reader

# Add with new configuration
claude mcp add --transport stdio --scope user pdf-reader -- node "/path/to/pdf-reader-docker-bridge.js"
```

## Troubleshooting

### Server Not Showing in List

1. **Check which scope you added it to:**
   ```bash
   claude mcp list
   ```
   The list shows servers from all scopes (local, project, user)

2. **Verify you're in the right directory:**
   - User scope servers are available everywhere
   - Local scope servers only work in the directory where they were added

3. **Check for conflicts:**
   - If a server with the same name exists in multiple scopes, local scope takes precedence

### Server Not Connecting

1. **Verify Docker is running:**
   ```bash
   docker info
   ```

2. **Check Docker image exists:**
   ```bash
   docker images | grep mcp-pdf-reader-server
   ```
   If not found, build it: `docker build -t mcp-pdf-reader-server .`

3. **Test Docker container manually:**
   ```bash
   docker run --rm -i mcp-pdf-reader-server python -c "from src.server import mcp; print('OK')"
   ```

4. **Test bridge script manually:**
   ```bash
   echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | node pdf-reader-docker-bridge.js
   ```

### Bridge Script Not Working

1. **Verify Node.js is installed:**
   ```bash
   node --version
   ```

2. **Check bridge file exists:**
   ```bash
   # Windows
   Test-Path "C:\Users\YourName\Desktop\mcp-servers\mcp_pdf_reader\pdf-reader-docker-bridge.js"
   
   # Mac/Linux
   ls /Users/YourName/Desktop/mcp-servers/mcp_pdf_reader/pdf-reader-docker-bridge.js
   ```

3. **Test bridge manually:**
   ```bash
   echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | node pdf-reader-docker-bridge.js
   ```

### CLI Command Not Found

If `claude` command is not found:

1. **Verify Claude Code is installed:**
   - Check if Claude Code CLI is in your PATH
   - On Windows, you may need to restart your terminal after installation

2. **Check installation:**
   ```bash
   claude --version
   ```

3. **Use full path if needed:**
   - Find the Claude Code executable and use the full path
   - Or add Claude Code to your system PATH

## Comparison: Methods

| Feature | CLI (Recommended) | Manual JSON |
|---------|------------------|-------------|
| **Setup** | Simplest - one command | Manual file editing |
| **Validation** | Automatic | Manual |
| **Path Handling** | Automatic | Must be exact |
| **Recommended** | ✅ Yes | ❌ Not recommended |

**Best Practice**: Always use the CLI method (`claude mcp add`) as it:
- Automatically validates the configuration
- Verifies the connection
- Handles scope management correctly
- Provides better error messages

## Additional Resources

- [PDF Reader MCP Server README](../README.md)
- [Claude Desktop Setup Guide](./CLAUDE_DESKTOP_SETUP.md)
- [Official Claude Code MCP Documentation](https://code.claude.com/docs/en/mcp)
- [MCP Protocol Documentation](https://modelcontextprotocol.io)

## CLI Commands Reference

### List all MCP servers
```bash
claude mcp list
```

### Add a stdio MCP server
```bash
claude mcp add --transport stdio --scope user <name> -- <command> [args...]
```

### Remove an MCP server
```bash
claude mcp remove --scope user <name>
```

### View detailed MCP information
```bash
claude mcp view
```

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify Docker container logs: `docker logs <container-id>`
3. Check MCP server status: `claude mcp list`
4. Ensure Docker is running: `docker info`
5. Review the [official Claude Code MCP documentation](https://code.claude.com/docs/en/mcp) for the latest information

