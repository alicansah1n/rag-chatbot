"""
RAG Chatbot - Ana Uygulama
Modüler ve Clean Code prensiplerine uygun yapı
"""
import streamlit as st
import pandas as pd

# Config
from config.settings import PAGE_TITLE, PAGE_ICON, LAYOUT

# Components
from components.sidebar import render_sidebar
from components.data_preview import render_data_preview, render_example_format
from components.analysis import render_data_analysis
from components.rag_processor import render_rag_preparation
from components.chatbot import render_chatbot_interface

# Utils
from utils.data_loader import load_csv


def initialize_session_state():
    """Session state'i başlatır."""
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = []


def main():
    """Ana uygulama fonksiyonu."""
    # Sayfa ayarları
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=LAYOUT
    )
    
    # Session state başlat
    initialize_session_state()
    
    # Başlık
    st.title(f"{PAGE_ICON} {PAGE_TITLE} - CSV Veri Seti")
    st.write("Veri setinizi yükleyin ve sorular sorun!")
    
    # Sidebar - Dosya yükleme
    uploaded_file = render_sidebar()
    
    # Ana içerik
    if uploaded_file is not None:
        # CSV'yi yükle
        df = load_csv(uploaded_file)
        
        # Veri önizleme
        render_data_preview(df)
        
        # Veri analizi
        render_data_analysis(df)
        
        # RAG sistemi hazırlığı
        render_rag_preparation(df)
        
        # Chatbot arayüzü
        render_chatbot_interface()
    
    else:
        # Dosya yüklenmemişse örnek göster
        render_example_format()


if __name__ == "__main__":
    main()