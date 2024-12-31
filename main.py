from pathlib import Path
import pdb
from app.services import ffmpeg_converter

filename = Path(
    r"D:\Users\user\OneDrive - Chunghwa Telecom Co., Ltd\文件\Projects\Python\sample\output.mp4"
)
output = r"D:\Users\user\OneDrive - Chunghwa Telecom Co., Ltd\文件\Projects\Python\sample\IMG_1117_cut.mp4"
ffmpeg_converter.cut_silence(filename)
# Your script code here
print("This is a script in debug mode.")


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
