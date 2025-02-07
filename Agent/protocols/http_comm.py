import requests
from ..logger import logger
from base import BaseComm

class HTTPComm(BaseComm):
    def __init__(self, server_url: str, agent_id: str, auth_token: str):
        self.server_url = server_url.rstrip('/')
        self.agent_id = agent_id
        self.auth_token = auth_token

    def poll_commands(self):
        try:
            url = f"{self.server_url}/api/agent/commands"
            params = {"agent_id": self.agent_id, "auth_token": self.auth_token}
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                commands = response.json().get("commands", [])
                logger.info("HTTP commands: %s", commands)
                return commands
        except Exception as e:
            logger.error("HTTP poll error: %s", e)
        return []

    def send_output(self, output: str) -> bool:
        try:
            url = f"{self.server_url}/api/agent/output"
            payload = {"agent_id": self.agent_id, "auth_token": self.auth_token, "output": output}
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code == 200:
                logger.info("HTTP send_output succeeded")
                return True
        except Exception as e:
            logger.error("HTTP send_output error: %s", e)
        return False

    def send_message(self, message: str) -> str:
        try:
            url = f"{self.server_url}/api/agent/message"
            payload = {"message": message}
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code == 200:
                logger.info("HTTP send_message succeeded")
                return response.json().get("response", "")
        except Exception as e:
            logger.error("HTTP send_message error: %s", e)
        return ""

    def heartbeat(self):
        try:
            url = f"{self.server_url}/api/agent/heartbeat"
            payload = {"agent_id": self.agent_id, "auth_token": self.auth_token}
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code == 200:
                logger.info("HTTP heartbeat sent")
                return True
        except Exception as e:
            logger.error("HTTP heartbeat error: %s", e)
        return False