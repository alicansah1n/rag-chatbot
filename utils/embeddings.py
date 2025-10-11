"""
Embedding işlemleri
"""
import streamlit as st
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
import time


@st.cache_resource
def load_embedding_model(model_name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
    """
    Embedding modelini yükler (cache'lenir).
    
    Args:
        model_name: Model adı
        
    Returns:
        SentenceTransformer: Yüklenen model
    """
    return SentenceTransformer(model_name)


def create_embeddings_batch(
    texts: List[str], 
    model: SentenceTransformer, 
    batch_size: int = 100,
    progress_callback=None
) -> np.ndarray:
    """
    Metinleri batch'ler halinde embedding'lere çevirir.
    
    Args:
        texts: Metin listesi
        model: Embedding modeli
        batch_size: Batch boyutu
        progress_callback: İlerleme callback fonksiyonu
        
    Returns:
        np.ndarray: Embedding array
    """
    embeddings_list = []
    start_time = time.time()
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        batch_embeddings = model.encode(batch, show_progress_bar=False)
        embeddings_list.extend(batch_embeddings)
        
        if progress_callback:
            current = min(i + batch_size, len(texts))
            progress = current / len(texts)
            elapsed = time.time() - start_time
            remaining = (elapsed * len(texts) / current) - elapsed if current > 0 else 0
            progress_callback(current, len(texts), progress, remaining)
    
    return np.array(embeddings_list)