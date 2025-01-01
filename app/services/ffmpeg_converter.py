import ffmpeg
from ffmpeg import Error as ffmpeg_Error
from ..utils import logger
from typing import TypedDict, NotRequired
from pathlib import Path
from enum import StrEnum, auto
from collections import deque
from collections.abc import Generator
import re
from enum import Enum
import tempfile
import time
import os
import concurrent.futures


class methods(StrEnum):
    SPEEDUP = auto()
    JUMPCUT = auto()
    CONVERT = auto()
    CUT_SILENCE = auto()
    CUT = auto()
    MERGE = auto()
    PROBE_ENCODING_INFO = auto()
    IS_VALID_VIDEO = auto()


class EncodeKwargs(TypedDict):
    video_track_timescale: NotRequired[int]
    vcodec: NotRequired[str]
    video_bitrate: NotRequired[int]
    acodec: NotRequired[str]
    ar: NotRequired[int]
    f: NotRequired[str]


def gen_filter(
    filter_text: list[str],
    videoSectionTimings: list[float],
) -> Generator[str, None, None]:
    yield filter_text[0]
    yield from (
        f"between(t,{videoSectionTimings[i]},{videoSectionTimings[i + 1]})"
        + ("+" if i != len(videoSectionTimings) - 2 else "")
        for i in range(0, len(videoSectionTimings), 2)
    )
    yield filter_text[1]


def probe_duration(file_path: Path) -> float:
    logger.info(f"Probing {file_path.name} duration")

    probe = ffmpeg.probe(str(file_path))
    s = probe["format"]["duration"]
    logger.info(f"{file_path.name} duration probed: {s}")

    return float(s)


def probe_encoding_info(file_path: Path) -> EncodeKwargs:
    logger.info(f"Probing {file_path.name} encoding info")
    # Probe the video file to get metadata
    probe = ffmpeg.probe(str(file_path))

    # Initialize the dictionary with default values
    encoding_info: EncodeKwargs = {}

    # Extract video stream information
    video_stream = next(
        (stream for stream in probe["streams"] if stream["codec_type"] == "video"), None
    )
    if video_stream:
        encoding_info["video_track_timescale"] = int(
            video_stream.get("time_base").split("/")[1]
        )
        encoding_info["vcodec"] = video_stream.get("codec_name")
        encoding_info["video_bitrate"] = int(video_stream.get("bit_rate", 0))

    # Extract audio stream information
    audio_stream = next(
        (stream for stream in probe["streams"] if stream["codec_type"] == "audio"), None
    )
    if audio_stream:
        encoding_info["acodec"] = audio_stream.get("codec_name")
        encoding_info["ar"] = int(audio_stream.get("sample_rate", 0))

    # Extract format information
    format_info = probe.get("format", {})
    encoding_info["f"] = format_info.get("format_name").split(",")[0]
    cleaned_None = {k: v for k, v in encoding_info.items() if v is not None and v != 0}
    logger.info(f"{file_path.name} probed: {cleaned_None}")

    return cleaned_None


def detect_silence(file_path: Path, dB: int = -35, duration: float = 1) -> deque[float]:
    logger.info(f"Detecting silences in {file_path.name} with {dB = }")

    output = (
        ffmpeg.input(str(file_path))
        .output("null", af=f"silencedetect=n={dB}dB:d={duration}", f="null")
        .run(capture_stdout=True, capture_stderr=True)
    )[1].decode("utf-8")

    # Regular expression to find all floats after "silence_start or end: "
    pattern = r"silence_(?:start|end): ([0-9.]+)"

    # Find all matches in the log data
    matches = re.findall(pattern, output)

    # Convert matches to a list of floats
    silence_end_floats: deque[float] = deque(float(match) for match in matches)

    # Handle silence start and end
    silence_end_floats.appendleft(0.0)
    silence_end_floats.append(float(probe_duration(file_path)))

    return silence_end_floats


