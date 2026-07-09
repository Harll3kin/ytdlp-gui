# yt-dlp GUI YouTube Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reskin the yt-dlp GUI with a YouTube-dark-mode-inspired look (CustomTkinter, gradient red→pink pills) and replace the scrolling log box with a progress bar + short status line.

**Architecture:** New `src/theme.py` module owns all design tokens and two custom Pillow-rendered widgets (`GradientButton`, `GradientProgressBar`) that CustomTkinter can't do natively (true gradients). `src/downloader.py` gains a pure `parse_progress` function. `src/app.py` is rewritten to use CustomTkinter widgets, `theme.py`'s components, and the new progress-based feedback loop, while keeping every existing behavior (auto-fill title, folder persistence, error handling, threading) intact.

**Tech Stack:** Python 3.10, CustomTkinter (new dependency, wraps tkinter), Pillow (already a CustomTkinter dependency), pytest, PyInstaller.

## Global Constraints

- Python 3.10, Windows only. `yt-dlp`/`ffmpeg` stay on PATH, not bundled (unchanged from before).
- New dependency: `customtkinter` (added to `requirements.txt`).
- Colors (exact hex, from the approved design spec):
  `BACKGROUND=#0F0F0F`, `WINDOW_BACKGROUND=#000000`, `SURFACE=#181818`,
  `INPUT_BACKGROUND=#121212`, `INPUT_BORDER=#303030`,
  `PILL_INACTIVE=#212121`, `PILL_INACTIVE_HOVER=#2A2A2A`,
  `PROGRESS_TRACK=#272727`, `TEXT_PRIMARY=#F1F1F1`,
  `TEXT_SECONDARY=#AAAAAA`, `TEXT_PLACEHOLDER=#717171`,
  `GRADIENT_START=#FF0000`, `GRADIENT_END=#FF4D6D`,
  `GRADIENT_END_HOVER=#FF7A93`.
- Gradient (`GRADIENT_START` → `GRADIENT_END`, horizontal) must be a real
  rendered gradient (Pillow), not an approximated solid color — this was
  an explicit user choice over the simpler solid-color alternative.
- No sidebar — single centered panel. No scrolling log — a progress bar
  (`GradientProgressBar`) + one short status line replace it entirely.
- `config.json` behavior, default folder
  (`%USERPROFILE%\Videos\EDIT\ASSETS\SFX`), auto-create missing folder,
  folder persisted to config only at download time, `FileNotFoundError`
  handling for missing yt-dlp, empty-link handling — all unchanged from
  the current `app.py`, just re-wired to push `("status", text)` /
  `("progress", fraction)` tuples instead of raw log lines.
- Packaging: `build.ps1`'s PyInstaller call must add `--collect-all
  customtkinter` (CustomTkinter ships theme JSON/font assets that
  PyInstaller's static analysis misses otherwise).
- Per this project's established convention, `app.py` and the new
  CustomTkinter widgets in `theme.py` are verified manually / via
  non-interactive construct-and-destroy smoke tests (no display
  automation available) — only pure logic (`parse_progress`,
  `render_gradient_pill`) gets `pytest` coverage.

## File Structure

```
YT-DLP DOWNLOADER/.claude/worktrees/ytdlp-gui/
  requirements.txt      # + customtkinter
  build.ps1               # + --collect-all customtkinter
  src/
    config.py             # unchanged
    downloader.py           # + parse_progress(line) -> float | None
    theme.py                 # NEW: color tokens, render_gradient_pill, GradientButton, GradientProgressBar
    app.py                    # rewritten: CustomTkinter window, new layout, progress-based feedback
  tests/
    test_config.py         # unchanged
    test_downloader.py       # + parse_progress tests
    test_theme.py             # NEW: render_gradient_pill tests
