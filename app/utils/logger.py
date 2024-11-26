import logging
import logging.config
import os
from datetime import datetime
import configparser

def setup_logger():
    config_path = './app/config/logger.conf'
    
    # Check if the configuration file exists
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file '{config_path}' does not exist.")
    
    # Load the configuration file
    config = configparser.ConfigParser()
    config.read(config_path)

    # Get the current date for the log filename
    datestamp = datetime.now().strftime('%Y-%m-%d')
    log_filename = f'./log/{datestamp}.log'

    # Ensure the log directory exists
    os.makedirs('./log', exist_ok=True)

    # Update the file handler's filename in the configuration
    config.set('handler_fileHandler', 'args', f"('{log_filename}', 'a')")

    # Apply the logging configuration
    logging.config.fileConfig(config)

    # Return the root logger
    return logging.getLogger()


# Initialize the logger
logger = setup_logger()

# Example usage
if __name__ == "__main__":
    # logger.debug('This is a debug message')
    logger.info('This is an info message')
    logger.warning('This is a warning message')
    logger.error('This is an error message')
    logger.critical('This is a critical message')