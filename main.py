from app import mideo_converter
from app import config
from app.models.tasks import MideoMergerTask, CutSlSpeedupTask
from pathlib import Path
from app.utils import logger
from app.services import ffmpeg_converter
import ffmpeg


file_path = Path(r"C:\Users\user\Downloads\2025-01-07_1736200862.mp4")
file_path = Path(
    r"D:\Users\user\OneDrive - Chunghwa Telecom Co., Ltd\文件\Projects\Python\sample\IMG_1117_1735874716.mp4"
)

ffmpeg_converter.cut_silence(file_path, None, -25, 0.2, 2)


class MyIter:
    def __init__(self):
        self._start = 0

    def __iter__(self):
        return iter([1, 2, 3])

    def __next__(self):
        if self._start < 10:
            self._start += 1
            return self._start
        else:
            raise StopIteration


if __name__ == "__main__":

    a = MyIter()
    for i in a:
        print(i)

    # Set a breakpoint
    pdb.set_trace()
