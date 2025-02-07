#!/usr/bin/env python3

import os
import json
import asyncio

from config import extract_config_values
from logging_config import logger

DB_NAME = extract_config_values("DB_NAME")

db_lock = asyncio.Lock()

def load_database():
    """
    Loads the JSON database file. If the file does not exist, a new one is created.
    If the file is corrupted, it is renamed as 'ruined_[DB_NAME].json' and a new database is generated.

    :return: A dictionary containing the database structure with keys:
             - "agents": {}  (Stores agent-related data)
             - "tasks": {}   (Stores pending tasks)
             - "results": {} (Stores task execution results)
    """
    # Create new agent database inside json file.
    if not os.path.exists(DB_NAME):
        with open(DB_NAME, "w") as db_file:
            json.dump({"agents": {}, "tasks": {}, "results": {}}, db_file, indent=4)
        logger.info(f"{DB_NAME} not found. Creating new database...")
    # Check if the json file not corrupted and create new instead.
    try:
        with open(DB_NAME, "r") as db_file:
            return json.load(db_file)
        # If the db corrupted the old file will be renamed and a new will created instead.
    except json.JSONDecodeError:
        logger.warning(f"Database file corrupted. Creating new database...")
        corrupted_db = f"ruined+{DB_NAME}" # Generate new name.
        # Ensure it doesn't overwrite an existing ruined file.
        counter = 1
        while os.path.exists(corrupted_db):
            corrupted_db = f"ruined_{counter}_{DB_NAME}"
        # Rename the corrupted file.
        os.rename(DB_NAME, corrupted_db)
        logger.warning(f"Old data base {DB_NAME} renamed to {corrupted_db}.")
        # Create a fresh database.
        with open(DB_NAME, "w") as db_file:
            json.dump({"agents": {}, "tasks": {}, "results": {}}, db_file, indent=4)

        return {"agents": {}, "tasks": {}, "results": {}}


async def save_database():
    """
    Asynchronously saves the database to a JSON file while ensuring thread safety and data integrity.

    Process:
    1. Acquires an asynchronous lock (`db_lock`) to prevent race conditions.
    2. Writes data to a temporary file (`DB_NAME.tmp`) to prevent corruption.
    3. Replaces the original database file (`DB_NAME`) atomically.
    4. Logs success or failure.

    :return: None
    """
    async with db_lock:
        try:
            temp_db_file = f"{DB_NAME}.tmp"
            with open(temp_db_file, "w") as db_file:
                json.dump({"agents": agent_data, "tasks": tasks, "results": results}, db_file, indent=4)
            os.replace(temp_db_file, DB_NAME)
            logger.debug(f"Database {DB_NAME} saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save database. {e}")


# Load and extract
db = load_database()
agent_data = db.get("agents", {})
tasks = db.get("tasks", {})
results = db.get("results", {})