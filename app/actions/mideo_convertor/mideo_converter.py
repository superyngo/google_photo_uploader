import os
from datetime import datetime, timedelta, date
from typing import LiteralString, TypedDict, Callable
from ...utils import logger
from ...services import ffmpeg_converter
from pathlib import Path


class HandleSpeedup(TypedDict):
    start_hour: int
    end_hour: int


def extract_epoch(filename: str) -> int | None:
    """Function to extract epoch time from filename"""

    try:
        return int(filename.split("_")[1].split(".")[0])
    except (IndexError, ValueError) as e:
        logger.error(f"Failed to extract epoch from {filename}: {str(e)}")
        return None


def list_video_files(
    root_path: str | Path,
    valid_extensions: set[str] | None = None,
    walkthrough: bool = True,
) -> list[Path]:
    if valid_extensions is None:
        valid_extensions = {
            ".mp4",
            ".avi",
            ".mov",
            ".mkv",
        }  # Add more extensions as needed

    root_path = Path(root_path)
    video_files: list[Path] = []

    # Use rglob to recursively find files with the specified extensions
    video_files = (
        [
            file
            for file in root_path.rglob("*")
            if file.is_file() and file.suffix in valid_extensions
        ]
        if walkthrough
        else [
            file
            for file in root_path.iterdir()
            if file.is_file() and file.suffix in valid_extensions
        ]
    )

    return video_files


def get_speedup_range(start_hour: int, end_hour: int) -> range | list[int]:
    # Create the speedup range, handling wrap-around at midnight
    if end_hour >= start_hour:
        return range(start_hour, end_hour + 1)
    else:
        return list(range(start_hour, 25)) + list(range(0, end_hour + 1))


type GroupedVideos = dict[date, dict[int, Path]]


def group_files_by_date(video_files: list[Path], start_hour: int = 0) -> GroupedVideos:
    grouped_files: GroupedVideos = {}

    for video_path in video_files:
        filename: str = os.path.basename(video_path)
        epoch_time: int | None = extract_epoch(filename)
        date_key: str | date

        if epoch_time is None:
            logger.warning(f"skip {filename} with no time.")
            continue
        else:
            file_datetime: datetime = datetime.fromtimestamp(epoch_time)
            if file_datetime.hour < start_hour:
                file_datetime -= timedelta(days=1)
            date_key = file_datetime.date()

        if date_key not in grouped_files:
            grouped_files[date_key] = {}
        grouped_files[date_key].update({epoch_time: video_path})

    return grouped_files


def merge_videos(video_dict: GroupedVideos, save_path: Path, delete_after: bool) -> int:
    """_summary_

    Args:
        video_dict (GroupedVideos): _description_
        save_path (Path): _description_
        delete_after (bool): _description_

    Returns:
        int: _description_
    """
    today: date = datetime.today().date()
    dir_to_delete: set[Path] = set()

    for date_key, videos in video_dict.items():

        if date_key == today:
            logger.info(f"Skipping today's date: {date_key}")
            continue

        # Sort the videos by epoch time
        sorted_videos = dict(sorted(videos.items()))

        # Prepare the input file list for ffmpeg
        input_files: list[Path] = []
        for video_path in sorted_videos.values():
            if ffmpeg_converter.is_valid(video_path):
                input_files.append(video_path)
                dir_to_delete.add(video_path.parent)

        if not input_files:
            logger.info(f"No valid videos found for {date_key}. Skipping.")
            continue

        # Write the input file list for ffmpeg
        with open("input.txt", "w") as f:
            for file in input_files:
                f.write(f"file '{file}'\n")

        # Define the output file path
        output_file: Path = save_path / f"{date_key}.mkv"
        logger.info(f"{output_file = }")
        try:
            # Use ffmpeg to concatenate videos
            ffmpeg_converter.merge("input.txt", output_file)
        except ffmpeg_converter.ffmpeg_Error as e:
            logger.error(
                f"Failed to concatenate videos for {date_key}. Error: {e.stderr.decode()}"
            )
            return 1

        # Remove the temporary input file list
        os.remove("input.txt")

        # Set the file's timestamp to the first video's epoch time
        first_video_epoch = next(iter(sorted_videos))
        os.utime(output_file, (first_video_epoch, first_video_epoch))

        # Clean up original video files and directories
        logger.info("Deleting source videos.")
        if delete_after:
            try:
                for video_path in sorted_videos.values():
                    os.remove(video_path)
                for dir in dir_to_delete:
                    os.rmdir(dir)
            except OSError as e:
                logger.error(
                    f"Failed to delete files or directories for {date_key}: {str(e)}"
                )
                return 2
        dir_to_delete.clear()

        logger.info(
            f"Processed {date_key}, saved to {output_file}, set timestamps, and deleted original files."
        )

    return 0


def speedup_videos(
    input_folder: Path, multiple: int, output_folder_name: str = "speedup"
):
    """_summary_

    Args:
        input_folder (Path): _description_
        multiple (int): _description_
        output_folder_name (str, optional): _description_. Defaults to "speedup".

    Returns:
        _type_: _description_
    """
    output_folder: Path = input_folder / output_folder_name
    output_folder.mkdir(parents=True, exist_ok=True)
    mkv_video_files: list[Path] = list_video_files(input_folder, {".mkv"}, False)
    for video in mkv_video_files:
        original_encode: ffmpeg_converter.EncodeKwargs = (
            ffmpeg_converter.probe_encoding_info(video)
        )
        output_file: Path = output_folder / (video.stem + "_speedup" + video.suffix)
        ffmpeg_converter.speedup(video, output_file, multiple, **original_encode)
        logger.info(
            f"Speeding up video saved to {output_file}, set timestamps as the original file."
        )
    return 0


def merger_handler(
    folder_path: Path,
    start_hour: int = 6,
    delete_after: bool = True,
) -> int:
    """_summary_

    Args:
        folder_path (Path): _description_
        start_hour (int, optional): _description_. Defaults to 6.
        delete_after (bool, optional): _description_. Defaults to True.

    Returns:
        int: _description_
    """
    logger.info(f"Start merging videos in {folder_path}")

    video_files: list[Path] = list_video_files(folder_path)

    grouped_videos: GroupedVideos = group_files_by_date(video_files, start_hour)

    do_merge: int = merge_videos(grouped_videos, folder_path, delete_after)

    return do_merge


def speedup_handler(
    folder_path: Path,
    multiple: int = 50,
) -> int:
    """_summary_

    Args:
        folder_path (Path): _description_
        multiple (int, optional): _description_. Defaults to 50.

    Returns:
        int: _description_
    """
    logger.info(f"Start speeding up videos in {folder_path}")

    do_speedup: int = speedup_videos(folder_path, multiple)

    return do_speedup


def main() -> None:
    """_summary_"""
    handle_speedup: HandleSpeedup = {"start_hour": 23, "end_hour": 5}

    base_path: Path = Path("H:", "data", "94f827b4b94e")

    video_files: list[Path] = list_video_files(base_path)

    grouped_videos: GroupedVideos = group_files_by_date(video_files, 5)

    do_merge: int = merge_videos(grouped_videos, base_path, handle_speedup)


if __name__ == "__main__":
    main()
