"""
C2.Backend.protocols.dns_server.py

Module responsible for initializing and managing a simple DNS server for handling agent communications.
Utilizes dnslib to parse and construct DNS queries and responses, supporting basic A-record resolution.
"""
#!/usr/bin/env python3

import socket
import subprocess
from dnslib import DNSRecord, QTYPE, RR, A, DNSHeader
from C2.Backend.utils.logging_config import loggers
from C2.Backend.utils.auxiliary import is_port_in_use

# Logger instance for DNS server events
dns_logger = loggers["dns"]

def stop_system_dns_service(service_name="systemd-resolved"):
    """
    Attempt to stop the specified DNS service to allow this server to bind to port 53.

    Args:
        service_name (str): The name of the system DNS service to stop.
    """
    dns_logger.info(f"Stopping DNS service: {service_name}")
    try:
        subprocess.run(["systemctl", "stop", service_name], check=True)
        dns_logger.info(f"Successfully stopped {service_name}.")
    except subprocess.CalledProcessError as e:
        dns_logger.error(f"Failed to stop {service_name}. Error: {e}")

def start_system_dns_service(service_name="systemd-resolved"):
    """
    Attempt to restart the specified DNS service after the DNS server stops.

    Args:
        service_name (str): The name of the system DNS service to start.
    """
    dns_logger.info(f"Starting DNS service: {service_name}")
    try:
        subprocess.run(["systemctl", "start", service_name], check=True)
        dns_logger.info(f"Successfully started {service_name}.")
    except subprocess.CalledProcessError as e:
        dns_logger.error(f"Failed to start {service_name}. Error: {e}")

def start_dns_server(stop_event):
    """
    Starts a simple DNS server on UDP port 53.

    Features:
    - Stops the default Ubuntu DNS service (systemd-resolved) to free port 53.
    - Listens for DNS queries and responds with a fixed IP address (127.0.0.1).
    - Utilizes dnslib to parse and construct DNS messages.
    - Periodically checks `stop_event` for a graceful shutdown.
    - Restarts the default DNS service when the server stops.

    Args:
        stop_event (threading.Event): An event object used to signal when the DNS server should stop.
    """
    stop_system_dns_service("systemd-resolved")

    port = 53
    if is_port_in_use(port):
        dns_logger.error(f"Port {port} is still in use. DNS server will not start.")
        start_system_dns_service("systemd-resolved")
        return

    dns_logger.info("Starting DNS server on UDP port 53...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", port))
    except Exception as e:
        dns_logger.error(f"Failed to bind DNS server to port {port}: {e}")
        start_system_dns_service("systemd-resolved")
        return

    sock.settimeout(1)
    fixed_ip = "127.0.0.1"

    dns_logger.info("DNS server is now running.")
    try:
        while not stop_event.is_set():
            try:
                data, addr = sock.recvfrom(512)
                dns_logger.debug(f"Received DNS query from {addr}")
                request = DNSRecord.parse(data)
                reply = DNSRecord(
                    DNSHeader(id=request.header.id, qr=1, aa=1, ra=1),
                    q=request.q
                )

                qname = request.q.qname
                qtype = QTYPE[request.q.qtype]
                dns_logger.debug(f"Query for {qname} type {qtype}")

                reply.add_answer(RR(rname=qname, rtype=QTYPE.A, rclass=1, ttl=60, rdata=A(fixed_ip)))
                sock.sendto(reply.pack(), addr)
                dns_logger.debug(f"Sent DNS reply to {addr} with IP {fixed_ip}")
            except socket.timeout:
                continue
            except Exception as e:
                dns_logger.error(f"DNS server error: {e}")

    finally:
        dns_logger.info("Stopping DNS server...")
        sock.close()
        dns_logger.info("DNS server stopped.")
        start_system_dns_service("systemd-resolved")
