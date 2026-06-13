import os
import tempfile
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.retrievers import BM25Retriever
from langchain_experimental.text_splitter import SemanticChunker

import langsmith
#from langchain_core.retrievers import EnsembleRetriever

load_dotenv()
#Recursive chunking used here 
def load_and_chunk(pdf_file):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_file.read())
        tmp_path = tmp.name

    loader = PyPDFLoader(tmp_path)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    chunks = splitter.split_documents(documents)
    return chunks
    #used semantic chunking here
  

#def load_and_chunk(pdf_file):
    #with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        #tmp.write(pdf_file.read())
        #tmp_path = tmp.name

    #loader = PyPDFLoader(tmp_path)
    #documents = loader.load()

    #embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    #splitter = SemanticChunker(
        #embeddings,
        #breakpoint_threshold_type="percentile",
        #breakpoint_threshold_amount=95
    #)
    #chunks = splitter.split_documents(documents)
    #return chunks

def build_vectorstore(chunks):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma.from_documents(chunks, embeddings)
    bm25_retriever = BM25Retriever.from_documents(chunks)
    bm25_retriever.k = 8
    return vectorstore, bm25_retriever

def get_answer(vectorstore, bm25_retriever, question):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    vector_retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 8, "fetch_k": 50}
    )

    # Manual hybrid search - no EnsembleRetriever needed
    def hybrid_retrieve(question):
        bm25_docs = bm25_retriever.invoke(question)
        vector_docs = vector_retriever.invoke(question)
        
        # Combine and deduplicate
        seen = set()
        combined = []
        for doc in bm25_docs + vector_docs:
            if doc.page_content not in seen:
                seen.add(doc.page_content)
                combined.append(doc)
        return combined

    prompt = PromptTemplate.from_template("""
You are a legal contract assistant. Answer the question based only on the context below.
- Give a clear, moderate length answer — not too short, not too long
- Include specific details like numbers, timeframes and conditions
- At the end, mention which section or page the answer came from

Context: {context}
Question: {question}
Answer:
""")
    def format_docs(docs):
        return "\n\n".join(
            f"[Page {doc.metadata.get('page', '?')}]: {doc.page_content}"
            for doc in docs
        )

    docs = hybrid_retrieve(question)
    context = format_docs(docs)
    
    chain = prompt | llm | StrOutputParser()
    
    return chain.invoke({"context": context, "question": question})

