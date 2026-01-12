import pandas as pd
import random
from datetime import datetime, timedelta

def generate_synthetic_data():
    """
    Gera DataFrames sintéticos para Produtos e Pedidos.
    Simula um banco de dados de e-commerce.
    """
    
    # 1. Dados de Produtos (Foco em descrições ricas para o RAG)
    products_data = {
        'id': range(101, 111),
        'nome': [
            'Tênis UltraBoost Runner', 'Fone NoiseCancelling Pro', 'Notebook DevStation X1', 
            'Cadeira ErgoLife Office', 'Smartwatch HealthTrack 5', 'Cafeteira Barista Express',
            'Mochila Tech Waterproof', 'Monitor 4K CrystalView', 'Teclado Mecânico RGB', 'Garrafa Térmica KeepHot'
        ],
        'categoria': [
            'Calçados', 'Áudio', 'Computadores', 'Móveis', 'Wearables', 
            'Eletrodomésticos', 'Acessórios', 'Periféricos', 'Periféricos', 'Acessórios'
        ],
        'descrição': [
            'Tênis de alta performance com amortecimento responsivo, ideal para maratonas e treinos longos em asfalto.',
            'Fone de ouvido over-ear com cancelamento de ruído ativo, bateria de 30 horas e conexão multiponto.',
            'Notebook com processador i9, 32GB RAM e GPU dedicada, perfeito para compilação de código e modelagem 3D.',
            'Cadeira ergonômica com suporte lombar ajustável, encosto em mesh respirável e certificação NR17.',
            'Relógio inteligente com monitoramento de ECG, oxigênio no sangue e GPS integrado para triatletas.',
            'Cafeteira expresso automática com moedor integrado e vaporizador de leite profissional.',
            'Mochila impermeável com compartimento para notebook de 17 polegadas e porta USB externa.',
            'Monitor IPS de 27 polegadas com resolução UHD, 99% sRGB e suporte HDR10 para designers.',
            'Teclado mecânico com switches brown táteis, iluminação RGB customizável e layout ABNT2.',
            'Garrafa de aço inoxidável com parede dupla, mantém bebidas quentes por 12h e geladas por 24h.'
        ],
        'preço': [899.90, 1200.00, 15000.00, 1800.00, 2500.00, 3500.00, 350.00, 2800.00, 700.00, 120.00],
        'estoque': [15, 8, 3, 5, 20, 4, 50, 10, 25, 100]
    }
    products_df = pd.DataFrame(products_data)

    # 2. Dados de Pedidos (Foco em status e datas para o Agente)
    possible_statuses = ['Pendente', 'Processando', 'Enviado', 'Entregue', 'Cancelado']
    
    # CORREÇÃO: Geramos a lista de status para os 15 pedidos PRIMEIRO
    generated_statuses = [random.choice(possible_statuses) for _ in range(15)]
    
    orders_data = {
        'id_pedido': range(5001, 5016),
        'id_cliente': [random.randint(1, 5) for _ in range(15)], # Simula 5 clientes recorrentes
        'status': generated_statuses, # Usa a lista gerada com 15 itens
        'data_compra': [(datetime.now() - timedelta(days=random.randint(1, 60))).strftime('%Y-%m-%d') for _ in range(15)],
        'valor_total': [random.uniform(100, 5000) for _ in range(15)],
        # CORREÇÃO: Itera sobre a lista 'generated_statuses' (tamanho 15), não sobre 'possible_statuses' (tamanho 5)
        'rastreio': [f'BR{random.randint(100000, 999999)}TX' if s in ['Enviado', 'Entregue'] else None for s in generated_statuses]
    }
    
    orders_df = pd.DataFrame(orders_data)
    
    # Ajuste lógico: Se entregue, tem data de entrega
    orders_df['previsao_entrega'] = pd.to_datetime(orders_df['data_compra']) + pd.to_timedelta(random.randint(3, 10), unit='d')
    orders_df['previsao_entrega'] = orders_df['previsao_entrega'].dt.strftime('%Y-%m-%d')
    
    return products_df, orders_df