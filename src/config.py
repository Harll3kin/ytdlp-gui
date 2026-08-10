import json
import os

import paths

DEFAULT_FOLDER = paths.default_download_dir()


def config_path() -> str:
    # Kept in the user data dir: a frozen .app cannot write next to its own
    # executable once it is installed in /Applications.
    return os.path.join(paths.data_dir(), "config.json")


def load_config(path: str | None = None) -> dict:
    path = path or config_path()
    if not os.path.exists(path):
        return {"last_folder": DEFAULT_FOLDER}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"last_folder": DEFAULT_FOLDER}
    if "last_folder" not in data:
        data["last_folder"] = DEFAULT_FOLDER
    return data


def save_config(data: dict, path: str | None = None) -> None:
    path = path or config_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
