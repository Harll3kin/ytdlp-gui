import json
import os

import config


def test_load_config_returns_default_when_file_missing(tmp_path):
    path = os.path.join(tmp_path, "config.json")

    result = config.load_config(path)

    assert result == {"last_folder": config.DEFAULT_FOLDER}


def test_save_then_load_config_roundtrip(tmp_path):
    path = os.path.join(tmp_path, "config.json")

    config.save_config({"last_folder": "D:\\Downloads"}, path)
    result = config.load_config(path)

    assert result == {"last_folder": "D:\\Downloads"}


def test_load_config_fills_missing_last_folder_key(tmp_path):
    path = os.path.join(tmp_path, "config.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({}, f)

    result = config.load_config(path)

    assert result == {"last_folder": config.DEFAULT_FOLDER}
