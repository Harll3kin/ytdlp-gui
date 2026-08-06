#!/bin/bash

# Build script for creating a macOS DMG installer
# Usage: bash build_installer_mac.sh [--clean]

set -e

PROJECT_NAME="ytdlp-gui"
VERSION="1.0.0"
APP_NAME="yt-dlp GUI"

echo "╔════════════════════════════════════════════════════════╗"
echo "║  Building $APP_NAME macOS Installer (DMG)             ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Clean if requested
if [[ "$1" == "--clean" ]]; then
    echo "🧹 Cleaning build artifacts..."
    rm -rf build dist "$PROJECT_NAME.spec"
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

# Generate icon if it doesn't exist
if [ ! -f "icon.icns" ]; then
    echo "🎨 Generating app icon..."
    python3 generate_icon.py
fi

# Build the app
echo "🔨 Building macOS app..."
pyinstaller --onefile --windowed \
    --name "$PROJECT_NAME" \
    --icon=icon.icns \
    --collect-all customtkinter \
    src/app.py 2>&1 | grep -v "WARNING:" || true

# Create DMG
echo "💿 Creating DMG installer..."

DMG_NAME="$PROJECT_NAME-$VERSION.dmg"
VOLUME_NAME="$APP_NAME"
TEMP_DMG="/tmp/${PROJECT_NAME}_temp.dmg"
MOUNTED_VOL="/Volumes/$VOLUME_NAME"

# Remove old DMG if exists
rm -f "dist/$DMG_NAME"

# Create temporary DMG
hdiutil create -volname "$VOLUME_NAME" -srcfolder "dist/$PROJECT_NAME.app" -ov -format UDZO "dist/$TEMP_DMG" > /dev/null

# Copy to final location
mv "$TEMP_DMG" "dist/$DMG_NAME"

echo ""
echo "✅ Build complete!"
echo ""
echo "📍 Installer created at: dist/$DMG_NAME"
echo ""
echo "To distribute:"
echo "  1. Upload dist/$DMG_NAME to your server"
echo "  2. User downloads and opens the .dmg file"
echo "  3. Drags 'yt-dlp GUI' app to Applications folder"
echo "  4. Done!"
echo ""
