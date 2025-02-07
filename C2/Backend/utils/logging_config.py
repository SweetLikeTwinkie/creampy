"""
C2.Backend.utils.logging_config.py

Module responsible for configuring and managing the logging system for the C2 framework.
It ensures all logs are properly stored, formatted, and rotated, while also redirecting Uvicorn logs.
"""
#!/usr/bin/env python3

import logging
import os
from logging.handlers import TimedRotatingFileHandler
from C2.Backend.utils.config import load_config

# Load configuration settings
config = load_config()
LOGGING_FILE_PATH = config['LOGGING_FILE_PATH']
DEBUG_MODE = config['DEBUG_MODE']

def setup_logging():
    """
    Initializes the logging system and configures logging for various components.

    Features:
    - Creates separate loggers for different subsystems.
    - Stores logs in a rotating file handler with daily log rotation.
    - Configures Uvicorn logs to integrate seamlessly into the logging system.
    - Enables console logging in debug mode.

    Returns:
        dict: A dictionary of configured loggers.
    """
    logs_dir = os.path.dirname(LOGGING_FILE_PATH)
    os.makedirs(logs_dir, exist_ok=True)

    # Define loggers for different system components
    loggers = {
        "c2server": logging.getLogger("c2server"),
        "http": logging.getLogger("http"),
        "smb": logging.getLogger("smb"),
        "dns": logging.getLogger("dns"),
        "icmp": logging.getLogger("icmp"),
        "uvicorn": logging.getLogger("uvicorn"),
        "ui": logging.getLogger("ui"),
    }

    # Set the log level based on debug mode
    log_level = logging.DEBUG if DEBUG_MODE else logging.INFO
    for logger in loggers.values():
        logger.setLevel(log_level)

    # Console logging (enabled only in debug mode)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # File logging with daily rotation
    log_handler = TimedRotatingFileHandler(LOGGING_FILE_PATH, when="midnight", interval=1, backupCount=7)
    log_handler.suffix = "%Y%m%d"

    # Define log format
    log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(message)s")
    log_handler.setFormatter(log_formatter)
    console_handler.setFormatter(log_formatter)

    # Attach handlers to loggers
    for logger in loggers.values():
        logger.addHandler(log_handler)
        if DEBUG_MODE:
            logger.addHandler(console_handler)  # Enable console output in debug mode

    # Redirect Uvicorn logs to custom logging system
    uvicorn_loggers = ["uvicorn", "uvicorn.access", "uvicorn.error"]

    for uvicorn_logger_name in uvicorn_loggers:
        uvicorn_logger = logging.getLogger(uvicorn_logger_name)
        uvicorn_logger.handlers.clear()  # Remove default handlers
        uvicorn_logger.addHandler(log_handler)  # Redirect logs to file
        uvicorn_logger.setLevel(log_level)  # Match log level
        uvicorn_logger.propagate = False  # Prevent logs from appearing in console

    return loggers

# Initialize and retrieve global logger instances
loggers = setup_logging()

def configure_uvicorn_logging_ui():
    """
    Redirects all Uvicorn logs (main, access, and error) to the 'ui' logger
    from the custom logging system, ensuring UI-related logs are properly captured.
    """
    ui_logger = loggers["ui"]

    # Redirect main Uvicorn logger
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.propagate = False
    uvicorn_logger.handlers.clear()
    for handler in ui_logger.handlers:
        uvicorn_logger.addHandler(handler)
    uvicorn_logger.setLevel(ui_logger.level)

    # Redirect Uvicorn access and error logs
    for name in ("uvicorn.access", "uvicorn.error"):
        logger_ = logging.getLogger(name)
        logger_.handlers.clear()
        for handler in ui_logger.handlers:
            logger_.addHandler(handler)
        logger_.setLevel(ui_logger.level)
