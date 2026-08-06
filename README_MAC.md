# yt-dlp GUI - macOS Build Instructions

## Quick Start

### 1. Install Python 3
If you don't have Python 3 installed, get it from [python.org](https://www.python.org/downloads/) or use Homebrew:
```bash
brew install python3
```

### 2. Clone/Extract Project
Extract the project folder to your desired location.

### 3. Install Dependencies
```bash
cd /path/to/ytdlp-gui
pip3 install -r requirements.txt
```

### 4. Build the App
```bash
bash build.sh
```

This creates a standalone macOS app at `dist/ytdlp-gui.app`

### 5. Run the App
```bash
open dist/ytdlp-gui.app
```

Or drag `dist/ytdlp-gui.app` to your Applications folder and run from Launchpad.

---

## Clean Build
If you need to rebuild from scratch:
```bash
bash build.sh --clean
```

---

## Troubleshooting

### "Command not found: bash"
This shouldn't happen on macOS, but if it does, try:
```bash
/bin/bash build.sh
```

### "pip3: command not found"
Make sure Python3 is installed:
```bash
python3 --version
```

### "Module customtkinter not found"
Reinstall dependencies:
```bash
pip3 install -r requirements.txt --force-reinstall
```

### App won't launch
Check for errors in Terminal:
```bash
open dist/ytdlp-gui.app
# Check if error appears
```

Or run the Python script directly:
```bash
python3 src/app.py
```

---

## What the App Does

- **Download from YouTube**: Paste a YouTube link
- **Choose format**: MP3 or MP4
- **MP3**: Converts to audio (stores in your chosen folder)
- **MP4**: Downloads video in H.264 codec (auto-saves to `~/Videos/EDIT/ASSETS`)
- **Auto-update**: yt-dlp updates automatically before each download
- **Progress**: Real-time download progress bar

---

## Notes

- The app requires `yt-dlp` to be installed via pip (done automatically by requirements.txt)
- MP4 downloads are optimized for Adobe Premiere Pro compatibility
- All downloads are saved locally on your Mac
