from fastapi import APIRouter, UploadFile, File, HTTPException
from services.status_manager import update_status, get_status
from services.extraction import extract_pdf_metadata, is_scanned_pdf, contains_financial_tables, is_legal_document
from llm_clients.langchain_router import LangChainRouter
import os
import asyncio


router = APIRouter()

@router.post("/upload/")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        return {"error": "Only PDF files are supported."}

    # Use filename as file_id
    file_id = file.filename
    update_status(file_id, "Uploading")
    await asyncio.sleep(1)  # Give time for the status to be sent

    try:
        # Save the uploaded file
        file_path = os.path.join("uploads", file.filename)
        with open(file_path, "wb") as f:
            f.write(file.file.read())

        # Extract metadata
        update_status(file_id, "Extracting")
        await asyncio.sleep(1)
        metadata = extract_pdf_metadata(file_path)
        metadata["is_scanned"] = is_scanned_pdf(file_path)

        # Route to appropriate LLM using LangChainRouter
        update_status(file_id, "Processing")
        await asyncio.sleep(1)

        router = LangChainRouter()
        helpers = {
            "contains_financial_tables": contains_financial_tables,
            "is_legal_document": is_legal_document
        }
        result, processing_type = router.route(file_path, metadata, helpers)

        # Handle None result
        if result is None:
            update_status(file_id, "Failed: No result received from processing")
            await asyncio.sleep(1)
            raise HTTPException(
                status_code=500,
                detail="No result received from processing"
            )

        # Ensure data is a string
        if result.get("data") is None:
            result["data"] = "No data extracted from document"

        if not result.get("success", False):
            update_status(file_id, "Failed: Processing error")
            await asyncio.sleep(1)
            error_message = result.get("error", "Unknown error")
            data_message = result.get("data", "No additional information")
            raise HTTPException(
                status_code=500,
                detail=f"Processing failed: {error_message}. {data_message}"
            )

        update_status(file_id, "Extracted")
        await asyncio.sleep(1)
        update_status(file_id, "Completed")
        await asyncio.sleep(1)

        return {
            "message": "File uploaded and processed successfully",
            "file_id": file_id,
            "file_path": file_path,
            "metadata": metadata,
            "processing_type": processing_type,
            "model": result.get("model", "Unknown"),
            "results": str(result.get("data", ""))
        }

    except Exception as e:
        update_status(file_id, f"Failed: {str(e)}")
        await asyncio.sleep(1)
        raise HTTPException(status_code=500, detail=str(e))
