import os
from app.utils.common import STR_DOWNLOADS_TIMESTAMP_FOLDER_PATH
from app.viewmodels.mideo_converter import HandleSpeedup

os.makedirs(STR_DOWNLOADS_TIMESTAMP_FOLDER_PATH, exist_ok=True)

os.environ['HTTPS_PROXY'] = ''
os.environ['HTTP_PROXY'] = ''

DB_PATH = r'D:\Users\user\OneDrive - Chunghwa Telecom Co., Ltd\Work\99_共享檔案\三駐點\存控\存控.db'
handle_speedup: HandleSpeedup = {'value': True, 'start_hour': 23, 'end_hour': 5}
