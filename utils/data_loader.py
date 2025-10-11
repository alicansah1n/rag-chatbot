"""
Veri yükleme ve işleme fonksiyonları
"""
import pandas as pd
from typing import List, Dict, Tuple


def load_csv(uploaded_file) -> pd.DataFrame:
    """
    CSV dosyasını yükler.
    
    Args:
        uploaded_file: Streamlit file uploader object
        
    Returns:
        pd.DataFrame: Yüklenen veri
    """
    return pd.read_csv(uploaded_file)


def get_column_types(df: pd.DataFrame) -> Tuple[List[str], List[str]]:
    """
    Veri setindeki sütun tiplerini belirler.
    
    Args:
        df: Pandas DataFrame
        
    Returns:
        Tuple[List[str], List[str]]: (numeric_cols, categorical_cols)
    """
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    return numeric_cols, categorical_cols


def prepare_documents(df: pd.DataFrame) -> List[Dict]:
    """
    DataFrame'i döküman listesine çevirir.
    
    Args:
        df: Pandas DataFrame
        
    Returns:
        List[Dict]: Döküman listesi
    """
    documents = []
    for idx, row in df.iterrows():
        text = " | ".join([f"{col}: {row[col]}" for col in df.columns])
        documents.append({
            'id': f'doc_{idx}',
            'text': text,
            'metadata': row.to_dict()
        })
    return documents


def calculate_outliers(df: pd.DataFrame, column: str) -> Tuple[pd.DataFrame, float, float]:
    """
    IQR yöntemi ile aykırı değerleri tespit eder.
    
    Args:
        df: Pandas DataFrame
        column: Sütun adı
        
    Returns:
        Tuple[pd.DataFrame, float, float]: (outliers, lower_bound, upper_bound)
    """
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
    return outliers, lower_bound, upper_bound