"""
C2.Backend.utils.manager.py

Module responsible for managing multiple network communication protocols for the C2 server.
Handles the lifecycle of HTTP, HTTPS, SMB, DNS, and ICMP servers.
Ensures proper startup and graceful shutdown of all running protocols.
"""
#!/usr/bin/env python3

import asyncio
import concurrent.futures
import threading
from C2.Backend.utils.logging_config import loggers
from C2.Backend.protocols.http_server import run_http_server, run_https_server
from C2.Backend.protocols.smb_server import start_smb_server
from C2.Backend.protocols.dns_server import start_dns_server
from C2.Backend.protocols.icmp_server import start_icmp_server

# Logger instance for C2 server
logger = loggers["c2server"]

class ProtocolManager:
    """
    Manages the lifecycle of multiple network communication protocols
    for a Command and Control (C2) server.

    Features:
    - HTTP and HTTPS servers run as asyncio tasks.
    - SMB, DNS, and ICMP servers run in separate threads using an executor.
    - Provides asynchronous methods to start and stop all protocols cleanly.
    """

    def __init__(self):
        """
        Initializes the ProtocolManager instance.

        - Creates a thread pool executor for running non-async protocols.
        - Maintains a list of running protocol tasks.
        - Uses an event (`stop_event`) to signal thread-based servers to stop.
        """
        self.loop = None  # Stores the current asyncio event loop
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)  # Thread pool for blocking protocols
        self.protocol_tasks = []  # Stores active tasks (async and thread-based)
        self.running = False  # Flag to track running status
        self.stop_event = threading.Event()  # Event to signal threads to stop execution

    async def start_all(self):
        """
        Asynchronously starts all protocols.

        - HTTP/HTTPS servers are executed as asyncio tasks.
        - SMB, DNS, and ICMP servers are executed in separate threads using the executor.
        - Ensures protocols do not start multiple times concurrently.
        """
        if self.running:
            logger.info("Protocols are already running.")
            return

        logger.info("Starting all protocols...")
        self.loop = asyncio.get_running_loop()
        self.stop_event.clear()  # Ensure previous stop signals are cleared

        # Start HTTP and HTTPS servers as asyncio tasks
        http_server_task = asyncio.create_task(run_http_server())
        https_server_task = asyncio.create_task(run_https_server())

        # Start SMB, DNS, and ICMP servers in separate threads
        smb_server_future = self.loop.run_in_executor(self.executor, start_smb_server, self.stop_event)
        dns_server_future = self.loop.run_in_executor(self.executor, start_dns_server, self.stop_event)
        icmp_server_future = self.loop.run_in_executor(self.executor, start_icmp_server, self.stop_event)

        # Track running protocol tasks
        self.protocol_tasks = [
            http_server_task,
            https_server_task,
            smb_server_future,
            dns_server_future,
            icmp_server_future
        ]
        self.running = True
        logger.info("All protocols started in background.")

    async def stop_all(self):
        """
        Asynchronously stops all running protocols.

        - Signals `stop_event` to terminate thread-based protocols.
        - Cancels all asyncio-based tasks.
        - Ensures a short delay to allow thread-based protocols to exit gracefully.
        - Resets state variables for future restarts.
        """
        if not self.running:
            logger.info("Protocols are not currently running.")
            return

        logger.info("Stopping all protocols...")

        # Signal thread-based servers to terminate
        self.stop_event.set()

        # Cancel asyncio-based tasks
        for task in self.protocol_tasks:
            if isinstance(task, asyncio.Task):
                task.cancel()

        # Allow thread-based servers time to terminate gracefully
        await asyncio.sleep(1)

        # Clear tracked tasks and reset running state
        self.protocol_tasks.clear()
        self.running = False
        logger.info("All protocols stopped.")

# Create a global instance of the ProtocolManager
protocol_manager = ProtocolManager()
