from app.viewmodels.mideo_converter import *

def main() -> None:
    
    base_path: LiteralString = os.path.join('H:', 'data', '94f827b4b94e')

    video_files: list[str] = list_video_files(base_path)
    
    grouped_videos: GroupedVideos = group_files_by_date(video_files, 6)
    
    do_merge: int = merge_videos(grouped_videos, base_path)
    
if __name__ == '__main__':
    main()