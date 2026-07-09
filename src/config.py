import json
import os
import sys

DEFAULT_FOLDER = os.path.join(
    os.path.expanduser("~"), "Videos", "EDIT", "ASSETS", "SFX"
)


def config_path() -> str:
    if getattr(sys, "frozen", False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, "config.json")


def load_config(path: str | None = None) -> dict:
    path = path or config_path()
    if not os.path.exists(path):
        return {"last_folder": DEFAULT_FOLDER}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "last_folder" not in data:
        data["last_folder"] = DEFAULT_FOLDER
    return data


def save_config(data: dict, path: str | None = None) -> None:
    path = path or config_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
