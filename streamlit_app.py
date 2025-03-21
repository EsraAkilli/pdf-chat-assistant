import streamlit as st
import requests

st.set_page_config(page_title="PDF Chat Assistant", layout="centered")
st.title("PDF Chat Assistant")

BACKEND_URL = "http://localhost:5050"

tab1, tab2 = st.tabs(["Genel Chat", "PDF Yükle & Sorgula"])

with tab1:
    st.subheader("💬 LLM Chat")
    prompt = st.text_input("Bir soru sor:", value="Merhaba")

    if st.button("Cevapla", key="chat"):
        with st.spinner("Yanıt üretiliyor..."):
            response = requests.get(f"{BACKEND_URL}/chat", params={"prompt": prompt})
            if response.status_code == 200:
                data = response.json()
                st.success("Asistan cevabı:")
                st.markdown(data["response"])
            else:
                st.error(f"Hata: {response.status_code}")

with tab2:
    st.subheader("📄 PDF Yükle ve Üzerinden Sorgula (RAG Search)")

    uploaded_file = st.file_uploader("PDF Yükleyin:", type=["pdf"])

    if uploaded_file:
        st.info("PDF yüklendi! PDF'i backend'e göndermek için 'PDF'i Gönder' butonuna tıklayın.")

        if st.button("PDF'i Gönder"):
            files = {'file': uploaded_file.getvalue()}
            res = requests.post(f"{BACKEND_URL}/upload", files=files)
            if res.status_code == 200:
                st.success("PDF başarıyla backend'e yüklendi ve işlendi!")
            else:
                st.error("PDF yükleme sırasında bir hata oluştu.")

    query = st.text_input("PDF içeriğinde arama yap:", value="Bu PDF'de yapay zeka hakkında neler var?")

    if st.button("Ara", key="search"):
        with st.spinner("Belge taranıyor..."):
            response = requests.get(f"{BACKEND_URL}/search", params={"prompt": query})
            if response.status_code == 200:
                data = response.json()
                highlighted = data["response"].replace(query, f"**:orange[{query}]**")
                st.success("Belgeye dayalı yanıt:")
                st.markdown(highlighted)
            else:
                st.error(f"Hata: {response.status_code}")