import os

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont

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


_VARIANT_COLORS = {
    "active": (GRADIENT_START, GRADIENT_END, (255, 255, 255, 255)),
    "active_hover": (GRADIENT_START, GRADIENT_END_HOVER, (255, 255, 255, 255)),
    "inactive": (PILL_INACTIVE, PILL_INACTIVE, (170, 170, 170, 255)),
    "inactive_hover": (PILL_INACTIVE_HOVER, PILL_INACTIVE_HOVER, (241, 241, 241, 255)),
    "disabled": (PILL_INACTIVE, PILL_INACTIVE, (113, 113, 113, 255)),
}


def _load_font(size: int):
    windir = os.environ.get("WINDIR", "C:\\Windows")
    font_path = os.path.join(windir, "Fonts", "segoeui.ttf")
    try:
        return ImageFont.truetype(font_path, size)
    except OSError:
        return ImageFont.load_default()


def _render_button_image(width, height, text, variant, font_size=14):
    start_hex, end_hex, text_color = _VARIANT_COLORS[variant]
    pill = render_gradient_pill(width, height, start_hex, end_hex)

    draw = ImageDraw.Draw(pill)
    font = _load_font(font_size)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    draw.text(
        ((width - text_width) / 2 - bbox[0], (height - text_height) / 2 - bbox[1]),
        text,
        font=font,
        fill=text_color,
    )
    return ctk.CTkImage(light_image=pill, dark_image=pill, size=(width, height))


class GradientButton(ctk.CTkButton):
    def __init__(self, master, text, width, height, command, **kwargs):
        self._images = {
            variant: _render_button_image(width, height, text, variant)
            for variant in _VARIANT_COLORS
        }
        self._is_active = True
        self._is_enabled = True
        self._mouse_inside = False

        super().__init__(
            master,
            text="",
            width=width,
            height=height,
            corner_radius=0,
            fg_color="transparent",
            hover=False,
            image=self._images["active"],
            command=command,
            **kwargs,
        )
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _current_variant(self):
        if not self._is_enabled:
            return "disabled"
        return "active" if self._is_active else "inactive"

    def _display_variant(self):
        variant = self._current_variant()
        if variant in ("active", "inactive") and getattr(self, "_mouse_inside", False):
            return variant + "_hover"
        return variant

    def _on_enter(self, _event=None):
        self._mouse_inside = True
        self.configure(image=self._images[self._display_variant()])

    def _on_leave(self, _event=None):
        self._mouse_inside = False
        self.configure(image=self._images[self._current_variant()])

    def set_active(self, is_active: bool) -> None:
        self._is_active = is_active
        self.configure(image=self._images[self._display_variant()])

    def set_enabled(self, enabled: bool) -> None:
        self._is_enabled = enabled
        self.configure(
            state=("normal" if enabled else "disabled"),
            image=self._images[self._display_variant()],
        )


class GradientProgressBar(ctk.CTkLabel):
    def __init__(self, master, width, height, **kwargs):
        self._width = width
        self._height = height
        self._current_image = self._render(0.0)
        super().__init__(master, text="", image=self._current_image, width=width, height=height, **kwargs)

    def _render(self, fraction: float):
        radius = self._height // 2
        mask = Image.new("L", (self._width, self._height), 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            [0, 0, self._width - 1, self._height - 1], radius=radius, fill=255
        )

        track = Image.new("RGBA", (self._width, self._height), (0, 0, 0, 0))
        base = Image.new("RGB", (self._width, self._height), _hex_to_rgb(PROGRESS_TRACK))
        track.paste(base, (0, 0), mask)

        fill_width = round(self._width * max(0.0, min(1.0, fraction)))
        if fill_width > 0:
            gradient = render_gradient_pill(self._width, self._height, GRADIENT_START, GRADIENT_END)
            fill_crop = gradient.crop((0, 0, fill_width, self._height))
            track.paste(fill_crop, (0, 0), fill_crop)

        return ctk.CTkImage(light_image=track, dark_image=track, size=(self._width, self._height))

    def set_progress(self, fraction: float) -> None:
        self._current_image = self._render(fraction)
        self.configure(image=self._current_image)
