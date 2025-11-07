# Setup Prompts for Claude Code

Use these prompts in Claude Code to automatically set up and connect the PDF Reader MCP server. Choose the prompt that matches your operating system.

## Windows Setup Prompt

Copy and paste this prompt into Claude Code:

```
I just cloned the PDF Reader MCP server repository. Please help me set it up and connect it to both Claude Code and Claude Desktop using Docker.

Setup requirements:
1. Build the Docker image: cd mcp_pdf_reader && docker build -t mcp-pdf-reader-server .
2. Verify the Docker image was created: docker images | grep mcp-pdf-reader-server
3. Configure Claude Code to use the MCP server via CLI:
   - Use: claude mcp add --transport stdio --scope user pdf-reader -- node "C:\Users\Braedn Heney\Desktop\mcp-servers\mcp_pdf_reader\pdf-reader-docker-bridge.js"
   - Verify connection with: claude mcp list
4. Configure Claude Desktop:
   - Edit C:\Users\Braedn Heney\AppData\Roaming\Claude\claude_desktop_config.json
   - Add the bridge script configuration using stdio transport
   - The bridge file is at: C:\Users\Braedn Heney\Desktop\mcp-servers\mcp_pdf_reader\pdf-reader-docker-bridge.js
   - Show me the exact JSON to add
5. Test both connections work

Please execute these steps and verify each one works before moving to the next. If you encounter any errors, troubleshoot and fix them before continuing.

Note: Docker Desktop and Node.js are already installed. The server uses stdio transport (not HTTP).
```

## Mac Setup Prompt

Copy and paste this prompt into Claude Code:

```
I just cloned the PDF Reader MCP server repository. Please help me set it up and connect it to both Claude Code and Claude Desktop using Docker.

Setup requirements:
1. Build the Docker image: cd mcp_pdf_reader && docker build -t mcp-pdf-reader-server .
2. Verify the Docker image was created: docker images | grep mcp-pdf-reader-server
3. Configure Claude Code to use the MCP server via CLI:
   - Use: claude mcp add --transport stdio --scope user pdf-reader -- node "/Users/YourName/Desktop/mcp-servers/mcp_pdf_reader/pdf-reader-docker-bridge.js"
   - Verify connection with: claude mcp list
4. Configure Claude Desktop:
   - Edit ~/Library/Application Support/Claude/claude_desktop_config.json
   - Add the bridge script configuration using stdio transport
   - The bridge file is at: /Users/YourName/Desktop/mcp-servers/mcp_pdf_reader/pdf-reader-docker-bridge.js
   - Show me the exact JSON to add
5. Test both connections work

Please execute these steps and verify each one works before moving to the next. If you encounter any errors, troubleshoot and fix them before continuing.

Note: Docker Desktop and Node.js are already installed. The server uses stdio transport (not HTTP). Use Mac paths.
```

## Linux Setup Prompt

Copy and paste this prompt into Claude Code:

```
I just cloned the PDF Reader MCP server repository. Please help me set it up and connect it to both Claude Code and Claude Desktop using Docker.

Setup requirements:
1. Build the Docker image: cd mcp_pdf_reader && docker build -t mcp-pdf-reader-server .
2. Verify the Docker image was created: docker images | grep mcp-pdf-reader-server
3. Configure Claude Code to use the MCP server via CLI:
   - Use: claude mcp add --transport stdio --scope user pdf-reader -- node "/home/YourName/Desktop/mcp-servers/mcp_pdf_reader/pdf-reader-docker-bridge.js"
   - Verify connection with: claude mcp list
4. Configure Claude Desktop:
   - Edit ~/.config/Claude/claude_desktop_config.json
   - Add the bridge script configuration using stdio transport
   - The bridge file is at: /home/YourName/Desktop/mcp-servers/mcp_pdf_reader/pdf-reader-docker-bridge.js
   - Show me the exact JSON to add
5. Test both connections work

Please execute these steps and verify each one works before moving to the next. If you encounter any errors, troubleshoot and fix them before continuing.

Note: Docker and Node.js are already installed. The server uses stdio transport (not HTTP). Use Linux paths.
```

