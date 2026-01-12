from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import os

def setup_rag_chain(products_df=None):
    """
    Configura o pipeline RAG carregando o índice FAISS do disco.
    """
    # 1. Configurar Embeddings (Mesmo modelo usado no build_data.py)
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    path = "processed_data/faiss_index"
    
    # 2. Carregar Vector Store (FAISS)
    if os.path.exists(path):
        try:
            vectorstore = FAISS.load_local(
                folder_path=path, 
                embeddings=embeddings, 
                allow_dangerous_deserialization=True # Necessário para carregar arquivos locais confiáveis
            )
        except Exception as e:
            print(f"Erro ao carregar FAISS: {e}")
            return None
    else:
        print(f"Caminho não encontrado: {path}")
        return None

    # 3. Configurar LLM (Llama 3) com System Prompt Otimizado
    # O parâmetro 'system' força o modelo a agir como vendedor, não como chatbot genérico
    llm = ChatOllama(
        model="llama3", 
        temperature=0.1, # Baixa temperatura para ser mais factual
    )
    
    # 4. Prompt Personalizado (Opcional, mas recomendado para qualidade)
    template = """
    Você é um assistente de vendas experiente e direto.
    Use as seguintes informações de produtos para responder à pergunta do usuário.
    Se não souber a resposta, diga apenas que não encontrou o produto.
    Não invente informações. Seja breve e cite o preço se disponível.

    Contexto: {context}

    Pergunta: {question}

    Resposta:
    """
    QA_CHAIN_PROMPT = PromptTemplate.from_template(template)

    # 5. Criar Chain de Recuperação
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3}) # Traz os 3 produtos mais similares
    
    rag_chain = RetrievalQA.from_chain_type(
        llm=llm, 
        chain_type="stuff", 
        retriever=retriever,
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
    )
    
    return rag_chain