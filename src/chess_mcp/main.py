#!/usr/bin/env python
import sys
from dotenv import load_dotenv
from chess_mcp.server import mcp, config

def setup_environment():
    if load_dotenv():
        print("Loaded environment variables from .env file")
    else:
        print("No .env file found or could not load it - using environment variables")

    # Chess.com API doesn't require authentication, just check if rate limiting is configured
    if config.rate_limit < 1:
        print("WARNING: CHESS_RATE_LIMIT environment variable is set to a very low value")
        print("This might cause API calls to be rate limited")
    
    print(f"Chess.com API configuration:")
    print(f"  Base URL: {config.base_url}")
    print(f"  Rate Limit: {config.rate_limit} requests per second")
    
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