def speedup(
    input_file: Path,
    output_file: Path | None,
    multiple: float | int,
    **othertags,
) -> int:
    SPEEDUP_METHOD_THRSHOLD: int = 4

    if output_file is None:
        output_file = input_file.parent / (
            input_file.name + "_" + methods.SPEEDUP + input_file.suffix
        )
    temp_output_file: Path = output_file.parent / (
        output_file.stem + "_processing" + output_file.suffix
    )
    output_kwargs: dict = (
        (
            {  # sepped up with select
                "vf": f"select='not(mod(n,{multiple}))',setpts=N/FRAME_RATE/TB",
                "af": f"aselect='not(mod(n,{multiple}))',asetpts=N/SR/TB",
            }
            if multiple > SPEEDUP_METHOD_THRSHOLD
            else {  # speed up with setpts and atempo
                "vf": f"setpts={1/multiple}*PTS",
                "af": f"atempo={multiple}",
            }
        )
        | {
            "map": 0,
            "shortest": None,
            "fps_mode": "vfr",
        }
        | othertags
    )
    logger.info(
        f"{methods.SPEEDUP} {input_file} to {output_file} with speed {multiple} and {output_kwargs = }"
    )
    try:
        # Speedup the video using ffmpeg-python
        (
            # speed up with select
            ffmpeg.input(input_file)
            .output(
                str(temp_output_file),
                **output_kwargs,
            )
            .run(),
        )
        temp_output_file.replace(output_file)
    except ffmpeg.Error as e:
        logger.error(
            f"Failed to {methods.SPEEDUP} videos for {input_file}. Error: {e.stderr}"
        )
        raise e
    return 0


def jumpcut(
    input_file: Path,
    output_file: Path | None,
    interval: float | int,
    lasting: float | int,
    interval_multiple: float | int = 0,  # 0 means unwated cut out
    lasting_multiple: float | int = 1,  # 0 means unwated cut out
    **othertags,
) -> int:
    if interval <= 0 or lasting <= 0:
        logger.error(f"Both 'interval' and 'lasting' must be greater than 0.")
        return 1
    if output_file is None:
        output_file = input_file.parent / (input_file.name + "_" + input_file.suffix)
    temp_output_file: Path = output_file.parent / (
        output_file.stem + "_processing" + output_file.suffix
    )
    interval_multiple_expr: str | float = (
        f"not(mod(n,{interval_multiple}))"
        if interval_multiple != 0
        else interval_multiple
    )
    lasting_multiple_expr: str | float = (
        f"not(mod(n,{lasting_multiple}))" if lasting_multiple != 0 else lasting_multiple
    )
    frame_select_expr: str = (
        f"if(lte(mod(t,{interval}),{lasting}),{lasting_multiple_expr},{interval_multiple_expr})"
    )
    output_kwargs: dict = {
        "vf": f"select='{frame_select_expr}',setpts=N/FRAME_RATE/TB",
        "af": f"aselect='{frame_select_expr}',asetpts=N/SR/TB",
        "map": 0,
        "shortest": None,
        "fps_mode": "vfr",
    } | othertags
    logger.info(
        f"{methods.JUMPCUT} {input_file} to {output_file} with {output_kwargs = }"
    )
    try:
        # Speedup the video using ffmpeg-python
        (ffmpeg.input(input_file).output(str(temp_output_file), **output_kwargs).run())
        temp_output_file.replace(output_file)
    except ffmpeg.Error as e:
        logger.error(
            f"Failed to {methods.JUMPCUT} videos for {input_file}. Error: {e.stderr}"
        )
        return 2
    return 0


def convert(
    input_file: Path, output_file: Path | None, **othertags: EncodeKwargs
) -> int:
    if output_file is None:
        output_file = input_file.parent / (
            input_file.name + "_" + methods.JUMPCUT + input_file.suffix
        )
    temp_output_file: Path = output_file.parent / (
        output_file.stem + "_processing" + output_file.suffix
    )

    logger.info(f"{methods.CONVERT} {input_file} to {output_file} with {othertags = }")
    try:
        # Speedup the video using ffmpeg-python
        (
            ffmpeg.input(input_file)
            .output(
                str(temp_output_file),
                **othertags,
            )
            .run()
        )
        temp_output_file.replace(output_file)
    except ffmpeg.Error as e:
        logger.error(f"Failed to convert videos for {input_file}. Error: {e.stderr}")
        raise e
    return 0


