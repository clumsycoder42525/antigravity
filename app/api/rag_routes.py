from fastapi import APIRouter
from pydantic import BaseModel
from ..services.rag_service import RAGService

router = APIRouter()
rag_service = RAGService()

class RAGRequest(BaseModel):
    question: str


@router.post("/rag")
def rag_endpoint(request: RAGRequest):
    """
    RAG Mode: Answer STRICTLY from uploaded documents.
    
    STRICT ISOLATION:
    - Uses ONLY ChromaDB + HuggingFace embeddings
    - NO Wikipedia, NO DuckDuckGo, NO Groq
    - Returns empty sources array (document-based only)
    """
    answer = rag_service.run_rag(request.question)
    
    return {
        "question": request.question,
        "answer": answer,
        "sources": [],  # RAG mode never uses external sources
        "mode": "rag"
    }
