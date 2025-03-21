import streamlit as st
import requests

st.set_page_config(page_title="PDF Chat Assistant", layout="centered")
BACKEND_URL = "http://localhost:5050"

st.sidebar.title("Select Function:")
page = st.sidebar.radio("", ["LLM Chat", "PDF Upload & Query"])

st.title("PDF Chat Assistant")
with st.expander("About the App"):
    st.write("This application allows you to perform RAG (Retrieval-Augmented Generation) on PDF documents.")
    st.write("You can upload PDFs and ask questions related to their content.")

if page == "LLM Chat":
    st.header("💬 LLM Chat")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question:"):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            response = requests.get(f"{BACKEND_URL}/chat", params={"prompt": prompt})
            if response.status_code == 200:
                content = response.json()["response"]
                st.markdown(content)
                st.session_state.messages.append({"role": "assistant", "content": content})

elif page == "PDF Upload & Query":
    st.header("📄 PDF Upload and Query")

    uploaded_file = st.file_uploader("📎 Upload PDF:", type=["pdf"])

    if uploaded_file:
        if st.button("Submit PDF"):
            with st.status("Uploading PDF...") as status:
                files = {'file': uploaded_file.getvalue()}
                st.write("Processing PDF...")
                res = requests.post(f"{BACKEND_URL}/upload", files=files)
                if res.status_code == 200:
                    status.update(label="PDF successfully uploaded!", state="complete", expanded=False)
                else:
                    status.update(label="An error occurred!", state="error", expanded=True)

    query = st.text_input("Search within the PDF content:", value="Does this PDF mention artificial intelligence?")

    if st.button("Search", key="search"):
        with st.spinner("Searching document..."):
            response = requests.get(f"{BACKEND_URL}/search", params={"prompt": query})
            if response.status_code == 200:
                data = response.json()
                highlighted = data["response"].replace(query, f"**:orange[{query}]**")
                st.success("Contextual answer based on the document:")
                st.markdown(highlighted)

                st.metric(label="Response Length", value=f"{len(data['response'])} characters")

            else:
                st.error("An error occurred during the query.")