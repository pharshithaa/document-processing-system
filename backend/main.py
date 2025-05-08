from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from upload import router as upload_router
from services.status_manager import get_status
from services.websocket_manager import add_connection, remove_connection
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from llm_clients.gemini import ask_gemini_question
import os
from PyPDF2 import PdfReader

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include upload router
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
    print(f"New WebSocket connection request for file: {file_id}")
    await websocket.accept()
    print(f"WebSocket connection accepted for file: {file_id}")
    add_connection(file_id, websocket)
    
    try:
        # Send initial status
        initial_status = get_status(file_id)
        print(f"Sending initial status for {file_id}: {initial_status}")
        await websocket.send_text(initial_status)
        
        last_status = initial_status
        while True:
            # Fetch the current status from the status manager
            current_status = get_status(file_id)
            if current_status != "Unknown" and current_status != last_status:
                print(f"Sending status update for {file_id}: {current_status}")
                await websocket.send_text(current_status)
                last_status = current_status
                
                # Stop sending updates if processing is complete
                if current_status in ['Completed', 'Failed', 'Stopped']:
                    print(f"Processing complete for {file_id}, closing connection")
                    break
                    
            await asyncio.sleep(0.1)  # Check status very frequently
    except WebSocketDisconnect:
        print(f"Client disconnected: {file_id}")
    except Exception as e:
        print(f"Error in WebSocket connection: {str(e)}")
    finally:
        remove_connection(file_id)

@app.post("/api/ask")
async def ask_question(request: Request):
    data = await request.json()
    document_id = data.get("document_id")
    question = data.get("question")
    if not document_id or not question:
        return {"error": "document_id and question are required"}
    # Assume file is stored in uploads/ with its filename as document_id
    file_path = os.path.join("uploads", document_id)
    if not os.path.exists(file_path):
        return {"error": "Document not found"}
    # Extract text from PDF
    reader = PdfReader(file_path)
    document_text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            document_text += page_text
    if not document_text.strip():
        return {"error": "No text found in document"}
    # Use Gemini to answer the question
    answer = ask_gemini_question(document_text, question)
    return {"answer": answer}

