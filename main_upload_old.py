import asyncio
from pathlib import Path
from app import config, tasks, upload_handler, browser_instances
from app import logger
import pdb


# sample
name = "abc"
browser_config: tasks.MyDriverConfig = {
    "user_data_dir": Path(config.AppPaths.APP_DATA) / name,
    "browser_executable_path": Path(
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ),
}

task1: tasks.UploaderTask = {
    "name": "xiaomi",
    "local_album_path": Path(r"D:\smb\xiaomi\xiaomi_camera_videos\94f827b4b94e"),
    "GPhoto_url": "https://photos.google.com/share/AF1QipN5ErAyjjFPCxWgw--uYgbrvJWZu1U39-3iyeChyQQv0PDxU59NnyNP_k4bZNMrvw?key=czBUY1Z4UWRjdDFMWXFYdS1NZnd4SXIyREgzTElR",
    "browser_config": browser_config,
    "delete_after": True,
}
task2: tasks.UploaderTask = {
    "name": "xiaomi_speedup",
    "local_album_path": Path(r"D:\smb\xiaomi\xiaomi_camera_videos\94f827b4b94e") / "cut_sl_speedup",
    "GPhoto_url": "https://photos.google.com/share/AF1QipMk6l7y_pzXMh1gTWH5G2lD_U30_Br2E-p2sKDw71YBY97zMh6krVC9cDsT-acFjQ",
    "browser_config": browser_config,
    "delete_after": True,
}

upload_assignments: tasks.UploaderInfo = {"filename": Path(), "assignments": [task1, task2]}


async def main():
    assignments = upload_assignments.get("assignments")
    logger.info(f"Start uploading tasks:{assignments}")

    if assignments:
        for task in assignments:
            await upload_handler(task)

    logger.info(f"All tasks done, close all browsers")
    keys = list(browser_instances.keys())
    for key in keys:
        if key in browser_instances:
            browser_instances[key].stop()
            del browser_instances[key]

    # Your script code here
    # print("This is a script in debug mode.")
    # Set a breakpoint
    # pdb.set_trace()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