```

---

### Task 1: Adicionar dependência CustomTkinter

**Files:**
- Modify: `requirements.txt`

**Interfaces:**
- Consumes: nada.
- Produces: `customtkinter` instalado e importável, disponível para as próximas tasks.

- [ ] **Step 1: Adicionar a dependência**

`requirements.txt` deve conter, nesta ordem:

```
pytest
pyinstaller
customtkinter
```

- [ ] **Step 2: Instalar**

Run: `pip install -r requirements.txt`
Expected: instala `customtkinter` (e suas dependências, incluindo Pillow) sem erro.

- [ ] **Step 3: Confirmar que importa**

Run: `python -c "import customtkinter; print(customtkinter.__version__)"`
Expected: imprime um número de versão, sem exceção.

- [ ] **Step 4: Commit**

```bash
git add requirements.txt
git commit -m "chore: add customtkinter dependency for redesign"
```

---

### Task 2: downloader.py — parse_progress

**Files:**
- Modify: `src/downloader.py` (adicionar ao final do arquivo)
- Modify: `tests/test_downloader.py` (adicionar ao final do arquivo)

**Interfaces:**
- Consumes: nada além de stdlib (`re`).
- Produces: `downloader.parse_progress(line: str) -> float | None` — devolve a fração de progresso (0.0–1.0) extraída de uma linha de progresso do yt-dlp (formato `[download]  58.3% of ...`), ou `None` se a linha não contiver progresso.

- [ ] **Step 1: Escrever os testes (vão falhar — parse_progress ainda não existe)**

Adicionar ao final de `tests/test_downloader.py`:

```python
def test_parse_progress_extracts_percentage_as_fraction():
    linha = "[download]  45.2% of   10.00MiB at    1.21MiB/s ETA 00:04"
    assert downloader.parse_progress(linha) == 0.452


def test_parse_progress_handles_whole_number_percentage():
    linha = "[download] 100% of   10.00MiB in 00:00:08"
    assert downloader.parse_progress(linha) == 1.0


def test_parse_progress_returns_none_for_non_progress_line():
    linha = "[ExtractAudio] Destination: song.mp3"
    assert downloader.parse_progress(linha) is None


def test_parse_progress_returns_none_for_empty_line():
    assert downloader.parse_progress("") is None
```

- [ ] **Step 2: Rodar os testes e confirmar que falham**

Run: `pytest tests/test_downloader.py -v`
Expected: FAIL com `AttributeError: module 'downloader' has no attribute 'parse_progress'`

- [ ] **Step 3: Implementar parse_progress**

Adicionar ao final de `src/downloader.py`:

```python
_PROGRESS_RE = re.compile(r"\[download\]\s+(\d+(?:\.\d+)?)%")


def parse_progress(line: str) -> float | None:
    match = _PROGRESS_RE.search(line)
    if match is None:
        return None
    return float(match.group(1)) / 100.0
```

Adicionar `import re` ao bloco de imports no topo de `src/downloader.py`
(junto com `import os` e `import subprocess`, um único bloco no início do
arquivo).

- [ ] **Step 4: Rodar os testes e confirmar que passam**

Run: `pytest tests/test_downloader.py -v`
Expected: `15 passed` (11 já existentes + 4 novos)

- [ ] **Step 5: Commit**

```bash
git add src/downloader.py tests/test_downloader.py
git commit -m "feat: parse download percentage from yt-dlp progress lines"
```

---

### Task 3: theme.py — tokens de cor e render_gradient_pill

**Files:**
- Create: `src/theme.py`
- Create: `tests/test_theme.py`

**Interfaces:**
- Consumes: nada além de `PIL` (Pillow, já instalado via `customtkinter`).
- Produces: constantes de cor listadas nos Global Constraints;
  `theme.render_gradient_pill(width: int, height: int, start_hex: str, end_hex: str) -> PIL.Image.Image` — imagem RGBA `width`×`height`, formato pílula (raio = `height // 2`), gradiente horizontal de `start_hex` a `end_hex`, transparente fora da pílula.

