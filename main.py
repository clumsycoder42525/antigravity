# ----------------------------
# ChromaDB SQLite Fix (Windows)
# ----------------------------
import sys
try:
    __import__('pysqlite3')
    sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
except ImportError:
    pass

from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging

# Routers
from app.api.routes import router as core_router
from app.api.upload_routes import router as upload_router
from app.api.rag_routes import router as rag_router
from app.routes.qa_pipeline import router as qa_router
from app.api.evaluation_routes import router as evaluation_router
from app.api.memory_routes import router as memory_router
from app.services.ticket_agent_service import router as booking_router

# ----------------------------
# Logging Setup
# ----------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("humind")


# ----------------------------
# Lifespan Events
# ----------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 HUMIND System Starting...")
    yield
    logger.info("🛑 HUMIND System Shutting Down...")


# ----------------------------
# FastAPI App
# ----------------------------
app = FastAPI(
    title="HUMIND Enterprise AI System",
    description="Multi-Agent System + HuggingFace RAG + ChromaDB",
    version="2.1.0",
    lifespan=lifespan
)


# ----------------------------
# Include Routers (FIXED)
# ----------------------------

# Core Multi-Agent System
app.include_router(core_router, prefix="/agent")

# File Upload for RAG
app.include_router(upload_router, prefix="/upload")

# RAG Query Endpoint
app.include_router(rag_router, prefix="/rag")

# Standalone QA Pipeline
app.include_router(qa_router, prefix="/qa")

# Structured Answer Evaluation
app.include_router(evaluation_router, prefix="/evaluation")

# Memory-Enabled Chat
app.include_router(memory_router, prefix="/chat")

# 🎟 Ticket Booking Agent
app.include_router(booking_router, prefix="/booking", tags=["Booking Agent"])

# ----------------------------
# Health Check
# ----------------------------
@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "system": "HuggingFace + ChromaDB RAG + Groq Agents"
    }


# ----------------------------
# Run Server
# ----------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)