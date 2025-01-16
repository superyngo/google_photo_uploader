import os
from pathlib import Path
from typing import LiteralString
from enum import StrEnum, auto
from ..types.types import PathEnum


os.environ["HTTPS_PROXY"] = ""
os.environ["HTTP_PROXY"] = ""

# set app name
APP_NAME: LiteralString = "MideoToGPhoto"


class Actions(StrEnum):
    CONVERTOR = auto()
    SPEEDUP = auto()
    UPLOADER = auto()


# set app base path
class AppPaths(PathEnum):
    PROGRAM_DATA = Path(os.environ["PROGRAMDATA"]) / APP_NAME  # C:\ProgramData
    APP_DATA = Path(os.environ["APPDATA"]) / APP_NAME  # C:\Users\user\AppData\Roaming
    CONFIG = APP_DATA / "config.conf"
    LOGS = APP_DATA / "Logs"


# set converter
# HANDLE_SPEEDUP: HandleSpeedup = {'start_hour': 23, 'end_hour': 5}
# BASE_PATH: LiteralString = os.path.join('H:', 'data', '94f827b4b94e')
