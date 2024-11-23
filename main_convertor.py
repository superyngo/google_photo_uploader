from app.config.config import handle_speedup, base_path
from app.viewmodels.mideo_converter import *

def main() -> None:

    video_files: list[str] = list_video_files(base_path)

    grouped_videos: GroupedVideos = group_files_by_date(video_files, 5)
    
    do_merge: int = merge_videos(grouped_videos, base_path, handle_speedup)


if __name__ == '__main__':
    main()