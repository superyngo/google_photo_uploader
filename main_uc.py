from app import config, tasks
from pathlib import Path
from app import upload_handler, logger, load_assignment
from app.services.my_driver import MyDriverConfig
import asyncio

assignment_name: str = config.Actions.UPLOADER
assignment_info_file: Path = config.AppPaths.PROGRAM_DATA / (assignment_name + ".json")
# assignment_info: tasks.UploaderInfo = load_assignment(assignment_info_file)

name = "abc"
browser_config: MyDriverConfig = {
    "user_data_dir": Path(config.AppPaths.APP_DATA) / name,
    "browser_executable_path": Path(
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    ),
}
task: tasks.UploaderTask = {
    "name": name,
    "local_album_path": Path(
        r"D:\Users\user\OneDrive - Chunghwa Telecom Co., Ltd\文件\Projects\Python\sample\cut_sl_speedup"
    ),
    "GPhoto_url": "https://photos.google.com/u/2/album/AF1QipPgIsi5cicSG2EPtPq_fD1mDUtvkTjdr4d16aGe",
    "browser_config": browser_config,
}


async def main():
    do_upload = await upload_handler(task)


# browser.restart()
