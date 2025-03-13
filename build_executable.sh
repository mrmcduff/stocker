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
from stockr.cli import main

if __name__ == "__main__":
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
        echo "Fix your PATH by adding ~/bin!"
        # echo "Adding ~/bin to PATH in .zshrc"
        # echo 'export PATH="$HOME/bin:$PATH"' >> ~/.zshrc
        # echo "Please run 'source ~/.zshrc' to update your PATH"
    fi
fi

# Cleanup
echo "Cleaning up build files..."
deactivate
rm -rf build-env build stockr.spec stockr_launcher.py

echo "Done!"
