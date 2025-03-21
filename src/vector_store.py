import numpy as np
from typing import List
import logging
from sklearn.metrics.pairwise import cosine_similarity
from .documents import Document
from .ollama_client import OllamaClient
from config import TOP_K_RESULTS

logger = logging.getLogger(__name__)


class SimpleVectorStore:
    """Dokümanları vektör olarak saklayan basit bir vektör deposu"""

    def __init__(self, client: OllamaClient):
        self.client = client
        self.documents: List[Document] = []
        self.embeddings: List[List[float]] = []
        logger.info("SimpleVectorStore initialized")

    def add(self, documents: List[Document]) -> None:
        """Dokümanları ve embeddings'lerini ekler"""
        if not documents:
            logger.warning("No documents to add to vector store")
            return

        texts = [doc.content for doc in documents]
        logger.info(f"Generating embeddings for {len(texts)} documents")
        new_embeddings = self.client.get_embeddings(texts)

        self.documents.extend(documents)
        self.embeddings.extend(new_embeddings)
        logger.info(f"Added {len(documents)} documents to vector store. Total: {len(self.documents)}")

    def similarity_search(self, query: str, k: int = TOP_K_RESULTS) -> List[Document]:
        """Sorguya en benzer k adet dokümanı döndürür"""
        if not self.embeddings:
            logger.warning("No documents in vector store for similarity search")
            return []

        logger.info(f"Performing similarity search for query: {query[:50]}...")
        query_embedding = self.client.get_embeddings([query])[0]

        query_embedding_np = np.array(query_embedding).reshape(1, -1)
        embeddings_np = np.array(self.embeddings)

        similarities = cosine_similarity(query_embedding_np, embeddings_np)[0]

        top_indices = np.argsort(similarities)[-k:][::-1]

        top_similarities = [similarities[i] for i in top_indices]
        logger.info(f"Top {k} similarity scores: {top_similarities}")

        return [self.documents[i] for i in top_indices]