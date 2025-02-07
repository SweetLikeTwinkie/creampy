"""
C2.Backend.utils.auxiliary.py

Utility module providing auxiliary functions for the C2 framework.
Includes functionalities for screen clearing, port checking, and protocol-based connectivity validation.
"""
#!/usr/bin/env python3

import os
import requests
import dns.resolver
import socket
from ping3 import ping

# ASCII Art Banner
BANNER = r"""
   ______                          ______  __
  / ____/_______  ____ _____ ___  / __ \ \/ /
 / /   / ___/ _ \/ __ `/ __ `__ \/ /_/ /\  /
/ /___/ /  /  __/ /_/ / / / / / / ____/ / /
\____/_/_  \___/\__,_/_/ /_/ /_/_/     /_/
            By: SweetLikeTwinkie <3
"""

# List of protocols and their corresponding endpoints
PROTOCOLS = [
    "https://c2server.com",
    "http://c2server.com",
    "dns://c2server.com",
    "icmp://c2server.com"
]

def clear_screen():
    """
    Clears the terminal screen and displays the banner.

    Uses 'cls' for Windows and 'clear' for Unix-based systems.
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    print(BANNER)

def is_port_in_use(port, host="127.0.0.1"):
    """
    Checks if a given port is currently in use.

    - Attempts to bind a socket to the specified host and port.
    - If binding fails, the port is considered occupied.

    Args:
        port (int): The port number to check.
        host (str): The IP address to bind to (default: "127.0.0.1").

    Returns:
        bool: True if the port is in use, False otherwise.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
        except socket.error:
            return True
    return False

def check_connectivity():
    """
    Checks network connectivity across multiple communication protocols.

    - Attempts HTTP and HTTPS connections using `requests`.
    - Resolves DNS records using `dnspython`.
    - Sends ICMP echo requests using `ping3`.

    Returns:
        str: The first reachable protocol URL (e.g., "https://c2server.com").
        None: If all protocol checks fail.
    """
    for protocol in PROTOCOLS:
        try:
            if protocol.startswith("https"):
                response = requests.get(protocol, timeout=3, verify=False)  # Ignore SSL verification
                if response.status_code == 200:
                    return protocol
            elif protocol.startswith("http"):
                response = requests.get(protocol, timeout=3)
                if response.status_code == 200:
                    return protocol
            elif protocol.startswith("dns"):
                answers = dns.resolver.resolve("c2server.com", "A")
                if answers:
                    return protocol
            elif protocol.startswith("icmp"):
                result = ping("c2server.com")
                if result is not None:
                    return protocol
        except Exception:
            continue  # Ignore errors and try the next protocol

    return None  # No working protocol found
