from typing import Dict
import asyncio
from fastapi import WebSocket

# Store active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

def broadcast_status(file_id: str, status: str):
    """Broadcast status update to all connected clients for a file"""
    if file_id in active_connections:
        try:
            asyncio.create_task(active_connections[file_id].send_text(status))
        except Exception as e:
            print(f"Error broadcasting status: {str(e)}")
            active_connections.pop(file_id, None)

def add_connection(file_id: str, websocket: WebSocket):
    """Add a new WebSocket connection"""
    active_connections[file_id] = websocket

def remove_connection(file_id: str):
    """Remove a WebSocket connection"""
    active_connections.pop(file_id, None) 