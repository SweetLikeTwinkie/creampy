#!/usr/bin/env python3
"""
C2.Tests.agent_test.py

A simple test script to interact with the C2 server's agent registration,
authentication, listing, and generation endpoints.
"""

import requests

# Make sure the BASE_URL is set to the same port as your server (here: port 8000)
BASE_URL = "http://localhost:8000/api"

def test_registration():
    agent_id = "agent_test_500"
    url = f"{BASE_URL}/agent/register"
    data = {"agent_id": agent_id}
    print("Using BASE_URL:", BASE_URL)
    response = requests.post(url, json=data)
    print("Registration response:", response.status_code, response.json())
    return agent_id, response.json().get("auth_token")

def test_authentication(agent_id, auth_token):
    url = f"{BASE_URL}/agent/authenticate"
    data = {"agent_id": agent_id, "auth_token": auth_token}
    response = requests.post(url, json=data)
    print("Authentication response:", response.status_code, response.json())

def test_list_agents():
    url = f"{BASE_URL}/agent/list"
    response = requests.get(url)
    print("List agents response:", response.status_code, response.json())

def test_generate_agent(agent_id, mode):
    url = f"{BASE_URL}/agent/generate"
    data = {"agent_id": agent_id, "mode": mode}
    response = requests.post(url, json=data)
    print("Generate agent response:", response.status_code, response.json())

if __name__ == "__main__":
    agent_id, auth_token = test_registration()
    test_authentication(agent_id, auth_token)
    test_list_agents()
    test_generate_agent(agent_id, "file")
    test_generate_agent(agent_id, "fileless")