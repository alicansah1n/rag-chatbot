"""
Chatbot arayüzü bileşeni
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
    """
    API key'i alır (secrets veya environment'tan).
    
    Returns:
        str: API key veya None
    """
    # Önce Streamlit secrets'tan dene
    try:
        return st.secrets["OPENAI_API_KEY"]
    except:
        pass
    
    # Sonra environment variable'dan dene
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "your_api_key_here":
        return api_key
    
    return None


def render_chatbot_interface():
    """Ana chatbot arayüzünü render eder."""
    if 'collection' not in st.session_state:
        st.info("⚠️ Lütfen önce veriyi işleyin ve hazırlayın.")
        return
    
    st.divider()
    st.subheader("💬 AI Chatbot - Veri Setiniz Hakkında Soru Sorun")
    
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
            placeholder="Örnek: Veri setindeki öğrencilerin ortalama CGPA'sı nedir?",
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
    """
    Kullanıcı sorusunu işler ve cevap üretir.
    
    Args:
        user_question: Kullanıcı sorusu
        api_key: OpenAI API key
    """
    with st.spinner("🤔 Analiz ediyorum..."):
        try:
            # 1. Embedding oluştur
            embedding_model = st.session_state['embedding_model']
            query_embedding = embedding_model.encode([user_question])[0]
            
            # 2. Benzer dökümanları bul
            collection = st.session_state['collection']
            results = query_collection(collection, query_embedding, TOP_K_RESULTS)
            
            # 3. Context oluştur
            context_docs = results['documents'][0]
            
            if not context_docs:
                st.error("❌ Veri setinde ilgili bilgi bulunamadı.")
                st.info("💡 Farklı bir soru deneyin veya daha genel bir soru sorun.")
                return
            
            # En alakalı ilk 50 kaydı kullan (maliyet optimizasyonu)
            context = "\n\n---\n\n".join(context_docs[:50])
            
            # 4. Prompt oluştur
            system_prompt = """Sen uzman bir veri analisti ve AI asistanısın. Görevin:

1. Verilen veri setindeki bilgilere dayanarak kullanıcının sorusunu yanıtlamak
2. Yanıtlarını açık, net ve profesyonel Türkçe ile sunmak
3. Sayısal analizler ve istatistikler sunmak
4. Veri setinde yeterli bilgi yoksa dürüstçe belirtmek
5. Gerektiğinde örneklerle açıklamak

Yanıt formatı:
- Kısa ve öz bir özet ile başla
- Detaylı analiz ve sayısal veriler sun
- Madde madde veya paragraf halinde düzenle
- Profesyonel ama anlaşılır bir dil kullan"""

            user_prompt = f"""Aşağıda veri setinden alınmış en alakalı {min(len(context_docs), 50)} kayıt bulunmaktadır.

=== VERİ SETİ KAYITLARI ===
{context}

=== KULLANICI SORUSU ===
{user_question}

=== TALİMATLAR ===
✓ SADECE yukarıdaki veri kayıtlarını kullan
✓ İstatistiksel bilgiler varsa bunları vurgula
✓ Sayısal verileri tablolar veya maddeler halinde sun
✓ Veri setinde cevap yoksa açıkça belirt
✓ Türkçe dilbilgisi kurallarına özen göster

Cevap:"""
            
            # 5. LLM'den cevap al
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
            
            # 6. Cevabı göster
            st.success("✅ **Analiz Sonucu:**")
            st.markdown(answer)
            
            # 7. Geçmişe kaydet
            st.session_state['chat_history'].append({
                'question': user_question,
                'answer': answer
            })
            
            # 8. Meta bilgiler
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("🤖 Model", LLM_MODEL)
            with col2:
                st.metric("📊 Kaynak Sayısı", min(len(context_docs), 50))
            with col3:
                st.metric("🔥 Güven Skoru", "Yüksek")
            
            # 9. Kaynakları göster
            with st.expander(f"📚 Kullanılan Veri Kaynakları ({min(len(context_docs), 5)} örnek)"):
                for i, doc in enumerate(context_docs[:5], 1):
                    st.markdown(f"**📄 Kaynak {i}:**")
                    st.code(doc[:400] + ("..." if len(doc) > 400 else ""), language="text")
                    if i < 5:
                        st.divider()
        
        except Exception as e:
            st.error(f"❌ Bir hata oluştu: {str(e)}")
            
            # Detaylı hata mesajı (debug için)
            if "API key" in str(e) or "api_key" in str(e):
                st.info("💡 API key'inizi kontrol edin. Streamlit Secrets veya .env dosyasında doğru tanımlandığından emin olun.")
            elif "rate limit" in str(e).lower():
                st.info("💡 OpenAI rate limit aşıldı. Birkaç saniye bekleyip tekrar deneyin.")
            else:
                st.info("💡 Lütfen tekrar deneyin veya farklı bir soru sorun.")
            
            # Hata detayı (geliştirme modu için)
            with st.expander("🔍 Hata Detayı (Geliştiriciler için)"):
                st.code(str(e))