## Quick Setup Prompt (Shorter Version - All Platforms)

```
Setup the PDF Reader MCP server with Docker:
1. Build Docker image: cd mcp_pdf_reader && docker build -t mcp-pdf-reader-server .
2. Connect Claude Code: claude mcp add --transport stdio --scope user pdf-reader -- node "[FULL_PATH_TO]/pdf-reader-docker-bridge.js"
3. Configure Claude Desktop: Edit the Claude Desktop config file and add the bridge script from mcp_pdf_reader/pdf-reader-docker-bridge.js
4. Verify: claude mcp list and test in both clients

Docker and Node.js are installed. The server uses stdio transport. Replace [FULL_PATH_TO] with the actual absolute path to the bridge script.
```

## Step-by-Step Prompt (Most Detailed - All Platforms)

```
I need to set up the PDF Reader MCP server that I just cloned from GitHub. Please help me:

STEP 1: Build the Docker Image
- Navigate to the mcp_pdf_reader directory
- Run docker build -t mcp-pdf-reader-server .
- Wait for it to complete (this may take several minutes)
- Verify with: docker images | grep mcp-pdf-reader-server
- Show me the image details

STEP 2: Test the Docker Image
- Test that the container can run: docker run --rm -i mcp-pdf-reader-server python -c "from src.server import mcp; print('OK')"
- Verify it prints "OK"
- If there are errors, help me troubleshoot

STEP 3: Configure Claude Code
- Get the absolute path to pdf-reader-docker-bridge.js
- Use the CLI command to add the MCP server to user scope
- Command: claude mcp add --transport stdio --scope user pdf-reader -- node "[ABSOLUTE_PATH]"
- Verify the connection with: claude mcp list
- Confirm you see "✓ Connected" status

STEP 4: Configure Claude Desktop
- Locate the Claude Desktop config file:
  * Windows: %APPDATA%\Claude\claude_desktop_config.json
  * Mac: ~/Library/Application Support/Claude/claude_desktop_config.json
  * Linux: ~/.config/Claude/claude_desktop_config.json
- Get the absolute path to pdf-reader-docker-bridge.js
- Add the bridge script configuration:
  * Use stdio transport (Claude Desktop doesn't support HTTP for this server)
  * Bridge file path: [ABSOLUTE_PATH]
  * No environment variables needed
- Show me the exact JSON configuration to add
- I'll need to restart Claude Desktop after this

STEP 5: Verify Both Connections
- Test Claude Code connection by asking it to list available MCP tools
- Verify Claude Desktop config syntax is correct
- Provide instructions for testing in Claude Desktop after restart

Please execute each step and confirm completion before moving to the next. If any step fails, stop and help me troubleshoot.
```

## Platform-Specific Notes

### Windows
- Use backslashes `\\` or forward slashes `/` in paths
- Config file: `C:\Users\YourName\AppData\Roaming\Claude\claude_desktop_config.json`
- PowerShell: Use `Resolve-Path` to get absolute paths

### Mac
- Use forward slashes `/` in paths
- Config file: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Use `realpath` or `pwd` to get absolute paths

### Linux
- Use forward slashes `/` in paths
- Config file: `~/.config/Claude/claude_desktop_config.json`
- Use `realpath` or `pwd` to get absolute paths

## Customization

Before using these prompts, replace:
- `YourName` with your actual username
- `[FULL_PATH_TO]` with the actual absolute path to the bridge script
- `[ABSOLUTE_PATH]` with the actual absolute path to the bridge script

You can find the absolute path by:
- **Windows:** `Resolve-Path ".\pdf-reader-docker-bridge.js"` in PowerShell
- **Mac/Linux:** `realpath pdf-reader-docker-bridge.js` or `pwd` + filename

## Additional Resources

- [Quick Start Guide](./QUICK_START.md)
- [Claude Code Setup Guide](./CLAUDE_CODE_SETUP.md)
- [Claude Desktop Setup Guide](./CLAUDE_DESKTOP_SETUP.md)
- [PDF Reader MCP Server README](../README.md)

