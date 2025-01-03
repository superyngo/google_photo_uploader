import ffmpeg
from ffmpeg import Error as ffmpeg_Error
from ..utils import logger
from typing import TypedDict, NotRequired, Sequence, Any
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


__ALL__: list[str] = [
    "probe_duration",
    "probe_encoding_info",
    "detect_silence",
    "speedup",
    "jumpcut",
    "convert",
    "merge",
    "cut",
    "cut_silence",
    "cut_silence_render",
    "EncodeKwargs",
]


class EncodeKwargs(TypedDict):
    video_track_timescale: NotRequired[int]
    vcodec: NotRequired[str]
    video_bitrate: NotRequired[int]
    acodec: NotRequired[str]
    ar: NotRequired[int]
    f: NotRequired[str]


def _gen_filter(
    filter_text: Sequence[str],
    videoSectionTimings: Sequence[float],
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


def detect_silence(
    file_path: Path, dB: int = -35, sl_duration: float = 1
) -> tuple[Sequence[float], float, float]:
    logger.info(f"Detecting silences in {file_path.name} with {dB = }")

    output = (
        ffmpeg.input(str(file_path))
        .output("null", af=f"silencedetect=n={dB}dB:d={sl_duration}", f="null")
        .run(capture_stdout=True, capture_stderr=True)
    )[1].decode("utf-8")

    # Regular expression to find all floats after "silence_start or end: "
    silence_seg_pattern = r"silence_(?:start|end): ([0-9.]+)"

    # Find all matches in the log data
    silence_seg_matches: list[float] = re.findall(silence_seg_pattern, output)

    # Convert matches to a list of floats
    silence_end_floats: deque[float] = deque(
        float(match) for match in silence_seg_matches
    )

    # Handle silence start and end
    silence_end_floats.appendleft(0.0)
    silence_end_floats.append(float(probe_duration(file_path)))

    # Regular expression to find all floats after silence_duration: "
    silence_duration_pattern = r"silence_duration: ([0-9.]+)"
    silence_duration_matches: list[float] = re.findall(silence_duration_pattern, output)

    total_silence_duration: float = sum(silence_duration_matches)
    total_duration_pattern = r"Duration: (^\d{2}:\d{2}:\d{2}\.\d{1,3}$)"

    return (silence_end_floats, total_silence_duration)


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
        | {  # common tags
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
        do = (
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
            input_file.name + "_" + methods.CONVERT + input_file.suffix
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


def merge(input_txt: Path, output_file: Path, **otherkwargs) -> int:
    logger.info(f"{methods.MERGE} {input_txt} to {output_file} with {otherkwargs = }")

    try:
        # Use ffmpeg to concatenate videos
        ffmpeg.input(str(input_txt), format="concat", safe=0).output(
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


def _create_cut_sl_filter_tempfile(
    filter_info: Sequence[str],
    videoSectionTimings: Sequence[float],
) -> Path:
    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", encoding="UTF-8", prefix=filter_info[2]
    ) as temp_file:
        for line in _gen_filter(filter_info, videoSectionTimings):
            temp_file.write(f"{line}\n")
        path: Path = Path(temp_file.name)
    return path


def cut_silence_render(
    input_file: Path,
    output_file: Path | None = None,
    dB: int = -30,
    sl_duration: float = 0.2,
    **othertags: EncodeKwargs,
) -> int:
    if sl_duration <= 0:
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
        f"{methods.CUT_SILENCE} {input_file} to {output_file} with {dB = } ,{sl_duration = } and {othertags = }"
    )

    silences_segment: Sequence[float] = detect_silence(input_file, dB, sl_duration)[0]

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

    video_filter_script: Path = _create_cut_sl_filter_tempfile(
        CSFiltersInfo.VIDEO.value, silences_segment
    )
    audio_filter_script: Path = _create_cut_sl_filter_tempfile(
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


def _convert_seconds_to_time(seconds: float) -> str:
    """Converts seconds to HH:MM:SS format."""
    # Convert seconds to hours, minutes, and seconds
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    timestamp = f"{hours:02}:{minutes:02}:{secs:02}.{milliseconds:03}"
    return timestamp


def _ensure_minimum_segment_length(
    video_segments: Sequence[float], seg_min_duration: float = 2
) -> list[float]:
    """
    Ensures that every segment in the video_segments list is at least seg_min_duration seconds long.

    Args:
        video_segments (list[float]): List of start and end times in seconds.
        seg_min_duration (float, optional): Minimum duration for each segment in seconds. Defaults to 2.

    Raises:
        ValueError: If video_segments does not contain pairs of start and end times.

    Returns:
        list[float]: Updated list of start and end times with adjusted segment durations.
    """
    if len(video_segments) % 2 != 0:
        raise ValueError("video_segments must contain pairs of start and end times.")

    updated_segments = []
    for i in range(0, len(video_segments), 2):
        start_time = video_segments[i]
        end_time = video_segments[i + 1]
        duration = end_time - start_time

        if duration >= seg_min_duration or len(video_segments) == 2:
            updated_segments.extend([start_time, end_time])
            continue

        if i == len(video_segments) - 2:
            # This is the last segment
            start_time = max(0, end_time - seg_min_duration)
        else:
            # Calculate the difference between the minimum duration and the current duration
            diff = seg_min_duration - duration
            # Adjust the start and end times to increase the duration to the minimum
            start_time = max(0, start_time - diff / 2)
            end_time = max(start_time + seg_min_duration, video_segments[-1])

        updated_segments.extend([start_time, end_time])

    # Ensure the hole video is long enough
    if updated_segments[-1] - updated_segments[1] < seg_min_duration:
        return []

    return updated_segments


def _merge_overlapping_segments(segments: Sequence[float]) -> Sequence[float]:
    # Sort segments by start time
    sorted_segments = sorted(
        (segments[i], segments[i + 1]) for i in range(0, len(segments), 2)
    )
    if len(sorted_segments) == 0:
        return []

    merged_segments = []
    current_start, current_end = sorted_segments[0]

    for start, end in sorted_segments[1:]:
        if start <= current_end:
            # Overlapping segments, merge them
            current_end = max(current_end, end)
        else:
            # No overlap, add the current segment and move to the next
            merged_segments.extend([current_start, current_end])
            current_start, current_end = start, end

    # Add the last segment
    merged_segments.extend([current_start, current_end])

    return merged_segments


def create_video_segments(
    input_video: Path, video_segments: Sequence[float]
) -> tuple[Sequence[Path], Path]:
    """
    Cuts the input video into segments based on the provided start and end times.s
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
            start_time = _convert_seconds_to_time(video_segments[i])
            end_time = _convert_seconds_to_time(video_segments[i + 1])
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
    return (cut_videos, input_txt_path)


def cut_silence(
    input_file: Path,
    output_file: Path | None = None,
    dB: int = -30,
    sl_duration: float = 0.2,
    seg_min_duration: float = 3,
    **othertags: EncodeKwargs,
) -> int:
    if sl_duration <= 0:
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
        f"{methods.CUT_SILENCE} {input_file} to {output_file} with {dB = } ,{sl_duration = }, {seg_min_duration = } and {othertags = }"
    )

    silences_segment: Sequence[float] = detect_silence(input_file, dB, sl_duration)[0]
    updated_segments = _merge_overlapping_segments(
        _ensure_minimum_segment_length(silences_segment, seg_min_duration)
    )
    if updated_segments == []:
        pass

    videos_segments: Sequence[Path]
    input_txt_path: Path

    videos_segments, input_txt_path = create_video_segments(
        input_file, updated_segments
    )
    try:
        merge(input_txt_path, temp_output_file)
        temp_output_file.replace(output_file)
        # Step 7: Clean up temporary files
        for video_path in videos_segments:
            os.remove(video_path)
        os.remove(input_txt_path)
        os.rmdir(input_txt_path.parent)
    except ffmpeg.Error as e:
        logger.error(f"Failed to cut silence for {input_file}. Error: {e.stderr}")
        return 2
    return 0
