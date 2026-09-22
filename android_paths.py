"""Configure private persistent storage before importing the backend."""
import os
import sys
from pathlib import Path


def setup_android_paths():
    root = Path(__file__).resolve().parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    if not (sys.platform == 'android' or 'ANDROID_ARGUMENT' in os.environ):
        return False
    from android.storage import app_storage_path
    private = Path(app_storage_path())
    for name in ('data', 'exports'):
        directory = private / name
        directory.mkdir(parents=True, exist_ok=True)
        os.environ['XSMB_' + name.upper() + '_DIR'] = str(directory)
    return True


IS_ANDROID = setup_android_paths()
