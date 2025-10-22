"""
Chatbot arayüzü bileşeni - DENGELI VERSİYON
"""
import streamlit as st
import os
from openai import OpenAI
from utils.vector_store import query_collection
from config.settings import LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS, TOP_K_RESULTS


def render_chat_history():
    """Chat geçmişini gösterir."""
    if len(st.session_state['chat_history']) > 0:
        st.write("📜 **Konuşma Geçmişi:**")
        for chat in st.session_state['chat_history']:
            with st.chat_message("user"):
                st.write(chat['question'])
            with st.chat_message("assistant"):
                st.write(chat['answer'])
        st.divider()


def get_api_key():
    """API key'i alır."""
    try:
        return st.secrets["OPENAI_API_KEY"]
    except:
        pass
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your_api_key_here":
        return api_key
    
    return None


def is_statistical_query(question: str) -> bool:
    """Sorunun istatistiksel olup olmadığını kontrol eder."""
    stat_keywords = [
        'ortalama', 'average', 'mean', 'ort',
        'toplam', 'total', 'sum',
        'maksimum', 'max', 'en yüksek', 'en fazla', 'en büyük',
        'minimum', 'min', 'en düşük', 'en az', 'en küçük',
        'medyan', 'median',
        'standart sapma', 'std', 'sapma',
        'varyans', 'variance',
        'yüzde', 'percent', 'oran', 'ratio'
    ]
    return any(keyword in question.lower() for keyword in stat_keywords)


def get_statistical_answer(question: str, dataset_stats: dict) -> str:
    """İstatistiksel soruya dataset_stats'tan direkt cevap üretir."""
    question_lower = question.lower()
    
    # Sayısal sütunlar için
    for col, stats in dataset_stats.get('numeric_stats', {}).items():
        col_lower = col.lower()
        
        if col_lower in question_lower:
            response = f"### 📊 {col.upper()} İstatistikleri\n\n"
            response += f"**Kaynak:** Tüm {dataset_stats['total_rows']:,} kayıttan hesaplandı\n\n"
            
            if 'ortalama' in question_lower or 'average' in question_lower or 'mean' in question_lower:
                response += f"📊 **Ortalama:** {stats['mean']:.2f}\n"
                return response
            
            if 'maksimum' in question_lower or 'max' in question_lower or 'en yüksek' in question_lower or 'en fazla' in question_lower or 'en büyük' in question_lower:
                response += f"⬆️ **Maksimum:** {stats['max']:.2f}\n"
                return response
            
            if 'minimum' in question_lower or 'min' in question_lower or 'en düşük' in question_lower or 'en az' in question_lower or 'en küçük' in question_lower:
                response += f"⬇️ **Minimum:** {stats['min']:.2f}\n"
                return response
            
            # Genel soru - tüm istatistikler
            response += f"📊 **Ortalama:** {stats['mean']:.2f}\n"
            response += f"📍 **Medyan:** {stats['median']:.2f}\n"
            response += f"📏 **Standart Sapma:** {stats['std']:.2f}\n"
            response += f"⬇️ **Minimum:** {stats['min']:.2f}\n"
            response += f"⬆️ **Maksimum:** {stats['max']:.2f}\n"
            response += f"📦 **Q1 (25%):** {stats['q1']:.2f}\n"
            response += f"📦 **Q3 (75%):** {stats['q3']:.2f}\n"
            
            return response
    
    # Kategorik sütunlar için
    for col, stats in dataset_stats.get('categorical_stats', {}).items():
        col_lower = col.lower()
        
        if col_lower in question_lower:
            response = f"### 🏷️ {col.upper()} Dağılımı\n\n"
            response += f"**Kaynak:** Tüm {dataset_stats['total_rows']:,} kayıttan hesaplandı\n\n"
            
            response += f"🔢 **Benzersiz değer sayısı:** {stats['unique_count']}\n"
            response += f"🏆 **En sık:** {stats['most_common']} ({stats['most_common_count']:,} kez, %{stats['most_common_pct']:.1f})\n\n"
            response += f"📊 **Dağılım:**\n"
            for key, count in stats['distribution'].items():
                pct = (count / dataset_stats['total_rows']) * 100
                response += f"- **{key}:** {count:,} adet (%{pct:.1f})\n"
            
            return response
    
    return None


