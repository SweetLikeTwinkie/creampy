"""
Tests.watch_db.py

A utility script that periodically retrieves and displays the list of registered agents from the database.
It continuously monitors changes in agent records and prints them to the console.
"""
#!/usr/bin/env python3

import time
from C2.Backend.API.agent_manager_pg import list_agents

def watch_agents(interval: int = 5):
    """
    Periodically retrieves and prints the list of agents from the database.

    Args:
        interval (int): Time interval (in seconds) between queries. Default is 5 seconds.
    """
    try:
        while True:
            agents = list_agents()
            print("----- Current Agents in DB -----")
            if not agents:
                print("No agents registered.")
            else:
                for agent in agents:
                    print(agent)
            print("--------------------------------")
            time.sleep(interval)
    except KeyboardInterrupt:
        print("Stopped watching the database.")

if __name__ == "__main__":
    watch_agents()
