#!/bin/bash
set -e

# Output environment variables for debugging
echo "Starting Chess.com MCP Server in Docker..."

# Run the MCP server
exec /app/.venv/bin/python -m chess_mcp.main "$@"
