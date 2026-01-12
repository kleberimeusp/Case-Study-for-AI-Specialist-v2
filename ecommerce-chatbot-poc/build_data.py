# build_data.py
import pandas as pd
import os
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings

# Configuração
BASE_PATH = "datasets_case"
OUTPUT_PATH = "processed_data"
os.makedirs(OUTPUT_PATH, exist_ok=True)

def process_and_save_data():
    print("⏳ Carregando CSVs brutos...")
    files = {
        'products': 'olist_products_dataset.csv',
        'items': 'olist_order_items_dataset.csv',
        'orders': 'olist_orders_dataset.csv',
        'translation': 'product_category_name_translation.csv'
    }
    
    # Leitura
    df_prod = pd.read_csv(f"{BASE_PATH}/{files['products']}")
    df_items = pd.read_csv(f"{BASE_PATH}/{files['items']}")
    df_orders = pd.read_csv(f"{BASE_PATH}/{files['orders']}")
    df_trans = pd.read_csv(f"{BASE_PATH}/{files['translation']}")

    print("⚙️ Processando Produtos...")
    # Merge Traduções
    df_prod = df_prod.merge(df_trans, on='product_category_name', how='left')
    df_prod['category'] = df_prod['product_category_name_english'].fillna(df_prod['product_category_name'])
    
    # Merge Preços (Média)
    avg_price = df_items.groupby('product_id')['price'].mean().reset_index()
    df_prod = df_prod.merge(avg_price, on='product_id', how='left')
    
    # Limpeza Final Produtos
    products_final = df_prod[['product_id', 'category', 'price']].dropna(subset=['category']).copy()
    products_final.rename(columns={'product_id': 'id', 'category': 'nome', 'price': 'preço'}, inplace=True)
    
    # Salvar em Parquet (Muito mais rápido que CSV)
    print("💾 Salvando produtos.parquet...")
    products_final.to_parquet(f"{OUTPUT_PATH}/products.parquet")

    print("⚙️ Processando Pedidos...")
    # Agregação de Valores
    order_values = df_items.groupby('order_id')['price'].sum().reset_index()
    order_values.rename(columns={'price': 'valor_total'}, inplace=True)
    
    # Merge Pedidos
    orders_final = df_orders.merge(order_values, on='order_id', how='left')
    
    # Seleção de Colunas CRÍTICAS (Remover lixo aumenta velocidade do Agente)
    cols_to_keep = ['order_id', 'customer_id', 'order_status', 'order_purchase_timestamp', 'valor_total']
    orders_final = orders_final[cols_to_keep].copy()
    
    # Formatação de Datas
    orders_final['data_compra'] = pd.to_datetime(orders_final['order_purchase_timestamp']).dt.strftime('%Y-%m-%d')
    orders_final.drop(columns=['order_purchase_timestamp'], inplace=True)
    orders_final['valor_total'] = orders_final['valor_total'].fillna(0.0)
    orders_final.rename(columns={'order_status': 'status'}, inplace=True)

    # Salvar em Parquet
    print("💾 Salvando orders.parquet...")
    orders_final.to_parquet(f"{OUTPUT_PATH}/orders.parquet")

    return products_final

def build_vector_store(products_df):
    print("🧠 Criando Índice Vetorial (Isso pode demorar uns minutos)...")
    
    # Limitar para POC (Olist tem 32k produtos, vamos indexar 2k mais populares para teste rápido)
    # Se quiser tudo, remova o .head(2000)
    products_sample = products_df.head(2000)
    
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    
    text_data = products_sample.apply(
        lambda x: f"Produto: {x['nome']}. Preço Médio: R$ {x['preço']:.2f}.", 
        axis=1
    ).tolist()
    
    vectorstore = FAISS.from_texts(text_data, embeddings)
    
    print("💾 Salvando índice FAISS no disco...")
    vectorstore.save_local(f"{OUTPUT_PATH}/faiss_index")

if __name__ == "__main__":
    prods = process_and_save_data()
    build_vector_store(prods)
    print("✅ Build concluído! Agora rode o app.py")