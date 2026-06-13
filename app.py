import streamlit as st
from rag import load_and_chunk, build_vectorstore, get_answer

st.title("Legal Contract Q&A")
st.write("Upload a legal contract and ask questions about it.")

if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None
if "bm25_retriever" not in st.session_state:
    st.session_state.bm25_retriever = None

uploaded_file = st.file_uploader("Upload PDF", type="pdf")

if uploaded_file:
    if st.session_state.vectorstore is None:
        with st.spinner("Processing PDF..."):
            chunks = load_and_chunk(uploaded_file)
            vectorstore, bm25_retriever = build_vectorstore(chunks)
            st.session_state.vectorstore = vectorstore
            st.session_state.bm25_retriever = bm25_retriever
        st.success(f"Ready. {len(chunks)} chunks created.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    # Chat input at bottom
    question = st.chat_input("Ask a question about the contract")

    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("Searching..."):
                result = get_answer(
                    st.session_state.vectorstore,
                    st.session_state.bm25_retriever,
                    question
                )
            st.write(result)
            st.session_state.messages.append({"role": "assistant", "content": result})