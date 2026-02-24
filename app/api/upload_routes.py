from fastapi import APIRouter, UploadFile, File
from ..services.rag_service import RAGService

router = APIRouter()
rag_service = RAGService()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    content = await file.read()
    rag_service.ingest_uploaded_file(file.filename, content)
    return {"message": "File uploaded successfully"}
