#!/usr/bin/env python3
"""
Main entry point for Graphiti MCP Server

This is a backwards-compatible wrapper around the original graphiti_mcp_server.py
to maintain compatibility with existing deployment scripts and documentation.

Usage:
    python main.py [args...]

All arguments are passed through to the original server implementation.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src directory to Python path for imports
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

load_dotenv()

# Import and run the original server
if __name__ == '__main__':
    from src.graphiti_mcp_server import mcp

    # Get host and port from environment variables with defaults
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port = int(os.getenv("MCP_PORT", "8000"))

    # Run the MCP server
    mcp.run(transport="http", host=host, port=port)
