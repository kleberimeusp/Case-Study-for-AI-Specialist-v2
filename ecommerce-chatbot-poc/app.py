import streamlit as st
from src.data_loader import load_optimized_data
from src.rag_engine import setup_rag_chain
from src.agent_engine import setup_pandas_agent
from src.router import route_query

# --- Configuração da Página ---
st.set_page_config(page_title="E-commerce AI (Fast)", page_icon="⚡", layout="wide")

st.title("⚡ Assistente Olist (Otimizado)")
st.markdown("IA Híbrida rodando localmente com Llama 3 e dados pré-processados (Parquet/FAISS).")

# --- Sidebar ---
with st.sidebar:
    st.header("📂 Dados")
    
    # Carrega dados otimizados (Parquet)
    products_df, orders_df = load_optimized_data()
    
    if products_df is None or orders_df is None:
        st.warning("⚠️ Dados não encontrados.")
        st.info("Execute 'python build_data.py' no terminal para gerar os arquivos otimizados.")
        st.stop()
    
    st.success(f"Carregado: {len(products_df)} produtos | {len(orders_df)} pedidos")

# --- Inicialização dos Modelos ---
if "rag_chain" not in st.session_state:
    with st.spinner("Carregando cérebro da IA..."):
        try:
            # RAG carrega índice do disco (Rápido)
            st.session_state.rag_chain = setup_rag_chain()
            
            # Agente recebe DataFrame limpo
            st.session_state.pandas_agent = setup_pandas_agent(orders_df)
            
            if st.session_state.rag_chain is None:
                st.error("Índice FAISS não encontrado. Rode o build_data.py!")
                st.stop()
                
            st.success("Sistema Online! 🚀")
        except Exception as e:
            st.error(f"Erro crítico: {e}")
            st.stop()

# --- Chat ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Olá! O sistema está otimizado. Pergunte sobre produtos ou pedidos."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Digite sua pergunta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Roteamento
    intent = route_query(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner(f"Processando ({intent})..."):
            try:
                response_text = ""
                
                if intent == "products":
                    # RAG
                    result = st.session_state.rag_chain.invoke({"query": prompt})
                    response_text = result['result']
                    
                elif intent == "orders":
                    # Agente
                    response_text = st.session_state.pandas_agent.run(prompt)
                
                st.write(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                
            except Exception as e:
                st.error(f"Erro na execução: {e}")
                st.info("Dica: Se o erro persistir, tente uma pergunta mais simples.")