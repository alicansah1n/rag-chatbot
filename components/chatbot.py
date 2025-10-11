"""
Chatbot arayüzü bileşeni
"""
import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
from utils.vector_store import query_collection
from config.settings import LLM_MODEL, LLM_TEMPERATURE, LLM_MAX_TOKENS, TOP_K_RESULTS


def render_chat_history():
    """
    Chat geçmişini gösterir.
    """
    if len(st.session_state['chat_history']) > 0:
        st.write("📜 **Konuşma Geçmişi:**")
        for chat in st.session_state['chat_history']:
            with st.chat_message("user"):
                st.write(chat['question'])
            with st.chat_message("assistant"):
                st.write(chat['answer'])
        st.divider()


def render_chatbot_interface():
    """
    Ana chatbot arayüzünü render eder.
    """
    if 'collection' not in st.session_state:
        return
    
    st.divider()
    st.subheader("💬 Chatbot - Soru Sorun!")
    
    # Chat geçmişini göster
    render_chat_history()
    
    # API Key kontrolü
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key or api_key == "your_api_key_here":
        st.warning("⚠️ Lütfen .env dosyasına OpenAI API key'inizi ekleyin!")
        api_key = st.text_input("Veya buraya API key girin:", type="password")
    
    if api_key and api_key != "your_api_key_here":
        # Soru input
        user_question = st.text_input(
            "❓ Sorunuzu yazın:",
            placeholder="Örnek: Bu veri setini açıklar mısın?"
        )
        
        if user_question:
            process_user_question(user_question, api_key)


def process_user_question(user_question: str, api_key: str):
    """
    Kullanıcı sorusunu işler ve cevap üretir.
    
    Args:
        user_question: Kullanıcı sorusu
        api_key: OpenAI API key
    """
    with st.spinner("🤔 Düşünüyorum..."):
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
                st.error("❌ Veri setinde ilgili bilgi bulunamadı. Lütfen farklı bir soru deneyin.")
                return
            
            context = "\n\n---\n\n".join(context_docs)
            
# 4. Prompt oluştur
            system_prompt = """Sen profesyonel bir veri analisti asistanısın. Kullanıcılara veri setleri hakkında sorular sorarak yardımcı oluyorsun.

Görevin:
1. Sana verilen veri setindeki bilgilere dayanarak kullanıcının sorusunu yanıtlamak
2. Yanıtlarını açık, net ve anlaşılır Türkçe ile vermek
3. Eğer veri setinde yeterli bilgi yoksa bunu dürüstçe belirtmek
4. Mümkün olduğunca sayısal veriler ve örnekler vermek"""

            user_prompt = f"""Aşağıda bir veri setinden alınmış ilgili kayıtlar bulunmaktadır. Bu kayıtlara dayanarak kullanıcının sorusunu yanıtla.

=== VERİ SETİ KAYITLARI ===
{context}

=== KULLANICI SORUSU ===
{user_question}

=== TALİMATLAR ===
- SADECE yukarıdaki veri setindeki bilgileri kullan
- Eğer veri setinde cevap yoksa, "Bu bilgi veri setinde mevcut değil" de
- Cevabını madde madde veya paragraf şeklinde düzenle
- Sayısal bilgiler varsa bunları vurgula
- Türkçe dilbilgisi kurallarına dikkat et

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
            st.success("✅ Cevap:")
            st.markdown(answer)
            
            # 7. Geçmişe kaydet
            st.session_state['chat_history'].append({
                'question': user_question,
                'answer': answer
            })
            
            # 8. Kaynakları göster
            with st.expander("📚 Kullanılan Veri Kaynakları (5 en alakalı kayıt)"):
                for i, doc in enumerate(context_docs, 1):
                    st.markdown(f"**Kaynak {i}:**")
                    st.code(doc[:300] + ("..." if len(doc) > 300 else ""), language="text")
                    st.divider()
        
        except Exception as e:
            st.error(f"❌ Bir hata oluştu: {str(e)}")
            st.info("💡 Lütfen tekrar deneyin veya farklı bir soru sorun.")