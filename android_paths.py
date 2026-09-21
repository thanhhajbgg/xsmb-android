"""Đường dẫn riêng cho Android — gọi setup_android_paths() TRƯỚC khi import src.*"""
import os
import sys
from pathlib import Path

_IS_ANDROID = hasattr(sys, "getandroidapilevel") or "ANDROID_ARGUMENT" in os.environ
_APP_DIR = None


def is_android() -> bool:
    return _IS_ANDROID


def app_data_dir() -> Path:
    global _APP_DIR
    if _APP_DIR is not None:
        return _APP_DIR
    if _IS_ANDROID:
        base = os.environ.get("ANDROID_PRIVATE") or os.environ.get("ANDROID_APP_PATH") or str(Path.home())
        _APP_DIR = Path(base) / "xsmb_data"
    else:
        base = os.environ.get("LOCALAPPDATA") or str(Path.home())
        _APP_DIR = Path(base) / "XSMB_AI_Indicator"
    _APP_DIR.mkdir(parents=True, exist_ok=True)
    return _APP_DIR


def db_path() -> Path:
    return app_data_dir() / "xsmb.db"


def log_path() -> Path:
    return app_data_dir() / "app_v2.log"


def setup_android_paths() -> None:
    if not _IS_ANDROID:
        return
    base = str(app_data_dir())
    os.environ.setdefault("XSMB_DATA_DIR", base)
    os.environ.setdefault("HOME", base)
    os.environ.setdefault("TMPDIR", base)