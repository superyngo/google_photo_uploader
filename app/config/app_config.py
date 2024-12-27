import os
from pathlib import Path
from typing import LiteralString, TypedDict
from enum import StrEnum, Enum, auto
from ..types.types import PathEnum


os.environ["HTTPS_PROXY"] = ""
os.environ["HTTP_PROXY"] = ""

# set app name
APP_NAME: LiteralString = "MideoToGPhoto"


class Actions(StrEnum):
    CONVERTOR: str = "mideo_converter"
    SPEEDUP: str = "speedup"
    UPLOADER: str = "GPhoto_upload"


class AppPaths(PathEnum):
    PROGRAM_DATA: Path = Path(os.environ["APPDATA"]) / APP_NAME
    APP_DATA: Path = PROGRAM_DATA / "config.conf"
    CONFIG: Path = Path(os.environ["PROGRAMDATA"]) / APP_NAME
    LOGS: Path = APP_DATA / "Logs"


# set app base path
APP_PATHS = {
    "program_data": (program_data := Path(os.environ["APPDATA"]) / APP_NAME),
    "config": program_data / "config.conf",
    "app_data": (app_data := Path(os.environ["PROGRAMDATA"]) / APP_NAME),
    "logs": app_data / "Logs",
}


# set converter
# HANDLE_SPEEDUP: HandleSpeedup = {'start_hour': 23, 'end_hour': 5}
# BASE_PATH: LiteralString = os.path.join('H:', 'data', '94f827b4b94e')
