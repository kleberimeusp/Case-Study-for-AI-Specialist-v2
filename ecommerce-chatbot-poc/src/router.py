def route_query(query):
    """
    Classifica a intenção do usuário baseada em palavras-chave.
    Em produção, isso seria um LLM Classifier ou Semantic Router.
    """
    query_lower = query.lower()
    
    # Palavras-chave de Pedidos (Transacional)
    order_keywords = [
        'pedido', 'status', 'entrega', 'rastreio', 'compra', 'chega', 
        'enviado', 'cancelado', 'minha compra', 'número'
    ]
    
    # Palavras-chave de Produtos (Semântico/Exploratório)
    product_keywords = [
        'produto', 'tem', 'vende', 'preço', 'custa', 'descrição', 
        'recomendação', 'melhor', 'barato', 'caro', 'estoque', 
        'tênis', 'fone', 'cadeira', 'notebook', 'serve para'
    ]
    
    # Lógica de prioridade
    if any(k in query_lower for k in order_keywords):
        return "orders"
    elif any(k in query_lower for k in product_keywords):
        return "products"
    
    # Default (fallback)
    return "products"