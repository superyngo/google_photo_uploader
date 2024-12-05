import os
from pathlib import Path
from app.viewmodels.mideo_converter import HandleSpeedup
from typing import LiteralString, TypedDict


os.environ['HTTPS_PROXY'] = ''
os.environ['HTTP_PROXY'] = ''

# set app name
APP_NAME:LiteralString = 'MideoToGPhoto'

# set app base path
APP_BASE_DIR: Path = Path.home() / 'AppData' / 'Roaming' / APP_NAME.lower()
CONFIG_PATH: Path = APP_BASE_DIR / 'config.conf'
SESSIONS_DIR: Path = APP_BASE_DIR / 'sessions'

class _ACTIONS(TypedDict):
    converter: str
    speedup: str
    uploader: str
# actions
ACTIONS: _ACTIONS = {
    'converter': 'mideo_converter',
    'speedup': 'speedup',
    'uploader': 'GPhoto_upload'
}

# set converter
# HANDLE_SPEEDUP: HandleSpeedup = {'start_hour': 23, 'end_hour': 5}
# BASE_PATH: LiteralString = os.path.join('H:', 'data', '94f827b4b94e')


