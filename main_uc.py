from app import config, tasks
from pathlib import Path
from app import upload_handler, logger, load_assignment
import asyncio

assignment_name: str = config.Actions.UPLOADER
assignment_info_file: Path = config.AppPaths.PROGRAM_DATA / (assignment_name + ".json")
# assignment_info: tasks.UploaderInfo = load_assignment(assignment_info_file)


task: tasks.UploaderTask = {
    "name": (name := "abc"),
    "local_album_path": Path(),
    "GPhoto_url": "",
    "browser_config": {
        "user_data_dir": Path(config.AppPaths.APP_DATA) / name,
        "browser_executable_path": Path(
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        ),
    },
}


async def main():
    do_upload = await upload_handler(task)


# browser.restart()