- [ ] **Step 1: Escrever os testes (vão falhar — theme.py ainda não existe)**

Criar `tests/test_theme.py`:

```python
import theme


def test_render_gradient_pill_returns_correct_size():
    image = theme.render_gradient_pill(100, 20, "#FF0000", "#FF4D6D")
    assert image.size == (100, 20)


def test_render_gradient_pill_starts_with_start_color():
    image = theme.render_gradient_pill(100, 20, "#FF0000", "#FF4D6D")
    r, g, b, a = image.getpixel((0, 10))
    assert (r, g, b) == (255, 0, 0)
    assert a == 255


def test_render_gradient_pill_ends_with_end_color():
    image = theme.render_gradient_pill(100, 20, "#FF0000", "#FF4D6D")
    r, g, b, a = image.getpixel((99, 10))
    assert (r, g, b) == (255, 77, 109)
    assert a == 255


def test_render_gradient_pill_is_transparent_outside_pill_corners():
    image = theme.render_gradient_pill(100, 20, "#FF0000", "#FF4D6D")
    r, g, b, a = image.getpixel((0, 0))
    assert a == 0
```

- [ ] **Step 2: Rodar os testes e confirmar que falham**

Run: `pytest tests/test_theme.py -v`
Expected: FAIL com `ModuleNotFoundError: No module named 'theme'`

- [ ] **Step 3: Implementar src/theme.py**

```python
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
```

- [ ] **Step 4: Rodar os testes e confirmar que passam**

Run: `pytest tests/test_theme.py -v`
Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add src/theme.py tests/test_theme.py
git commit -m "feat: add YouTube-dark color tokens and gradient pill renderer"
```

---

### Task 4: theme.py — GradientButton e GradientProgressBar

**Files:**
- Modify: `src/theme.py` (adicionar ao final do arquivo)

**Interfaces:**
- Consumes: `theme.render_gradient_pill`, `theme._hex_to_rgb`, os tokens de cor (Task 3); `customtkinter` (Task 1).
- Produces: `theme.GradientButton(master, text, width, height, command, **kwargs)` — subclasse de `CTkButton`; métodos `set_active(is_active: bool) -> None` (alterna entre pílula em gradiente e pílula cinza sólida, ambas clicáveis) e `set_enabled(enabled: bool) -> None` (habilita/desabilita o clique, mostrando a variante "disabled" quando desabilitado). `theme.GradientProgressBar(master, width, height, **kwargs)` — subclasse de `CTkLabel`; método `set_progress(fraction: float) -> None` (redesenha a barra com a fração preenchida, `0.0`–`1.0`).

- [ ] **Step 1: Implementar GradientButton (adicionar ao final de src/theme.py)**

```python
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

    def _on_enter(self, _event):
        variant = self._current_variant()
        if variant in ("active", "inactive"):
            self.configure(image=self._images[variant + "_hover"])

    def _on_leave(self, _event):
        self.configure(image=self._images[self._current_variant()])

    def set_active(self, is_active: bool) -> None:
        self._is_active = is_active
        self.configure(image=self._images[self._current_variant()])

    def set_enabled(self, enabled: bool) -> None:
        self._is_enabled = enabled
        self.configure(
            state=("normal" if enabled else "disabled"),
            image=self._images[self._current_variant()],
        )
```

Atualizar o bloco de imports no topo de `src/theme.py` para:

```python
import os

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
```

(substituindo a linha `from PIL import Image, ImageDraw` da Task 3 por
este bloco).

- [ ] **Step 2: Implementar GradientProgressBar (adicionar ao final de src/theme.py)**

```python
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
```

- [ ] **Step 3: Verificação manual (sem teste automatizado — widgets de UI, conforme convenção do projeto)**

Rode este script como comando único (não commitar):

```python
import sys
sys.path.insert(0, "src")
import customtkinter as ctk
import theme

root = ctk.CTk()

