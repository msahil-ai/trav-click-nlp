from typing import List, Dict, Any

class SoftMatcher:
    def __init__(
        self,
        vector_store,
        embed_model,
        top_k: int = 5
    ):
        """
        vector_store : FAISS / Chroma / Qdrant wrapper
        embed_model  : embedding model with encode()
        top_k        : number of semantic matches
        """
        self.vector_store = vector_store
        self.embed_model = embed_model
        self.top_k = top_k

    # -----------------------------
    # 1️⃣ Semantic Matching
    # -----------------------------
    def semantic_search(self, query: str):
        """
        Perform semantic (soft) matching using embeddings
        """
        query_embedding = self.embed_model.encode(query).tolist()

        results = self.vector_store.query(
            query_embeddings=[query_embedding],
            n_results=self.top_k
        )

        return results
    

    # -----------------------------
    # 2️⃣ Rule-based Re-ranking
    # -----------------------------
    def structured_rerank(
        self,
        results: dict,
        filters: Dict[str, Any]
    ) -> dict:
        """
        Apply rule-based filtering on top of semantic search.
        """
        # Safely unpack ChromaDB's nested lists
        metadatas = results.get("metadatas", [[]])[0]
        documents = results.get("documents", [[]])[0]
        ids = results.get("ids", [[]])[0]
        
        # Safely handle distances if they exist
        distances = results.get("distances", [[]])[0] if "distances" in results and results["distances"] else [0.0] * len(ids)

        filtered_metadatas = []
        filtered_documents = []
        filtered_ids = []
        filtered_distances = []

        for i, meta in enumerate(metadatas):
            
            # 1. City Filter: Exact match
            if "city" in filters and filters["city"]:
                requested_city = str(filters["city"]).strip().lower()
                package_city = str(meta.get("city", "")).strip().lower()
                if requested_city != package_city:
                    continue  # Drop it if it's the wrong city
            
            # 2. Duration Filter: Package must be AT LEAST the requested duration
            if "min_duration" in filters and filters["min_duration"]:
                if meta.get("duration_days", 0) < filters["min_duration"]:
                    continue  # Drop it if it has fewer days than requested
            
            # 3. People Filter: Exact match OR a better deal (larger capacity)
            if "min_people" in filters and filters["min_people"]:
                if meta.get("people", 0) < filters["min_people"]:
                    continue  # Drop it if it can't fit the requested group size

            # If it survives the filters, it is a valid package!
            filtered_metadatas.append(meta)
            filtered_documents.append(documents[i])
            filtered_ids.append(ids[i])
            filtered_distances.append(distances[i])

        # Repackage the filtered results back into the Chroma dictionary format
        return {
            "metadatas": [filtered_metadatas],
            "documents": [filtered_documents],
            "ids": [filtered_ids],
            "distances": [filtered_distances]
        }

    # -----------------------------
    # 3️⃣ Combined Pipeline
    # -----------------------------
    def retrieve(
        self,
        query: str,
        filters: Dict[str, Any] = None
    ) -> dict:
        """
        Full pipeline:
        Query → Semantic Search → Rule-based Re-ranking
        """
        semantic_results = self.semantic_search(query)

        if filters:
            final_results = self.structured_rerank(
                semantic_results, filters
            )
        else:
            final_results = semantic_results

        return final_results