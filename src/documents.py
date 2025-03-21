from typing import List, Dict, Any
from dataclasses import dataclass
import logging
from config import CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """Doküman parçalarını temsil eden sınıf"""
    content: str
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TokenTextSplitter:
    """Metni küçük parçalara bölen sınıf"""

    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        logger.info(f"TokenTextSplitter initialized with chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")

    def split_text(self, text: str) -> List[str]:
        """Metni yaklaşık olarak belirtilen boyutta parçalara böler"""
        if not text:
            return []

        words = text.split()
        chunks = []

        if len(words) <= self.chunk_size:
            return [text]

        i = 0
        while i < len(words):
            chunk = ' '.join(words[i:i + self.chunk_size])
            chunks.append(chunk)
            i += self.chunk_size - self.chunk_overlap

        logger.debug(f"Split text into {len(chunks)} chunks")
        return chunks

    def apply(self, documents: List[Document]) -> List[Document]:
        """Doküman listesini alıp içeriklerini parçalayarak yeni doküman listesi döndürür"""
        result = []
        for doc in documents:
            text_chunks = self.split_text(doc.content)
            for i, chunk in enumerate(text_chunks):
                result.append(Document(
                    content=chunk,
                    metadata={
                        **doc.metadata.copy(),
                        "chunk": i,
                        "total_chunks": len(text_chunks)
                    }
                ))

        logger.info(f"Applied text splitting to {len(documents)} documents, resulting in {len(result)} chunks")
        return result