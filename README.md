<<<<<<< HEAD
# 🤖 RAG-Based Document QA Chatbot

> **Retrieval-Augmented Generation (RAG)** tabanlı, CSV veri setleri üzerinde çalışan akıllı chatbot sistemi.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 📌 Proje Hakkında

Bu proje, kullanıcıların **CSV formatındaki veri setlerini yükleyerek doğal dil ile sorgulama yapabilmesini** sağlayan bir **RAG (Retrieval-Augmented Generation)** chatbot uygulamasıdır.

---

## ✨ Özellikler

- 📊 **Veri Analizi**: İstatistiksel özet, korelasyon analizi, görselleştirmeler  
- 🤖 **AI-Powered İçgörüler**: GPT ile otomatik veri analizi  
- 💬 **Doğal Dil Sorguları**: Veri setinize doğal dilde soru sorun  
- 🔍 **Semantic Search**: Vektör tabanlı akıllı arama  
- 📈 **Görselleştirme**: Histogram, box plot, scatter plot  
- 🎯 **Clean Code**: Modüler ve sürdürülebilir mimari  

---

## 🛠️ Teknoloji Stack

- **Frontend**: Streamlit  
- **LLM**: OpenAI GPT-3.5-turbo  
- **Embeddings**: SentenceTransformers (`all-MiniLM-L6-v2`)  
- **Vector Database**: ChromaDB  
- **Veri Analizi**: Pandas, Matplotlib, Seaborn  
- **Dil**: Python 3.9+  

---

##  Kurulum ve Çalıştırma (Local)

🔹 **Projeyi klonlayın:**
```bash
git clone https://github.com/alicansah1n/rag-chatbot.git
cd rag-chatbot
```
🔹 **Adım 2: Virtual Environment Oluşturun**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# veya
.venv\Scripts\activate     # Windows
```
🔹 **Adım 3: Bağımlılıkları Yükleyin**
```bash
pip install -r requirements.txt
```
🔹 **Adım 4: Environment Variables Tanımlayın**
```bash
OPENAI_API_KEY=your_api_key_here
```
🔹 **Adım 5: Uygulamayı Çalıştırın**
```bash
streamlit run app.py
```
---
📖 Kullanım

CSV dosyanızı yükleyin

Veri analiz özetini inceleyin

“Veriyi İşle” butonuna tıklayın

Chatbot’a doğal dilde sorular sorun
---
📁 Proje Yapısı
rag-chatbot/
├── app.py
├── config/
│   └── settings.py
├── utils/
│   ├── data_loader.py
│   ├── embeddings.py
│   ├── vector_store.py
│   └── llm_handler.py
├── components/
│   ├── sidebar.py
│   ├── data_preview.py
│   ├── analysis.py
│   ├── rag_processor.py
│   └── chatbot.py
└── requirements.txt
---
🔒 Güvenlik

API key’ler .env dosyasında saklanır

.gitignore ile gizli dosyalar korunur
---
👤 Yazar

Ali Can Şahin
GitHub: @alicansah1n

LinkedIn: linkedin.com/in/alicansah1n



unutmaaaaaaaaaaaaaaaaaaaaaaaaaaa: api keyini sil!!!!!!!!!!



=======
# 🤖 RAG-Based Document QA Chatbot

> **Retrieval-Augmented Generation (RAG)** tabanlı, CSV veri setleri üzerinde çalışan akıllı chatbot sistemi.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 📌 Proje Hakkında

Bu proje, kullanıcıların **CSV formatındaki veri setlerini yükleyerek doğal dil ile sorgulama yapabilmesini** sağlayan bir **RAG (Retrieval-Augmented Generation)** chatbot uygulamasıdır.

---

## ✨ Özellikler

- 📊 **Veri Analizi**: İstatistiksel özet, korelasyon analizi, görselleştirmeler  
- 🤖 **AI-Powered İçgörüler**: GPT ile otomatik veri analizi  
- 💬 **Doğal Dil Sorguları**: Veri setinize doğal dilde soru sorun  
- 🔍 **Semantic Search**: Vektör tabanlı akıllı arama  
- 📈 **Görselleştirme**: Histogram, box plot, scatter plot  
- 🎯 **Clean Code**: Modüler ve sürdürülebilir mimari  

---

## 🛠️ Teknoloji Stack

- **Frontend**: Streamlit  
- **LLM**: OpenAI GPT-3.5-turbo  
- **Embeddings**: SentenceTransformers (`all-MiniLM-L6-v2`)  
- **Vector Database**: ChromaDB  
- **Veri Analizi**: Pandas, Matplotlib, Seaborn  
- **Dil**: Python 3.9+  

---

##  Kurulum ve Çalıştırma (Local)

🔹 **Projeyi klonlayın:**
```bash
git clone https://github.com/alicansah1n/rag-chatbot.git
cd rag-chatbot
```
🔹 **Adım 2: Virtual Environment Oluşturun**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# veya
.venv\Scripts\activate     # Windows
```
🔹 **Adım 3: Bağımlılıkları Yükleyin**
```bash
pip install -r requirements.txt
```
🔹 **Adım 4: Environment Variables Tanımlayın**
```bash
OPENAI_API_KEY=your_api_key_here
```
🔹 **Adım 5: Uygulamayı Çalıştırın**
```bash
streamlit run app.py
```
---
📖 Kullanım

CSV dosyanızı yükleyin

Veri analiz özetini inceleyin

“Veriyi İşle” butonuna tıklayın

Chatbot’a doğal dilde sorular sorun
---
📁 Proje Yapısı
rag-chatbot/
├── app.py
├── config/
│   └── settings.py
├── utils/
│   ├── data_loader.py
│   ├── embeddings.py
│   ├── vector_store.py
│   └── llm_handler.py
├── components/
│   ├── sidebar.py
│   ├── data_preview.py
│   ├── analysis.py
│   ├── rag_processor.py
│   └── chatbot.py
└── requirements.txt
---
🔒 Güvenlik

API key’ler .env dosyasında saklanır

.gitignore ile gizli dosyalar korunur
---
👤 Yazar

Ali Can Şahin
GitHub: @alicansah1n

LinkedIn: linkedin.com/in/alicansah1n



unutmaaaaaaaaaaaaaaaaaaaaaaaaaaa: api keyini sil!!!!!!!!!!



>>>>>>> 3633c2799da0cc2c2423acf6b23f3bdeabab126b
