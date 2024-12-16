from typing import TypedDict, NotRequired
from pathlib import Path


class CsBasicComponent:
    def __getattr__(self, name):
        raise AttributeError(f"'{self.__class__.__name__}' '{name}' was not set")


class MyDataclass:
    def __init__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if key in self.__slots__:
                setattr(self, key, value)
            else:
                raise AttributeError(
                    f"'{key}' is not a valid attribute for {self.__class__.__name__}"
                )

    def __getattr__(self, name):
        if name in self.__slots__:
            raise AttributeError(f"'{name}' was not set during initialization")
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )


# MideoMergerTask
class MideoMergerTask(TypedDict):
    folder_path: Path
    start_hour: int
    delete_after: bool


# SpeedupTask
class SpeedupTask(TypedDict):
    folder_path: Path
    multiple: int


# UploaderSession
class UploaderTask(TypedDict):
    local_album: Path
    GPhoto_url: str


class UploaderSession(TypedDict):
    name: str
    profile: Path
    chrome_path: Path | None
    tasks: list[UploaderTask]


# Actions
class AssignmentInfo(TypedDict):
    filename: str
    selected: set[int] | None


class UploaderInfo(AssignmentInfo):
    action: list[UploaderSession]


class SpeedupInfo(AssignmentInfo):
    action: list[SpeedupTask]


class MideoMergerInfo(AssignmentInfo):
    action: list[MideoMergerTask]