button = theme.GradientButton(root, text="Baixar", width=200, height=44, command=lambda: None)
button.pack()
button.set_active(False)
button.set_active(True)
button.set_enabled(False)
button.set_enabled(True)

progress = theme.GradientProgressBar(root, width=300, height=8)
progress.pack()
progress.set_progress(0.0)
progress.set_progress(0.5)
progress.set_progress(1.0)

root.update_idletasks()
root.destroy()
print("Widgets constructed and destroyed without error")
```

Expected: imprime `Widgets constructed and destroyed without error`, sem exceção.

- [ ] **Step 4: Commit**

```bash
git add src/theme.py
git commit -m "feat: add GradientButton and GradientProgressBar custom widgets"
```

---

### Task 5: app.py — janela CustomTkinter com progresso

**Files:**
- Modify: `src/app.py` (substituir todo o conteúdo)

**Interfaces:**
- Consumes: `config.load_config`, `config.save_config`; `downloader.build_args`, `downloader.fetch_title`, `downloader.run_download`, `downloader.parse_progress` (Task 2); `theme.BACKGROUND`, `theme.WINDOW_BACKGROUND`, `theme.SURFACE`, `theme.INPUT_BACKGROUND`, `theme.INPUT_BORDER`, `theme.PILL_INACTIVE`, `theme.TEXT_PRIMARY`, `theme.TEXT_SECONDARY`, `theme.GRADIENT_END`, `theme.GradientButton`, `theme.GradientProgressBar` (Tasks 3–4).
- Produces: `app.App`, `app.main()` — sem mudança de interface pública em relação à versão anterior.

- [ ] **Step 1: Substituir todo o conteúdo de src/app.py**

```python
import os
import queue
import threading
from tkinter import StringVar, filedialog

import customtkinter as ctk

import config
import downloader
import theme

MP3_QUALIDADES = ["320", "192", "128"]
MP4_QUALIDADES = ["Melhor", "1080p", "720p", "480p"]

ctk.set_appearance_mode("Dark")


