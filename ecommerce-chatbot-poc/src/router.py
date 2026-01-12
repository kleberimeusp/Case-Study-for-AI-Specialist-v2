def route_query(query):
    """
    Roteador Otimizado para Llama 3.
    Usa palavras-chave estritas para evitar erros de classificação.
    """
    query_lower = query.lower()
    
    # Palavras-chave FORTES para Pedidos/Dados
    # Se tiver qualquer uma dessas, vai para o Agente Pandas
    keywords_orders = [
        "pedido", "status", "entrega", "entregue", "cancelado", 
        "faturamento", "venda", "quanto custou", "valor total", 
        "media", "soma", "quantidade", "quantos", "tabela", "dado"
    ]
    
    # Verifica se é sobre pedidos
    if any(k in query_lower for k in keywords_orders):
        # Proteção extra: Se tiver "produto" na frase, mas for sobre "quantidade de vendas", é Pedido.
        # Mas se for "qual produto comprar", é Produto.
        if "comprar" in query_lower or "indique" in query_lower or "sugira" in query_lower:
            return "products"
        return "orders"
    
    # Se não for explicitamente sobre dados/pedidos, assume que é sobre Produtos (RAG)
    # Isso é mais seguro para perguntas como "quero decorar jardim"
    return "products"