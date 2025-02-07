"""
C2.Backend.API.agent_manager_pg

This module manages Agent records in a PostgreSQL database using SQLAlchemy. 
It includes functionality for registering, authenticating, listing, 
and updating the status of agents.
"""
#!/usr/bin/env python3

import os
import uuid
import datetime

from sqlalchemy import create_engine, Column, String, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Retrieve PostgreSQL connection URL from environment variable or use a default.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/c2_db")

# Create SQLAlchemy engine and session factory
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()


class Agent(Base):
    """
    Represents an Agent in the C2 system.

    Attributes:
        id (int): Primary key for database record.
        agent_id (str): Unique identifier for the agent.
        auth_token (str): Authentication token for the agent.
        ip_address (str): Last known IP address of the agent.
        registered_at (datetime): Timestamp when the agent was first registered.
        last_seen (datetime): Timestamp when the agent was last active.
        status (str): Current status of the agent (e.g., 'Online', 'Offline').
    """
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, unique=True, index=True, nullable=False)
    auth_token = Column(String, nullable=False)
    ip_address = Column(String, nullable=True)
    registered_at = Column(DateTime, nullable=False)
    last_seen = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)


def init_db():
    """
    Initialize the database by creating all defined tables.

    This function should be called at the application startup to ensure 
    the database schema is created or updated as needed.
    """
    Base.metadata.create_all(bind=engine)


def register_agent(agent_id: str, ip_address: str) -> str:
    """
    Register a new Agent or update an existing one.

    If the agent already exists, its IP address, last-seen timestamp, and 
    status are updated. If it is a new agent, a unique authentication token 
    is generated. In both cases, the function returns the agent's token.

    Args:
        agent_id (str): Unique identifier for the Agent.
        ip_address (str): IP address from which the Agent is registering.

    Returns:
        str: Authentication token associated with the Agent.
    """
    session = SessionLocal()
    now = datetime.datetime.utcnow()

    agent = session.query(Agent).filter(Agent.agent_id == agent_id).first()
    if agent:
        # Agent exists, update timestamp, IP, and status
        agent.last_seen = now
        agent.ip_address = ip_address
        agent.status = "Online"
        auth_token = agent.auth_token
    else:
        # Create a new Agent record with a generated authentication token
        auth_token = str(uuid.uuid4())
        agent = Agent(
            agent_id=agent_id,
            auth_token=auth_token,
            ip_address=ip_address,
            registered_at=now,
            last_seen=now,
            status="Online",
        )
        session.add(agent)

    session.commit()
    session.close()
    return auth_token


def authenticate_agent(agent_id: str, auth_token: str) -> bool:
    """
    Validate the authentication token for a given Agent.

    Args:
        agent_id (str): Unique identifier for the Agent.
        auth_token (str): The token provided by the Agent.

    Returns:
        bool: True if the token is valid; otherwise, False.
    """
    session = SessionLocal()
    agent = session.query(Agent).filter(Agent.agent_id == agent_id).first()
    session.close()

    # Check if the agent exists and the token matches
    return agent is not None and agent.auth_token == auth_token


def update_agent_status(agent_id: str, status: str):
    """
    Update the status and last-seen time for an existing Agent.

    Args:
        agent_id (str): Unique identifier for the Agent.
        status (str): The new status (e.g., 'Online', 'Offline').
    """
    session = SessionLocal()
    agent = session.query(Agent).filter(Agent.agent_id == agent_id).first()
    if agent:
        agent.status = status
        agent.last_seen = datetime.datetime.utcnow()
        session.commit()
    session.close()


def list_agents():
    """
    Retrieve all registered agents with their details.

    Returns:
        list: A list of dictionaries, each representing an Agent's data.
    """
    session = SessionLocal()
    agents = session.query(Agent).all()
    session.close()

    agent_list = []
    for agent in agents:
        agent_list.append({
            "agent_id": agent.agent_id,
            "ip_address": agent.ip_address,
            "registered_at": agent.registered_at.isoformat(),
            "last_seen": agent.last_seen.isoformat(),
            "status": agent.status,
        })
    return agent_list
