import os
import sys
from pathlib import Path

from app.services.rag_service import RAGService
from app.config.settings import settings


DOCUMENTS_DIR = Path("./documents")
CHROMA_DIR = Path(settings.chroma_persist_dir)


def ensure_documents_folder():
    """
    Ensure documents folder exists.
    """
    if not DOCUMENTS_DIR.exists():
        DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
        print("📁 Created './documents' folder.")
        print("➡ Please add PDF files inside it and run again.")
        sys.exit(0)


def is_vector_store_empty():
    """
    Naive check: if Chroma persist directory doesn't exist or is empty.
    """
    if not CHROMA_DIR.exists():
        return True

    # Check if directory has files
    return not any(CHROMA_DIR.iterdir())


def main():
    print("🚀 Starting HUMIND RAG CLI")

    ensure_documents_folder()

    rag_service = RAGService()

    # Ingest only if DB is empty
    if is_vector_store_empty():
        print("📥 No existing vector store found. Ingesting documents...")
        rag_service.ingest_from_directory(str(DOCUMENTS_DIR))
        print("✅ Ingestion complete.")
    else:
        print("📦 Existing vector store found. Skipping ingestion.")

    # Interactive loop
    while True:
        try:
            query = input("\n💬 Ask a question (type 'exit' to quit): ").strip()

            if query.lower() in ["exit", "quit"]:
                print("👋 Exiting RAG CLI.")
                break

            if not query:
                continue

            response = rag_service.run_rag(query)

            print("\n💡 RESPONSE:")
            print(response)

        except KeyboardInterrupt:
            print("\n👋 Interrupted. Exiting safely.")
            break

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
