# protocols/icmp_server.py
#!/usr/bin/env python3

from logging_config import loggers
from scapy.layers.inet import IP, ICMP
from scapy.all import sniff, send

# Logger instance for ICMP server events
icmp_logger = loggers['icmp']

def handle_icmp_request(pkt):
    """
    Handles incoming ICMP (Ping) requests and responds with an ICMP Echo Reply.

    Features:
    - Detects ICMP Echo Requests (Type 8).
    - Logs incoming ping requests for monitoring and debugging.
    - Replies with an ICMP Echo Reply (Type 0).
    - Extracts optional payload data (useful for ICMP-based C2 communication).
    - Can be extended to implement covert command execution via ICMP.

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

        # Extract payload data (optional, useful for ICMP-based C2)
        if pkt[ICMP].payload:
            payload_data = bytes(pkt[ICMP].payload).decode(errors="ignore")
            icmp_logger.debug(f"Received ICMP Payload: {payload_data}")

            # Example: If the payload contains a command, process it (expand for ICMP-based C2)
            if "C2_CMD" in payload_data:
                icmp_logger.info(f"Received Command via ICMP: {payload_data}")

        # Construct and send an ICMP Echo Reply (Type 0) with a simple acknowledgment payload
        reply = IP(dst=src_ip, src=dst_ip) / ICMP(type=0, id=seq_id, seq=seq_num) / "Reply_OK"
        send(reply, verbose=False)

        icmp_logger.debug(f"Sent ICMP Reply to {src_ip} (ID: {seq_id}, Seq: {seq_num})")


def start_icmp_server(stop_event):
    """
    Starts an ICMP listener to handle incoming ping requests (Echo Requests).

    Features:
    - Uses Scapy to sniff incoming ICMP packets.
    - Calls `handle_icmp_request()` to process valid ICMP Echo Requests.
    - Filters traffic to capture only ICMP packets.
    - Uses a `stop_event` to allow graceful shutdown of the listener.
    - Implements error handling to ensure stability.

    Args:
        stop_event (threading.Event): An event used to signal when to stop the listener.
    """
    icmp_logger.info("Listening for incoming ICMP-based communications...")

    try:
        # Start sniffing ICMP packets until `stop_event` is set
        sniff(
            filter="icmp",               # Capture only ICMP packets
            prn=handle_icmp_request,     # Process each captured packet with this function
            store=False,                 # Do not store packets in memory (reduces memory usage)
            stop_filter=lambda pkt: stop_event.is_set()  # Stop sniffing when `stop_event` is triggered
        )
    except Exception as e:
        icmp_logger.error(f"Error in ICMP server: {e}")

    icmp_logger.info("ICMP listener stopped.")
