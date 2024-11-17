import logging
import logging.config
from datetime import datetime
import os

# Ensure the log directory exists
log_dir = "./log"
os.makedirs(log_dir, exist_ok=True)

logging_config: str = r"./app/config/logging.conf"
dynamic_logging_config: str = r"./app/config/logging_dynamic.conf"

# Determine today's log filename
today_date = datetime.now().strftime("%Y-%m-%d")
log_file = os.path.join(log_dir, f"{today_date}.log")

# Update the logging configuration dynamically
def update_logging_conf():
    with open(logging_config, "r") as f:
        config = f.read()

    # Replace the placeholder with the actual log file
    updated_config = config.replace('./log/default.log', log_file)
    with open(dynamic_logging_config, "w") as f:
        f.write(updated_config)

update_logging_conf()

# Load the updated logging configuration
logging.config.fileConfig(dynamic_logging_config)

# Custom logger function
def logger(message):
    log = logging.getLogger()
    log.info(message)

# Example usage
if __name__ == "__main__":
    logger("This is an info message.")
