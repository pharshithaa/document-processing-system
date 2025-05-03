from typing import Dict
from services.websocket_manager import broadcast_status

# Simulating a status dictionary for demonstration
status_db: Dict[str, str] = {}

def update_status(file_id: str, status: str):
    """Updates the status of the file in the status_db and broadcasts it."""
    status_db[file_id] = status
    broadcast_status(file_id, status)

# Alias for backward compatibility if needed
set_status = update_status

def get_status(file_id: str) -> str:
    """Gets the status of the file from the status_db."""
    return status_db.get(file_id, "Unknown Status")
