#!/usr/bin/env node

/**
 * Docker Bridge for PDF Reader MCP Server
 * 
 * This bridge script runs the PDF Reader MCP server in a Docker container
 * and forwards stdio communication between Claude Desktop/Code and the container.
 * 
 * The PDF Reader MCP server uses stdio transport (FastMCP), so this bridge
 * simply runs Docker with stdio forwarding - no HTTP conversion needed.
 * 
 * Usage: node pdf-reader-docker-bridge.js
 */

const { spawn } = require('child_process');
const path = require('path');

// Docker image name
const DOCKER_IMAGE = 'mcp-pdf-reader-server';

// Get the directory where this script is located
const scriptDir = __dirname;

// Log to stderr (won't interfere with JSON-RPC on stdout)
function log(message) {
  console.error(`[PDF Reader Bridge] ${new Date().toISOString()} - ${message}`);
}

// Spawn Docker container with stdio forwarding
const dockerArgs = [
  'run',
  '--rm',           // Remove container when it exits
  '-i',             // Interactive mode (keep stdin open)
  DOCKER_IMAGE,
  'python',
  'src/server.py'
];

log(`Starting Docker container: ${DOCKER_IMAGE}`);
log(`Command: docker ${dockerArgs.join(' ')}`);

const docker = spawn('docker', dockerArgs, {
  stdio: ['pipe', 'pipe', 'pipe'],
  cwd: scriptDir
});

// Forward stdin/stdout/stderr
process.stdin.pipe(docker.stdin);
docker.stdout.pipe(process.stdout);
docker.stderr.pipe(process.stderr);

// Handle process termination
docker.on('error', (error) => {
  log(`Docker spawn error: ${error.message}`);
  log(`Make sure Docker is installed and the image is built:`);
  log(`  docker build -t ${DOCKER_IMAGE} .`);
  process.exit(1);
});

docker.on('exit', (code, signal) => {
  if (code !== null) {
    log(`Docker container exited with code ${code}`);
  }
  if (signal !== null) {
    log(`Docker container terminated by signal ${signal}`);
  }
  process.exit(code || 0);
});

// Handle parent process termination
process.on('SIGINT', () => {
  log(`Received SIGINT, terminating Docker container...`);
  docker.kill('SIGINT');
});

process.on('SIGTERM', () => {
  log(`Received SIGTERM, terminating Docker container...`);
  docker.kill('SIGTERM');
});

