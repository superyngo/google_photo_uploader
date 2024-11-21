import os
from datetime import datetime, timedelta
from typing import LiteralString
import ffmpeg
from app.utils.logger import logger
type GroupedVideos = dict[str, dict[int,str]]

# Function to extract epoch time from filename
def extract_epoch(filename: str) -> int | None:
    try:
        return int(filename.split('_')[1].split('.')[0])
    except (IndexError, ValueError) as e:
        logger.error(f"Failed to extract epoch from {filename}: {str(e)}")
        return None

def list_video_files(root_path: str, valid_extensions: set[str]|None=None) -> list[str]: 
    if valid_extensions is None:
        valid_extensions = {'.mp4', '.avi', '.mov', '.mkv'}  # Add more extensions as needed

    video_files: list[str] = []
    for dirpath, _, filenames in os.walk(root_path):
        for filename in filenames:
            if any(filename.lower().endswith(ext) for ext in valid_extensions):
                video_files.append(os.path.join(dirpath, filename))
    
    return video_files

def group_files_by_date(video_files: list[str], start_hour: int=0) -> GroupedVideos:
    grouped_files: GroupedVideos = {}

    for video_path in video_files:
        filename: str = os.path.basename(video_path)
        epoch_time: int | None = extract_epoch(filename)

        if epoch_time is None:
            date_key = 'notime'
            continue
        else:
            file_datetime: datetime = datetime.fromtimestamp(epoch_time)
            if file_datetime.hour < start_hour:
                file_datetime -= timedelta(days=1)
            date_key: str = file_datetime.strftime('%Y%m%d')

        if date_key not in grouped_files:
            grouped_files[date_key] = {}
        grouped_files[date_key].update({epoch_time: video_path})

    return grouped_files

# Function to check if a video file is valid using ffprobe
def is_valid_video(file_path) -> bool:
    try:
        ffmpeg.probe(file_path)
        message: str = f"Checking file: {file_path}, Status: Valid"
        logger.info(message)
        return True
    except ffmpeg.Error as e:
        message = f"Checking file: {file_path}, Error: {e.stderr.decode()}"
        logger.info(message)
        return False

def merge_videos(video_dict: GroupedVideos, base_path: str) -> int:
    today = datetime.now().strftime('%Y%m%d')
    dir_to_delete: set = set()
    
    for date_str, videos in video_dict.items():
        dir_to_delete.clear()
        
        if date_str == today:
            logger.info(f"Skipping today's date: {date_str}")
            continue
        
        # Sort the videos by epoch time
        sorted_videos = dict(sorted(videos.items()))
        
        # Prepare the input file list for ffmpeg
        input_files = []
        for epoch_time, video_path in sorted_videos.items():
            if is_valid_video(video_path):
                input_files.append(video_path)
                dir_to_delete.add(os.path.dirname(video_path))
                
        if not input_files:
            logger.info(f"No valid videos found for {date_str}. Skipping.")
            continue
        
        # Write the input file list for ffmpeg
        with open('input.txt', 'w') as f:
            for file in input_files:
                f.write(f"file '{file}'\n")
        
        # Define the output file path
        output_file = os.path.join(base_path, f"{date_str}.mkv")
        
        try:
            # Use ffmpeg to concatenate videos
            ffmpeg.input('input.txt', format='concat', safe=0).output(output_file, c='copy').run()
        except ffmpeg.Error as e:
            logger.error(f"Failed to concatenate videos for {date_str}. Error: {e.stderr.decode()}")
            return 1
        
        # Remove the temporary input file list
        os.remove('input.txt')
        
        # Set the file's timestamp to the first video's epoch time
        first_video_epoch = next(iter(sorted_videos))
        os.utime(output_file, (first_video_epoch, first_video_epoch))
        
        # Clean up original video files and directories
        try:
            for epoch_time, video_path in sorted_videos.items():
                os.remove(video_path)
            for dir in dir_to_delete:
                os.rmdir(dir)
        except OSError as e:
            logger.error(f"Failed to delete files or directories for {date_str}: {str(e)}")
            return 2
    
        logger.info(f"Processed {date_str}, saved to {output_file}, set timestamps, and deleted original files.")
    
    return 0

def main() -> None:
    base_path: LiteralString = os.path.join('H:', 'data', '94f827b4b94e')

    video_files: list[str] = list_video_files(base_path)
    
    grouped_videos: GroupedVideos = group_files_by_date(video_files, 5)
    
    do_merge: int = merge_videos(grouped_videos, base_path)

if __name__ == '__main__':
    main()
# for date_str, hours in grouped_folders.items():
#     if date_str >= today:
#         message = f"Skipping today's or future date: {date_str}"
#         logger.info(message)
#         continue

#     if not hours:
#         message = f"No hours to process for {date_str}. Skipping."
#         logger.info(message)
#         continue

#     input_files = []
#     first_video_epoch = None

#     for hour in hours:
#         hour_path = os.path.join(base_path, hour)
#         videos = sorted([v for v in os.listdir(hour_path) if v.endswith('.mp4')])

#         for video in videos:
#             video_path = os.path.join(hour_path, video)
#             if is_valid_video(video_path):
#                 if not first_video_epoch:
#                     first_video_epoch = extract_epoch(video)
#                 input_files.append(video_path)

#     if not input_files:
#         message = f"No valid videos found for {date_str}. Skipping."
#         logger.info(message)
#         continue

#     # Create a temporary text file for ffmpeg input
#     with open('input.txt', 'w') as f:
#         for file in input_files:
#             f.write(f"file '{file}'\n")

#     # Define the output file
#     output_file = os.path.join(base_path, f"{date_str}.mkv")

#     # Run ffmpeg command to concatenate videos without re-encoding using ffmpeg-python
#     try:
#         # Run ffmpeg command to concatenate videos without re-encoding
#         ffmpeg.input('input.txt', format='concat', safe=0).output(output_file, c='copy').run()
#     except ffmpeg.Error as e:
#         message = f"Failed to concatenate videos for {date_str}. Error: {e.stderr.decode()}"
#         logger.error(message)
#         continue

#     # Remove the temporary text file
#     os.remove('input.txt')

#     # Set the creation and modification time of the output file to the first video's epoch time
#     if first_video_epoch:
#         os.utime(output_file, (first_video_epoch, first_video_epoch))

#     # Delete original video files and folders
#     try:
#         for hour in hours:
#             hour_path = os.path.join(base_path, hour)
#             for video in os.listdir(hour_path):
#                 os.remove(os.path.join(hour_path, video))
#             os.rmdir(hour_path)
#     except OSError as e:
#         message = f"Failed to delete files or directories for {date_str}: {str(e)}"
#         logger.error(message)
#         continue

#     message = f"Processed {date_str}, saved to {output_file}, set timestamps, and deleted original files."
#     logger.info(message)
    
