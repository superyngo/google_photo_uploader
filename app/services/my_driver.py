import zendriver as zd
from typing import TypedDict, NotRequired
from pathlib import Path
from ..utils import composer
import time, os


# Multiton state
_instances: dict[Path, zd.Browser] = {}


class MyDriverConfig(TypedDict):
    user_data_dir: NotRequired[Path]
    browser_executable_path: NotRequired[Path]


async def restart(self) -> None:
    await self.stop()
    browser_config = {
        k: v
        for (k, v) in self.config.__dict__.items()
        if k in ["user_data_dir", "browser_executable_path"]
    }
    browser_id: Path = browser_config.get("user_data_dir", Path())
    _instances[browser_id] = await zd.start(**browser_config)
    self = _instances[browser_id]


# browser_config = {
#     "user_data_dir": Path(config.APP_PATHS["app_data"]) / name,
#     "browser_executable_path": Path(
#         r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
#     ),
# }


async def init_my_driver(browser_config: MyDriverConfig | None = None) -> zd.Browser:
    """init a driver

    Args:
        browser_config (MyDriverConfig | None, optional): config for driver/browser. Defaults to None.

    Returns:
        uc.Browser: browser
    """
    browser_config = browser_config or {}

    browser_id: Path = browser_config.get("user_data_dir", Path())
    if browser_id in _instances and not _instances[browser_id].stopped:
        return _instances[browser_id]

    browser: zd.Browser = await zd.start(**browser_config)
    # do_compose: int = composer.compose(browser, {"restart": restart})
    _instances[browser_id] = browser
    return browser
