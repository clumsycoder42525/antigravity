import sys
print(f"Python version: {sys.version}")

try:
    print("Importing chromadb...")
    import chromadb
    print("chromadb imported.")
except ImportError as e:
    print(f"Failed to import chromadb: {e}")
except Exception as e:
    print(f"Error importing chromadb: {e}")

try:
    print("Importing langchain...")
    import langchain
    print("langchain imported.")
except ImportError as e:
    print(f"Failed to import langchain: {e}")

try:
    print("Importing sentence_transformers...")
    from sentence_transformers import SentenceTransformer
    print("sentence_transformers imported.")
except ImportError as e:
    print(f"Failed to import sentence_transformers: {e}")

try:
    print("Importing transformers...")
    from transformers import pipeline
    print("transformers imported.")
except ImportError as e:
    print(f"Failed to import transformers: {e}")
