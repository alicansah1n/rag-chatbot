"""
Veri önizleme bileşeni
"""
import streamlit as st
import pandas as pd


def render_data_preview(df: pd.DataFrame):
    """
    Veri setinin önizlemesini gösterir.
    
    Args:
        df: Pandas DataFrame
    """
    # Veri seti bilgileri
    st.subheader("📊 Veri Seti Bilgileri")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Satır Sayısı", len(df))
    with col2:
        st.metric("Sütun Sayısı", len(df.columns))
    with col3:
        st.metric("Toplam Veri", f"{len(df) * len(df.columns)} hücre")
    
    # İlk 5 satırı göster
    st.subheader("🔍 Veri Önizleme (İlk 5 Satır)")
    st.dataframe(df.head(5), use_container_width=True)
    
    # Sütun isimleri
    st.subheader("📋 Sütunlar")
    cols = df.columns.tolist()
    st.write(f"**Toplam {len(cols)} sütun:** " + ", ".join(cols))
    
    # Veri tipi bilgileri
    with st.expander("🔬 Detaylı Bilgi"):
        st.write("**Veri Tipleri:**")
        st.write(df.dtypes)
        st.write("**Eksik Değerler:**")
        st.write(df.isnull().sum())


def render_example_format():
    """
    Örnek CSV formatını gösterir (dosya yüklenmemişse).
    """
    st.info("👈 Lütfen sol taraftan CSV dosyanızı yükleyin")
    
    st.subheader("📝 Örnek CSV Formatı")
    st.write("CSV dosyanız şu şekilde olabilir:")
    example_df = pd.DataFrame({
        'soru': ['Python nedir?', 'Machine Learning nedir?'],
        'cevap': ['Python bir programlama dilidir.', 'ML yapay zeka dalıdır.']
    })
    st.dataframe(example_df, use_container_width=True)