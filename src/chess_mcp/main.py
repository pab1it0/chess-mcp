#!/usr/bin/env python
"""Main entry point for the Chess.com MCP Server."""

import logging
import sys
from typing import Literal

import structlog
from dotenv import load_dotenv

from chess_mcp.server import mcp

logger = structlog.get_logger(__name__)


def setup_environment() -> bool:
    """
    Set up the environment for the server.

    Returns:
        True if setup was successful, False otherwise
    """
    try:
        load_dotenv()

        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.StackInfoRenderer(),
                structlog.dev.set_exc_info,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.dev.ConsoleRenderer(),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=False,
        )

        logger.info("Chess.com MCP Server starting")
        return True
    except Exception as e:
        logger.error("Failed to setup environment", error=str(e), error_type=type(e).__name__)
        return False


def run_server(transport: Literal["stdio", "sse"] = "stdio") -> None:
    """
    Main entry point for the Chess.com MCP Server.

    Args:
        transport: The transport protocol to use (stdio or sse)
    """
    if not setup_environment():
        logger.error("Environment setup failed, exiting")
        sys.exit(1)

    try:
        logger.info("Starting MCP server", transport=transport)
        mcp.run(transport=transport)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(
            "Server error",
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True
        )
        sys.exit(1)


if __name__ == "__main__":
    run_server()
