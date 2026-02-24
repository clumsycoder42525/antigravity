import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from app.services.rag_service import RAGService

try:
    print("Initializing RAGService...")
    service = RAGService()
    print("Running query...")
    answer = service.run_rag("What is the system purpose?")
    print(f"Answer: {answer}")
    print("RAG query successful.")
except Exception as e:
    print(f"Failed to run RAG query: {e}")
    import traceback
    traceback.print_exc()
