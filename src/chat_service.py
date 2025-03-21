import logging
from src.ollama_client import OllamaClient
from src.vector_store import SimpleVectorStore

logger = logging.getLogger(__name__)

class ChatService:
    """Sohbet işlevselliğini sağlayan servis"""

    def __init__(self, client: OllamaClient, vector_store: SimpleVectorStore):
        self.client = client
        self.vector_store = vector_store
        logger.info("ChatService initialized")

    def generate_message(self, prompt: str) -> str:
        """Genel bir soruya cevap üretir"""
        logger.info(f"Generating general response for prompt: {prompt[:50]}...")
        system_prompt = "You are a helpful assistant. Provide clear, concise answers strictly based on the user's input. Do not add additional roles, characters, or simulate dialogues."
        full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"
        response = self.client.generate(full_prompt)
        logger.info(f"Generated response of length {len(response)}")
        return response

    def search_in_context(self, query: str) -> str:
        """Doküman bağlamında sorguya cevap verir"""
        logger.info(f"Searching in context for query: {query[:50]}...")
        similar_documents = self.vector_store.similarity_search(query)

        if not similar_documents:
            logger.warning("No similar documents found for the query")
            return "Sorry, I couldn't find relevant information in the provided documents."

        information = "\n\n".join([doc.content for doc in similar_documents])

        system_prompt = (
            "You are a helpful assistant strictly using ONLY the following document context to answer the user. "
            "Do not invent additional details. If you don't know the answer based on the given information, reply with 'Unknown'.\n\n"
            f"Context:\n{information}"
        )

        full_prompt = f"{system_prompt}\n\nUser question: {query}\n\nAssistant response:"
        response = self.client.generate(full_prompt)
        logger.info(f"Generated context-based response of length {len(response)}")
        return response