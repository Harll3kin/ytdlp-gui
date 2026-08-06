#!/bin/bash

# Check macOS build requirements with interactive prompts

echo "╔════════════════════════════════════════════════════════╗"
echo "║     yt-dlp GUI - macOS Setup (Interactive)            ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "❌ Homebrew not found."
    echo ""
    read -p "Install Homebrew? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        echo "✅ Homebrew installed!"
    else
        echo "⏭️  Skipped Homebrew installation"
    fi
else
    echo "✅ Homebrew already installed"
fi

echo ""

# Check if Python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found."
    echo ""
    read -p "Install Python3? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v brew &> /dev/null; then
            echo "🐍 Installing Python3 via Homebrew..."
            brew install python3
            echo "✅ Python3 installed!"
        else
            echo "⚠️  Homebrew not available. Cannot install Python3 automatically."
            echo "   Visit: https://www.python.org/downloads/"
            exit 1
        fi
    else
        echo "❌ Python3 is required. Exiting."
        exit 1
    fi
else
    echo "✅ Python3 already installed: $(python3 --version)"
fi

echo ""

# Check if pip3 is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 not found."
    echo ""
    read -p "Install pip3? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📦 Installing pip3..."
        python3 -m ensurepip --upgrade
        echo "✅ pip3 installed!"
    else
        echo "❌ pip3 is required. Exiting."
        exit 1
    fi
else
    echo "✅ pip3 already installed: $(pip3 --version)"
fi

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║              All requirements ready!                  ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "Next step:"
echo "  Run: bash build_installer_mac.sh"
echo ""
