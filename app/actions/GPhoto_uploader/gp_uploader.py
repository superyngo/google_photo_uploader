import asyncio
from zendriver import Browser

from app.services.my_driver import MyDriverConfig
from app.services import init_my_driver
from app.models.tasks import UploaderTask


async def start_browser(task: UploaderTask) -> int:
    browser_config: MyDriverConfig = task.get("browser_config", {})
    browser: Browser = await init_my_driver(browser_config)
    await browser.get(task["GPhoto_url"])
    return 0


async def upload_handler(task: UploaderTask) -> int:
    """_summary_

    Args:
        task (UploaderTask): _description_

    Returns:
        _type_: Browser
    """
    browser_config: MyDriverConfig = task.get("browser_config", {})
    browser: Browser = await init_my_driver(browser_config)
    do_get = await browser.get(task["GPhoto_url"])
    return 0


from app import config, tasks
from pathlib import Path

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
