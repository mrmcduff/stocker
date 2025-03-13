#!/bin/bash
# Script to build a standalone executable for stockr using uv

# Exit on error
set -e

echo "Creating build environment with uv..."
uv venv build-env
source build-env/bin/activate

echo "Installing dependencies with uv..."
uv pip install -e .
uv pip install pyinstaller

echo "Creating launcher script..."
cat > stockr_launcher.py << 'EOF'
#!/usr/bin/env python
"""
Launcher for the Stock Analyzer CLI tool.
"""
import sys
import time

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
EOF

echo "Building executable with PyInstaller..."
pyinstaller --onefile --name stockr stockr_launcher.py

echo "Executable created at: $(pwd)/dist/stockr"

# Ask if user wants to install to ~/bin
read -p "Install to ~/bin? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    mkdir -p ~/bin
    cp dist/stockr ~/bin/
    echo "Installed to ~/bin/stockr"

    # Check if ~/bin is in PATH
    if [[ ":$PATH:" != *":$HOME/bin:"* ]]; then
        echo "update path to include ~/bin"
    fi
fi

# Cleanup
echo "Cleaning up build files..."
deactivate
rm -rf build stockr.spec stockr_launcher.py

echo "Done!"
