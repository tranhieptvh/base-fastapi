import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Create logs directory if it doesn't exist
LOGS_DIR = "logs"
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Configure logging
def setup_logger(name: str = "app"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create formatters
    file_formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )

    # Create handlers
    # Daily rotating file handler
    log_file = os.path.join(LOGS_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.log")
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.INFO)

    # Add handlers to logger
    logger.addHandler(file_handler)

    return logger

# Create default logger
logger = setup_logger()

# Example usage:
# from src.core.logging import logger
# logger.info("This is an info message")
# logger.error("This is an error message")
# logger.warning("This is a warning message")
# logger.debug("This is a debug message") 