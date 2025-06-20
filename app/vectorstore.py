# app/vectorstore.py

import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class VectorStore:
    def __init__(self, index_path="data/index.faiss"):
        self.index_path = index_path
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.dim = self.model.get_sentence_embedding_dimension()

        # FAISS index setup
        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
            print("🔁 Loaded existing FAISS index")
        else:
            self.index = faiss.IndexFlatL2(self.dim)
            print("📦 Created new FAISS index")

        # Metadata store (in-memory; in prod you'd use a DB)
        self.metadata = []

    def save_keywords(self, keywords, source_url):
        vectors = self.model.encode(keywords)
        self.index.add(np.array(vectors).astype("float32"))

        # Add metadata info
        for kw in keywords:
            self.metadata.append({"keyword": kw, "url": source_url})

        # Save FAISS index to disk
        faiss.write_index(self.index, self.index_path)
        print(f"✅ Saved {len(keywords)} keywords from {source_url} into vector DB")

    def search_similar(self, query, top_k=5):
        query_vector = self.model.encode([query]).astype("float32")
        D, I = self.index.search(query_vector, top_k)

        results = []
        for i in I[0]:
            if i < len(self.metadata):
                results.append(self.metadata[i])

        return results
