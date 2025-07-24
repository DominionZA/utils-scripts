#!/usr/bin/env python3
"""
Simple script to run the Aura MCP server.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from aura_mcp.server import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main()) 