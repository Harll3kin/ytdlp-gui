import os
import sys

APP_NAME = "ytdlp-gui"


def data_dir() -> str:
    """Writable per-user folder for config and the updatable yt-dlp copy.

    Never write inside the app bundle: on macOS that invalidates the code
    signature, and in /Applications it is not writable by a normal user.
    """
    if sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    elif os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~\\AppData\\Local")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
    path = os.path.join(base, APP_NAME)
    os.makedirs(path, exist_ok=True)
    return path


def bin_dir() -> str:
    path = os.path.join(data_dir(), "bin")
    os.makedirs(path, exist_ok=True)
    return path


def _videos_root() -> str:
    # macOS names the folder "Movies"; Windows and Linux use "Videos".
    name = "Movies" if sys.platform == "darwin" else "Videos"
    return os.path.join(os.path.expanduser("~"), name)


def assets_dir() -> str:
    """Where MP4 downloads go, so they land next to the editing assets."""
    return os.path.join(_videos_root(), "EDIT", "ASSETS")


def default_download_dir() -> str:
    return os.path.join(assets_dir(), "SFX")
