import asyncio
from nodriver import Browser, Tab
import nodriver as zd
from ...utils import logger
from app.services.my_driver import MyDriverConfig
from app.services import init_my_driver
from app.models.tasks import UploaderTask
from app import config, tasks
from pathlib import Path
import os


# sample
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


async def upload(tab: Tab, task: dict) -> None:

    # Locate the 新增相片 and click
    Add_New = await tab.find("//span[text()='新增相片']")
    do = await Add_New.click()
    logger.info("新增相片")

    # Interact with the "Select from Computer" button
    upload_button = await tab.find('//span[text()="從電腦中選取"]')
    do = await upload_button.click()
    print("從電腦中選取")

    # Locate the file input element
    file_input = await tab.find('//input[@type="file"]')
    folder: Path = task["local_album_path"]
    mkv_files = [folder / file for file in os.listdir(folder) if file.endswith(".mkv")]

    do = await file_input.send_file(*mkv_files)  # Set files for upload

    # Wait for confirmation message
    await tab.wait_for("", "你已備份")
    print("Upload successfully")


async def upload_handler(task: UploaderTask) -> int:
    """_summary_

    Args:
        task (UploaderTask): _description_

    Returns:
        _type_: Browser
    """

    browser_config: MyDriverConfig = task.get("browser_config", {})
    tab: Tab = await init_my_driver(browser_config)

    do_get = await tab.get(task["GPhoto_url"])

    do_upload = await upload(tab, task)
    return 0


def main():
    pass


if __name__ == "main":
    main()
