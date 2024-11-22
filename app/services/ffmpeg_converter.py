import ffmpeg
from app.utils.logger import logger
import os

def speedup(input_file: str, speed: int) -> int:
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
            raise e
    finally:
        # Remove the temporary input file
        if os.path.exists(temp_input_file):
            os.remove(temp_input_file)

    return 0

def merge(input_txt: str, output_file:str) -> int:
  try:
    # Use ffmpeg to concatenate videos
    ffmpeg.input(input_txt, format='concat', safe=0).output(output_file, c='copy').run()
    return 0
  except ffmpeg.Error as e:
    logger.error(f"Failed mergin {input_txt}. Error: {e.stderr.decode()}")
    raise e
  
def is_valid(file_path: str) -> bool:
    """Function to check if a video file is valid using ffprobe.
    """
    try:
        ffmpeg.probe(file_path)
        message: str = f"Checking file: {file_path}, Status: Valid"
        logger.info(message)
        return True
    except ffmpeg.Error as e:
        message = f"Checking file: {file_path}, Error: {e.stderr.decode()}"
        logger.info(message)
        return False




