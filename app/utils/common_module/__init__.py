# from .common import common
from logging import Logger
from .logger_module import setup_logger
from .common import load_assignment
from ...config import config
from pathlib import Path

_log_path: Path = config.APP_PATHS["logs"]
logger: Logger = setup_logger(_log_path)

__all__: list[str] = ["logger", "load_assignment"]
