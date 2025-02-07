"""
Agent.config

Handles loading and merging of agent configuration from default settings and remote sources.
Provides flexibility for dynamic configuration updates.
"""
#!/usr/bin/env python3

import requests

# Remote configuration endpoint
CONFIG_URL = "http://localhost:8080/api/config"


def get_remote_config():
    """
    Fetches the configuration from a remote server.

    Returns:
        dict: The remote configuration if successfully retrieved, otherwise an empty dictionary.
    """
    try:
        response = requests.get(CONFIG_URL, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print("Failed to fetch remote config: ", e)
    return {}


def load_initial_config():
    """
    Loads the initial configuration by merging default settings with remote configurations.

    Returns:
        dict: The final agent configuration.
    """
    default_config = {
        "agent_id": "agent_default",
        "auth_token": "default_token",
        "poll_interval": 10,
        "heartbeat_interval": 30,
        "protocols": {
            "http": {"enabled": True, "server_url": "http://localhost:8080"},
            "dns": {"enabled": True, "server_ip": "127.0.0.1"},
            "icmp": {"enabled": True, "server_ip": "127.0.0.1"},
            "smb": {"enabled": True, "server_ip": "127.0.0.1"},
        },
        "update_endpoint": "http://localhost:8000/api/agent/update",
    }

    remote_config = get_remote_config()
    default_config.update(remote_config)

    return default_config
