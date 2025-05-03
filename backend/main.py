from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File
from upload import router as upload_router
from services.status_manager import get_status
from services.websocket_manager import add_connection, remove_connection
import asyncio
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development. In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Changed the prefix from "/api/upload" to "/api"
app.include_router(upload_router, prefix="/api", tags=["Upload"])

# Test endpoints
@app.get("/test/status/{file_id}")
async def test_get_status(file_id: str):
    """Test endpoint to get status of a file"""
    return {"file_id": file_id, "status": get_status(file_id)}

@app.post("/test/status/{file_id}")
async def test_set_status(file_id: str, status: str):
    """Test endpoint to manually set a status"""
    from services.status_manager import update_status
    update_status(file_id, status)
    return {"message": f"Status for {file_id} set to {status}"}

@app.websocket("/ws/status/{file_id}")
async def websocket_status(websocket: WebSocket, file_id: str):
    await websocket.accept()
    add_connection(file_id, websocket)
    
    try:
        # Send initial status
        initial_status = get_status(file_id)
        await websocket.send_text(initial_status)
        
        while True:
            # Fetch the current status from the status manager
            status = get_status(file_id)
            await websocket.send_text(status)
            await asyncio.sleep(2)  # Check status every 2 seconds
    except WebSocketDisconnect:
        print(f"Client disconnected: {file_id}")
        remove_connection(file_id)
    except Exception as e:
        print(f"Error in WebSocket connection: {str(e)}")
        remove_connection(file_id)

