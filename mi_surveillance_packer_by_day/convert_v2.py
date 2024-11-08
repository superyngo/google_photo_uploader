import os
import logging
from datetime import datetime
import ffmpeg

# Function to convert epoch to human-readable date
def epoch_to_date(epoch):
    return datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')

# Function to extract epoch time from filename
def extract_epoch(filename):
    try:
        return int(filename.split('_')[1].split('.')[0])
    except (IndexError, ValueError) as e:
        logging.error(f"Failed to extract epoch from {filename}: {str(e)}")
        return None

# Function to check if a video file is valid using ffprobe
def is_valid_video(file_path):
    try:
        ffmpeg.probe(file_path)
        message = f"Checking file: {file_path}, Status: Valid"
        logging.info(message)
        print(message)
        return True
    except ffmpeg.Error as e:
        message = f"Checking file: {file_path}, Error: {e.stderr.decode()}"
        logging.info(message)
        print(message)
        return False

# Set up logging
today_str = datetime.now().strftime('%Y-%m-%d')
log_file = f'process_log_{today_str}.log'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Create file handler
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.INFO)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create a logging format
formatter = logging.Formatter('%(asctime)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logging.getLogger().addHandler(file_handler)
logging.getLogger().addHandler(console_handler)

# Path to your video folders
base_path = os.path.join('G:', 'data', '94f827b4b94e')

# Get list of all folders
folders = sorted([f for f in os.listdir(base_path) if os.path.isdir(os.path.join(base_path, f))])

# Group folders by date
grouped_folders = {}
for folder in folders:
    date_str = folder[:8]
    if date_str not in grouped_folders:
        grouped_folders[date_str] = []
    grouped_folders[date_str].append(folder)

# Get today's date in the same format as the folder names
today = datetime.now().strftime('%Y%m%d')

for date_str, hours in grouped_folders.items():
    if date_str >= today:
        message = f"Skipping today's or future date: {date_str}"
        logging.info(message)
        print(message)
        continue

    if not hours:
        message = f"No hours to process for {date_str}. Skipping."
        logging.info(message)
        print(message)
        continue

    input_files = []
    first_video_epoch = None

    for hour in hours:
        hour_path = os.path.join(base_path, hour)
        videos = sorted([v for v in os.listdir(hour_path) if v.endswith('.mp4')])

        for video in videos:
            video_path = os.path.join(hour_path, video)
            if is_valid_video(video_path):
                if not first_video_epoch:
                    first_video_epoch = extract_epoch(video)
                input_files.append(video_path)

    if not input_files:
        message = f"No valid videos found for {date_str}. Skipping."
        logging.info(message)
        print(message)
        continue

    # Create a temporary text file for ffmpeg input
    with open('input.txt', 'w') as f:
        for file in input_files:
            f.write(f"file '{file}'\n")

    # Define the output file
    output_file = os.path.join(base_path, f"{date_str}.mkv")

    # Run ffmpeg command to concatenate videos without re-encoding using ffmpeg-python
    try:
        # Run ffmpeg command to concatenate videos without re-encoding
        ffmpeg.input('input.txt', format='concat', safe=0).output(output_file, c='copy').run()
    except ffmpeg.Error as e:
        message = f"Failed to concatenate videos for {date_str}. Error: {e.stderr.decode()}"
        logging.error(message)
        print(message)
        continue

    # Remove the temporary text file
    os.remove('input.txt')

    # Set the creation and modification time of the output file to the first video's epoch time
    if first_video_epoch:
        os.utime(output_file, (first_video_epoch, first_video_epoch))

    # Delete original video files and folders
    try:
        for hour in hours:
            hour_path = os.path.join(base_path, hour)
            for video in os.listdir(hour_path):
                os.remove(os.path.join(hour_path, video))
            os.rmdir(hour_path)
    except OSError as e:
        message = f"Failed to delete files or directories for {date_str}: {str(e)}"
        logging.error(message)
        print(message)
        continue

    message = f"Processed {date_str}, saved to {output_file}, set timestamps, and deleted original files."
    logging.info(message)
    print(message)
