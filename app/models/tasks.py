from typing import TypedDict
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
                raise AttributeError(f"'{key}' is not a valid attribute for {self.__class__.__name__}")
    def __getattr__(self, name):
        if name in self.__slots__:
            raise AttributeError(f"'{name}' was not set during initialization")
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

class MideoMerger(TypedDict):
    name: str
    folder: Path
    start_hour: int
    delete_after: bool

class speedup(TypedDict):
    name: str
    folder: Path
    multiple: int

class GPhotoUploader(TypedDict):
    name: str
    profile: Path
    local_album: Path
    GPhoto_url: str