class App:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title("yt-dlp GUI")
        self.root.configure(fg_color=theme.WINDOW_BACKGROUND)

        self.cfg = config.load_config()
        self.pasta_atual = self.cfg["last_folder"]
        self.last_auto_title = ""
        self.log_queue = queue.Queue()

        self._montar_ui()
        self.root.after(100, self._drenar_log)

    def _label(self, parent, texto):
        ctk.CTkLabel(
            parent,
            text=texto.upper(),
            font=("Segoe UI", 11, "bold"),
            text_color=theme.TEXT_SECONDARY,
        ).pack(anchor="w", pady=(0, 6))

    def _montar_ui(self):
        panel = ctk.CTkFrame(self.root, fg_color=theme.BACKGROUND, corner_radius=20)
        panel.pack(padx=24, pady=24, fill="both", expand=True)

        inner = ctk.CTkFrame(panel, fg_color="transparent")
        inner.pack(padx=26, pady=26, fill="both", expand=True)

        ctk.CTkLabel(
            inner, text="▶ yt-dlp GUI", font=("Segoe UI", 16, "bold"), text_color=theme.TEXT_PRIMARY
        ).pack(anchor="w", pady=(0, 16))

        self._label(inner, "Link do vídeo")
        self.link_var = StringVar()
        link_entry = ctk.CTkEntry(
            inner,
            textvariable=self.link_var,
            placeholder_text="Cole o link do YouTube...",
            width=380,
            height=40,
            corner_radius=20,
            fg_color=theme.INPUT_BACKGROUND,
            border_color=theme.INPUT_BORDER,
            border_width=1,
            text_color=theme.TEXT_PRIMARY,
            placeholder_text_color=theme.TEXT_PLACEHOLDER,
        )
        link_entry.pack(fill="x", pady=(0, 14))
        link_entry.bind("<FocusOut>", self._on_link_focus_out)

        self._label(inner, "Formato")
        formato_row = ctk.CTkFrame(inner, fg_color="transparent")
        formato_row.pack(fill="x", pady=(0, 14))
        formato_row.columnconfigure((0, 1), weight=1)

        self.formato_var = StringVar(value="mp3")
        self.mp3_button = theme.GradientButton(
            formato_row, text="MP3", width=180, height=36, command=lambda: self._selecionar_formato("mp3")
        )
        self.mp3_button.grid(row=0, column=0, padx=(0, 6), sticky="ew")
        self.mp4_button = theme.GradientButton(
            formato_row, text="MP4", width=180, height=36, command=lambda: self._selecionar_formato("mp4")
        )
        self.mp4_button.grid(row=0, column=1, padx=(6, 0), sticky="ew")
        self.mp3_button.set_active(True)
        self.mp4_button.set_active(False)

        self.qualidade_var = StringVar()
        self.qualidade_menu = ctk.CTkOptionMenu(
            inner,
            variable=self.qualidade_var,
            values=MP3_QUALIDADES,
            width=380,
            height=36,
            corner_radius=18,
            fg_color=theme.INPUT_BACKGROUND,
            button_color=theme.INPUT_BACKGROUND,
            button_hover_color=theme.SURFACE,
            text_color=theme.TEXT_PRIMARY,
            dropdown_fg_color=theme.INPUT_BACKGROUND,
            dropdown_text_color=theme.TEXT_PRIMARY,
        )
        self.qualidade_menu.pack(fill="x", pady=(0, 14))
        self._atualizar_qualidades()

        self._label(inner, "Nome do arquivo")
        self.nome_var = StringVar()
        ctk.CTkEntry(
            inner,
            textvariable=self.nome_var,
            width=380,
            height=40,
            corner_radius=20,
            fg_color=theme.INPUT_BACKGROUND,
            border_color=theme.INPUT_BORDER,
            border_width=1,
            text_color=theme.TEXT_PRIMARY,
        ).pack(fill="x", pady=(0, 14))

        self._label(inner, "Pasta de destino")
        folder_row = ctk.CTkFrame(inner, fg_color=theme.SURFACE, corner_radius=14)
        folder_row.pack(fill="x", pady=(0, 20))
        self.pasta_label = ctk.CTkLabel(
            folder_row, text=self.pasta_atual, text_color=theme.TEXT_SECONDARY, font=("Segoe UI", 12)
        )
        self.pasta_label.pack(side="left", padx=14, pady=10)
        ctk.CTkButton(
            folder_row,
            text="Trocar",
            fg_color="transparent",
            hover_color=theme.SURFACE,
            text_color=theme.GRADIENT_END,
            width=60,
            command=self._trocar_pasta,
        ).pack(side="right", padx=10)

        self.baixar_button = theme.GradientButton(
            inner, text="Baixar", width=380, height=44, command=self._on_baixar
        )
        self.baixar_button.pack(fill="x", pady=(0, 18))

        status_row = ctk.CTkFrame(inner, fg_color="transparent")
        status_row.pack(fill="x")
        self.status_label = ctk.CTkLabel(
            status_row, text="", text_color=theme.TEXT_SECONDARY, font=("Segoe UI", 12)
        )
        self.status_label.pack(side="left")
        self.percent_label = ctk.CTkLabel(
            status_row, text="", text_color=theme.GRADIENT_END, font=("Segoe UI", 12, "bold")
        )
        self.percent_label.pack(side="right")

        self.progress_bar = theme.GradientProgressBar(inner, width=380, height=7)
        self.progress_bar.pack(fill="x", pady=(8, 0))

    def _selecionar_formato(self, formato):
        self.formato_var.set(formato)
        self.mp3_button.set_active(formato == "mp3")
        self.mp4_button.set_active(formato == "mp4")
        self._atualizar_qualidades()

    def _atualizar_qualidades(self):
        valores = MP3_QUALIDADES if self.formato_var.get() == "mp3" else MP4_QUALIDADES
        self.qualidade_menu.configure(values=valores)
        self.qualidade_var.set(valores[0])

    def _on_link_focus_out(self, event):
        url = self.link_var.get().strip()
        if not url:
            return
        threading.Thread(target=self._buscar_titulo, args=(url,), daemon=True).start()

    def _buscar_titulo(self, url):
        try:
            titulo = downloader.fetch_title(url)
        except FileNotFoundError:
            self.log_queue.put(
                ("status", "Erro: yt-dlp não encontrado no PATH. Instale com 'pip install yt-dlp'.")
            )
            return
        except Exception as exc:
            self.log_queue.put(("status", f"Erro ao buscar título: {exc}"))
            return
        self.root.after(0, self._preencher_nome, titulo)

    def _preencher_nome(self, titulo):
        nome_atual = self.nome_var.get()
        if nome_atual == "" or nome_atual == self.last_auto_title:
            self.nome_var.set(titulo)
            self.last_auto_title = titulo

    def _trocar_pasta(self):
        pasta = filedialog.askdirectory(initialdir=self.pasta_atual)
        if pasta:
            self.pasta_atual = pasta
            self.pasta_label.configure(text=pasta)

    def _on_baixar(self):
        url = self.link_var.get().strip()
        if not url:
            self.log_queue.put(("status", "Erro: cole um link antes de baixar."))
            return

        nome_arquivo = self.nome_var.get().strip() or "video"
        formato = self.formato_var.get()
        qualidade = self.qualidade_var.get()
        pasta = self.pasta_atual

        try:
            os.makedirs(pasta, exist_ok=True)
            config.save_config({"last_folder": pasta})

            self.baixar_button.set_enabled(False)
            args = downloader.build_args(url, formato, qualidade, nome_arquivo, pasta)
        except Exception as exc:
            self.log_queue.put(("status", f"Erro ao preparar o download: {exc}"))
            self.baixar_button.set_enabled(True)
            return

        self.log_queue.put(("progress", 0.0))
        self.log_queue.put(("status", "Baixando..."))
        threading.Thread(target=self._rodar_download, args=(args,), daemon=True).start()

    def _rodar_download(self, args):
        def on_output(linha):
            fracao = downloader.parse_progress(linha)
            if fracao is not None:
                self.log_queue.put(("progress", fracao))

        def on_done(codigo):
            if codigo == 0:
                self.log_queue.put(("progress", 1.0))
                self.log_queue.put(("status", "Concluído."))
            else:
                self.log_queue.put(("status", f"Erro: yt-dlp saiu com código {codigo}."))

        try:
            downloader.run_download(args, on_output=on_output, on_done=on_done)
        except FileNotFoundError:
            self.log_queue.put(
                ("status", "Erro: yt-dlp não encontrado no PATH. Instale com 'pip install yt-dlp'.")
            )
        except Exception as exc:
            self.log_queue.put(("status", f"Erro inesperado: {exc}"))
        finally:
            self.root.after(0, lambda: self.baixar_button.set_enabled(True))

    def _drenar_log(self):
        try:
            while not self.log_queue.empty():
                kind, valor = self.log_queue.get_nowait()
                if kind == "progress":
                    self.progress_bar.set_progress(valor)
                    self.percent_label.configure(text=f"{round(valor * 100)}%")
                elif kind == "status":
                    self.status_label.configure(text=valor)
        finally:
            self.root.after(100, self._drenar_log)


