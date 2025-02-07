"""
C2.Backend.protocols.smb_server.py

Module responsible for initializing and managing an SMB server for agent tasking and file transfers.
Utilizes Impacket's SimpleSMBServer to provide a network share over SMB, supporting SMB2 for
modern client compatibility.
"""
#!/usr/bin/env python3

import os
import time
import threading

from C2.Backend.utils.logging_config import loggers
from impacket.smbserver import SimpleSMBServer
from C2.Backend.utils.auxiliary import is_port_in_use

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

    # Define SMB share directory path
    smb_share_path = "smb_tasks"

    # Ensure the SMB share directory exists; create it if necessary
    if not os.path.exists(smb_share_path):
        os.makedirs(smb_share_path)
        smb_logger.info(f"Created SMB share directory: {smb_share_path}")

    try:
        # Initialize the SMB server instance
        smb_server = SimpleSMBServer()

        # Add a network share named "TASKS" pointing to the defined directory
        smb_server.addShare("TASKS", smb_share_path)

        # Enable SMB2 protocol for improved client compatibility
        smb_server.setSMB2Support(True)

        smb_logger.info("SMB share 'TASKS' added successfully.")
        smb_logger.info("Starting SMB server on port 445...")

        # Start the SMB server in a separate daemon thread to prevent blocking the main process
        server_thread = threading.Thread(target=smb_server.start, daemon=True)
        server_thread.start()

        # Monitor the `stop_event` to determine when to shut down the server
        while not stop_event.is_set():
            time.sleep(1)  # Sleep briefly to reduce CPU usage

        smb_logger.info("Stop event received. Stopping SMB server...")

        # Attempt a graceful shutdown of the SMB server
        try:
            if hasattr(smb_server, "stop"):
                # If the `stop` method exists, use it to shut down the server
                smb_server.stop()
            elif hasattr(smb_server, "socket"):
                # If no stop method, attempt to close the server socket
                smb_server.socket.close()
            else:
                smb_logger.error("No method available for graceful shutdown of the SMB server.")
        except Exception as e:
            smb_logger.error(f"Error stopping SMB server: {e}")

        # Optionally wait for the server thread to exit within a timeout period
        server_thread.join(timeout=5)
        smb_logger.info("SMB server stopped.")

    except Exception as e:
        smb_logger.error(f"SMB Server failed to start: {e}")
