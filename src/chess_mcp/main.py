#!/usr/bin/env python
import sys
import dotenv
from chess_mcp.server import mcp, config

def setup_environment():
    # Note: We're keeping the dotenv import for consistency with tripadvisor-mcp
    # but not using its functionality
    print("Using environment variables for configuration")

    # Chess.com API doesn't require authentication
    print(f"Chess.com API configuration:")
    print(f"  Base URL: {config.base_url}")
    
    return True

def run_server():
    """Main entry point for the Chess.com MCP Server"""
    # Setup environment
    if not setup_environment():
        sys.exit(1)
    
    print("\nStarting Chess.com MCP Server...")
    print("Running server in standard mode...")
    
    # Run the server with the stdio transport
    mcp.run(transport="stdio")

if __name__ == "__main__":
    run_server()
