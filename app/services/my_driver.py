import nodriver as uc
from typing import TypedDict, NotRequired
from pathlib import Path


# Multiton state
_instances: dict[Path, uc.Browser] = {}


class MyDriverConfig(TypedDict):
    user_data_dir: NotRequired[Path]
    browser_executable_path: NotRequired[Path]


async def init_my_driver(browser_config: MyDriverConfig | None = None) -> uc.Browser:
    """init a driver

    Args:
        browser_config (MyDriverConfig | None, optional): config for driver/browser. Defaults to None.

    Returns:
        uc.Browser: browser
    """
    browser_config = browser_config or {}
    browse_id: Path = browser_config.get("user_data_dir", Path())
    if browse_id in _instances and not _instances[browse_id].stopped:
        return _instances[browse_id]

    browser: uc.Browser = await uc.start(**browser_config)
    _instances[browse_id] = browser
    return browser
