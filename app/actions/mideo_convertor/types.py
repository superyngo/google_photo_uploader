from typing import TypedDict, NotRequired


class CutSlConfig(TypedDict):
    dB: NotRequired[int]
    sl_duration: NotRequired[float]
    seg_min_duration: NotRequired[float]
