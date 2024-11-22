import os
from datetime import datetime, timedelta
from typing import LiteralString, TypedDict, NotRequired
import ffmpeg
from app.utils.logger import logger

type GroupedVideos = dict[str, dict[int,str]]
class HandleSpeedup(TypedDict):
    value: bool
    start_hour: NotRequired[int]
    end_hour: NotRequired[int]


# Function to extract epoch time from filename
def extract_epoch(filename: str) -> int|None:
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


def mark_speedup(video_files: list[str], start_hour: int=0, end_hour: int=0) -> list[str]:
    video_files_speedup: list[str] = []
    speedup_range: list[int]|range
    # Create the speedup range, handling wrap-around at midnight
    if end_hour >= start_hour:
        speedup_range = range(start_hour, end_hour + 1)
    else:
        speedup_range = list(range(end_hour, 25)) + list(range(0, start_hour + 1))

    for video_path in video_files:
        filename: str = os.path.basename(video_path)
        epoch_time: int | None = extract_epoch(filename)
        
        if epoch_time is None:
            continue
        
        file_hour: int = datetime.fromtimestamp(epoch_time).hour
        
        if file_hour in speedup_range: 
            video_files_speedup.append(video_path)

    return video_files_speedup

def speedup_videos(input_file: str, speed: int) -> int:
    # Get the directory, base name, and extension of the input file
    directory: str
    original_filename: str
    base_name: str
    extension: str
    temp_input_file: str
    directory, original_filename = os.path.split(input_file)
    base_name, extension = os.path.splitext(original_filename)
    
    # Define the temporary input file name
    temp_input_file = os.path.join(directory, f"{base_name}_temp{extension}")
    
    # Rename the original input file to the temporary input file
    os.rename(input_file, temp_input_file)
    
    # Define the output file name
    output_file = os.path.join(directory, f"{base_name}_output{extension}")
    
    try:
        # Speedup the video using ffmpeg-python
        (
            ffmpeg
            .input(temp_input_file)
            .output(
                output_file,
                vf=f"select='not(mod(n,{speed}))',setpts=N/FRAME_RATE/TB",
                af=f"aselect='not(mod(n,{speed}))',asetpts=N/SR/TB",
                shortest=True,
                vsync='vfr'
            )
            .run()
        )
        
        # Rename the output file back to the original file name
        os.rename(output_file, input_file)
    except ffmpeg.Error as e:
            logger.error(f"Failed to speedup videos for {input_file}. Error: {e.stderr.decode()}")
            return 1
    finally:
        # Remove the temporary input file
        if os.path.exists(temp_input_file):
            os.remove(temp_input_file)

    return 0

def group_files_by_date(video_files: list[str], start_hour: int=0) -> GroupedVideos:
    grouped_files: GroupedVideos = {}

    for video_path in video_files:
        filename: str = os.path.basename(video_path)
        epoch_time: int | None = extract_epoch(filename)

        if epoch_time is None:
            date_key: str = 'notime'
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
    today: str = datetime.now().strftime('%Y%m%d')
    dir_to_delete: set = set()
    
    for date_str, videos in video_dict.items():
        dir_to_delete.clear()
        
        if date_str == today:
            logger.info(f"Skipping today's date: {date_str}")
            continue
        
        # Sort the videos by epoch time
        sorted_videos = dict(sorted(videos.items()))
        
        # Prepare the input file list for ffmpeg
        input_files: list[str] = []
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
            for _epoch_time, video_path in sorted_videos.items():
                os.remove(video_path)
            for dir in dir_to_delete:
                os.rmdir(dir)
        except OSError as e:
            logger.error(f"Failed to delete files or directories for {date_str}: {str(e)}")
            return 2
    
        logger.info(f"Processed {date_str}, saved to {output_file}, set timestamps, and deleted original files.")
    
    return 0

def main() -> None:
    handle_speedup: HandleSpeedup = {'value': True, 'start_hour': 23, 'end_hour': 5}

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
