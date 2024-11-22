from app.viewmodels.mideo_converter import *
from app.config.config import handle_speedup

def main() -> None:

    base_path: LiteralString = os.path.join('H:', 'data', '94f827b4b94e')

    video_files: list[str] = list_video_files(base_path)

    if handle_speedup['value']:
        video_files_speedup: list[str] = mark_speedup(video_files)
        for video_path in video_files_speedup:
            do_speedup: int = speedup_videos(video_path, 100)

    grouped_videos: GroupedVideos = group_files_by_date(video_files, 5)
    
    do_merge: int = merge_videos(grouped_videos, base_path)


if __name__ == '__main__':
    main()