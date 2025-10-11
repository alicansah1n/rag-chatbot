"""
Sidebar bileşeni - Dosya yükleme
"""
import streamlit as st


def render_sidebar():
    """
    Sidebar'ı render eder ve yüklenen dosyayı döndürür.
    
    Returns:
        uploaded_file: Yüklenen dosya veya None
    """
    with st.sidebar:
        st.header("📁 Veri Seti Yükleme")
        
        uploaded_file = st.file_uploader(
            "CSV dosyanızı seçin",
            type=['csv'],
            help="Veri setinizi buraya yükleyin"
        )
        
        if uploaded_file is not None:
            st.success("✅ Dosya yüklendi!")
        
        return uploaded_file