def main():
    root = ctk.CTk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Rodar verificação não interativa**

Run: `python -m py_compile src/app.py`
Expected: sem erro.

Run: `python -c "import sys; sys.path.insert(0, 'src'); import app"`
Expected: sem erro (não abre janela — está protegido por `if __name__ ==
'__main__':`).

Rode este script como comando único (não commitar):

```python
import sys
sys.path.insert(0, "src")
import customtkinter as ctk
import app

root = ctk.CTk()
instance = app.App(root)
root.update_idletasks()
root.destroy()
print("App constructed and destroyed without error")
```

Expected: imprime `App constructed and destroyed without error`, sem
exceção.

- [ ] **Step 3: Checklist manual (rodar `python src/app.py`)**

Marque cada item ao confirmar (esta parte é validada por um humano, não
pela IA — sem ferramenta de automação de GUI disponível):

- [ ] A janela abre com fundo escuro, painel único centralizado, sem
  sidebar, parecido com o mockup aprovado.
- [ ] Botão "Baixar" e a pílula de formato selecionado mostram o
  gradiente vermelho→rosa; passar o mouse por cima troca para a variante
  mais clara (hover).
- [ ] Clicar em MP3/MP4 alterna qual pílula fica com o gradiente e qual
  fica cinza sólida, e atualiza as opções de qualidade.
