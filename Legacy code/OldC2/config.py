# config.py
#!/usr/bin/env python3

import os
import yaml
import logging

CONFIG_FILE = "server_config.yaml"

def load_config():
    """Loads and returns the server configuration from the YAML file in strict mode.

    This function ensures that the configuration file exists and is properly formatted.
    It raises errors if required keys are missing.
    """
    if not os.path.exists(CONFIG_FILE):
        logging.error("[ERROR] Config file not found. Run setup first.")
        exit(1)

    with open(CONFIG_FILE, "r") as config_file:
        config = yaml.safe_load(config_file)

    # Ensure the configuration is a dictionary
    if not isinstance(config, dict):
        raise TypeError(f"[ERROR] Invalid config format! Expected dictionary, got {type(config)}")

    # Return the configuration values directly
    return {
        "LISTENER_IP": config["server"]["ip"],
        "LISTENER_PORT": config["server"]["port"],
        "RAW_SECRET_KEY": config["server"]["secret_key"],
        "MASTER_PASSWORD": config["server"]["master_password"],
        "DEBUG_MODE": config["server"]["debug_mode"],
        "USE_HTTPS": config["https"]["use_https"],
        "SERVER_CRT": config["https"]["server_crt"],
        "SERVER_KEY": config["https"]["server_key"],
        "LOGGING_FILE_PATH": config["c2"]["logging_file_path"],
    }




