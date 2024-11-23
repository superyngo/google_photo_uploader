import os
from datetime import datetime, timedelta
from typing import LiteralString, TypedDict, NotRequired, Callable
from app.utils.logger import logger
from app.services import ffmpeg_converter
from ffmpeg import Error as ffmpeg_Error

type GroupedVideos = dict[str, dict[int,str]]
class HandleSpeedup(TypedDict):
    start_hour: int
    end_hour: int

def extract_epoch(filename: str) -> int|None:
    """Function to extract epoch time from filename
    """
    
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

# def mark_speedup(video_files: list[str], start_hour: int=0, end_hour: int=0) -> list[str]:
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
            logger.info(f"{filename} has no epoch time.")
            continue
        
        file_hour: int = datetime.fromtimestamp(epoch_time).hour
        
        if file_hour in speedup_range: 
            video_files_speedup.append(video_path)

    return video_files_speedup

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

def get_speedup_range(start_hour: int, end_hour:int) -> range|list[int]:
    # Create the speedup range, handling wrap-around at midnight
    if end_hour >= start_hour:
        return range(start_hour, end_hour + 1)
    else:
        return list(range(start_hour, 25)) + list(range(0,  end_hour + 1))

def covert_replace(ff_func: Callable, input_file: str, **kwargs) -> int:
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
    output_file: str = os.path.join(directory, f"{base_name}_output{extension}")
    
    try:
        ff_func(input_file, output_file, **kwargs)
            
        # Rename the output file back to the original file name
        os.rename(output_file, input_file)
    finally:
    # Remove the temporary input file
        if os.path.exists(temp_input_file):
            os.remove(temp_input_file)

def merge_videos(video_dict: GroupedVideos, base_path: str, handle_speedup: HandleSpeedup|None=None) -> int:
    today: str = datetime.now().strftime('%Y%m%d')
    dir_to_delete: set = set()
    speedup_range: list[int]|range =[]
    if handle_speedup is not None:
        speedup_range = get_speedup_range(**handle_speedup)
    
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
            file_hour: int = datetime.fromtimestamp(epoch_time).hour
            if ffmpeg_converter.is_valid(video_path):
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
            ffmpeg_converter.merge('input.txt', output_file)
        except ffmpeg_Error as e:
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

        # Speedup if needed
        if handle_speedup is not None:
            directory: str
            original_filename: str
            base_name: str
            extension: str
            directory, original_filename = os.path.split(output_file)
            base_name, extension = os.path.splitext(original_filename)
            
            # Define the speedup output file path
            speedup_output_dir: str = os.path.join(directory, 'speedup')
            os.makedirs(speedup_output_dir, exist_ok=True)
            speedup_output_file: str = os.path.join(speedup_output_dir, f"{base_name}_speedup{extension}")
            encode_info: ffmpeg_converter.EncodeKwargs = {'video_track_timescale': 90000, 'vcodec': 'hevc', 'video_bitrate': 920811, 'acodec': 'pcm_alaw', 'ar': 16000, 'f': 'mov'}
            do_speedup: int = ffmpeg_converter.speedup(output_file, speedup_output_file, 100, **encode_info)
            
            # Set the file's timestamp to the first video's epoch time
            os.utime(speedup_output_file, (first_video_epoch, first_video_epoch))
            logger.info(f"Sped up {output_file} to {speedup_output_file} with same timestamps")
    
    return 0

def main() -> None:
    handle_speedup: HandleSpeedup = {'value': True, 'start_hour': 23, 'end_hour': 5}

    base_path: LiteralString = os.path.join('H:', 'data', '94f827b4b94e')

    video_files: list[str] = list_video_files(base_path)

    grouped_videos: GroupedVideos = group_files_by_date(video_files, 5)
    
    do_merge: int = merge_videos(grouped_videos, base_path, handle_speedup)

if __name__ == '__main__':
    main()

