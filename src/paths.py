
from pathlib import Path
import os
APP="XSMB_AI_Indicator"
def get_data_dir():
 base=Path(os.environ.get("LOCALAPPDATA") or (Path.home()/".local"/"share"))
 p=base/APP; p.mkdir(parents=True,exist_ok=True); return p
