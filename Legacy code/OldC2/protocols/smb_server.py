# protocols/smb_server.py
#!/usr/bin/env python3

import os
import time
import threading

from logging_config import loggers
from impacket.smbserver import SimpleSMBServer
from utils.auxiliary import is_port_in_use

# Logger instance for SMB server events
smb_logger = loggers["smb"]

def start_smb_server(stop_event):
    """
    Starts an SMB server for agent tasking and file transfers.

    Features:
    - Uses Impacket's SimpleSMBServer to create an SMB share.
    - Adds an SMB share named "TASKS" for agents to retrieve task files.
    - Enables SMB2 support for better compatibility with modern clients.
    - Logs important events for monitoring and debugging.
    - Runs the server in a separate thread to prevent blocking.
    - Monitors `stop_event` to allow a graceful shutdown when required.

    If port 445 is already in use, the function logs an error and exits.

    Args:
        stop_event (threading.Event): An event object used to signal when the SMB server should stop.
    """

    smb_logger.info("Initializing SMB Server...")

    # Check if the required SMB port (445) is already in use
    if is_port_in_use(445):
        smb_logger.error("Port 445 is already in use. SMB server will not start.")
        return

    # Ensure the SMB share directory exists
    smb_share_path = "smb_tasks"
    if not os.path.exists(smb_share_path):
        os.makedirs(smb_share_path)
        smb_logger.info(f"Created SMB share directory: {smb_share_path}")

    try:
        # Initialize the SMB server instance
        smb_server = SimpleSMBServer()
        smb_server.addShare("TASKS", smb_share_path)  # Create SMB share named "TASKS"
        smb_server.setSMB2Support(True)  # Enable SMB2 protocol support

        smb_logger.info("SMB share 'TASKS' added successfully.")
        smb_logger.info("Starting SMB server on port 445...")

        # Start the SMB server in a separate daemon thread
        server_thread = threading.Thread(target=smb_server.start, daemon=True)
        server_thread.start()

        # Monitor stop_event to determine when to shut down the server
        while not stop_event.is_set():
            time.sleep(1)  # Sleep briefly to reduce CPU usage

        smb_logger.info("Stop event received. Stopping SMB server...")

        # Attempt a graceful shutdown of the SMB server
        try:
            if hasattr(smb_server, "stop"):
                smb_server.stop()  # Preferred method if available
            elif hasattr(smb_server, "socket"):
                smb_server.socket.close()  # Alternative shutdown method
            else:
                smb_logger.error("No method available for graceful shutdown of the SMB server.")
        except Exception as e:
            smb_logger.error(f"Error stopping SMB server: {e}")

        # Optionally wait for the server thread to exit
        server_thread.join(timeout=5)
        smb_logger.info("SMB server stopped.")

    except Exception as e:
        smb_logger.error(f"SMB Server failed to start: {e}")
