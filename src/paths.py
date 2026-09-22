"""Writable application data, shared by desktop and Android services."""
import os
from pathlib import Path

APP = 'XSMB_AI_Indicator'


def get_data_dir():
    override = os.environ.get('XSMB_DATA_DIR')
    base = Path(os.environ.get('LOCALAPPDATA') or Path.home() / '.local' / 'share')
    directory = Path(override) if override else base / APP
    directory.mkdir(parents=True, exist_ok=True)
    return directory
