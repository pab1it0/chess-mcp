#!/bin/bash
set -e

# Output environment variables for debugging (excluding secrets)
echo "Starting Chess.com MCP Server in Docker..."
echo "  Rate Limit: ${CHESS_RATE_LIMIT:-5} requests per second"

# Run the MCP server
exec /app/.venv/bin/python -m chess_mcp.main "$@"
