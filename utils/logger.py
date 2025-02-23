import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger():
    """Configuring a logger with file rotation"""
    # Create a directory for logs if it does not exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Path to log file
    log_file = os.path.join(log_dir, "bot.log")
    
    # Setting up formatting
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create a handler for a file with rotation
    # Maximum file size is 10MB, we store the last 5 files
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # Setting up the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    
    return logger 