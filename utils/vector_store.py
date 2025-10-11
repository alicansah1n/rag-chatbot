"""
Vector store işlemleri (ChromaDB)
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict
import numpy as np


def create_chroma_client() -> chromadb.Client:
    """
    ChromaDB client oluşturur.
    
    Returns:
        chromadb.Client: Client instance
    """
    return chromadb.Client(Settings(
        anonymized_telemetry=False,
        is_persistent=False
    ))


def create_or_reset_collection(
    client: chromadb.Client, 
    collection_name: str,
    description: str = "Dataset embeddings"
):
    """
    Collection oluşturur veya sıfırlar.
    
    Args:
        client: ChromaDB client
        collection_name: Collection adı
        description: Açıklama
        
    Returns:
        Collection object
    """
    try:
        client.delete_collection(collection_name)
    except:
        pass
    
    return client.create_collection(
        name=collection_name,
        metadata={"description": description}
    )


def add_documents_to_collection(
    collection,
    documents: List[Dict],
    embeddings: np.ndarray,
    texts: List[str]
):
    """
    Dökümanları collection'a ekler.
    
    Args:
        collection: ChromaDB collection
        documents: Döküman listesi
        embeddings: Embedding array
        texts: Metin listesi
    """
    collection.add(
        ids=[doc['id'] for doc in documents],
        embeddings=embeddings.tolist(),
        documents=texts,
        metadatas=[doc['metadata'] for doc in documents]
    )


def query_collection(
    collection,
    query_embedding: np.ndarray,
    n_results: int = 5
) -> Dict:
    """
    Collection'dan benzer dökümanları sorgular.
    
    Args:
        collection: ChromaDB collection
        query_embedding: Sorgu embedding'i
        n_results: Döndürülecek sonuç sayısı
        
    Returns:
        Dict: Sorgu sonuçları
    """
    return collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=n_results
    )