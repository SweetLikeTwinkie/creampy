# protocols/http_server.py
#!/usr/bin/env python3

import os
import uvicorn
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
from pydantic import BaseModel
from config import load_config
from utils.auxiliary import is_port_in_use
from logging_config import loggers

config = load_config()
SSL_CERT = config["SERVER_CRT"]
SSL_KEY = config["SERVER_KEY"]

http_logger = loggers["http"]
# Redirect Uvicorn logs to our logging system
uvicorn_logger = logging.getLogger("uvicorn")

# Remove default Uvicorn handlers (so it doesn't log to console)
uvicorn_logger.propagate = False  # Prevents logs from going to the root logger
uvicorn_logger.handlers.clear()

# Attach the same handlers as http_logger (file logging only)
for handler in http_logger.handlers:
    uvicorn_logger.addHandler(handler)

# Match log level with our logging system
uvicorn_logger.setLevel(http_logger.level)

# Explicitly redirect Uvicorn access and error logs
logging.getLogger("uvicorn.access").handlers.clear()
logging.getLogger("uvicorn.access").addHandler(http_logger.handlers[0])
logging.getLogger("uvicorn.access").setLevel(http_logger.level)

logging.getLogger("uvicorn.error").handlers.clear()
logging.getLogger("uvicorn.error").addHandler(http_logger.handlers[0])
logging.getLogger("uvicorn.error").setLevel(http_logger.level)

c2_app = FastAPI(title="CreamPY Command & Control server", version="2.0.0", description="Python based c2 app.")
c2_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Allow requests from any origin
    allow_credentials=True,    # Allow credentials (cookies, authentication headers)
    allow_methods=["*"],       # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"]        # Allow all headers
)
connected_agents: Dict[str, WebSocket] = {} # Stores active agents connected via WebSockets

#  data validation and serialization models
class AgentRegistration(BaseModel):
    data: str
class TaskRequest(BaseModel):
    password: str
    agent_id: str
    task_name: str
class AuthMessage(BaseModel):
    password: str

@c2_app.get("/")
async def root():
    """
    Root endpoint for the C2 server.

    :return: A JSON response indicating the server is running.
    """
    return {"message": "C2 Server Running"}

async def run_http_server():
    """
    Starts the C2 HTTP server on port 80 using Uvicorn.

    Features:
    - Ensures port 80 is available before starting.
    - Uses FastAPI (`c2_app`) as the application.
    - Logs status updates and errors.
    """
    if is_port_in_use(80):
        http_logger.error("Port 80 is already in use. HTTP server will not start.")
        return

    http_logger.info("Starting HTTP C2 server on port 80...")

    try:
        server_config = uvicorn.Config(
            "protocols.http_server:c2_app",
            host="0.0.0.0",
            port=80,
            log_level=http_logger.level,
            access_log=True
        )
        server = uvicorn.Server(server_config)
        await server.serve()
    except Exception as e:
        http_logger.error(f"HTTP Server failed to start: {e}")


async def run_https_server():
    """
    Starts the C2 HTTPS server on port 443 using Uvicorn.

    Features:
    - Ensures SSL certificates exist before starting.
    - Ensures port 443 is available before starting.
    - Uses FastAPI (`c2_app`) as the application.
    - Logs status updates and errors.
    """

    if is_port_in_use(443):
        http_logger.error("Port 443 is already in use. HTTPS server will not start.")
        return
    # Ensure SSL certificate files exist
    if not os.path.exists(SSL_KEY) or not os.path.exists(SSL_CERT):
        http_logger.error(f"Missing SSL certificate files! Ensure {SSL_KEY} and {SSL_CERT} exist.")
        return  # Stop execution if SSL certs are missing

    http_logger.info("Starting HTTPS C2 server on port 443...")

    try:
        http_config = uvicorn.Config(
            c2_app,
            host="0.0.0.0",
            port=443,
            log_level=http_logger.level,
            access_log=True,
            ssl_keyfile=SSL_KEY,
            ssl_certfile=SSL_CERT
        )
        server = uvicorn.Server(http_config)
        await server.serve()
    except Exception as e:
        http_logger.error(f"HTTPS Server failed to start: {e}")