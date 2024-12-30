# Created by DarkTrick - 4fb5f723849d32782e723c34bfd132e442d378d7

import subprocess
import tempfile
import sys
import os
import logging
import json
import re
from collections import deque
import ffmpeg

# ===========================
# ==== Configure logging ====
# ===========================
log_level = logging.ERROR
log_filename = "silence_cutter.log"
logger = logging.getLogger("")
logger.setLevel(log_level)
log_handler = logging.FileHandler(log_filename, delay=True)
logger.addHandler(log_handler)


def findSilences(filename, dB=-35) -> deque[float]:
    """
    returns a list:
      even elements (0,2,4, ...) denote silence start time
      uneven elements (1,3,5, ...) denote silence end time

    """
    logging.debug(f"findSilences ()")
    logging.debug(f"    - filename = {filename}")
    logging.debug(f"    - dB = {dB}")

    # command = [
    #     "ffmpeg",
    #     "-i",
    #     filename,
    #     "-af",
    #     "silencedetect=n=" + str(dB) + "dB:d=1",
    #     "-f",
    #     "null",
    #     "-",
    # ]
    # output = subprocess.run(
    #     command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    # ).stderr.decode("utf-8")

    output = (
        ffmpeg.input(filename)
        .output("null", af="silencedetect=n={}dB:d=1".format(dB), f="null")
        .run(capture_stdout=True, capture_stderr=True)
    )[1].decode("utf-8")

    # Regular expression to find all floats after "silence_start or end: "
    pattern = r"silence_(?:start|end): (\d+\.\d+|\d+)"

    # Find all matches in the log data
    matches = re.findall(pattern, output)

    # Convert matches to a list of floats
    silence_end_floats: deque[float] = deque(float(match) for match in matches)

    # Handle silence start and end
    silence_end_floats.appendleft(0.0)
    silence_end_floats.append(float(getVideoDuration(filename)))

    return silence_end_floats


def getVideoDuration(filename: str) -> float:
    logging.debug(f"getVideoDuration ()")
    logging.debug(f"    - filename = {filename}")

    command = [
        "ffprobe",
        "-i",
        filename,
        "-v",
        "quiet",
        "-show_entries",
        "format=duration",
        "-hide_banner",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
    ]
    print(command)
    output = subprocess.run(command, stdout=subprocess.PIPE)
    s = str(output.stdout, "UTF-8")
    return float(s)


def getSectionsOfNewVideo(silences, duration):
    """Returns timings for parts, where the video should be kept"""
    return [0.0] + silences + [duration]


def ffmpeg_filter_getSegmentFilter(videoSectionTimings):
    ret = ""
    for i in range(int(len(videoSectionTimings) / 2)):
        start = videoSectionTimings[2 * i]
        end = videoSectionTimings[2 * i + 1]
        ret += "between(t," + str(start) + "," + str(end) + ")+"
    # cut away last "+"
    ret = ret[:-1]
    return ret


