from pathlib import Path
import pdb
from app.services import ffmpeg_converter
import ffmpeg
from collections import deque

dB = -35
duration = 0.2
filename = Path(r"C:\Users\user\Downloads\2025-01-01.mp4_cut_silence.mp4")
output = Path(r"F:\Users\user\Downloads\IMG_1174_cut.mp4")
# ffmpeg_converter.cut_silence(filename)
# silences_segment: deque[float] = ffmpeg_converter.detect_silence(
#     input_file, dB, duration
# )
# update1 = ffmpeg_converter.ensure_minimum_segment_length(silences_segment)
# updated_segments = ffmpeg_converter.merge_overlapping_segments(update1)
ffmpeg_converter.cut_silence2(filename, None, -30, 0.2)
start_time = "00:00:14"
end_time = "00:00:16"
ffmpeg_converter.cut(filename, None, start_time, end_time)
ffmpeg.input(str(filename), ss=start_time).output(str(output), to=end_time).run()

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
