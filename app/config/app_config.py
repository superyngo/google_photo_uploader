import os
from pathlib import Path
from typing import LiteralString, TypedDict


os.environ["HTTPS_PROXY"] = ""
os.environ["HTTP_PROXY"] = ""

# set app name
APP_NAME: LiteralString = "MideoToGPhoto"


class _Actions(TypedDict):
    converter: str
    speedup: str
    uploader: str


# actions
ACTIONS: _Actions = {
    "converter": "mideo_converter",
    "speedup": "speedup",
    "uploader": "GPhoto_upload",
}


class _AppPaths(TypedDict):
    program_data: Path
    app_data: Path
    config: Path
    logs: Path


# set app base path
APP_PATHS: _AppPaths = {
    "program_data": (program_data := Path(os.environ["APPDATA"]) / APP_NAME),
    "config": program_data / "config.conf",
    "app_data": (app_data := Path(os.environ["PROGRAMDATA"]) / APP_NAME),
    "logs": app_data / "Logs",
}


# set converter
# HANDLE_SPEEDUP: HandleSpeedup = {'start_hour': 23, 'end_hour': 5}
# BASE_PATH: LiteralString = os.path.join('H:', 'data', '94f827b4b94e')
