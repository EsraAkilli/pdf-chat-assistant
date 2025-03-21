from flask import Flask, request, jsonify
import logging
import os
from src.pdf_reader import PDFReader
from src.documents import TokenTextSplitter
from src.vector_store import SimpleVectorStore
from src.ollama_client import OllamaClient
from src.chat_service import ChatService
from config import PDF_PATH

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

ollama_client = OllamaClient()
vector_store = SimpleVectorStore(ollama_client)
chat_service = ChatService(ollama_client, vector_store)

def init_pdf_document(pdf_path):
    """PDF dosyasını okur ve vector store'a ekler"""
    if not os.path.exists(pdf_path):
        logger.error(f"PDF dosyası bulunamadı: {pdf_path}")
        return

    pdf_reader = PDFReader(pdf_path)
    documents = pdf_reader.get()

    text_splitter = TokenTextSplitter()
    chunked_documents = text_splitter.apply(documents)

    vector_store.add(chunked_documents)
    logger.info(f"PDF dokümanı başarıyla işlendi: {pdf_path}")

@app.route('/chat', methods=['GET'])
def chat():
    prompt = request.args.get('prompt', 'Merhaba')
    response = chat_service.generate_message(prompt)
    return jsonify({"response": response})

@app.route('/search', methods=['GET'])
def search():
    prompt = request.args.get('prompt', 'Dökümanı özetle')
    response = chat_service.search_in_context(prompt)
    return jsonify({"response": response})


if __name__ == '__main__':
    init_pdf_document(PDF_PATH)

    app.run(host='0.0.0.0', port=5050, debug=True)