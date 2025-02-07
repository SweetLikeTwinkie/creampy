"""
#C2.Backend.server.py

This script serves as the entry point for the C2 Backend server. It applies a
specialized logging configuration that redirects logs to the UI, and then
launches the Uvicorn server using the `admin_api` FastAPI application.
"""
#!/usr/bin/env python3

import uvicorn
from C2.Backend.API.admin_api import app
from C2.Backend.utils.logging_config import configure_uvicorn_logging_ui

if __name__ == "__main__":
    # Apply custom logging configuration to direct logs to the UI
    configure_uvicorn_logging_ui()

    # Run the Uvicorn server on all interfaces (0.0.0.0) at port 8000
    # and disable Uvicorn's default logging to maintain our custom setup
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config=None,  # Prevents default Uvicorn log overrides
        log_level="info"
    )