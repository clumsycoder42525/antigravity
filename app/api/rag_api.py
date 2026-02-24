from fastapi import APIRouter, HTTPException
from ..schemas.rag_schemas import RAGRequest, RAGResponse
from rag_system.app.rag_agent import RAGAgent
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
rag_agent = RAGAgent()

@router.post("/rag", response_model=RAGResponse)
async def rag_query(request: RAGRequest):
    try:
        answer = rag_agent.ask(request.query)
        return RAGResponse(answer=answer)
    except Exception as e:
        logger.error(f"RAG query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
