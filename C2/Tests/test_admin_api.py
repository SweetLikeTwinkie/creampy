#!/usr/bin/env python3
"""
Tests.test_admin_api.py

A simple administrative console for interacting with a C2 server via REST API and WebSockets.
Provides basic controls to check server status, start/stop/restart protocols, fetch configuration details,
and generate agents (file-based or fileless) based on operator choice.
"""

import asyncio
import websockets
import requests
import threading

# Base API and WebSocket URLs
BASE_URL = "http://localhost:8000/api"
WS_URL = "ws://localhost:8000/ws/logs"

def send_request(endpoint, method="GET", data=None):
    """
    Sends an HTTP request to the C2 API.

    Args:
        endpoint (str): API endpoint to send the request to.
        method (str): HTTP method (default is "GET").
        data (dict, optional): JSON payload for POST requests.

    Returns:
        None
    """
    url = f"{BASE_URL}/{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            print("Unsupported method")
            return
        print(f"Response: {response.status_code} - {response.json()}")
    except requests.RequestException as e:
        print(f"Request failed: {e}")

def listen_to_logs():
    """
    Listens to real-time logs from the C2 WebSocket stream and prints received log messages.
    """
    async def log_listener():
        async with websockets.connect(WS_URL) as ws:
            try:
                while True:
                    message = await ws.recv()
                    print(f"[LOG] {message}")
            except websockets.exceptions.ConnectionClosed:
                print("Log stream disconnected.")

    asyncio.run(log_listener())

def start_log_listener():
    """
    Starts the log listener in a separate daemon thread.
    """
    thread = threading.Thread(target=listen_to_logs, daemon=True)
    thread.start()

def generate_agent_request():
    """
    Prompts the operator for agent parameters and sends a request to generate an agent.
    This functionality lets the operator choose between a file-based agent or a fileless (in-memory) agent.
    """
    print("\n--- Agent Generation ---")
    agent_id = input("Enter agent ID: ")
    mode = input("Enter mode ('file' for file-based, 'fileless' for in-memory loader): ")
    # Additional configuration parameters can be collected here as needed.
    payload = {
        "agent_id": agent_id,
        "mode": mode
    }
    send_request("agent/generate", method="POST", data=payload)

def main():
    """
    Entry point for the C2 Admin API Test Console.
    """
    start_log_listener()
    while True:
        print("\nC2 Admin API Test Console")
        print("1. Check server status")
        print("2. Start protocols")
        print("3. Stop protocols")
        print("4. Restart protocols")
        print("5. Get config")
        print("6. Generate agent")
        print("7. Exit")

        choice = input("Select an option: ")

        if choice == "1":
            send_request("status")
        elif choice == "2":
            send_request("control/start", method="POST")
        elif choice == "3":
            send_request("control/stop", method="POST")
        elif choice == "4":
            send_request("control/restart", method="POST")
        elif choice == "5":
            send_request("config")
        elif choice == "6":
            generate_agent_request()
        elif choice == "7":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
