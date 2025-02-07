# admin_api.py
#!/usr/bin/env python3

"""
admin_api.py
FastAPI-based API for managing and monitoring the C2 server
Provides HTTP endpoints for server control and WebSocket for real-time log streaming
"""
from ipaddress import ip_address

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os
import aiofiles
from pydantic import BaseModel
from agent_manager import init_db, register_agent, authenticate_agent, list_agents, update_agent_status


from logging_config import loggers
from config import load_config
from manager import protocol_manager

# Initialize FastAPI application
app = FastAPI(title="C2 Admin API", version="1.0.0")

# Enable Cross-Origin Resource Sharing (CORS) for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"], # Allows requests from the React development server (localhost:3001)
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
    Check the current status of protocol execution.
    Returns:
        JSON response indicating whether protocols are running.
    Example response:
        { "running": true }
    """
    return {"running": protocol_manager.running}


@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """
    WebSocket endpoint for real-time log streaming.
    Sends new log file entries to the connected client.
    """
    await websocket.accept()
    log_file_path = config["LOGGING_FILE_PATH"]

    # Ensure the log file exists before attempting to read
    if not os.path.exists(log_file_path):
        open(log_file_path, "w").close()

    try:
        async with aiofiles.open(log_file_path, "r") as afp:
            # Go to the end of the file
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
    Retrieve the current server configuration.
    Returns:
        JSON object containing configuration settings.
    """
    return config


@app.post("/api/control/{action}")
async def control_server(action: str):
    """
    Control the C2 server's protocol execution.
    Allows starting, stopping, or restarting all protocols.

    Supported actions:
        - POST /api/control/start: Starts all protocols.
        - POST /api/control/stop: Stops all protocols.
        - POST /api/control/restart: Restarts all protocols.

    Returns:
        JSON response indicating whether the action was successfully triggered.
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
def start_up():
    init_db()

class AgentRegistrationRequest(BaseModel):
    agent_id: str

class AgentRegistrationResponse(BaseModel):
    auth_token: str

class AgentAuthRequest(BaseModel):
    agent_id: str
    auth_token: str

@app.post('/api/agent/register', response_model=AgentRegistrationResponse)
def api_register_agent(request: AgentRegistrationRequest, req: Request):
    """

    :param request:
    :param req:
    :return:
    """
    ip_address = req.client.host
    token = register_agent(request.agent_id, ip_address)
    return AgentRegistrationResponse(auth_token=token)

@app.post('/api/agent/authenticate')
def api_authenticate_agent(request: AgentAuthRequest):
    """

    :param request:
    :return:
    """
    if authenticate_agent(request.agent_id, request.auth_token):
        return {"message": "Authentication successful!"}
    return HTTPException(status_code=401, detail="Authentication failed.")

@app.get('/api/agent/list')
def api_list_agents():s
    """

    :return:
    """
    agents = list_agents()
    return {"agents": agents}