def render_chatbot_interface():
    """Ana chatbot arayüzünü render eder."""
    if 'collection' not in st.session_state:
        st.info("⚠️ Lütfen önce veriyi işleyin ve hazırlayın.")
        return
    
    st.divider()
    st.subheader("💬 AI Chatbot - Veri Setiniz Hakkında Soru Sorun")
    
    # Kullanım kılavuzu
    with st.expander("💡 Nasıl Soru Sorulur?", expanded=False):
        dataset_stats = st.session_state.get('dataset_stats', {})
        numeric_cols = dataset_stats.get('numeric_columns', [])
        categorical_cols = dataset_stats.get('categorical_columns', [])
        
        st.write("### ✅ Kesin İstatistikler İçin:")
        if numeric_cols:
            st.write(f"**Sayısal sütunlar:** `{', '.join(numeric_cols[:5])}`")
            st.code(f"Örnek: Ortalama {numeric_cols[0]} nedir?", language="text")
        
        if categorical_cols:
            st.write(f"**Kategorik sütunlar:** `{', '.join(categorical_cols[:5])}`")
            st.code(f"Örnek: {categorical_cols[0]} dağılımı nedir?", language="text")
        
        st.write("### 📊 Genel Sorular İçin:")
        st.write("- **'Bu veri setini açıkla'** → Genel bakış")
        st.write("- **'Ne amaçla kullanılır?'** → İş yorumları")
        st.write("- **'Hangi analizler yapılabilir?'** → Öneriler")
    
    # Chat geçmişini göster
    render_chat_history()
    
    # API Key kontrolü
    api_key = get_api_key()
    
    if not api_key:
        st.error("❌ OpenAI API key bulunamadı!")
        st.info("💡 Lütfen Streamlit Secrets'a veya .env dosyasına API key'inizi ekleyin.")
        api_key = st.text_input("Veya buraya API key girin:", type="password", key="api_key_input")
    
    if api_key:
        # Soru input
        user_question = st.text_input(
            "❓ Sorunuzu yazın:",
            placeholder="Örnek: Bu veri setini açıklar mısın?",
            key="user_question_input"
        )
        
        col1, col2 = st.columns([1, 5])
        with col1:
            submit_button = st.button("🚀 Gönder", type="primary")
        
        if submit_button and user_question:
            process_user_question(user_question, api_key)
        elif submit_button and not user_question:
            st.warning("⚠️ Lütfen bir soru yazın!")


