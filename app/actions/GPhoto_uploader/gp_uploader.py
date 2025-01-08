import asyncio
from zendriver import Browser

from app.services.my_driver import MyDriverConfig
from app.services import init_my_driver
from app.models.tasks import UploaderTask
from app import config, tasks
from pathlib import Path
import os

# sample
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


async def upload(browser: Browser, task: UploaderTask) -> None:

    res = browser.get(task["GPhoto_url"])

    if res["status"] == 404 and bool_headless:
        self.driver.quit()
        self.driver = None
        self.login()
        self.driver.get(self.config_data["album_url"])
    elif res["status"] == 404:
        self.login()
        self.driver.get(self.config_data["album_url"])

    # Locate the input element by aria-label using XPath
    _add_photo_click = self.driver._wait_element(
        By.XPATH, '//button[@aria-label="新增相片"]'
    ).click()
    print("新增相片")
    # Interact with the input element
    _upload_click = self.driver._wait_element(
        By.XPATH, '//span[text()="從電腦中選取"]'
    ).click()
    print("從電腦中選取")
    file_input = self.driver.find_element(By.XPATH, '//input[@type="file"]')
    files_path = self._list_mkv_files(self.config_data["mideo_folder"])
    file_input.send_keys(files_path)
    self.driver._wait_element(By.XPATH, f"//div[contains(text(), '你已備份')]")
    print("Upload successfully")
    self.driver.quit()
    self.driver = None


def _list_mkv_files(self, mideo_folder: Path) -> str:
    # Get all .mkv files in the folder
    mkv_files = [
        mideo_folder / file
        for file in os.listdir(mideo_folder)
        if file.endswith(".mkv")
    ]
    # Join the list of files into a single string separated by newline characters
    mkv_files_str = "\n".join(str(mkv_files))
    return mkv_files_str


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
    do_upload = await upload(browser, task)
    return 0


def main():
    pass


if __name__ == "main":
    main()
