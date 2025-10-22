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
        # Modern başlık - Gradient
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 15px; border-radius: 10px; margin-bottom: 20px;">
            <h2 style="color: white; margin: 0; font-size: 20px;">📁 Veri Seti Yükleme</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Hızlı başlangıç kutusu - AÇIK ARKA PLAN
        st.markdown("""
        <div style="background-color: rgba(255, 255, 255, 0.95); padding: 15px; border-radius: 8px; 
                    border-left: 4px solid #667eea; margin-bottom: 20px;">
            <h4 style="margin-top: 0; color: #2c3e50;">⚡ Hızlı Başlangıç</h4>
            <ol style="margin-bottom: 0; padding-left: 20px; font-size: 14px; color: #2c3e50;">
                <li style="color: #2c3e50;">CSV dosyanızı seçin</li>
                <li style="color: #2c3e50;">Otomatik analiz başlasın</li>
                <li style="color: #2c3e50;">AI ile konuşmaya başlayın</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
        
        # Dosya yükleme alanı
        uploaded_file = st.file_uploader(
            "Dosyanızı sürükleyin veya seçin",
            type=['csv'],
            help="Maksimum 50MB • CSV formatı • UTF-8 encoding",
            key="file_uploader"
        )
        

        
        # Alt bilgi - BEYAZ YAZI
        st.markdown("""
        <div style="text-align: center; margin-top: 20px; padding-top: 10px; 
                    border-top: 1px solid rgba(255,255,255,0.2);">
            <p style="font-size: 12px; color: rgba(255,255,255,0.7); margin: 0;">
                🔒 Verileriniz güvenli ve geçici
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        return uploaded_file