from fastapi import APIRouter, UploadFile, File, HTTPException
from ..schemas.rag_schemas import UploadResponse
from rag_system.app.rag_agent import RAGAgent
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
rag_agent = RAGAgent()

@router.post("/upload", response_model=UploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
    
    try:
        content = await file.read()
        num_chunks = rag_agent.ingest_pdf(content, file.filename)
        return UploadResponse(filename=file.filename, chunks=num_chunks)
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
