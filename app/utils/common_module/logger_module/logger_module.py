import logging
from logging import config as LoggerConfig, Logger
import os
from datetime import datetime
import configparser
from pathlib import Path

def setup_logger() -> Logger:
    # Determine the path to the logger module
    module_path: Path = Path(__file__).parent

    # Construct the path to the configuration file within the package's config folder
    config_path: Path = module_path / 'config' / 'logger.conf'
    
    # Check if the configuration file exists
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file '{config_path}' does not exist.")
    
    # Load the configuration file
    config = configparser.ConfigParser()
    config.read(config_path)

    # Ensure the log directory exists in the executing root
    log_directory: Path = Path.cwd() / 'log'
    log_directory.mkdir(parents=True, exist_ok=True)
    
    # Get the current date for the log filename
    datestamp: str = datetime.now().strftime('%Y-%m-%d')
    log_filename: Path = log_directory / f"{datestamp}.log"
    
    # Update the file handler's filename in the configuration
    config.set('handler_fileHandler', 'args', f"(r'{log_filename}', 'a')")

    # Apply the logging configuration
    LoggerConfig.fileConfig(config)

    # Return the root logger
    return logging.getLogger()


# Initialize the logger
logger: Logger = setup_logger()

# Example usage
if __name__ == "__main__":
    # logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message')
    logger.critical('This is a critical message')