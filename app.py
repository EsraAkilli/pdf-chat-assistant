from flask import Flask, request, jsonify
import logging
import tempfile

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

def process_pdf_and_add_to_vectorstore(pdf_path):
    """PDF dosyasını okur ve vector store'a ekler"""
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

@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "PDF dosyası gönderilmedi"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Dosya seçilmedi"}), 400

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        file.save(temp_file.name)
        logger.info(f"Yüklenen PDF geçici olarak kaydedildi: {temp_file.name}")

        process_pdf_and_add_to_vectorstore(temp_file.name)

    return jsonify({"message": "PDF başarıyla işlendi ve vektör deposuna eklendi."}), 200

if __name__ == '__main__':
    # Başlangıçta default PDF'i yükle
    process_pdf_and_add_to_vectorstore(PDF_PATH)

    app.run(host='0.0.0.0', port=5050, debug=True)