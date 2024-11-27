from pathlib import Path
import os
from .logger import logger

# Ensure the log directory exists in the executing root
log_directory: Path = Path.cwd() / 'log'
os.makedirs(log_directory, exist_ok=True)

__all__: list[str] = ['logger']

