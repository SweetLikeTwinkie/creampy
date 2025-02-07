"""
C2.Backend.utils.config.py

Module responsible for loading and managing the server configuration.
Reads the configuration from a YAML file and ensures required keys exist.
"""
#!/usr/bin/env python3

import os
import yaml
import logging

CONFIG_FILE = "C2/Backend/server_config.yaml"

def load_config():
    """
    Loads and returns the server configuration from the YAML file in strict mode.

    This function ensures that the configuration file exists and is properly formatted.
    It raises errors if required keys are missing to prevent misconfigurations.

    Returns:
        dict: A dictionary containing the server configuration parameters.

    Raises:
        TypeError: If the YAML content is not a dictionary.
        SystemExit: If the configuration file is missing.
    """
    if not os.path.exists(CONFIG_FILE):
        logging.error("[ERROR] Config file not found. Run setup first.")
        exit(1)

    with open(CONFIG_FILE, "r") as config_file:
        config = yaml.safe_load(config_file)

    # Ensure the configuration is a dictionary
    if not isinstance(config, dict):
        raise TypeError(f"[ERROR] Invalid config format! Expected dictionary, got {type(config)}")

    # Return the configuration values directly, ensuring key existence
    return {
        "LISTENER_IP": config["server"]["ip"],
        "LISTENER_PORT": config["server"]["port"],
        "RAW_SECRET_KEY": config["server"]["secret_key"],
        "MASTER_PASSWORD": config["server"]["master_password"],
        "DEBUG_MODE": config["server"]["debug_mode"],
        "USE_HTTPS": config["https"]["use_https"],
        "SERVER_CRT": config["https"]["server_crt"],
        "SERVER_KEY": config["https"]["server_key"],
        "LOGGING_FILE_PATH": config["C2"]["logging_file_path"],
    }
