import sys
import os

# Add rag_system to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from app.rag_agent import RAGAgent

def ingest():
    print("Starting PDF ingestion into RAG system...")
    try:
        agent = RAGAgent()
        agent.ingest_documents()
        print("Ingestion completed successfully.")
    except Exception as e:
        print(f"Ingestion failed: {e}")

if __name__ == "__main__":
    ingest()