- [ ] Colar um link e sair do campo preenche "Nome do arquivo" com o
  título do vídeo.
- [ ] Baixar um vídeo mostra a barra de progresso enchendo (gradiente) e
  a porcentagem/status atualizando em tempo real, terminando em
  "Concluído." com a barra cheia.
- [ ] Durante o download, o botão "Baixar" fica desabilitado (variante
  cinza/disabled) e volta ao normal ao terminar.
- [ ] Link inválido ou pasta sem permissão mostra a mensagem de erro na
  linha de status, sem travar o app.
- [ ] Fechar e reabrir o app mantém a última pasta usada.

- [ ] **Step 4: Commit**

```bash
git add src/app.py
git commit -m "feat: rebuild GUI with YouTube-dark CustomTkinter design and progress bar"
```

---

### Task 6: Empacotamento — corrigir build.ps1 para CustomTkinter

**Files:**
- Modify: `build.ps1`

**Interfaces:**
- Consumes: `src/app.py` como ponto de entrada (Task 5).
- Produces: `dist/ytdlp-gui.exe` funcional com CustomTkinter empacotado corretamente.

- [ ] **Step 1: Atualizar build.ps1**

Alterar a linha final de `build.ps1` de:

```powershell
pyinstaller --onefile --windowed --name ytdlp-gui src/app.py
```

para:

```powershell
pyinstaller --onefile --windowed --name ytdlp-gui --collect-all customtkinter src/app.py
```

(as outras linhas do arquivo — bloco `param`, `$ErrorActionPreference`, a
limpeza condicionada a `-Clean` — continuam iguais.)

- [ ] **Step 2: Rodar o build**

Run: `./build.ps1 -Clean`
Expected: termina sem erro e cria `dist/ytdlp-gui.exe`.

- [ ] **Step 3: Smoke test não interativo do .exe**

```powershell
$proc = Start-Process -FilePath "dist/ytdlp-gui.exe" -PassThru
Start-Sleep -Seconds 5
$stillRunning = Get-Process -Id $proc.Id -ErrorAction SilentlyContinue
if ($stillRunning) {
    Write-Output "OK: process still running after 5s (PID $($proc.Id))"
    Stop-Process -Id $proc.Id -Force
} else {
    Write-Output "FAIL: process exited within 5s — check for a startup crash"
}
```

Expected: `OK: process still running after 5s (...)`. Se `FAIL`, o
`.exe` provavelmente está travando por falta dos assets do
CustomTkinter — confirme que `--collect-all customtkinter` foi mesmo
usado no Step 1 e rode `./build.ps1 -Clean` de novo.

- [ ] **Step 4: Repetir o checklist manual do Task 5 (Step 3) contra o .exe compilado**

Run: `./dist/ytdlp-gui.exe`

Repita os mesmos itens do checklist manual do Task 5, agora rodando o
`.exe` diretamente.

- [ ] **Step 5: Commit**

```bash
git add build.ps1
git commit -m "build: collect customtkinter assets when packaging the exe"
```
