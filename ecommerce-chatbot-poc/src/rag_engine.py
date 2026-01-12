from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langchain.chains import RetrievalQA

def setup_rag_chain(products_df):
    """
    Cria a cadeia RAG usando Ollama (Local).
    Não precisa de API Key!
    """
    # 1. Embeddings Locais (nomic-embed-text é ótimo para retrieval)
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    # 2. Preparar textos
    text_data = products_df.apply(
        lambda x: f"Produto: {x['nome']}. Descrição: {x['descrição']}. Preço: R$ {x['preço']:.2f}. Estoque: {x['estoque']}", 
        axis=1
    ).tolist()

    # 3. Criar Vector Store
    # Pode demorar um pouco na primeira vez para vetorizar localmente
    vectorstore = FAISS.from_texts(text_data, embeddings)
    
    # 4. Configurar LLM Local
    llm = ChatOllama(
        model="llama3", 
        temperature=0
    )
    
    # 5. Criar Chain
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    rag_chain = RetrievalQA.from_chain_type(
        llm=llm, 
        chain_type="stuff", 
        retriever=retriever
    )
    
    return rag_chain