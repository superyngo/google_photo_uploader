from .config.config import APP_NAME, CONFIG_PATH, APP_BASE_DIR, SESSIONS_DIR, HANDLE_SPEEDUP, BASE_PATH
from .utils import common
from .utils.logger import logger
# Create App directories if they don't exist
APP_BASE_DIR.mkdir(parents=True, exist_ok=True)
SESSIONS_DIR.mkdir(exist_ok=True)

__all__: list[str] = ['common', 'logger']