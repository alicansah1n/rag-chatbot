"""
RAG işleme bileşeni - Embedding ve Vector Store hazırlığı
"""
import streamlit as st
import time
import pandas as pd
from utils.data_loader import prepare_documents, get_column_types
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


def calculate_dataset_statistics(df: pd.DataFrame) -> dict:
    """
    Veri setinin istatistiklerini önceden hesaplar.
    
    Args:
        df: Pandas DataFrame
        
    Returns:
        dict: Hesaplanmış tüm istatistikler
    """
    numeric_cols, categorical_cols = get_column_types(df)
    
    stats = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'numeric_columns': numeric_cols,
        'categorical_columns': categorical_cols,
        'numeric_stats': {},
        'categorical_stats': {}
    }
    
    # Sayısal sütunlar için istatistikler
    for col in numeric_cols:
        stats['numeric_stats'][col] = {
            'mean': float(df[col].mean()),
            'median': float(df[col].median()),
            'std': float(df[col].std()),
            'min': float(df[col].min()),
            'max': float(df[col].max()),
            'q1': float(df[col].quantile(0.25)),
            'q3': float(df[col].quantile(0.75)),
            'missing': int(df[col].isna().sum()),
            'missing_pct': float(df[col].isna().sum() / len(df) * 100)
        }
    
    # Kategorik sütunlar için istatistikler
    for col in categorical_cols:
        value_counts = df[col].value_counts()
        stats['categorical_stats'][col] = {
            'unique_count': int(df[col].nunique()),
            'most_common': str(value_counts.index[0]) if len(value_counts) > 0 else None,
            'most_common_count': int(value_counts.iloc[0]) if len(value_counts) > 0 else 0,
            'most_common_pct': float(value_counts.iloc[0] / len(df) * 100) if len(value_counts) > 0 else 0,
            'distribution': {str(k): int(v) for k, v in value_counts.head(10).items()},
            'missing': int(df[col].isna().sum()),
            'missing_pct': float(df[col].isna().sum() / len(df) * 100)
        }
    
    return stats


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
            # ADIM 0: İSTATİSTİK HESAPLAMA (YENİ!)
            # ═══════════════════════════════════════
            main_status.markdown("### 🔄 Adım 0/5: İstatistikler hesaplanıyor...")
            step0_progress = st.progress(0)
            step0_status = st.empty()
            
            step0_status.text("📊 Veri seti analiz ediliyor...")
            step0_progress.progress(0.3)
            
            dataset_stats = calculate_dataset_statistics(df)
            
            step0_progress.progress(1.0)
            step0_status.empty()
            step0_progress.empty()
            st.success(f"✅ Adım 0 tamamlandı: {len(df):,} satır ve {len(df.columns)} sütun analiz edildi")
            main_progress.progress(0.15)
            
            time.sleep(0.3)
            
            # ═══════════════════════════════════════
            # ADIM 1/5: VERİ HAZIRLAMA
            # ═══════════════════════════════════════
            main_status.markdown("### 🔄 Adım 1/5: Veri hazırlanıyor...")
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
            main_progress.progress(0.30)
            
            with st.expander("🔍 Örnek Dökümanlar (İlk 3)"):
                for i in range(min(3, len(documents))):
                    st.code(documents[i]['text'][:200] + "...", language="text")
            
            time.sleep(0.3)
            
            # ═══════════════════════════════════════
            # ADIM 2/5: EMBEDDING MODEL YÜKLEME
            # ═══════════════════════════════════════
            main_status.markdown("### 🔄 Adım 2/5: Embedding modeli yükleniyor...")
            step2_progress = st.progress(0)
            step2_status = st.empty()
            
            step2_status.text("📥 Model indiriliyor...")
            step2_progress.progress(0.3)
            
            embedding_model = load_embedding_model(EMBEDDING_MODEL)
            
            step2_progress.progress(1.0)
            step2_status.empty()
            step2_progress.empty()
            st.success(f"✅ Adım 2 tamamlandı: Model yüklendi ({EMBEDDING_MODEL})")
            main_progress.progress(0.45)
            
            time.sleep(0.3)
            
            # ═══════════════════════════════════════
            # ADIM 3/5: EMBEDDING OLUŞTURMA
            # ═══════════════════════════════════════
            main_status.markdown("### 🔄 Adım 3/5: Embeddings oluşturuluyor...")
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
            main_progress.progress(0.70)
            
            time.sleep(0.3)
            
            # ═══════════════════════════════════════
            # ADIM 4/5: VECTOR STORE KAYDETME
            # ═══════════════════════════════════════
            main_status.markdown("### 🔄 Adım 4/5: Vector store'a kaydediliyor...")
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
            main_progress.progress(0.90)
            
            time.sleep(0.3)
            
            # ═══════════════════════════════════════
            # ADIM 5/5: SESSION STATE'E KAYDETME (YENİ!)
            # ═══════════════════════════════════════
            main_status.markdown("### 🔄 Adım 5/5: Sistem hazırlanıyor...")
            step5_progress = st.progress(0)
            step5_status = st.empty()
            
            step5_status.text("💾 Veriler hafızaya kaydediliyor...")
            step5_progress.progress(0.5)
            
            # Session state'e kaydet
            st.session_state['collection'] = collection
            st.session_state['embedding_model'] = embedding_model
            st.session_state['documents'] = documents
            st.session_state['dataset_stats'] = dataset_stats  # ← YENİ!
            st.session_state['dataframe'] = df  # ← YENİ! (Chatbot için)
            
            step5_progress.progress(1.0)
            step5_status.empty()
            step5_progress.empty()
            st.success("✅ Adım 5 tamamlandı: Tüm veriler hafızada")
            main_progress.progress(1.0)
            
            time.sleep(0.5)
            
            # Ana progress temizle
            main_progress.empty()
            main_status.empty()
            
            # Başarı mesajı
            st.success("🎉 Tüm adımlar başarıyla tamamlandı!")
            
            # İstatistik özeti göster
            with st.expander("📊 Hesaplanan İstatistikler Özeti"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("📊 Toplam Satır", f"{dataset_stats['total_rows']:,}")
                with col2:
                    st.metric("📁 Toplam Sütun", dataset_stats['total_columns'])
                with col3:
                    st.metric("🔢 Sayısal Sütun", len(dataset_stats['numeric_columns']))
                
                st.write("**✅ Chatbot artık tüm istatistiklere anında erişebilir!**")
            
            st.info("📊 Sistem hazır! Aşağıdan chatbot'a soru sorabilirsiniz.")
            
        except Exception as e:
            st.error(f"❌ Hata oluştu: {str(e)}")
            st.info("💡 Lütfen sayfayı yenileyin ve tekrar deneyin.")