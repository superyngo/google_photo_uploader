# 1.load action instruction
# 2.execute action
from pathlib import Path
import asyncio
import nodriver as uc
from app.models.tasks import GPhotoUploader
from ... import config
from ...utils import load_instruction
from ...models.tasks import ActionInstruct
ACTION_NAME: str = config.ACTIONS['uploader']
ACTION_INSTRUCTIONS_FILE: Path = config.CONFIG_PATH / (ACTION_NAME + '.json')
ACTION_INSTRUCTIONS: ActionInstruct = load_instruction(ACTION_INSTRUCTIONS_FILE)

tasks = ACTION_INSTRUCTIONS['tasks']

async def start_session(tasks: GPhotoUploader) -> int:
    browser = await uc.start()
    page = await browser.get('https://www.nowsecure.nl')
    a = tasks['profile']
    return 0
