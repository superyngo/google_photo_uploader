# 1.load action instruction
# 2.execute action
from pathlib import Path
import asyncio
import nodriver as uc
from ... import config
from ...utils import load_assignment
from ...models.tasks import UploaderInfo, UploaderSession
ASSIGNMENT_NAME: str = config.ACTIONS['uploader']
ASSIGNMENT_INFO_FILE: Path = config.CONFIG_PATH / (ASSIGNMENT_NAME + '.json')
ASSIGNMENT_INFO: UploaderInfo = load_assignment(ASSIGNMENT_INFO_FILE)

sessions: list[UploaderSession] = ASSIGNMENT_INFO['action']

async def start_session(session: UploaderSession) -> uc.Browser:
    profile: Path = session['profile']
    chrome_path: Path|None = session['chrome_path']    
    browser = await uc.start(
        user_data_dir='/path/to/existing/profile',  # by specifying it, it won't be automatically cleaned up when finished
        browser_executable_path=chrome_path,
    )

    # page = await browser.get('https://www.nowsecure.nl')
    return browser
