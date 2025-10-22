import streamlit as st
import pandas as pd
from config.settings import PAGE_TITLE, PAGE_ICON, LAYOUT
from components.sidebar import render_sidebar
from components.data_preview import render_data_preview, render_example_format
from components.analysis import render_data_analysis
from components.rag_processor import render_rag_preparation
from components.chatbot import render_chatbot_interface
from utils.data_loader import load_csv


def load_css(file_name):
    with open(file_name, encoding='utf-8') as f:  # UTF-8 encoding ekledik
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)


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

    load_css('styles/custom.css')
    
    # Session state başlat
    initialize_session_state()
    
    # Başlık
    st.title(f"{PAGE_ICON} {PAGE_TITLE} - Veri Analiz ve Chatbot")
    
    # Profesyonel açıklama - Sadece Markdown
    st.info("**CSV veri setlerinizi yapay zeka ile analiz edin.** Veri bilimciler, analistler ve verilerinden içgörü elde etmek isteyen herkes için geliştirilmiş platform.")
    
    # Özellikler - 4 kolon
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("### 📊")
        st.markdown("**Otomatik İstatistikler**")
        st.caption("Tüm veri setiniz analiz edilir.")
    
    with col2:
        st.markdown("### 🤖")
        st.markdown("**AI Chatbot**")
        st.caption("İlk 100 satır analiz edilir.")
    
    with col3:
        st.markdown("### 📈")
        st.markdown("**Görselleştirmeler**")
        st.caption("Tüm veri setinize göre öngörülen grafikler.")
    
    with col4:
        st.markdown("### 💡")
        st.markdown("**Akıllı Öneriler**")
        st.caption("Veri odaklı içgörüler")
    
    # Önemli notlar - Expander
    with st.expander("⚠️ Önemli Bilgiler ve Limitasyonlar", expanded=False):
        st.markdown("""
        #### 🎯 Bu Platform Kimin İçin?
        - **Veri bilimciler** ve **analistler** için
        - Elinde **CSV formatında veri seti** olan herkes
        - Hızlı **analiz, öngörü ve fikir** almak isteyenler
        
        ---
        
        #### 🤖 Chatbot Hakkında
        Bu proje **deploy edilmiş** ve **ücretsiz** olduğu için:
        - **Token limiti** nedeniyle chatbot sadece **ilk 100 satırı** analiz eder
        - Tüm veri setinizi işlemek için **Token limitini** kendiniz ayarlayabilirsiniz.
        - Daha fazla satır için chatbot yanıtları **tam kesin olmayabilir**
        - **Genel sorular** ve **veri seti hakkında yorumlar** için idealdir
        
        💡 **Örnek kullanım:**  
        *"Bu veri setini açıkla", "Ortalama yaş nedir?", "Hangi analizler yapılabilir?"*
        
        ---
        
        #### 📊 Görselleştirmeler ve Grafikler
        - Korelasyon matrisleri, dağılım grafikleri, istatistikler.
        - Görselleştirmeler için AI yorumlaması için buton aktif edilmiştir.
        - Chatbot'tan farklı olarak **limit yoktur**
        
        ---
        
        #### 🔬 Beta Sürümü - MVP Aşaması
        - Proje **aktif geliştirme** aşamasındadır
        - AI yanıtları **hata yapabilir**
        - **Kritik iş kararları** için sonuçları manuel kontrol edin
        - Geri bildirimleriniz projeyi geliştirir 🙏
        
        ---
        
        #### 🔒 Veri Güvenliği
        - Yüklediğiniz dosyalar **sadece oturum süresince** saklanır
        - Oturum kapandığında veriler **otomatik silinir**
        - Sunucuda **kalıcı depolama yapılmaz**
        
        ---
        
        #### 📁 Teknik Gereksinimler
        - **Format:** CSV dosyası
        - **Maksimum boyut:** 50MB
        """)
    
    st.divider()
    
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
        
        render_example_format()


if __name__ == "__main__":
    main()