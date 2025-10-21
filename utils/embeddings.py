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
    """
    embeddings_list = []
    start_time = time.time()
    
    # Çok küçük batch size kullan
    safe_batch_size = 32  # 50'den 32'ye düşürdük
    
    for i in range(0, len(texts), safe_batch_size):
        batch = texts[i:i + safe_batch_size]
        
        # Her batch'i daha da küçük parçalara böl
        for j in range(0, len(batch), 8):  # 8'er 8'er işle
            mini_batch = batch[j:j + 8]
            mini_embeddings = model.encode(
                mini_batch, 
                show_progress_bar=False,
                batch_size=8
            )
            embeddings_list.extend(mini_embeddings)
        
        if progress_callback:
            current = min(i + safe_batch_size, len(texts))
            progress = current / len(texts)
            elapsed = time.time() - start_time
            remaining = (elapsed * len(texts) / current) - elapsed if current > 0 else 0
            progress_callback(current, len(texts), progress, remaining)
    
    return np.array(embeddings_list)