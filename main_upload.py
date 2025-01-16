import os
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
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    ),
}

task1: tasks.UploaderTask = {
    "name": name,
    "local_album_path": Path(
        r"D:\Users\user\OneDrive - Chunghwa Telecom Co., Ltd\文件\Projects\Python\sample\cut_sl_speedup"
    ),
    "GPhoto_url": "https://photos.google.com/u/2/album/AF1QipPgIsi5cicSG2EPtPq_fD1mDUtvkTjdr4d16aGe",
    "browser_config": browser_config,
    "delete_after": True,
}

upload_assignments: tasks.UploaderInfo = {"filename": Path(), "assignments": [task1]}


async def main():
    assignments = upload_assignments.get("assignments")
    logger.info(f"Start uploading tasks:{assignments}")

    if not assignments:
        logger.info("No assignment")
        return

    for task in assignments:
        folder: Path = task["local_album_path"]
        task["mkv_files"] = mkv_files = [
            folder / file for file in os.listdir(folder) if file.endswith(".mkv")
        ]

        if not mkv_files:
            logger.info(f"No mkv files in {folder}, pass")
            return

        logger.info(f"Start uploading {mkv_files} to {task["GPhoto_url"]}")
        await upload_handler(task)

    # Clear tabs
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