def ffmpeg_filter_getSegmentFilter(videoSectionTimings):
    return "+".join(
        f"between(t,{videoSectionTimings[2 * i]},{videoSectionTimings[2 * i + 1]})"
        for i in range(len(videoSectionTimings) // 2)
    )


def getFileContent_videoFilter(videoSectionTimings):
    ret = "select='"
    ret += ffmpeg_filter_getSegmentFilter(videoSectionTimings)
    ret += "', setpts=N/FRAME_RATE/TB"
    return ret


def getFileContent_audioFilter(videoSectionTimings):
    ret = "aselect='"
    ret += ffmpeg_filter_getSegmentFilter(videoSectionTimings)
    ret += "', asetpts=N/SR/TB"
    return ret


def writeFile(filename, content):
    logging.debug(f"writeFile ()")
    logging.debug(f"    - filename = {filename}")

    with open(filename, "w") as file:
        file.write(str(content))


def ffmpeg_run(file, videoFilter, audioFilter, outfile):
    logging.debug(f"ffmpeg_run ()")

    # # prepare filter files
    # vFile = tempfile.NamedTemporaryFile(
    #     mode="w", encoding="UTF-8", prefix="silence_video"
    # )
    # aFile = tempfile.NamedTemporaryFile(
    #     mode="w", encoding="UTF-8", prefix="silence_audio"
    # )

    # videoFilter_file = vFile.name  # "/tmp/videoFilter" # TODO: replace with tempfile
    # audioFilter_file = aFile.name  # "/tmp/audioFilter" # TODO: replace with tempfile
    # writeFile(videoFilter_file, videoFilter)
    # writeFile(audioFilter_file, audioFilter)
    video_filter_file, audio_filter_file = None, None
    # for prefix, avfilter in {
    #     "silence_video": [videoFilter, video_filter_file],
    #     "silence_audio": [audioFilter, audio_filter_file],
    # }.items():
    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", encoding="UTF-8", prefix="silence_video"
    ) as temp_file:
        temp_file.write(videoFilter)
        video_filter_file = temp_file.name

    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", encoding="UTF-8", prefix="silence_audio"
    ) as temp_file:
        temp_file.write(audioFilter)
        audio_filter_file = temp_file.name

    command = [
        "ffmpeg",
        "-i",
        file,
        "-filter_script:v",
        video_filter_file,
        "-filter_script:a",
        audio_filter_file,
        outfile,
    ]
    print(command)
    subprocess.run(command)

    # vFile.close()
    # aFile.close()


def cut_silences(infile, outfile, dB=-35):
    logging.debug(f"cut_silences ()")
    logging.debug(f"    - infile = {infile}")
    logging.debug(f"    - outfile = {outfile}")
    logging.debug(f"    - dB = {dB}")

    print("detecting silences")
    silences: deque[float] = findSilences(infile, dB)
    with open("1_silences.json", "w") as file:
        json.dump(list(silences), file)

    # duration = getVideoDuration(infile)
    # with open("2_duration.json", "w") as file:
    #     json.dump(duration, file)
    # videoSegments = getSectionsOfNewVideo(silences, duration)

    videoFilter = getFileContent_videoFilter(silences)
    with open("4_videoFilter.json", "w") as file:
        json.dump(videoFilter, file)

    audioFilter = getFileContent_audioFilter(silences)
    with open("4_audioFilter.json", "w") as file:
        json.dump(audioFilter, file)

    print("create new video")
    ffmpeg_run(infile, videoFilter, audioFilter, outfile)


def printHelp():
    print("Usage:")
    print("   silence_cutter.py [infile] [optional: outfile] [optional: dB]")
    print("   ")
    print("        [outfile]")
    print("         Default: [infile]_cut")
    print("   ")
    print("        [dB]")
    print("         Default: -30")
    print("         A suitable value might be around -50 to -35.")
    print("         The lower the more volume will be defined das 'silent'")
    print(
        "         -30: Cut Mouse clicks and mouse movent; cuts are very recognizable."
    )
    print(
        "         -35: Cut inhaling breath before speaking; cuts are quite recognizable."
    )
    print("         -40: Cuts are almost not recognizable.")
    print("         -50: Cuts are almost not recognizable.")
    print("              Cuts nothing, if there is background noise.")
    print("         ")
    print("")
    print("Dependencies:")
    print("          ffmpeg")
    print("          ffprobe")


def main():
    logging.debug(f"main ()")
    args = sys.argv[1:]
    if len(args) < 1:
        printHelp()
        return

    if args[0] == "--help":
        printHelp()
        return

    infile = args[0]

    if not os.path.isfile(infile):
        print("ERROR: The infile could not be found:\n" + infile)
        return

    # set default values for optionl arguments
    tmp = os.path.splitext(infile)
    outfile = tmp[0] + "_cut" + tmp[1]
    dB = -30

    if len(args) >= 2:
        outfile = args[1]

    if len(args) >= 3:
        dB = args[2]

    cut_silences(infile, outfile, dB)


if __name__ == "__main__":
    main()
