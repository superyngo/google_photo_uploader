from app import config, tasks
from pathlib import Path
from app import upload_handler, logger, load_assignment
import asyncio

assignment_name: str = config.ACTIONS["uploader"]
assignment_info_file: Path = config.APP_PATHS["program_data"] / (
    assignment_name + ".json"
)
# assignment_info: tasks.UploaderInfo = load_assignment(assignment_info_file)


task: tasks.UploaderTask = {
    "name": (name := "abc"),
    "local_album_path": Path(),
    "GPhoto_url": "",
    "browser_config": {
        "user_data_dir": Path(config.APP_PATHS["app_data"]) / name,
        "browser_executable_path": Path(
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
        ),
    },
}


async def main():
    browser = await upload_handler(task)
