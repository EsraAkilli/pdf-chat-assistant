import fitz
from typing import List
import logging
import os
from .documents import Document

logger = logging.getLogger(__name__)


class PDFReader:
    """PDF dosyalarını okuyan sınıf"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        logger.info(f"PDFReader initialized with file_path={file_path}")

    def get(self) -> List[Document]:
        """PDF dosyasından metin içeriğini okur ve Document listesi olarak döndürür"""
        if not os.path.exists(self.file_path):
            logger.error(f"PDF file not found: {self.file_path}")
            return []

        try:
            doc = fitz.open(self.file_path)
            all_text = ""

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                all_text += text

            file_name = os.path.basename(self.file_path)
            logger.info(f"Successfully read PDF: {file_name}, {len(doc)} pages")

            return [Document(
                content=all_text,
                metadata={
                    "source": self.file_path,
                    "type": "pdf",
                    "title": file_name,
                    "pages": len(doc)
                }
            )]
        except Exception as e:
            logger.error(f"Error reading PDF: {str(e)}")
            return []