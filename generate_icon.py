#!/usr/bin/env python3
"""Generate icon.icns for the macOS app bundle.

Uses iconutil, which is the supported way to build a multi-resolution .icns;
`sips -s format icns` only produces a single low-resolution image.
Failure is not fatal: the build just falls back to the default icon.
"""

import os
import shutil
import subprocess
import sys

from PIL import Image, ImageDraw

ICONSET = "icon.iconset"
OUTPUT = "icon.icns"
SIZES = [16, 32, 64, 128, 256, 512, 1024]


def draw_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    radius = size // 5
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=(255, 0, 0, 255))

    # Play triangle, centred and optically balanced.
    left = size * 0.36
    right = size * 0.72
    top = size * 0.28
    bottom = size * 0.72
    draw.polygon([(left, top), (right, size / 2), (left, bottom)], fill=(255, 255, 255, 255))
    return img


def main() -> int:
    if sys.platform != "darwin":
        print("icon.icns is only needed on macOS; skipping.")
        return 0

    if not shutil.which("iconutil"):
        print("iconutil not available; skipping icon generation.")
        return 0

    shutil.rmtree(ICONSET, ignore_errors=True)
    os.makedirs(ICONSET, exist_ok=True)

    for size in SIZES:
        draw_icon(size).save(os.path.join(ICONSET, f"icon_{size}x{size}.png"))
        # Retina variant expected by iconutil.
        if size <= 512:
            draw_icon(size * 2).save(os.path.join(ICONSET, f"icon_{size}x{size}@2x.png"))

    result = subprocess.run(
        ["iconutil", "-c", "icns", ICONSET, "-o", OUTPUT],
        capture_output=True,
        text=True,
    )
    shutil.rmtree(ICONSET, ignore_errors=True)

    if result.returncode != 0:
        print(f"iconutil failed, continuing without a custom icon: {result.stderr.strip()}")
        return 0

    print(f"Created {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
