# logging_config.py

import logging
from logging.handlers import RotatingFileHandler

def setup_logging(log_file='app.log', log_level=logging.INFO):
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)

    console_handler = logging.StreamHandler()
    file_handler = RotatingFileHandler(log_file, maxBytes=10 * 1024 * 1024, backupCount=5)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger

# Initialize logger
logger = setup_logging()
