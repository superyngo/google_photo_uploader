# from .common import common
from pathlib import Path
from logging import Logger
from .logger_module import setup_logger
from .common import load_assignment
from ...config.app_config import APP_PATHS

_log_path: Path = APP_PATHS["logs"]
logger: Logger = setup_logger(_log_path)

__all__: list[str] = ["logger", "load_assignment"]
