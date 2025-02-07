# logging_config.py
#!/usr/bin/env python3

import logging
import os

from logging.handlers import TimedRotatingFileHandler
from config import load_config

config = load_config()
LOGGING_FILE_PATH = config['LOGGING_FILE_PATH']
DEBUG_MODE = config['DEBUG_MODE']

def setup_logging():
    """
    Initializes the logging system and ensures Uvicorn logs are correctly captured.

    :return: None
    """
    logs_dir = os.path.dirname(LOGGING_FILE_PATH)
    os.makedirs(logs_dir, exist_ok=True)

    # Create loggers for different components
    loggers = {
        "c2server": logging.getLogger("c2server"),
        "http": logging.getLogger("http"),
        "smb": logging.getLogger("smb"),
        "dns": logging.getLogger("dns"),
        "icmp": logging.getLogger("icmp"),
        "uvicorn": logging.getLogger("uvicorn"),
        "ui": logging.getLogger("ui"),
    }

    # Set log levels
    log_level = logging.DEBUG if DEBUG_MODE else logging.INFO
    for logger in loggers.values():
        logger.setLevel(log_level)

    # Console Logging (Only in Debug Mode)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # File Logging with Rotation (Daily Logs)
    log_handler = TimedRotatingFileHandler(LOGGING_FILE_PATH, when="midnight", interval=1, backupCount=7)
    log_handler.suffix = "%Y%m%d"

    # Define Log Format
    log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    log_handler.setFormatter(log_formatter)
    console_handler.setFormatter(log_formatter)

    # Attach Handlers to Loggers
    for logger in loggers.values():
        logger.addHandler(log_handler)
        if DEBUG_MODE:
            logger.addHandler(console_handler)  # Show logs in console only if debugging is enabled

    # Redirect Uvicorn logs to our logging system
    uvicorn_loggers = ["uvicorn", "uvicorn.access", "uvicorn.error"]

    # Remove default Uvicorn handlers (prevents console logs)
    for uvicorn_logger_name in uvicorn_loggers:
        uvicorn_logger = logging.getLogger(uvicorn_logger_name)
        uvicorn_logger.handlers.clear()  # Remove default handlers
        uvicorn_logger.addHandler(log_handler)  # Redirect to log file
        uvicorn_logger.setLevel(log_level)  # Match log level
        uvicorn_logger.propagate = False  # Prevent logs from appearing in the console

    return loggers

# Global logger instance
loggers = setup_logging()

def configure_uvicorn_logging_ui():
    """
    Redirect all Uvicorn logs (main, access, error) to the 'ui' logger
    from our custom logging system.
    """
    ui_logger = loggers["ui"]

    # Redirect the main Uvicorn logger
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.propagate = False
    uvicorn_logger.handlers.clear()
    for handler in ui_logger.handlers:
        uvicorn_logger.addHandler(handler)
    uvicorn_logger.setLevel(ui_logger.level)

    # Redirect access/error logs
    for name in ("uvicorn.access", "uvicorn.error"):
        logger_ = logging.getLogger(name)
        logger_.handlers.clear()
        for handler in ui_logger.handlers:
            logger_.addHandler(handler)
        logger_.setLevel(ui_logger.level)