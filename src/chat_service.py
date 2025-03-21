import logging
from .ollama_client import OllamaClient
from .vector_store import SimpleVectorStore

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
        system_prompt = "Sen yardımcı bir asistansın."
        full_prompt = f"{system_prompt}\n\nKullanıcı: {prompt}\n\nAsistan:"
        response = self.client.generate(full_prompt)
        logger.info(f"Generated response of length {len(response)}")
        return response

    def generate_joke(self, topic: str) -> str:
        """Belirli bir konuda şaka üretir"""
        logger.info(f"Generating joke about topic: {topic}")
        prompt = f"Lütfen {topic} konusunda komik bir şaka yap."
        return self.generate_message(prompt)

    def search_in_context(self, query: str) -> str:
        """Doküman bağlamında sorguya cevap verir"""
        logger.info(f"Searching in context for query: {query[:50]}...")
        similar_documents = self.vector_store.similarity_search(query)

        if not similar_documents:
            logger.warning("No similar documents found for the query")
            return "Üzgünüm, bu soruya cevap verebilecek bilgi bulamadım."

        # Bulunan doküman içeriklerini birleştirme
        information = "\n\n".join([doc.content for doc in similar_documents])

        system_prompt = f"""Sen yardımcı bir asistansın.
Sadece aşağıdaki bilgileri kullanarak soruya cevap ver.
Başka bilgi kullanma. Eğer bilmiyorsan, basitçe "Bilinmiyor" diye cevap ver.

Bilgi:
{information}
"""

        full_prompt = f"{system_prompt}\n\nKullanıcı: {query}\n\nAsistan:"
        response = self.client.generate(full_prompt)
        logger.info(f"Generated context-based response of length {len(response)}")
        return response