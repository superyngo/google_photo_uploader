import asyncio
from nodriver import Browser

from app.services.my_driver import MyDriverConfig
from ...services import init_my_driver
from ...models.tasks import UploaderTask


async def upload_handler(task: UploaderTask) -> Browser:
    """_summary_

    Args:
        task (UploaderTask): _description_

    Returns:
        _type_: Browser
    """
    browser_config: MyDriverConfig = task.get("browser_config", {})
    browser: Browser = await init_my_driver(browser_config)
    return browser
