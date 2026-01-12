# src/data_loader.py
import pandas as pd
import os
import streamlit as st

@st.cache_data
def load_optimized_data():
    """
    Carrega os dados pré-processados em Parquet.
    Leitura instantânea.
    """
    path = "processed_data"
    
    if not os.path.exists(f"{path}/products.parquet") or not os.path.exists(f"{path}/orders.parquet"):
        st.error("Dados processados não encontrados. Rode 'python build_data.py' primeiro.")
        return None, None

    # Leitura rápida
    products_df = pd.read_parquet(f"{path}/products.parquet")
    orders_df = pd.read_parquet(f"{path}/orders.parquet")
    
    return products_df, orders_df