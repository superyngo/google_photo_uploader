import ffmpeg
from ffmpeg import Error as ffmpeg_Error
from ..utils import logger
from typing import TypedDict, NotRequired, Literal
from pathlib import Path
from enum import StrEnum, auto
from collections import deque
import re


class methods(StrEnum):
    SPEEDUP = auto()
    JUMPCUT = auto()
    CONVERT = auto()
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


def detect_silence(file_path: Path, dB=-35, lasting=1) -> deque[float]:
    logger.info(f"Detecting silences in {file_path.name} with {dB = }")

    output = (
        ffmpeg.input(str(file_path))
        .output("null", af=f"silencedetect=n={dB}dB:d={lasting}", f="null")
        .run(capture_stdout=True, capture_stderr=True)
    )[1].decode("utf-8")

    # Regular expression to find all floats after "silence_start or end: "
    pattern = r"silence_(?:start|end): (\d+\.\d+|\d+)"

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
        output_file.stem + "_processing_" + output_file.suffix
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
        output_file = input_file.parent / (
            input_file.name + "_" + methods.JUMPCUT + input_file.suffix
        )
    temp_output_file: Path = output_file.parent / (
        output_file.stem + "_processing_" + output_file.suffix
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
        output_file.stem + "_processing_" + output_file.suffix
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
    if output_file is None:
        output_file = input_file.parent / (
            input_file.name + "_" + methods.JUMPCUT + input_file.suffix
        )
    temp_output_file: Path = output_file.parent / (
        output_file.stem + "_processing_" + output_file.suffix
    )

    output_kwargs: dict = {
        "to": end_time,
        "vcodec": "copy",
        "acodec": "copy",
        "map": 0,
    } | othertags
    logger.info(f"{methods.CUT} {input_file} to {output_file} with {output_kwargs = }")
    try:
        # Re encode the video using ffmpeg-python
        (
            ffmpeg.input(str(input_file), ss=start_time)
            .output(str(output_file), **output_kwargs)
            .run()
        )
    except ffmpeg.Error as e:
        logger.error(f"Failed to cut videos for {input_file}. Error: {e.stderr}")
        raise e
    return 0


def cut_silence(file_path: Path, dB=-35, lasting=1, **othertags: EncodeKwargs) -> int:
    silences: deque[float] = detect_silence(file_path, dB, lasting)
    videoFilter = getFileContent_videoFilter(silences)
    audioFilter = getFileContent_audioFilter(silences)
    ffmpeg_run(infile, videoFilter, audioFilter, outfile)

    pass
