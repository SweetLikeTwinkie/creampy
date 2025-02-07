import requests

CONFIG_URL = "http://localhost:8080/api/config"

def get_remote_config():
    try:
        response = requests.get(CONFIG_URL, timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print("Failed to fetch remote config: ", e)
    return {}

def load_initial_config():
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
