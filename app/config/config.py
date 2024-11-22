import os
from app.utils.common import STR_DOWNLOADS_TIMESTAMP_FOLDER_PATH
from app.viewmodels.mideo_converter import HandleSpeedup
from typing import LiteralString

os.makedirs(STR_DOWNLOADS_TIMESTAMP_FOLDER_PATH, exist_ok=True)

os.environ['HTTPS_PROXY'] = ''
os.environ['HTTP_PROXY'] = ''


handle_speedup: HandleSpeedup = {'value': True, 'start_hour': 23, 'end_hour': 5}
base_path: LiteralString = os.path.join('H:', 'data', '94f827b4b94e')