def merge(input_txt: str, output_file: str | Path, **otherkwargs) -> int:
    logger.info(f"{methods.MERGE} {input_txt} to {output_file} with {otherkwargs = }")

    try:
        # Use ffmpeg to concatenate videos
        ffmpeg.input(input_txt, format="concat", safe=0).output(
            str(output_file), c="copy", **otherkwargs
        ).run()
        return 0
    except ffmpeg.Error as e:
        logger.error(f"Failed merging {input_txt}. Error: {e.stderr.decode()}")
        raise e


def is_valid_video(file_path: Path | str) -> bool:
    """Function to check if a video file is valid using ffprobe."""
    try:
        ffmpeg.probe(file_path)
        message: str = f"Checking file: {file_path}, Status: Valid"
        logger.info(message)
        return True
    except ffmpeg.Error as e:
        message = f"Checking file: {file_path}, Error: {e.stderr.decode()}"
        logger.info(message)
        return False


def cut(
    input_file: Path,
    output_file: Path | None,
    start_time: str,
    end_time: str,
    **othertags: EncodeKwargs,
) -> int:
    """Cut a video file using ffmpeg-python.

    Raises:
        e: _description_

    Returns:
        _type_: _description_
    """
    if output_file is None:
        output_file = input_file.parent / (
            input_file.name + "_" + methods.CUT + input_file.suffix
        )
    temp_output_file: Path = output_file.parent / (
        output_file.stem + "_processing" + output_file.suffix
    )

    output_kwargs: dict = {
        "ss": start_time,
        "to": end_time,
        "vcodec": "copy",
        "acodec": "copy",
        "map": 0,
    } | othertags
    logger.info(f"{methods.CUT} {input_file} to {output_file} with {output_kwargs = }")
    try:
        # Re encode the video using ffmpeg-python
        (
            ffmpeg.input(str(input_file))
            .output(str(temp_output_file), **output_kwargs)
            .run()
        )
        temp_output_file.replace(output_file)
    except ffmpeg.Error as e:
        logger.error(f"Failed to cut videos for {input_file}. Error: {e.stderr}")
        raise e
    return 0


def create_CS_filter_tempfile(
    filter_info: list[str],
    videoSectionTimings: list[float],
) -> Path:
    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", encoding="UTF-8", prefix=filter_info[2]
    ) as temp_file:
        for line in gen_filter(filter_info, videoSectionTimings):
            temp_file.write(f"{line}\n")
        path: Path = Path(temp_file.name)
    return path


def cut_silence(
    input_file: Path,
    output_file: Path = None,
    dB: int = -35,
    duration: float = 0.2,
    **othertags: EncodeKwargs,
) -> int:
    if duration <= 0:
        logger.error(f"Duration must be greater than 0.")
        return 1

    if output_file is None:
        output_file = input_file.parent / (
            input_file.name + "_" + methods.CUT_SILENCE + input_file.suffix
        )
    temp_output_file: Path = output_file.parent / (
        output_file.stem + "_processing" + output_file.suffix
    )
    logger.info(
        f"{methods.CUT_SILENCE} {input_file} to {output_file} with {dB = } ,{duration = } and {othertags = }"
    )

    silences_segment: deque[float] = detect_silence(input_file, dB, duration)

    class CSFiltersInfo(Enum):
        VIDEO = [
            "select='",
            "', setpts=N/FRAME_RATE/TB",
            f"temp_{time.strftime("%Y%m%d-%H%M%S")}_video_filter_",
        ]
        AUDIO = [
            "aselect='",
            "', asetpts=N/SR/TB",
            f"temp_{time.strftime("%Y%m%d-%H%M%S")}_audio_filter_",
        ]

    video_filter_script: Path = create_CS_filter_tempfile(
        CSFiltersInfo.VIDEO.value, silences_segment
    )
    audio_filter_script: Path = create_CS_filter_tempfile(
        CSFiltersInfo.AUDIO.value, silences_segment
    )

    output_kwargs = {
        "filter_script:v": video_filter_script,
        "filter_script:a": audio_filter_script,
    } | othertags

    try:
        (
            ffmpeg.input(str(input_file))
            .output(str(temp_output_file), **output_kwargs)
            .run()
        )
        os.remove(video_filter_script)
        os.remove(audio_filter_script)
        temp_output_file.replace(output_file)
    except ffmpeg.Error as e:
        logger.error(f"Failed to cut silence for {input_file}. Error: {e.stderr}")
        return 2
    return 0


