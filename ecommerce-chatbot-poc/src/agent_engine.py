from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_ollama import ChatOllama

def setup_pandas_agent(orders_df):
    """
    Cria o agente Pandas usando Llama 3 Local.
    """
    llm = ChatOllama(
        model="llama3", 
        temperature=0
    )
    
    # Usamos agent_type="zero-shot-react-description" pois modelos locais
    # às vezes lutam com o formato "openai-tools"
    agent = create_pandas_dataframe_agent(
        llm, 
        orders_df, 
        verbose=True,
        allow_dangerous_code=True,
        agent_type="zero-shot-react-description",
        handle_parsing_errors=True # Ajuda se o Llama 3 errar a formatação
    )
    
    return agent