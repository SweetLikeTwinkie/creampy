from ..logger import logger
from base import BaseComm
from smb.SMBConnection import SMBConnection

class SMBComm(BaseComm):
    def __init__(self, server_ip: str, agent_id: str, auth_token: str, server_name: str = "SMBSERVER"):
        self.server_ip = server_ip
        self.agent_id = agent_id
        self.auth_token = auth_token
        self.server_name = server_name

    def poll_commands(self):
        logger.info("SMB poll_commands not implemented")
        return []

    def send_message(self, message: str) -> str:
        logger.info("SMB send_message not implemented")
        return ""

    def heartbeat(self):
        logger.info("SMB heartbeat not implemented")
