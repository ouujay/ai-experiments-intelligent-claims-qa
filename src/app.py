"""
Intelligent Claims QA Service
FastAPI microservice for extracting and querying medical claim documents
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any
import uuid
import asyncio

from .ocr_utils import load_and_ocr, preprocess_text
from .preparse import preparse_invoice_text, merge_preparse_into_llm
from .claims_llm import llm_normalize, answer_question

# Initialize FastAPI app
app = FastAPI(
    title="Intelligent Claims QA Service",
    description="Extract structured data from medical claim documents and answer questions",
    version="1.0.0"
)

# In-memory storage for extracted documents
DOCUMENT_STORE: Dict[str, Dict[str, Any]] = {}


class AskRequest(BaseModel):
    """Request model for /ask endpoint"""
    document_id: str
    question: str


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Intelligent Claims QA Service",
        "status": "running",
        "endpoints": ["/extract", "/ask"]
    }


@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    """
    Extract structured data from medical claim document

    Args:
        file: Image or PDF file containing medical claim sheet

    Returns:
        JSON with document_id and extracted data
    """
    try:
        # Validate file type
        allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp']
        file_extension = '.' + file.filename.split('.')[-1].lower()

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )

        # Read file bytes
        file_bytes = await file.read()

        if len(file_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")

        # Step 1: OCR extraction
        ocr_text = load_and_ocr(file_bytes, file.filename)
        cleaned_text = preprocess_text(ocr_text)

        if not cleaned_text:
            raise HTTPException(status_code=400, detail="No text could be extracted from the document")

        # Step 2: Regex pre-parsing
        preparsed_data = preparse_invoice_text(cleaned_text, file.filename)

        # Step 3: LLM normalization
        llm_data = await llm_normalize(cleaned_text, file.filename)

        # Step 4: Merge preparsed and LLM data
        final_data = merge_preparse_into_llm(preparsed_data, llm_data)

        # Generate unique document ID
        doc_id = str(uuid.uuid4())

        # Store in memory
        DOCUMENT_STORE[doc_id] = {
            "raw_text": cleaned_text,
            "data": final_data,
            "filename": file.filename
        }

        return {
            "document_id": doc_id,
            "data": final_data
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@app.post("/ask")
async def ask(request: AskRequest):
    """
    Answer questions about extracted claim data

    Args:
        request: Contains document_id and question

    Returns:
        JSON with answer
    """
    try:
        # Check if document exists
        if request.document_id not in DOCUMENT_STORE:
            raise HTTPException(status_code=404, detail="Document not found")

        # Retrieve stored document
        doc = DOCUMENT_STORE[request.document_id]
        claim_data = doc["data"]
        raw_text = doc["raw_text"]

        # Answer the question using LLM
        answer = await answer_question(request.question, claim_data, raw_text)

        return {
            "answer": answer
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error answering question: {str(e)}")


@app.get("/documents")
async def list_documents():
    """
    List all stored documents (for debugging)

    Returns:
        List of document IDs and filenames
    """
    return {
        "documents": [
            {"document_id": doc_id, "filename": doc["filename"]}
            for doc_id, doc in DOCUMENT_STORE.items()
        ]
    }


@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document from storage

    Args:
        document_id: ID of document to delete

    Returns:
        Success message
    """
    if document_id not in DOCUMENT_STORE:
        raise HTTPException(status_code=404, detail="Document not found")

    del DOCUMENT_STORE[document_id]

    return {"message": "Document deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
