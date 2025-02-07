"""
C2.Backend.protocols.icmp_server.py

Module responsible for handling ICMP-based communications for the Command & Control (C2) framework.
Utilizes Scapy to listen for incoming ICMP Echo Requests and respond with Echo Replies,
enabling potential covert command and control functionalities.
"""
#!/usr/bin/env python3

from C2.Backend.utils.logging_config import loggers
from scapy.layers.inet import IP, ICMP
from scapy.all import sniff, send

# Logger instance for ICMP server events
icmp_logger = loggers['icmp']

def handle_icmp_request(pkt):
    """
    Handles incoming ICMP (Ping) requests and responds with an ICMP Echo Reply.

    Features:
    - Detects ICMP Echo Requests (Type 8) and logs relevant metadata.
    - Extracts payload data to facilitate ICMP-based command processing.
    - Sends an ICMP Echo Reply (Type 0) with a predefined acknowledgment payload.
    - Can be extended for advanced ICMP-based C2 communication strategies.

    Args:
        pkt (scapy.packet.Packet): The captured ICMP packet.
    """
    # Verify if the packet is an ICMP Echo Request (Type 8)
    if pkt.haslayer(ICMP) and pkt[ICMP].type == 8:
        src_ip = pkt[IP].src    # Extract sender's IP address
        dst_ip = pkt[IP].dst    # Extract destination IP address
        seq_id = pkt[ICMP].id   # Extract ICMP ID (used to match requests/replies)
        seq_num = pkt[ICMP].seq # Extract ICMP sequence number

        icmp_logger.debug(f"Received ICMP Ping from {src_ip} (ID: {seq_id}, Seq: {seq_num})")

        # Extract and log optional payload data (useful for ICMP-based C2 operations)
        if pkt[ICMP].payload:
            payload_data = bytes(pkt[ICMP].payload).decode(errors="ignore")
            icmp_logger.debug(f"Received ICMP Payload: {payload_data}")

            # Example: Detect and log C2-related commands embedded in ICMP payloads
            if "C2_CMD" in payload_data:
                icmp_logger.info(f"Received Command via ICMP: {payload_data}")

        # Construct and send an ICMP Echo Reply (Type 0) as a response
        reply = IP(dst=src_ip, src=dst_ip) / ICMP(type=0, id=seq_id, seq=seq_num) / "Reply_OK"
        send(reply, verbose=False)
        icmp_logger.debug(f"Sent ICMP Reply to {src_ip} (ID: {seq_id}, Seq: {seq_num})")

def start_icmp_server(stop_event):
    """
    Starts an ICMP listener to handle incoming ping requests (Echo Requests).

    Features:
    - Uses Scapy to sniff incoming ICMP packets and process valid Echo Requests.
    - Calls `handle_icmp_request()` to handle each detected ICMP request.
    - Filters traffic to capture only ICMP packets for efficiency.
    - Monitors `stop_event` to allow for a graceful shutdown.
    - Implements error handling to ensure stability and robustness.

    Args:
        stop_event (threading.Event): An event used to signal when to stop the listener.
    """
    icmp_logger.info("Listening for incoming ICMP-based communications...")

    try:
        # Start sniffing ICMP packets until `stop_event` is triggered
        sniff(
            filter="icmp",               # Capture only ICMP packets
            prn=handle_icmp_request,     # Process each captured packet using the handler function
            store=False,                 # Avoid storing packets in memory (reduces memory usage)
            stop_filter=lambda pkt: stop_event.is_set()  # Stop sniffing when `stop_event` is set
        )
    except Exception as e:
        icmp_logger.error(f"Error in ICMP server: {e}")

    icmp_logger.info("ICMP listener stopped.")
