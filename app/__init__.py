from .actions import mideo_converter, GPhoto_uploader
from .config import config
from . import utils
from .utils import logger, load_assignment
from .models import tasks
from .services.my_driver import browser_instances

# from .actions.GPhoto_uploader.gp_uploader import upload_handler

# Create App directories if they don't exist
config.AppPaths.PROGRAM_DATA.mkdir(parents=True, exist_ok=True)
config.AppPaths.APP_DATA.mkdir(parents=True, exist_ok=True)


__all__: list[str] = [
    "config",
    "utils",
    "logger",
    "mideo_converter",
    "GPhoto_uploader",
    "tasks",
    "load_assignment",
    "browser_instances",
]
