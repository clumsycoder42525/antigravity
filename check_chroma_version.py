import chromadb
print(f"ChromaDB version: {chromadb.__version__}")
try:
    from chromadb.config import Settings as ChromaSettings
    print("chromadb.config.Settings import successful.")
except ImportError as e:
    print(f"ImportError: {e}")
except AttributeError as e:
    # This is likely the error
    print(f"AttributeError: {e}")
except Exception as e:
    print(f"Error: {e}")
