from app import mideo_converter
from app import config


def main() -> None:

    video_files: list[str] = mideo_converter.list_video_files(config.BASE_PATH)

    grouped_videos: mideo_converter.GroupedVideos = mideo_converter.group_files_by_date(
        video_files, 5
    )

    do_merge: int = mideo_converter.merge_videos(
        grouped_videos, base_path, handle_speedup
    )


if __name__ == "__main__":
    main()
