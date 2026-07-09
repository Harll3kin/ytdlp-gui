from PIL import Image, ImageDraw

BACKGROUND = "#0F0F0F"
WINDOW_BACKGROUND = "#000000"
SURFACE = "#181818"
INPUT_BACKGROUND = "#121212"
INPUT_BORDER = "#303030"
PILL_INACTIVE = "#212121"
PILL_INACTIVE_HOVER = "#2A2A2A"
PROGRESS_TRACK = "#272727"
TEXT_PRIMARY = "#F1F1F1"
TEXT_SECONDARY = "#AAAAAA"
TEXT_PLACEHOLDER = "#717171"
GRADIENT_START = "#FF0000"
GRADIENT_END = "#FF4D6D"
GRADIENT_END_HOVER = "#FF7A93"


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


def render_gradient_pill(width: int, height: int, start_hex: str, end_hex: str) -> Image.Image:
    start_rgb = _hex_to_rgb(start_hex)
    end_rgb = _hex_to_rgb(end_hex)

    row = Image.new("RGB", (width, 1))
    for x in range(width):
        ratio = x / max(width - 1, 1)
        r = round(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
        g = round(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
        b = round(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
        row.putpixel((x, 0), (r, g, b))
    gradient = row.resize((width, height))

    mask = Image.new("L", (width, height), 0)
    radius = height // 2
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, width - 1, height - 1], radius=radius, fill=255)

    result = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    result.paste(gradient, (0, 0), mask)
    return result
