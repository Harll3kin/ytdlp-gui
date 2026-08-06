#!/bin/bash

# Build script for macOS
# Usage: bash build.sh [--clean]

set -e

if [[ "$1" == "--clean" ]]; then
    echo "Cleaning build artifacts..."
    rm -rf build dist ytdlp-gui.spec
fi

echo "Installing dependencies..."
pip3 install -r requirements.txt

echo "Building macOS app..."
pyinstaller --onefile --windowed --name ytdlp-gui --collect-all customtkinter src/app.py

echo "✅ Build complete! App is at: dist/ytdlp-gui.app"
echo ""
echo "To run: open dist/ytdlp-gui.app"
