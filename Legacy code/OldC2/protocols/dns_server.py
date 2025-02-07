# protocols/dns_server.py
#!/usr/bin/env python3

import socket
import time
import subprocess
from dnslib import DNSRecord, QTYPE, RR, A, DNSHeader
from logging_config import loggers
from utils.auxiliary import is_port_in_use

dns_logger = loggers["dns"]

def stop_system_dns_service(service_name="systemd-resolved"):
    """
    Attempt to stop the specified DNS service so this server can bind to port 53.
    """
    dns_logger.info(f"Stopping DNS service: {service_name}")
    try:
        # Running systemctl stop <service_name>
        subprocess.run(["systemctl", "stop", service_name], check=True)
        dns_logger.info(f"Successfully stopped {service_name}.")
    except subprocess.CalledProcessError as e:
        dns_logger.error(f"Failed to stop {service_name}. Error: {e}")

def start_system_dns_service(service_name="systemd-resolved"):
    """
    Attempt to start the specified DNS service again after this server stops.
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

    1. Stops the Ubuntu default DNS service (systemd-resolved) to free port 53.
    2. Listens for DNS queries and responds with a fixed IP address (127.0.0.1).
    3. Uses dnslib to parse and construct DNS messages.
    4. Periodically checks the stop_event for graceful shutdown.
    5. Restarts the Ubuntu default DNS service when done.

    :param stop_event: A threading.Event used to signal when to stop the DNS server.
    """
    # *** Stop systemd-resolved to free up port 53 ***
    stop_system_dns_service("systemd-resolved")

    port = 53

    # Double-check port availability after stopping systemd-resolved
    if is_port_in_use(port):
        dns_logger.error(f"Port {port} is still in use. DNS server will not start.")
        # Attempt to restart the DNS service before returning
        start_system_dns_service("systemd-resolved")
        return

    dns_logger.info("Starting DNS server on UDP port 53...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", port))
    except Exception as e:
        dns_logger.error(f"Failed to bind DNS server to port {port}: {e}")
        # Attempt to restart the DNS service before returning
        start_system_dns_service("systemd-resolved")
        return

    # Set a short timeout so we can periodically check the stop_event
    sock.settimeout(1)
    fixed_ip = "127.0.0.1"  # Fixed IP to reply with for any query

    dns_logger.info("DNS server is now running.")
    try:
        while not stop_event.is_set():
            try:
                data, addr = sock.recvfrom(512)  # Standard DNS packet size
                dns_logger.debug(f"Received DNS query from {addr}")

                request = DNSRecord.parse(data)
                reply = DNSRecord(
                    DNSHeader(id=request.header.id, qr=1, aa=1, ra=1),
                    q=request.q
                )

                qname = request.q.qname
                qtype = QTYPE[request.q.qtype]
                dns_logger.debug(f"Query for {qname} type {qtype}")

                # Add an answer: reply with a fixed IP address for any A-record query
                reply.add_answer(
                    RR(rname=qname, rtype=QTYPE.A, rclass=1, ttl=60, rdata=A(fixed_ip))
                )

                sock.sendto(reply.pack(), addr)
                dns_logger.debug(f"Sent DNS reply to {addr} with IP {fixed_ip}")
            except socket.timeout:
                # Check the stop_event periodically
                continue
            except Exception as e:
                dns_logger.error(f"DNS server error: {e}")

    finally:
        # This block ensures we clean up and restore the service no matter how the loop exits.
        dns_logger.info("Stopping DNS server...")
        sock.close()
        dns_logger.info("DNS server stopped.")

        # *** Restart systemd-resolved after our DNS server stops ***
        start_system_dns_service("systemd-resolved")