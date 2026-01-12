import streamlit as st
from src.data_generator import generate_synthetic_data
from src.rag_engine import setup_rag_chain
from src.agent_engine import setup_pandas_agent
from src.router import route_query

# --- Configuração da Página ---
st.set_page_config(page_title="E-commerce AI (Local Ollama)", page_icon="🦙", layout="wide")

st.title("🦙 Assistente de E-commerce (Rodando Local)")
st.markdown("""
Esta POC utiliza **Ollama (Llama 3)** rodando na sua máquina.
Sem custos de API, privacidade total.
""")

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Dados")
    
    @st.cache_data
    def load_data():
        return generate_synthetic_data()

    products_df, orders_df = load_data()
    
    st.success("Dados gerados com sucesso!")
    with st.expander("Ver Tabelas"):
        st.write("Produtos:", products_df.head())
        st.write("Pedidos:", orders_df.head())

# --- Inicialização dos Modelos ---
if "rag_chain" not in st.session_state:
    with st.spinner("Inicializando Llama 3 e vetorizando dados locais..."):
        try:
            st.session_state.rag_chain = setup_rag_chain(products_df)
            st.session_state.pandas_agent = setup_pandas_agent(orders_df)
            st.success("Modelos Locais Carregados! 🚀")
        except Exception as e:
            st.error(f"Erro ao conectar com Ollama. Verifique se ele está rodando! Erro: {e}")
            st.stop()

# --- Chat ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Olá! Sou seu assistente local. Pergunte sobre produtos ou pedidos."}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input("Digite sua pergunta..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    intent = route_query(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner(f"Llama 3 pensando ({intent})..."):
            try:
                if intent == "products":
                    result = st.session_state.rag_chain.invoke({"query": prompt})
                    response_text = result['result']
                elif intent == "orders":
                    response_text = st.session_state.pandas_agent.run(prompt)
                
                st.write(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})
                
            except Exception as e:
                st.error(f"Erro: {str(e)}")
                st.info("Dica: Modelos locais menores podem falhar em lógica complexa. Tente simplificar a pergunta.")