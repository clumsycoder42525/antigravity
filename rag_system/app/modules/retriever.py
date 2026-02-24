class Retriever:
    def __init__(self, vector_store, embedding_provider):
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider

    def retrieve(self, query, n_results=3):
        query_embedding = self.embedding_provider.generate_embedding(query)
        results = self.vector_store.query(query_embedding, n_results=n_results)
        
        retrieved_docs = []
        # Flatten ChromaDB results
        docs = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        
        for doc, meta in zip(docs, metadatas):
            retrieved_docs.append({
                "content": doc,
                "metadata": meta
            })
        return retrieved_docs
