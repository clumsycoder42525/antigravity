import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

try:
    print("Initializing RAGService...")
    from app.services.rag_service import RAGService
    service = RAGService()
    print("RAGService initialized successfully.")
except Exception as e:
    print(f"Failed to initialize RAGService: {e}")
    import traceback
    traceback.print_exc()
