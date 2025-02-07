"""
Tests.test_agent_registration_api

A utility script for interacting with the C2 agent API.
Provides functions to register, authenticate, and list agents via HTTP requests.
"""
#!/usr/bin/env python3

import requests

# Base URL for the agent API
BASE_URL = 'http://127.0.0.1:8000/api/agent'

def register_agent(agent_id: str) -> str:
    """
    Registers an Agent by calling the /register endpoint.

    Args:
        agent_id (str): The unique identifier of the agent.

    Returns:
        str: Authentication token if registration is successful, empty string otherwise.
    """
    url = f"{BASE_URL}/register"
    payload = {"agent_id": agent_id}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        data = response.json()
        print(f'Agent {agent_id} registered')
        return data.get("auth_token", "")
    else:
        print(f'Agent {agent_id} registration failed')
        return ""

def authenticate_agent(agent_id: str, auth_token: str):
    """
    Authenticates an Agent by calling the /authenticate endpoint.

    Args:
        agent_id (str): The unique identifier of the agent.
        auth_token (str): The authentication token provided during registration.
    """
    url = f"{BASE_URL}/authenticate"
    payload = {"agent_id": agent_id, "auth_token": auth_token}
    response = requests.post(url, json=payload)
    print("Authentication response: ", response.status_code, response.json())

def list_agents():
    """
    Retrieves and prints the list of registered agents by calling the /list endpoint.
    """
    url = f"{BASE_URL}/list"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        print('Agent list: ')
        for agent in data.get("agents", []):
            print(agent)
    else:
        print("Error listing agents:", response.status_code, response.text)

if __name__ == '__main__':
    test_agent_id = 'agent_001'
    auth_token = register_agent(test_agent_id)
    if auth_token:
        authenticate_agent(test_agent_id, auth_token)
    list_agents()
