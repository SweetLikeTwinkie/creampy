"""
C2.Agent.logger

Provides a simple logging configuration for agents.
Logs messages to the console with timestamps and severity levels.
"""
#!/usr/bin/env python3

import logging
import sys

def setup_logger(name="agent", level=logging.DEBUG):
    """
    Configures and returns a logger instance.

    Args:
        name (str): The name of the logger. Defaults to "agent".
        level (int): Logging level (default is DEBUG).

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(handler)
    return logger

logger = setup_logger()


