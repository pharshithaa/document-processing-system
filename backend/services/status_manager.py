from fastapi import FastAPI
import asyncio

# Store status updates
status_updates = {}

def update_status(file_id: str, status: str):
    """Update the status of a file processing task"""
    print(f"Updating status for {file_id} to: {status}")
    status_updates[file_id] = status

def get_status(file_id: str) -> str:
    """Get the current status of a file processing task"""
    status = status_updates.get(file_id, "Unknown")
    print(f"Getting status for {file_id}: {status}")
    return status
