import sqlite3
import uuid
import datetime

DATABASE = 'agents.db'

def init_db():
    """
    Initializes the SQLite database and creates the agents table if it doesn't exist.
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT UNIQUE,
            auth_token TEXT,
            ip_address TEXT,
            registered_at TEXT,
            last_seen TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def register_agent(agent_id: str, ip_address: str) -> str:
    """
    Registers an agent or updates an existing agent's details.
    Returns an authentication token.

    :param agent_id: Unique identifier for the agent
    :param ip_address: IP address of the agent registering
    :return: auth_token string for the agent
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    now = datetime.datetime.utcnow().isoformat()
    c.execute("SELECT * FROM agents WHERE agent_id=?", (agent_id,))
    row = c.fetchone()
    if row:
        # Update the agent's last seen time and ip address
        c.execute(
            "UPDATE agents SET last_seen=?, ip_address=?, status=? WHERE agent_id=?",
            (now, ip_address, 'online', agent_id)
        )
        auth_token = row[2]
    else:
        # Create a new agent entry with a generated authentication token
        auth_token = str(uuid.uuid4())
        c.execute(
            "INSERT INTO agents (agent_id, auth_token, ip_address, registered_at, last_seen, status) VALUES (?, ?, ?, ?, ?, ?)",
            (agent_id, auth_token, ip_address, now, now, 'online')
        )
    conn.commit()
    conn.close()
    return auth_token

def authenticate_agent(agent_id: str, auth_token: str) -> bool:
    """
    Validates the provided authentication token for the given agent.

    :param agent_id: Agent's unique identifier
    :param auth_token: Token provided by the agent
    :return: True if valid, False otherwise
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT auth_token FROM agents WHERE agent_id=?", (agent_id,))
    row = c.fetchone()
    conn.close()
    return bool(row and row[0] == auth_token)

def update_agent_status(agent_id: str, status: str):
    """
    Updates the status and last seen timestamp of an agent.

    :param agent_id: Agent's unique identifier
    :param status: New status (e.g., 'online', 'offline')
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    now = datetime.datetime.utcnow().isoformat()
    c.execute("UPDATE agents SET status=?, last_seen=? WHERE agent_id=?", (status, now, agent_id))
    conn.commit()
    conn.close()

def list_agents():
    """
    Retrieves all registered agents with their details.

    :return: List of agent dictionaries
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT agent_id, ip_address, registered_at, last_seen, status FROM agents")
    rows = c.fetchall()
    conn.close()
    agents = []
    for row in rows:
        agents.append({
            "agent_id": row[0],
            "ip_address": row[1],
            "registered_at": row[2],
            "last_seen": row[3],
            "status": row[4]
        })
    return agents
