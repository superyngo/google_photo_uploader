import zendriver as zd
from zendriver import Tab
from typing import TypedDict, NotRequired
from pathlib import Path
from ..utils import composer
import time, os
import time

from zendriver.cdp import network

response_codes: dict[str, int] = {}


async def get_response(tab, url) -> int:

    await tab.send(network.enable())

    global response_codes
    # Add a handler for ResponseReceived events
    tab.add_handler(
        network.ResponseReceived,
        lambda e: (
            response_codes.update({e.response.url: e.response.status})
            if e.response.url == url
            else None
        ),
    )
    await tab.get(url)

    while response_codes.get(url) is None:
        time.sleep(1)

    await tab.send(network.disable())
    return response_codes[url]


# Multiton state
_instances: dict[Path, zd.Tab] = {}


class MyDriverConfig(TypedDict):
    user_data_dir: NotRequired[Path]
    browser_executable_path: NotRequired[Path]


# Restrart not working yet
async def _restart(self) -> None:
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
#     "user_data_dir": Path(config.AppPaths.APP_DATA) / name,
#     "browser_executable_path": Path(
#         r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
#     ),
# }


async def init_my_driver(browser_config: MyDriverConfig | None = None) -> zd.Tab:
    """init a driver

    Args:
        browser_config (MyDriverConfig | None, optional): config for driver/browser. Defaults to None.

    Returns:
        uc.Browser: browser
    """
    global _instances

    browser_config = browser_config or {}

    browser_id: Path = browser_config.get("user_data_dir", Path())
    if browser_id in _instances and not _instances[browser_id].stopped:
        return _instances[browser_id]

    browser: zd.Browser = await zd.start(**browser_config)

    tab: Tab = await browser.get("about:blank")

    do_compose: int = composer.compose(tab, {"get_response": get_response})
    _instances[browser_id] = tab
    return tab
