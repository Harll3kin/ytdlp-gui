#!/usr/bin/env python3
"""
Generate a simple icon for the macOS app if it doesn't exist.
This creates a basic icon.icns file.
"""

import os
import subprocess
from PIL import Image, ImageDraw

def create_simple_icon():
    """Create a simple icon with YouTube-ish colors."""

    # Create a simple icon image
    size = 1024
    img = Image.new('RGB', (size, size), color='#FF0000')  # Red background (YouTube style)
    draw = ImageDraw.Draw(img)

    # Add a simple play button in the center
    margin = size // 4
    points = [
        (margin, margin),
        (size - margin, size // 2),
        (margin, size - margin)
    ]
    draw.polygon(points, fill='white')

    # Save as PNG first
    png_path = 'icon_temp.png'
    img.save(png_path)

    # Convert PNG to ICNS using sips (built-in macOS tool)
    try:
        subprocess.run([
            'sips',
            '-s', 'format', 'icns',
            png_path,
            '--out', 'icon.icns'
        ], check=True, capture_output=True)
        print("✅ icon.icns created successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creating ICNS: {e}")
        print("You can create an icon manually or use a web tool to convert PNG to ICNS")
        return False
    finally:
        # Clean up temp PNG
        if os.path.exists(png_path):
            os.remove(png_path)

    return True

if __name__ == '__main__':
    if os.path.exists('icon.icns'):
        print("✅ icon.icns already exists!")
    else:
        print("Creating icon.icns...")
        try:
            create_simple_icon()
        except ImportError:
            print("⚠️  Pillow not installed. Installing...")
            subprocess.run(['pip3', 'install', 'Pillow'], check=True)
            create_simple_icon()
