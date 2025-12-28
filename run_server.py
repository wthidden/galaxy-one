#!/usr/bin/env python3
"""
StarWeb Server Launcher
Run this script from the project root to start the game server.
"""
import sys
import os
import traceback

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Import and run the server
from server.main import main
import asyncio

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user.")
    except Exception as e:
        print(f"Server error: {e}")
        traceback.print_exc()
        sys.exit(1)
