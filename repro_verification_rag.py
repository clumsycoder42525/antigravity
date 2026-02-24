try:
    from app.config.settings import settings
    print("Imports: config... OK")
    from app.rag.chunker import Chunker
    print("Imports: chunker... OK")
    from app.api.upload_routes import router as upload_router
    print("Imports: upload_routes... OK")
    from app.api.rag_routes import router as rag_router
    print("Imports: rag_routes... OK")
    from app.services.vector_store_service import VectorStoreService
    print("Imports: vector_store_service... OK")
    # We avoid instantiating LLM/Embedder to prevent download
    print("Verification script finished successfully (Static Imports).")
except ImportError as e:
    print(f"Import failed: {e}")
    exit(1)
except Exception as e:
    print(f"Error: {e}")
    exit(1)
