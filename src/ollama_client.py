import requests
import json
import logging
from typing import List
from config import OLLAMA_API_BASE, MODEL_NAME

logger = logging.getLogger(__name__)


class OllamaClient:
    """Ollama API ile iletişim kuran istemci sınıfı"""

    def __init__(self, base_url: str = OLLAMA_API_BASE, model: str = MODEL_NAME):
        self.base_url = base_url
        self.model = model
        self.generate_url = f"{base_url}/api/generate"
        self.embeddings_url = f"{base_url}/api/embeddings"
        logger.info(f"OllamaClient initialized with base_url={base_url}, model={model}")

    def generate(self, prompt: str, temperature: float = 0.4) -> str:
        """Verilen prompt'a göre metin üretir"""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature
        }

        try:
            response = requests.post(self.generate_url, json=payload)
            response.raise_for_status()

            text = ""
            for line in response.text.splitlines():
                if not line.strip():
                    continue

                data = json.loads(line)
                if "response" in data:
                    text += data["response"]

            logger.debug(f"Generated text of length {len(text)}")
            return text
        except Exception as e:
            logger.error(f"Generate error: {str(e)}")
            return f"Error generating text: {str(e)}"

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Metinler listesi için embeddings vektörleri oluşturur"""
        embeddings = []

        for i, text in enumerate(texts):
            payload = {
                "model": self.model,
                "prompt": text
            }

            try:
                response = requests.post(self.embeddings_url, json=payload)
                response.raise_for_status()
                data = response.json()
                embeddings.append(data["embedding"])
                logger.debug(f"Generated embedding for text {i + 1}/{len(texts)}")
            except Exception as e:
                logger.error(f"Embedding error for text {i + 1}/{len(texts)}: {str(e)}")
                embeddings.append([0.0] * 1024)

        logger.info(f"Generated {len(embeddings)} embeddings")
        return embeddings