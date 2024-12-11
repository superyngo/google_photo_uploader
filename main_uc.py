import asyncio
import nodriver as uc
from app import logger
from app import *

browser = await uc.start(
    headless=False,
    # user_data_dir="/path/to/existing/profile",  # by specifying it, it won't be automatically cleaned up when finished
    browser_executable_path=None,
    # browser_args=["--some-browser-arg=true", "--some-other-option"],
    # lang="en-US",  # this could set iso-language-code in navigator, not recommended to change
)
tab = await browser.get("https://somewebsite.com")


browser = await uc.start()
page = await browser.get("https://google.com")
await page.save_screenshot()
await page.get_content()
await page.scroll_down(150)

# save. when no filepath is given, it is saved in '.session.dat'
await browser.cookies.save()

# load. when no filepath is given, it is loaded from '.session.dat'
await browser.cookies.load()
browser.stop()
