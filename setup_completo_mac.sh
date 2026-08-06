#!/bin/bash

# All-in-one macOS setup and build script
# Just run this ONE script, sit back, and get your DMG!

echo "╔════════════════════════════════════════════════════════╗"
echo "║        yt-dlp GUI - Complete macOS Setup              ║"
echo "║         (This script does EVERYTHING)                 ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

REPO_URL="https://github.com/Harll3kin/ytdlp-gui.git"
PROJECT_DIR="ytdlp-gui"

# Step 1: Check and install Homebrew if needed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found."
    read -p "Install Homebrew? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        echo "✅ Homebrew installed!"
    else
        echo "⚠️  Homebrew is required. Please install from: https://brew.sh"
        exit 1
    fi
else
    echo "✅ Homebrew already installed"
fi

echo ""

# Step 2: Check and install Python3 if needed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found."
    read -p "Install Python3? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🐍 Installing Python3..."
        brew install python3
        echo "✅ Python3 installed!"
    else
        echo "❌ Python3 is required to build this app."
        exit 1
    fi
else
    echo "✅ Python3 already installed: $(python3 --version)"
fi

echo ""

# Step 3: Check and install Git if needed
if ! command -v git &> /dev/null; then
    echo "❌ Git not found."
    read -p "Install Git? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📥 Installing Git..."
        brew install git
        echo "✅ Git installed!"
    else
        echo "❌ Git is required to download the project."
        exit 1
    fi
else
    echo "✅ Git already installed: $(git --version)"
fi

echo ""

# Step 4: Clone the repository
if [ -d "$PROJECT_DIR" ]; then
    echo "📂 Project directory already exists"
    read -p "Use existing directory? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing old directory..."
        rm -rf "$PROJECT_DIR"
        echo "🔄 Cloning repository..."
        git clone "$REPO_URL" "$PROJECT_DIR"
    fi
else
    echo "🔄 Cloning repository..."
    git clone "$REPO_URL" "$PROJECT_DIR"
fi

cd "$PROJECT_DIR" || exit 1

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║           Installing Python dependencies...           ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

pip3 install -r requirements.txt

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║              Building macOS app...                    ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

chmod +x *.sh
bash generate_icon.py 2>/dev/null || python3 generate_icon.py
bash build_installer_mac.sh

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║                   ✅ ALL DONE!                        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "📍 Your installer is ready at:"
echo "   $(pwd)/dist/ytdlp-gui-1.0.0.dmg"
echo ""
echo "📤 To share it:"
echo "   • Copy the .dmg file anywhere you want"
echo "   • Anyone can open it and drag the app to Applications"
echo ""
