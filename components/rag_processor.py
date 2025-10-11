"""
RAG işleme bileşeni - Embedding ve Vector Store hazırlığı
"""
import streamlit as st
import time
from utils.data_loader import prepare_documents
from utils.embeddings import load_embedding_model, create_embeddings_batch
from utils.vector_store import (
    create_chroma_client,
    create_or_reset_collection,
    add_documents_to_collection
)
from config.settings import (
    EMBEDDING_MODEL,
    BATCH_SIZE,
    COLLECTION_NAME
)


def render_rag_preparation(df):
    """
    RAG sistemi hazırlık bölümünü render eder.
    
    Args:
        df: Pandas DataFrame
    """
    st.divider()
    st.subheader("🧠 RAG Sistemi Hazırlığı")
    
    if st.button("🚀 Veriyi İşle ve Hazırla", type="primary"):
        main_progress = st.progress(0)
        main_status = st.empty()
        
        try:
            # ═══════════════════════════════════════
            # ADIM 1/4: VERİ HAZIRLAMA
            # ═══════════════════════════════════════
            main_status.markdown("### 🔄 Adım 1/4: Veri hazırlanıyor...")
            step1_progress = st.progress(0)
            step1_status = st.empty()
            
            documents = prepare_documents(df)
            total_rows = len(df)
            
            for idx in range(total_rows):
                if idx % 100 == 0 or idx == total_rows - 1:
                    progress = (idx + 1) / total_rows
                    step1_progress.progress(progress)
                    step1_status.text(f"📊 {idx + 1:,}/{total_rows:,} satır işlendi")
            
            step1_progress.progress(1.0)
            step1_status.empty()
            step1_progress.empty()
            st.success(f"✅ Adım 1 tamamlandı: {len(documents):,} döküman oluşturuldu")
            main_progress.progress(0.25)
            
            with st.expander("🔍 Örnek Dökümanlar (İlk 3)"):
                for i in range(min(3, len(documents))):
                    st.code(documents[i]['text'][:200] + "...", language="text")
            
            time.sleep(0.3)
            
            # ═══════════════════════════════════════
            # ADIM 2/4: EMBEDDING MODEL YÜKLEME
            # ═══════════════════════════════════════
            main_status.markdown("### 🔄 Adım 2/4: Embedding modeli yükleniyor...")
            step2_progress = st.progress(0)
            step2_status = st.empty()
            
            step2_status.text("📥 Model indiriliyor...")
            step2_progress.progress(0.3)
            
            embedding_model = load_embedding_model(EMBEDDING_MODEL)
            
            step2_progress.progress(1.0)
            step2_status.empty()
            step2_progress.empty()
            st.success(f"✅ Adım 2 tamamlandı: Model yüklendi ({EMBEDDING_MODEL})")
            main_progress.progress(0.50)
            
            time.sleep(0.3)
            
            # ═══════════════════════════════════════
            # ADIM 3/4: EMBEDDING OLUŞTURMA
            # ═══════════════════════════════════════
            main_status.markdown("### 🔄 Adım 3/4: Embeddings oluşturuluyor...")
            step3_progress = st.progress(0)
            step3_status = st.empty()
            
            texts = [doc['text'] for doc in documents]
            start_time = time.time()
            
            def progress_callback(current, total, progress, remaining):
                step3_progress.progress(progress)
                step3_status.text(
                    f"📊 {current:,}/{total:,} döküman ({progress*100:.1f}%) | "
                    f"Kalan: ~{int(remaining/60)}dk {int(remaining%60)}sn"
                )
            
            embeddings = create_embeddings_batch(
                texts,
                embedding_model,
                batch_size=BATCH_SIZE,
                progress_callback=progress_callback
            )
            
            total_time = time.time() - start_time
            
            step3_progress.progress(1.0)
            step3_status.empty()
            step3_progress.empty()
            st.success(
                f"✅ Adım 3 tamamlandı: {len(embeddings):,} embedding oluşturuldu "
                f"({int(total_time/60)}dk {int(total_time%60)}sn)"
            )
            st.info(f"📐 Embedding boyutu: {embeddings.shape[0]:,} × {embeddings.shape[1]} boyut")
            main_progress.progress(0.75)
            
            time.sleep(0.3)
            
            # ═══════════════════════════════════════
            # ADIM 4/4: VECTOR STORE KAYDETME
            # ═══════════════════════════════════════
            main_status.markdown("### 🔄 Adım 4/4: Vector store'a kaydediliyor...")
            step4_progress = st.progress(0)
            step4_status = st.empty()
            
            step4_status.text("🔧 ChromaDB başlatılıyor...")
            step4_progress.progress(0.2)
            client = create_chroma_client()
            
            step4_status.text("📦 Collection oluşturuluyor...")
            step4_progress.progress(0.4)
            collection = create_or_reset_collection(client, COLLECTION_NAME)
            
            step4_status.text("💾 Veriler kaydediliyor...")
            step4_progress.progress(0.6)
            add_documents_to_collection(collection, documents, embeddings, texts)
            
            step4_progress.progress(1.0)
            step4_status.empty()
            step4_progress.empty()
            st.success("✅ Adım 4 tamamlandı: Vector store hazır")
            main_progress.progress(1.0)
            
            # Session state'e kaydet
            st.session_state['collection'] = collection
            st.session_state['embedding_model'] = embedding_model
            st.session_state['documents'] = documents
            
            time.sleep(0.5)
            
            # Ana progress temizle
            main_progress.empty()
            main_status.empty()
            
            # Başarı mesajı
            st.success("🎉 Tüm adımlar başarıyla tamamlandı!")
            st.info("📊 Sistem hazır! Aşağıdan chatbot'a soru sorabilirsiniz.")
            
        except Exception as e:
            st.error(f"❌ Hata oluştu: {str(e)}")
            st.info("💡 Lütfen sayfayı yenileyin ve tekrar deneyin.")