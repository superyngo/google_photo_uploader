import os
from pathlib import Path
from typing import LiteralString
from enum import StrEnum, auto, Enum
from ..types.types import PathEnum

os.environ["HTTPS_PROXY"] = ""
os.environ["HTTP_PROXY"] = ""
os.environ["PYTHONUTF8"] = "1"


__all__: list[str] = ["Actions", "AppPaths"]


# set app name
APP_NAME: LiteralString = "MideoToGPhoto"


class Actions(StrEnum):
    CONVERTER = auto()
    SPEEDUP = auto()
    UPLOADER = auto()


# set app base path
class AppPaths(PathEnum):
    PROGRAM_DATA = Path(os.environ["PROGRAMDATA"]) / APP_NAME  # C:\ProgramData
    APP_DATA = Path(os.environ["APPDATA"]) / APP_NAME  # C:\Users\user\AppData\Roaming
    CONFIG = APP_DATA / "config.conf"
    LOGS = APP_DATA / "Logs"