def convert_seconds_to_time(seconds: float) -> str:
    """Converts seconds to HH:MM:SS format."""
    # Convert seconds to hours, minutes, and seconds
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    timestamp = f"{hours:02}:{minutes:02}:{secs:02}.{milliseconds:03}"
    return timestamp


def ensure_minimum_segment_length(
    video_segments: list[float], min_duration: float = 120.0
) -> list[float]:
    """
    Ensures that every segment in the video_segments list is at least min_duration seconds long.

    Args:
        video_segments (List[float]): List of start and end times in seconds.
        min_duration (float): Minimum duration for each segment in seconds (default is 120 seconds).

    Returns:
        List[float]: Updated list of start and end times with adjusted segment durations.
    """
    updated_segments = []
    for i in range(0, len(video_segments), 2):
        start_time = video_segments[i]
        end_time = video_segments[i + 1]
        duration = end_time - start_time
        if duration < min_duration:
            # Calculate the difference between the minimum duration and the current duration
            diff = min_duration - duration
            # Adjust the start and end times to increase the duration to the minimum
            start_time = max(0, start_time - diff / 2)
            end_time = start_time + min_duration
        updated_segments.extend([start_time, end_time])

    return updated_segments


def create_video_segments(
    input_video: str, video_segments: deque[float]
) -> list[list[Path], Path]:
    """
    Cuts the input video into segments
    """
    # Step 1: Validate input
    if len(video_segments) % 2 != 0:
        raise ValueError(
            "video_segments must contain an even number of elements (start and end times)."
        )

    # Step 2: Create a temporary folder for storing cut videos
    temp_dir: Path = Path(tempfile.mkdtemp())
    cut_videos: list[Path] = []  # List to store paths of cut video segments

    # Step 3: Use threading to process video segments
    # Get the number of CPU cores
    num_cores = os.cpu_count()

    # Use ThreadPoolExecutor to manage the threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_cores) as executor:
        futures = []
        for i in range(0, len(video_segments), 2):
            start_time = convert_seconds_to_time(video_segments[i])
            end_time = convert_seconds_to_time(video_segments[i + 1])
            if start_time == end_time:
                continue
            output_path: Path = temp_dir / f"{i // 2}.mp4"
            cut_videos.append(output_path)

            # Submit the cut task to the executor
            future = executor.submit(
                cut, input_video, output_path, start_time, end_time
            )
            futures.append(future)

        # Optionally, wait for all futures to complete
        concurrent.futures.wait(futures)

    # Step 4: Sort the cut video paths by filename (index order)
    cut_videos.sort(key=lambda video_file: int(video_file.stem))

    # Step 5: Create input.txt for FFmpeg concatenation
    input_txt_path: Path = temp_dir / "input.txt"
    with open(input_txt_path, "w") as f:
        for video_path in cut_videos:
            f.write(f"file '{video_path}'\n")
    return [cut_videos, input_txt_path]


def cut_silence2(
    input_file: Path,
    output_file: Path = None,
    dB: int = -35,
    duration: float = 0.2,
    **othertags: EncodeKwargs,
) -> int:
    if duration <= 0:
        logger.error(f"Duration must be greater than 0.")
        return 1

    if output_file is None:
        output_file = input_file.parent / (
            input_file.name + "_" + methods.CUT_SILENCE + input_file.suffix
        )
    temp_output_file: Path = output_file.parent / (
        output_file.stem + "_processing" + output_file.suffix
    )
    logger.info(
        f"{methods.CUT_SILENCE} {input_file} to {output_file} with {dB = } ,{duration = } and {othertags = }"
    )

    silences_segment: deque[float] = detect_silence(input_file, dB, duration)
    updated_segments = ensure_minimum_segment_length(silences_segment)
    videos_segments, input_txt_path = create_video_segments(
        input_file, updated_segments
    )
    try:
        merge(input_txt_path, temp_output_file)
        temp_output_file.replace(output_file)
        # Step 7: Clean up temporary files
        # for video_path in videos_segments:
        #     os.remove(video_path)
        # os.remove(input_txt_path)
        # os.rmdir(input_txt_path.parent)
    except ffmpeg.Error as e:
        logger.error(f"Failed to cut silence for {input_file}. Error: {e.stderr}")
        return 2
    return 0
