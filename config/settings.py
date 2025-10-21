"""
🎯 RAG Chatbot - Evrensel Veri Analiz Platformu
Herhangi bir CSV veri seti ile çalışabilen akıllı analiz sistemi
"""

# ═══════════════════════════════════════════
# 📱 SAYFA AYARLARI
# ═══════════════════════════════════════════
PAGE_TITLE = "RAG Akıllı Veri Analiz Platformu"
PAGE_ICON = "🔍"
LAYOUT = "wide"

# ═══════════════════════════════════════════
# 🤖 YAPAY ZEKA MODEL AYARLARI
# ═══════════════════════════════════════════
EMBEDDING_MODEL = "all-MiniLM-L6-v2"    # Metin vektörleştirme modeli
LLM_MODEL = "gpt-4o"                    # Cevap üretici AI modeli
LLM_TEMPERATURE = 0.3                   # Yaratıcılık seviyesi (0-1)
LLM_MAX_TOKENS = 1500                   # Maksimum cevap uzunluğu
LLM_TOP_P = 0.9                         # Kelime çeşitliliği kontrolü

# ═══════════════════════════════════════════
# 🔍 RAG SİSTEM AYARLARI
# ═══════════════════════════════════════════
BATCH_SIZE = 100                        # Veri işleme toplu boyutu
TOP_K_RESULTS = 100                     # Her aramada getirilen sonuç sayısı
COLLECTION_NAME = "user_dataset"        # Dinamik veri koleksiyonu

# ═══════════════════════════════════════════
# 📊 VERİ ANALİZİ AYARLARI
# ═══════════════════════════════════════════
DEFAULT_BINS = 30                       # Grafiklerde varsayılan grup sayısı
MAX_HISTOGRAM_BINS = 100                # Maksimum histogram detayı
MIN_HISTOGRAM_BINS = 10                 # Minimum histogram detayı

# ═══════════════════════════════════════════
# 🎨 ARAYÜZ METİNLERİ
# ═══════════════════════════════════════════
APP_DESCRIPTION = """
📊 Herhangi bir CSV veri setini yükleyin, anında analiz edin ve yapay zeka 
destekli chatbot ile verileriniz hakkında detaylı sorular sorun!

⚠️ Not: Orta ölçekli veri setleri için optimize edilmiştir (max 100K satır).
"""

UPLOAD_HELP = "CSV dosyanızı yükleyin (Max: 50MB | Önerilen: 10-50K satır)"