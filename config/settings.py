"""
Proje ayarları ve sabitler
"""

# Sayfa ayarları
PAGE_TITLE = "RAG Chatbot"
PAGE_ICON = "🤖"
LAYOUT = "wide"

# Model ayarları
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "gpt-3.5-turbo"
LLM_TEMPERATURE = 0.3
LLM_MAX_TOKENS = 800
LLM_TOP_P = 0.9

# RAG ayarları
BATCH_SIZE = 100
TOP_K_RESULTS = 5
COLLECTION_NAME = "insurance_data"

# Veri analizi ayarları
DEFAULT_BINS = 30
MAX_HISTOGRAM_BINS = 100
MIN_HISTOGRAM_BINS = 10