#!/usr/bin/env python
import sys
from chess_mcp.server import mcp, config

def setup_environment():
    return True

def run_server():
    """Main entry point for the Chess.com MCP Server"""
    if not setup_environment():
        sys.exit(1)
    
    mcp.run(transport="stdio")

if __name__ == "__main__":
    run_server()
