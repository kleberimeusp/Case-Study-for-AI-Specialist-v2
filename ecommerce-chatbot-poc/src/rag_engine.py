# src/rag_engine.py
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langchain.chains import RetrievalQA
import os

def setup_rag_chain(products_df=None): # products_df agora é opcional pois carregamos do disco
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    path = "processed_data/faiss_index"
    
    if os.path.exists(path):
        # Carrega índice pronto (Rápido)
        vectorstore = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
    else:
        # Fallback (Lento)
        return None

    llm = ChatOllama(model="llama3", temperature=0)
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    rag_chain = RetrievalQA.from_chain_type(
        llm=llm, 
        chain_type="stuff", 
        retriever=retriever
    )
    
    return rag_chain