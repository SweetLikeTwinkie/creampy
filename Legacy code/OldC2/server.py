# server.py
#!/usr/bin/env python3

import uvicorn
from admin_api import app
from logging_config import configure_uvicorn_logging_ui

if __name__ == "__main__":
    # Run the specialized function to redirect logs to 'ui'
    configure_uvicorn_logging_ui()

    # Start Uvicorn, disabling its default logging config
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_config=None,  # crucial to prevent overrides
        log_level="info"
    )