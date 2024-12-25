import ffmpeg
from ffmpeg import Error as ffmpeg_Error
from ..utils import logger
from typing import TypedDict, NotRequired, Literal
from pathlib import Path


class EncodeKwargs(TypedDict):
    video_track_timescale: NotRequired[int]
    vcodec: NotRequired[str]
    video_bitrate: NotRequired[int]
    acodec: NotRequired[str]
    ar: NotRequired[int]
    f: NotRequired[str]


def probe_encoding_info(file_path: Path) -> EncodeKwargs:
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
    logger.info(file_path.name + " probed:", cleaned_None)

    return cleaned_None


def speedup(
    input_file: Path,
    output_file: Path,
    multiple: float | int,
    **othertags,
) -> int:
    logger.info(
        f"speedup {input_file} to {output_file} with speed {multiple} and {othertags = }"
    )
    temp_output_file: Path = output_file.parent / (
        output_file.stem + "_processing_" + output_file.suffix
    )
    try:
        # Speedup the video using ffmpeg-python
        (
            ffmpeg.input(input_file).output(
                str(temp_output_file),
                vf=f"select='not(mod(n,{multiple}))',setpts=N/FRAME_RATE/TB",
                af=f"aselect='not(mod(n,{multiple}))',asetpts=N/SR/TB",
                map=0,
                shortest=None,
                fps_mode="vfr",
                **othertags,
            )
            # ffmpeg.input(input_file)
            # .output(
            #     str(temp_output_file),
            #     vf=f"setpts={1/multiple}*PTS",
            #     af=f"atempo={multiple}",
            #     map=0,
            #     shortest=None,
            #     fps_mode="vfr",
            # )
            .run(),
        )
        temp_output_file.replace(output_file)
    except ffmpeg.Error as e:
        logger.error(f"Failed to speedup videos for {input_file}. Error: {e.stderr}")
        raise e
    return 0


def jumpcut_speedup(
    input_file: Path,
    output_file: Path,
    interval: float | int,
    lasting: float | int,
    multiple: float | int | None = 0,  # unwated part speedup instead of cut
    **othertags,
) -> int:
    temp_output_file: Path = output_file.parent / (
        output_file.stem + "_processing_" + output_file.suffix
    )
    frame_select_expr: str = (
        f"lte(mod(t,{interval}),{lasting})"
        if multiple in (0, None)
        else f"if(lte(mod(t,{interval}),{lasting}),1,not(mod(n,{multiple})))"
    )
    try:
        # Speedup the video using ffmpeg-python
        (
            ffmpeg.input(input_file)
            .output(
                str(temp_output_file),
                vf=f"select='{frame_select_expr}',setpts=N/FRAME_RATE/TB",
                af=f"aselect='{frame_select_expr}',asetpts=N/SR/TB",
                map=0,
                shortest=None,
                fps_mode="vfr",
                **othertags,
            )
            .run()
        )
        temp_output_file.replace(output_file)
    except ffmpeg.Error as e:
        logger.error(f"Failed to speedup videos for {input_file}. Error: {e.stderr}")
        raise e
    return 0


def convert(input_file: Path, output_file: Path, **othertags: EncodeKwargs) -> int:
    temp_output_file: Path = output_file.parent / (
        output_file.stem + "_processing_" + output_file.suffix
    )

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


def merge(input_txt: str, output_file: str | Path) -> int:
    try:
        # Use ffmpeg to concatenate videos
        ffmpeg.input(input_txt, format="concat", safe=0).output(
            str(output_file), c="copy"
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
    input_file: Path | str,
    output_file: Path | str,
    start_time: str,
    end_time: str,
    **othertags: EncodeKwargs,
) -> int:
    try:
        # Re encode the video using ffmpeg-python
        (
            ffmpeg.input(str(input_file), ss=start_time)
            .output(str(output_file), to=end_time, vcodec="copy", acodec="copy", map=0)
            .run()
        )
    except ffmpeg.Error as e:
        logger.error(f"Failed to cut videos for {input_file}. Error: {e.stderr}")
        raise e
    return 0
