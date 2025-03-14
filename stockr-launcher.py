#!/usr/bin/env python
"""
Launcher for the Stock Analyzer CLI tool.
"""
import sys

def show_startup_message():
    """Show a simple startup message while imports are loading."""
    print("Starting Stock Analyzer...", flush=True)
    print("Please wait while dependencies are loaded...", flush=True)

if __name__ == "__main__":
    # Show startup message first
    show_startup_message()

    # Import main function - this may take a moment
    from stockr.cli import main

    # Run the main function
    main()
