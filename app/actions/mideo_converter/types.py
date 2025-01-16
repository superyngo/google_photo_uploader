from typing import TypedDict, NotRequired
from pathlib import Path


class CutSlConfig(TypedDict):
    dB: NotRequired[int]
    sl_duration: NotRequired[float]
    seg_min_duration: NotRequired[float]


class MideoMergerTask(TypedDict):
    folder_path: Path
    start_hour: int
    delete_after: bool


# SpeedupTask
class CutSlSpeedupTask(TypedDict):
    folder_path: Path
    multiple: int | float
    same_encode: NotRequired[bool]
    cut_sl_config: NotRequired[CutSlConfig]
