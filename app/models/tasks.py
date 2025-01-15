from typing import TypedDict, NotRequired
from pathlib import Path
from ..services.my_driver import MyDriverConfig


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
class CutSlSpeedupTask(TypedDict):
    folder_path: Path
    multiple: int | float
    same_encode: NotRequired[bool]


class UploaderTask(TypedDict):
    name: str
    local_album_path: Path
    GPhoto_url: str
    browser_config: NotRequired[MyDriverConfig]
    delete_after: NotRequired[bool]


# Actions
class AssignmentInfo(TypedDict):
    filename: Path
    selected: NotRequired[set[int]]


class SpeedupInfo(AssignmentInfo):
    assignments: list[CutSlSpeedupTask]


class MideoMergerInfo(AssignmentInfo):
    assignments: list[MideoMergerTask]


class UploaderInfo(AssignmentInfo):
    assignments: list[UploaderTask]