def process_user_question(user_question: str, api_key: str):
    """Kullanıcı sorusunu işler ve cevap üretir."""
    with st.spinner("🤔 Analiz ediyorum..."):
        try:
            dataset_stats = st.session_state.get('dataset_stats', {})
            total_records = dataset_stats.get('total_rows', len(st.session_state.get('documents', [])))
            
            # 1. İstatistiksel soru mu kontrol et
            if is_statistical_query(user_question) and dataset_stats:
                stat_answer = get_statistical_answer(user_question, dataset_stats)
                
                if stat_answer:
                    st.success("✅ **KESİN Analiz Sonucu (Tüm Veri Setinden):**")
                    st.markdown(stat_answer)
                    
                    st.session_state['chat_history'].append({
                        'question': user_question,
                        'answer': stat_answer
                    })
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("📊 Veri Kaynağı", "Hesaplanmış İstatistikler")
                    with col2:
                        st.metric("💾 Toplam Veri", f"{total_records:,} satır")
                    with col3:
                        st.metric("⚡ Güvenilirlik", "100%")
                    
                    st.info("💡 Bu cevap **TÜM** veri setinden hesaplanan kesin istatistiklere dayanmaktadır.")
                    return
            
            # 2. RAG kullan
            embedding_model = st.session_state['embedding_model']
            query_embedding = embedding_model.encode([user_question])[0]
            
            collection = st.session_state['collection']
            results = query_collection(collection, query_embedding, TOP_K_RESULTS)
            
            context_docs = results['documents'][0]
            
            if not context_docs:
                st.error("❌ **Üzgünüm, bu soruyu cevaplayamıyorum.**")
                st.warning("**Neden:** Veri setinde bu soruyla alakalı hiçbir bilgi bulunamadı.")
                st.info("💡 **Önerim:** Daha genel bir soru sorun veya farklı kelimeler kullanın.")
                return
            
            context = "\n\n---\n\n".join(context_docs)
            
            # 3. DENGELI PROMPT
            has_numeric = len(dataset_stats.get('numeric_columns', [])) > 0
            has_categorical = len(dataset_stats.get('categorical_columns', [])) > 0
            
            numeric_cols_str = ", ".join(dataset_stats.get('numeric_columns', []))
            categorical_cols_str = ", ".join(dataset_stats.get('categorical_columns', []))
            
            system_prompt = """Sen profesyonel bir veri analistisin. Hem hesaplama yaparsın hem yorumlarsın.

İKİ TÜR SORU VAR:

═══════════════════════════════════════
📊 TİP 1: HESAPLAMA/İSTATİSTİK SORULARI
═══════════════════════════════════════
Örnekler:
- "Ortalama/toplam/maksimum X nedir?"
- "Kaç kişi Y özelliğine sahip?"
- "X ile Y arasındaki fark?"

YAPMAN GEREKEN:
✅ Verilen kayıtlardan hesapla
✅ Net rakam ver
✅ "Bu X kayıttan hesaplandı" de
✅ Yetersizse: "Kesin sonuç için tüm veriyi işlemek gerek" de

═══════════════════════════════════════
💡 TİP 2: GENEL/YORUMLAMA SORULARI
═══════════════════════════════════════
Örnekler:
- "Bu veri setini açıkla"
- "Ne amaçla kullanılır?"
- "İş dünyasında ne anlama gelir?"
- "Hangi kararlar alınabilir?"

YAPMAN GEREKEN:
✅ Veri setinin yapısını açıkla
✅ Sütunları yorumla
✅ İş/bilim açısından ne anlama geldiğini söyle
✅ Kullanım alanlarını öner
✅ Hangi soruların cevaplanabileceğini belirt

ÖRNEK CEVAP (Sigorta veri seti için):
"Bu veri seti sigorta şirketlerinin prim belirleme için kullanır. 
Yaş, BMI, sigara gibi risk faktörleri ile sigorta maliyeti arasındaki 
ilişkiyi analiz eder. Şirketler bu verileri kullanarak:
- Risk profili oluşturur
- Prim fiyatlandırması yapar
- Yüksek riskli müşterileri tespit eder"

═══════════════════════════════════════
❌ YASAKLAR (SADECE BUNLAR!)
═══════════════════════════════════════
❌ Veri setinde OLMAYAN spesifik bilgileri UYDURMA (isim, adres, vb.)
❌ Kesin olmayan rakamları kesinmiş gibi sunma
❌ "Muhtemelen X kişidir" gibi spesifik tahminler yapma

✅ İZİN VERİLENLER
✅ Genel yorumlar: "Bu veri seti muhtemelen X amacıyla toplanmış"
✅ İş yorumları: "Bu bilgiler Y için kullanılabilir"
✅ Öneriler: "Z analizi yapılabilir"
✅ Hesaplamalar: Verilen kayıtlardan hesapla

CEVAP FORMATI:
1. Direkt cevap
2. Detaylı açıklama
3. Kaynak bilgisi (hesaplama yapıldıysa)"""

            user_prompt = f"""VERİ SETİ BİLGİLERİ:
- Toplam: {total_records:,} kayıt
- Analiz için kullanılan: {len(context_docs)} en alakalı kayıt
- Sayısal sütunlar: {numeric_cols_str or "Yok"}
- Kategorik sütunlar: {categorical_cols_str or "Yok"}

═══════════════════════════════════════
VERİ ÖRNEKLERİ (İlk {len(context_docs)} kayıt):
═══════════════════════════════════════
{context}

═══════════════════════════════════════
KULLANICI SORUSU:
═══════════════════════════════════════
{user_question}

═══════════════════════════════════════
TALİMATLAR:
═══════════════════════════════════════
1. Soru HESAPLAMA gerektiriyorsa → Kayıtlardan hesapla + "X kayıttan hesaplandı" de
2. Soru GENEL/YORUM gerektiriyorsa → Veri yapısını yorumla, kullanım alanlarını söyle
3. SPESİFİK bilgi yoksa → "Bu bilgi veri setinde yok" de
4. Türkçe sütun adı varsa → İngilizce karşılığını bul ve kullan

CEVAP VER:"""
            
            # 4. LLM çağrısı
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS,
                top_p=0.9
            )
            answer = response.choices[0].message.content
            
            # 5. Cevap gösterimi
            st.success("✅ **Analiz Sonucu:**")
            st.markdown(answer)
            
            st.session_state['chat_history'].append({
                'question': user_question,
                'answer': answer
            })
            
            # 6. Meta bilgiler
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🤖 Model", LLM_MODEL)
            with col2:
                st.metric("📊 Kullanılan Veri", f"{len(context_docs)}/{total_records:,}")
            with col3:
                reliability = int((len(context_docs) / total_records) * 100)
                st.metric("⚡ Kapsam", f"~{reliability}%")
            
            # 7. UYARI (sadece hesaplama sorularında)
            if is_statistical_query(user_question):
                st.warning(f"""⚠️ **NOT:** Bu hesaplama {len(context_docs)} kayıttan yapıldı.

**Kesin istatistik için:**
Sütun isimlerini kullanın: `{numeric_cols_str.split(',')[0] if numeric_cols_str else 'N/A'}`""")
            
            # 8. Kaynaklar
            with st.expander(f"📚 Kullanılan {min(len(context_docs), 5)} Veri Kaynağı"):
                for i, doc in enumerate(context_docs[:5], 1):
                    st.markdown(f"**📄 Kaynak {i}:**")
                    st.code(doc[:400] + ("..." if len(doc) > 400 else ""), language="text")
                    if i < 5:
                        st.divider()
        
        except Exception as e:
            st.error(f"❌ Bir hata oluştu: {str(e)}")
            
            if "API key" in str(e) or "api_key" in str(e):
                st.info("💡 API key'inizi kontrol edin.")
            elif "rate limit" in str(e).lower():
                st.info("💡 OpenAI rate limit aşıldı. Bekleyin.")
            else:
                st.info("💡 Tekrar deneyin.")
            
            with st.expander("🔍 Hata Detayı"):
                st.code(str(e))