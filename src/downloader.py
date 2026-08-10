import gzip
import os
import re
import shutil
import subprocess
import sys

import paths

IS_WINDOWS = os.name == "nt"


def _no_window_kwargs() -> dict:
    """subprocess.CREATE_NO_WINDOW is defined only on Windows.

    Referencing it on macOS/Linux raises AttributeError, so it must never be
    passed unconditionally.
    """
    if IS_WINDOWS:
        return {"creationflags": subprocess.CREATE_NO_WINDOW}
    return {}


def _bundled_path(*names: str) -> str | None:
    """Locate a binary shipped inside the frozen app, if any.

    PyInstaller puts --add-binary payloads under sys._MEIPASS, which is not the
    same directory as sys.executable. In a macOS .app they may also land in
    Contents/Resources, so both layouts are checked.
    """
    if not getattr(sys, "frozen", False):
        return None

    exe_dir = os.path.dirname(sys.executable)
    roots = [
        getattr(sys, "_MEIPASS", None),
        exe_dir,
        os.path.join(exe_dir, "..", "Frameworks"),
        os.path.join(exe_dir, "..", "Resources"),
    ]
    for root in roots:
        if not root:
            continue
        for name in names:
            candidate = os.path.normpath(os.path.join(root, name))
            if os.path.exists(candidate):
                return candidate
    return None


# Shipped gzipped: yt-dlp is itself a PyInstaller onefile executable with an
# archive appended past the end of the Mach-O, and code signing rewrites nested
# executables, which corrupts it. A .gz is not executable code, so nothing in
# the packaging pipeline touches it.
BUNDLED_YTDLP_GZ = _bundled_path("yt-dlp.gz")
BUNDLED_YTDLP = _bundled_path("yt-dlp.exe", "yt-dlp")
FFMPEG_LOCATION = _bundled_path("ffmpeg.exe", "ffmpeg")

MP4_HEIGHT_LIMITS = {
    "Best": None,
    "1080p": 1080,
    "720p": 720,
    "480p": 480,
}

ILLEGAL_FILENAME_CHARS = '\\/:*?"<>|'

_ytdlp_executable: str | None = None


def _make_executable(path: str) -> None:
    try:
        os.chmod(path, os.stat(path).st_mode | 0o111)
    except OSError:
        pass


def _extract_bundled_ytdlp(target: str) -> None:
    """Materialise the bundled yt-dlp at `target`, byte for byte.

    Written to a temporary file first so an interrupted launch cannot leave a
    truncated executable behind.
    """
    partial = target + ".part"
    if BUNDLED_YTDLP_GZ is not None:
        with gzip.open(BUNDLED_YTDLP_GZ, "rb") as src, open(partial, "wb") as dst:
            shutil.copyfileobj(src, dst)
    else:
        shutil.copyfile(BUNDLED_YTDLP, partial)
    os.replace(partial, target)


def _resolve_ytdlp() -> str:
    """Return the yt-dlp to run, preferring a writable copy of the bundled one.

    `yt-dlp -U` rewrites its own binary. Inside the app bundle that would break
    the code signature, and /Applications is not user-writable, so the bundled
    binary is unpacked once into the user data dir and updated there.
    """
    if BUNDLED_YTDLP_GZ is None and BUNDLED_YTDLP is None:
        return "yt-dlp"

    target = os.path.join(paths.bin_dir(), "yt-dlp.exe" if IS_WINDOWS else "yt-dlp")
    if not os.path.exists(target):
        try:
            _extract_bundled_ytdlp(target)
        except OSError:
            return BUNDLED_YTDLP or "yt-dlp"
    _make_executable(target)
    return target


def ytdlp_executable() -> str:
    global _ytdlp_executable
    if _ytdlp_executable is None:
        _ytdlp_executable = _resolve_ytdlp()
    return _ytdlp_executable


def sanitize_filename(nome: str) -> str:
    return "".join("_" if c in ILLEGAL_FILENAME_CHARS else c for c in nome)


def mp4_format_selector(qualidade: str) -> str:
    """Prefer H.264 (avc1): Premiere Pro cannot read AV1 or VP9.

    YouTube serves AV1 for many modern uploads, which is what produces the
    "unsupported compression type av01" error on import.
    """
    height = MP4_HEIGHT_LIMITS.get(qualidade)
    limit = f"[height<={height}]" if height else ""
    return (
        f"bestvideo[vcodec^=avc1]{limit}+bestaudio[acodec^=mp4a]/"
        f"bestvideo[vcodec^=avc1]{limit}+bestaudio/"
        f"best[vcodec^=avc1]{limit}/"
        f"bestvideo{limit}+bestaudio/best{limit}"
    )


def build_args(url: str, formato: str, qualidade: str, nome_arquivo: str, pasta: str) -> list[str]:
    output_template = os.path.join(pasta, f"{sanitize_filename(nome_arquivo)}.%(ext)s")
    args = [ytdlp_executable(), "-o", output_template]
    if FFMPEG_LOCATION is not None:
        args += ["--ffmpeg-location", FFMPEG_LOCATION]

    if formato == "mp3":
        args += ["-x", "--audio-format", "mp3", "--audio-quality", qualidade]
    elif formato == "mp4":
        args += ["-f", mp4_format_selector(qualidade)]
        args += ["--merge-output-format", "mp4"]
    else:
        raise ValueError(f"Unknown format: {formato}")

    args.append(url)
    return args


def update_ytdlp() -> tuple[bool, str]:
    """Refresh the managed yt-dlp copy. Never raises; failure is not fatal.

    YouTube breaks older yt-dlp releases regularly (HTTP 403), so this runs at
    startup rather than being left to the user.
    """
    try:
        result = subprocess.run(
            [ytdlp_executable(), "-U"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
            **_no_window_kwargs(),
        )
    except FileNotFoundError:
        return False, "yt-dlp not found. Install it with 'pip install yt-dlp'."
    except subprocess.TimeoutExpired:
        return False, "yt-dlp update timed out; using the current version."

    if result.returncode != 0:
        return False, "Could not update yt-dlp; using the current version."
    return True, "yt-dlp is up to date."


def fetch_title(url: str) -> str:
    result = subprocess.run(
        [ytdlp_executable(), "--get-title", url],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        **_no_window_kwargs(),
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Failed to fetch the video title.")
    return result.stdout.strip()


def run_download(args, on_output, on_done):
    process = subprocess.Popen(
        args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding="utf-8",
        errors="replace",
        **_no_window_kwargs(),
    )
    for line in process.stdout:
        on_output(line.rstrip("\n"))
    process.wait()
    on_done(process.returncode)


_PROGRESS_RE = re.compile(r"\[download\]\s+(\d+(?:\.\d+)?)%")


def parse_progress(line: str) -> float | None:
    match = _PROGRESS_RE.search(line)
    if match is None:
        return None
    return float(match.group(1)) / 100.0
