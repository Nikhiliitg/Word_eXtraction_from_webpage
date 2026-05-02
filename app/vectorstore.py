import os
import faiss
import numpy as np
import json
from sentence_transformers import SentenceTransformer

class VectorStore:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.index_path = os.path.join(data_dir, "index.faiss")
        self.meta_path = os.path.join(data_dir, "metadata.json")
        
        os.makedirs(self.data_dir, exist_ok=True)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        
        # Load Index
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
        else:
            self.index = faiss.IndexFlatL2(384)

        # Load Metadata
        if os.path.exists(self.meta_path):
            with open(self.meta_path, 'r') as f:
                self.metadata = json.load(f)
        else:
            self.metadata = []

    def save_keywords(self, keywords, source_url):
        # 1. Create a single 'Topic Vector' for the whole page
        page_profile = " ".join(keywords)
        vector = self.model.encode([page_profile]).astype("float32")
        
        # 2. Add to FAISS
        self.index.add(vector)
        
        # 3. Add 1 entry to metadata for this page
        self.metadata.append({
            "url": source_url,
            "keywords": keywords
        })

        # 4. Save both
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, 'w') as f:
            json.dump(self.metadata, f)
            
        print(f"✅ Indexed {source_url}. Brain now has {len(self.metadata)} pages.")

    def search_similar(self, query, top_k=3):
        if not self.metadata:
            print("❌ Search failed: Metadata is empty.")
            return []

        # Encode the search query
        query_vector = self.model.encode([query]).astype("float32")
        
        # Search
        D, I = self.index.search(query_vector, top_k)
        
        results = []
        for i in I[0]:
            if i != -1 and i < len(self.metadata):
                results.append(self.metadata[i])
        
        print(f"🔍 Search for '{query}' found {len(results)} matches.")
        return results