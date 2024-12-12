from .config import config
from . import utils
from .utils import logger

from .actions.mideo_convertor import mideo_converter

# Create App directories if they don't exist
config.APP_PATHS["program_data"].mkdir(parents=True, exist_ok=True)
config.APP_PATHS["app_data"].mkdir(parents=True, exist_ok=True)


__all__: list[str] = [
    "config",
    "utils",
    "logger",
    "mideo_converter",
]
