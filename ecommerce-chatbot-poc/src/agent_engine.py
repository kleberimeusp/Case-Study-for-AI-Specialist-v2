import pandas as pd
from langchain_experimental.tools import PythonAstREPLTool
from langchain_ollama import ChatOllama

def setup_pandas_agent(df):
    """
    Função de entrada que o app.py chama.
    Configura e retorna nosso motor otimizado.
    """
    # Configura o LLM
    llm = ChatOllama(model="llama3", temperature=0)
    
    # Retorna a instância da nossa classe otimizada
    return FastPandasEngine(df, llm)

class FastPandasEngine:
    """
    Motor de execução otimizado (Fast Track).
    Tenta resolver via código direto primeiro, usa LLM só se necessário.
    """
    def __init__(self, df, llm):
        self.df = df
        self.llm = llm
        # Ferramenta segura para rodar pandas
        self.repl = PythonAstREPLTool(locals={"df": df})

    def run(self, query):
        query = query.lower()
        
        # --- ATALHO 1: Consultas de Status (Instantâneo) ---
        if "status" in query or "pedido" in query:
            # Tenta achar um ID de pedido (32 caracteres hexadecimais)
            words = query.split()
            potential_ids = [w for w in words if len(w) == 32]
            
            if potential_ids:
                order_id = potential_ids[0]
                # Busca direta no Pandas (sem LLM)
                result = self.df[self.df['order_id'] == order_id]
                if not result.empty:
                    status = result.iloc[0]['status']
                    return f"✅ O status do pedido `{order_id}` é: **{status}**."
                else:
                    return f"❌ Pedido `{order_id}` não encontrado."

        # --- ATALHO 2: Contagens Simples (Rápido) ---
        if "quantos" in query and "cancelado" in query:
            count = len(self.df[self.df['status'] == 'canceled'])
            return f"📊 Total de pedidos cancelados: **{count}**."

        if "total" in query and "pedidos" in query:
            count = len(self.df)
            return f"📊 Total de pedidos registrados: **{count}**."

        # --- MODO LLM (Para perguntas complexas) ---
        prompt = f"""
        Temos um dataframe 'df' com colunas: order_id, customer_id, status, valor_total, data_compra.
        Pergunta: {query}
        
        REGRAS:
        1. Retorne APENAS uma linha de código Python Pandas.
        2. NÃO use markdown (sem
```).
        3. NÃO use crases (`) no código. Use aspas simples (') ou duplas (").
        4. Exemplo correto: df[df['status'] == 'delivered'].shape[0]
        """
        
        try:
            # Pede o código
            code = self.llm.invoke(prompt).content
            
            # Limpeza agressiva do código gerado
            code = code.strip()
            code = code.replace("```python", "").replace("```", "")
            code = code.replace("`", "'") # CORREÇÃO DO ERRO DE CRASE
            
            # Executa
            result = self.repl.run(code)
            return f"🤖 Análise IA: {result}"
            
        except Exception as e:
            return f"⚠️ Não consegui calcular. Tente ser mais específico. (Erro: {str(e)})"