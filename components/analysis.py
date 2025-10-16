"""
Veri analizi bileşenleri
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from dotenv import load_dotenv
from openai import OpenAI
from utils.data_loader import get_column_types, calculate_outliers
import numpy as np

def render_statistical_summary(df: pd.DataFrame, numeric_cols: list, categorical_cols: list):
    """
    İstatistiksel özet tabını render eder.
    
    Args:
        df: Pandas DataFrame
        numeric_cols: Sayısal sütunlar
        categorical_cols: Kategorik sütunlar
    """
    st.subheader("📊 İstatistiksel Özet")
    
    # Sayısal sütunları belirleyelim.
    if len(numeric_cols) > 0:
        st.write("### 🔢 Sayısal Sütunlar")
        st.dataframe(df[numeric_cols].describe().T, use_container_width=True)
        
        selected_col = st.selectbox(
            "Detaylı analiz için bir sütun seçin:",
            numeric_cols,
            key="stat_col"
        )
        
        if selected_col:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Ortalama", f"{df[selected_col].mean():.2f}")
            with col2:
                st.metric("Medyan", f"{df[selected_col].median():.2f}")
            with col3:
                st.metric("Std Sapma", f"{df[selected_col].std():.2f}")
            with col4:
                st.metric("Aralık", f"{df[selected_col].max() - df[selected_col].min():.2f}")
            
            q1 = df[selected_col].quantile(0.25)
            q2 = df[selected_col].quantile(0.50)
            q3 = df[selected_col].quantile(0.75)
            
            st.write("**Çeyreklik Değerler:**")
            st.write(f"Q1 (25%): {q1:.2f} | Q2 (50%): {q2:.2f} | Q3 (75%): {q3:.2f}")
            
            outliers, lower_bound, upper_bound = calculate_outliers(df, selected_col)
            
            if len(outliers) > 0:
                st.warning(f"⚠️ **{len(outliers)} aykırı değer tespit edildi!**")
                with st.expander("Aykırı değerleri göster"):
                    st.dataframe(outliers[[selected_col]], use_container_width=True)
            else:
                st.success("✅ Aykırı değer bulunamadı")
    else:
        st.info("ℹ️ Veri setinde sayısal sütun bulunamadı.")
    
    # Kategorik sütunlar
    if len(categorical_cols) > 0:
        st.write("### 🏷️ Kategorik Sütunlar")
        
        selected_cat = st.selectbox(
            "Bir kategorik sütun seçin:",
            categorical_cols,
            key="cat_col"
        )
        
        if selected_cat:
            value_counts = df[selected_cat].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Dağılım:**")
                for value, count in value_counts.items():
                    percentage = (count / len(df)) * 100
                    st.write(f"• {value}: {count:,} (%{percentage:.1f})")
            
            with col2:
                st.write("**İstatistikler:**")
                st.metric("Benzersiz Değer", df[selected_cat].nunique())
                st.metric("En Sık Değer", value_counts.index[0])
                st.metric("Frekans", f"{value_counts.iloc[0]:,}")


def render_correlation_analysis(df: pd.DataFrame, numeric_cols: list):
    """
    Gelişmiş korelasyon analizi tabını render eder.
    
    Args:
        df: Pandas DataFrame
        numeric_cols: Sayısal sütunlar
    """
    st.subheader("🔗 Korelasyon Analizi")
    
    if len(numeric_cols) >= 2:
        
        # ═══════════════════════════════════════
        # AYARLAR PANELİ
        # ═══════════════════════════════════════
        st.write("### ⚙️ Görselleştirme Ayarları")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            show_values = st.checkbox("Değerleri göster", value=True, key="corr_show_values")
        
        with col2:
            threshold = st.slider(
                "Minimum korelasyon eşiği:", 
                0.0, 1.0, 0.0, 0.05,
                key="corr_threshold",
                help="Bu değerin altındaki korelasyonlar gizlenir"
            )
        
        with col3:
            matrix_style = st.selectbox(
                "Matris stili:",
                ["Tam Matris", "Alt Üçgen", "Sadece Güçlü Korelasyonlar"],
                key="corr_style"
            )
        
        st.divider()
        
        # ═══════════════════════════════════════
        # KORELASYON MATRİSİ HESAPLAMA
        # ═══════════════════════════════════════
        corr_matrix = df[numeric_cols].corr()
        
        # ═══════════════════════════════════════
        # DİNAMİK BOYUT HESAPLAMA
        # ═══════════════════════════════════════
        n_cols = len(numeric_cols)
        
        # Her sütun için 1.5 inch, minimum 10, maksimum 20
        fig_width = min(max(10, n_cols * 1.5), 20)
        fig_height = min(max(8, n_cols * 1.2), 18)
        
        # ═══════════════════════════════════════
        # MASK OLUŞTURMA
        # ═══════════════════════════════════════
        mask = None
        
        if matrix_style == "Alt Üçgen":
            # Üst üçgeni gizle (simetrik olduğu için)
            mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        
        elif matrix_style == "Sadece Güçlü Korelasyonlar":
        # Eşiğin altındakileri gizle
            mask = np.abs(corr_matrix.values) < threshold  # ← .values ekle
        # Köşegeni de gizle (kendisiyle korelasyon = 1)
            np.fill_diagonal(mask, True)
        
        # ═══════════════════════════════════════
        # HEATMAP ÇİZİMİ
        # ═══════════════════════════════════════
        st.write("### 🎨 Korelasyon Matrisi")
        
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        
        # Font boyutunu sütun sayısına göre ayarla
        annot_fontsize = max(8, 14 - n_cols)
        
        sns.heatmap(
            corr_matrix,
            annot=show_values,
            fmt='.2f',
            cmap='coolwarm',
            center=0,
            square=True,
            linewidths=0.5,
            cbar_kws={"shrink": 0.8, "label": "Korelasyon Katsayısı"},
            mask=mask,
            ax=ax,
            annot_kws={"size": annot_fontsize}
        )
        
        plt.title(
            'Korelasyon Matrisi', 
            fontsize=16, 
            fontweight='bold', 
            pad=20
        )
        plt.xlabel('')
        plt.ylabel('')
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        
        st.pyplot(fig)
        plt.close()
        
        # İstatistik bilgisi
        total_pairs = (n_cols * (n_cols - 1)) // 2
        strong_corr = np.sum(np.abs(corr_matrix.values[np.triu_indices_from(corr_matrix.values, k=1)]) > 0.5)
        
        st.info(
            f"📊 **Toplam {total_pairs} korelasyon çifti** var. "
            f"**{strong_corr} tanesi** güçlü (|r| > 0.5)"
        )
        
        # ═══════════════════════════════════════
        # EN GÜÇLÜ KORELASYONLAR
        # ═══════════════════════════════════════
        st.divider()
        st.write("### 🔍 En Güçlü Korelasyonlar")
        
        # Korelasyon çiftlerini oluştur
        corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_pairs.append({
                    'Değişken 1': corr_matrix.columns[i],
                    'Değişken 2': corr_matrix.columns[j],
                    'Korelasyon': corr_matrix.iloc[i, j]
                })
        
        corr_df = pd.DataFrame(corr_pairs)
        corr_df['Mutlak'] = corr_df['Korelasyon'].abs()
        corr_df = corr_df.sort_values('Mutlak', ascending=False)
        
        # En güçlü 5 korelasyon
        for idx, row in corr_df.head(5).iterrows():
            corr_value = row['Korelasyon']
            
            if abs(corr_value) > 0.7:
                strength, emoji = "Çok Güçlü", "🔴"
            elif abs(corr_value) > 0.5:
                strength, emoji = "Güçlü", "🟠"
            elif abs(corr_value) > 0.3:
                strength, emoji = "Orta", "🟡"
            else:
                strength, emoji = "Zayıf", "🟢"
            
            direction = "pozitif" if corr_value > 0 else "negatif"
            st.write(
                f"{emoji} **{row['Değişken 1']}** ↔ **{row['Değişken 2']}**: "
                f"{corr_value:.3f} ({strength} {direction})"
            )
        
        # ═══════════════════════════════════════
        # BİLGİLENDİRME
        # ═══════════════════════════════════════
        with st.expander("ℹ️ Korelasyon Nasıl Yorumlanır?"):
            st.write("""
            **Korelasyon Katsayısı (Pearson r):**
            
            **Değer Aralığı:**
            - **+1.0**: Mükemmel pozitif ilişki (biri artarsa diğeri de artar)
            - **+0.7 - +1.0**: Çok güçlü pozitif
            - **+0.5 - +0.7**: Güçlü pozitif
            - **+0.3 - +0.5**: Orta pozitif
            - **0.0 - +0.3**: Zayıf pozitif / İlişki yok
            - **-0.3 - 0.0**: Zayıf negatif
            - **-0.5 - -0.3**: Orta negatif
            - **-0.7 - -0.5**: Güçlü negatif
            - **-1.0 - -0.7**: Çok güçlü negatif
            - **-1.0**: Mükemmel negatif ilişki (biri artarsa diğeri azalır)
            
            **Önemli Notlar:**
            - Korelasyon ≠ Nedensellik! (Correlation ≠ Causation)
            - Sadece doğrusal ilişkileri ölçer
            - Outlier'lar sonucu etkileyebilir
            """)
        # ═══════════════════════════════════════
        # AI FEATURE IMPORTANCE ANALİZİ
        # ═══════════════════════════════════════
        st.divider()
        st.write("### 🤖 AI-Powered Feature Importance")
        st.write("GPT, en önemli değişkenleri ve ilişkileri analiz eder.")

        if st.button("🧠 Feature Importance Analizi Yap", type="primary", key="feat_importance"):
            with st.spinner("🔍 Korelasyon matrisi analiz ediliyor..."):
                
                load_dotenv()
                api_key = os.getenv("OPENAI_API_KEY")
                
                if not api_key or api_key == "your_api_key_here":
                    st.error("⚠️ OpenAI API key bulunamadı!")
                else:
                    try:
                        
                        client = OpenAI(api_key=api_key)
                        
                        # En güçlü korelasyonları özet olarak hazırla
                        top_corr_summary = "\n".join([
                            f"- {row['Değişken 1']} ↔ {row['Değişken 2']}: {row['Korelasyon']:.3f}"
                            for _, row in corr_df.head(10).iterrows()
                        ])
                        
                        # Ortalama korelasyonları hesapla (her değişkenin genel önemi)
                        avg_corr = corr_matrix.abs().mean().sort_values(ascending=False)
                        importance_summary = "\n".join([
                            f"- {col}: Ortalama korelasyon = {val:.3f}"
                            for col, val in avg_corr.items()
                        ])
                        
                        prompt = f"""
Sen bir veri bilimcisisin. Aşağıdaki korelasyon analizini değerlendir:

**VERİ SETİ:**
- Değişkenler: {', '.join(numeric_cols)}
- Toplam {len(numeric_cols)} sayısal değişken

**EN GÜÇLÜ KORELASYONLAR (İlk 10):**
{top_corr_summary}

**DEĞİŞKEN ÖNEMLİLİK SIRALAMAS (Ortalama Mutlak Korelasyon):**
{importance_summary}

**GÖREV:**
1. **En önemli 3 değişkeni** belirle ve neden önemli olduklarını
2. **Dikkat edilmesi gereken güçlü ilişkileri** (pozitif/negatif) belirt 
3. **Multicollinearity (çoklu bağlantı)** riski var mı? Hangi değişkenler arasında?
4. **Feature selection** için öneriler ver (hangi değişkenler çıkarılabilir?)
5. **İş/bilim açısından** bu korelasyonlar ne anlama geliyor?

Yanıtını Türkçe, madde madde ve net bir şekilde ver.
"""
                        
                        response = client.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {
                                    "role": "system",
                                    "content": "Sen profesyonel bir veri bilimcisisin. Feature importance ve korelasyon analizi konusunda uzmansın."
                                },
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ],
                            temperature=0.7,
                            max_tokens=1200
                        )
                        
                        analysis = response.choices[0].message.content
                        
                        st.success("✅ Analiz tamamlandı!")
                        st.markdown(analysis)
                        
                        # İndirme butonu
                        st.download_button(
                            label="📥 Feature Importance Raporunu İndir",
                            data=analysis,
                            file_name="feature_importance_analysis.txt",
                            mime="text/plain",
                            key="download_feat_importance"
                        )
                        
                    except Exception as e:
                        st.error(f"❌ Hata oluştu: {str(e)}")
        

    
    else:
        st.warning("⚠️ Korelasyon analizi için en az 2 sayısal sütun gerekli.")


def get_recommended_charts(df: pd.DataFrame, numeric_cols: list, categorical_cols: list) -> dict:
    """
    Veri setine göre önerilen grafikleri belirler.
    
    Returns:
        dict: {chart_name: (enabled, reason)}
    """
    recommendations = {}
    
    # Histogram
    recommendations["Histogram"] = (
        len(numeric_cols) > 0,
        "Sayısal değişkenlerin dağılımını gösterir"
    )
    
    # Box Plot
    recommendations["Box Plot"] = (
        len(numeric_cols) > 0,
        "Aykırı değerleri ve çeyrekleri gösterir"
    )
    
    # Violin Plot
    recommendations["Violin Plot"] = (
        len(numeric_cols) > 0 and len(df) > 30,
        "Dağılım + box plot birleşimi (30+ satır gerekli)"
    )
    
    # KDE Plot
    recommendations["KDE Plot"] = (
        len(numeric_cols) > 0 and len(df) > 50,
        "Smooth dağılım eğrisi (50+ satır gerekli)"
    )
    
    # Scatter Plot
    recommendations["Scatter Plot"] = (
        len(numeric_cols) >= 2,
        "İki sayısal değişken arası ilişki"
    )
    
    # Pair Plot
    recommendations["Pair Plot (Scatter Matrix)"] = (
        len(numeric_cols) >= 2 and len(numeric_cols) <= 6 and len(df) <= 1000,
        "Tüm sayısal değişken çiftleri (max 6 sütun, 1000 satır)"
    )
    
    # Count Plot
    recommendations["Count Plot"] = (
        len(categorical_cols) > 0,
        "Kategorik değerlerin frekansı"
    )
    
    # Grouped Bar Chart
    recommendations["Grouped Bar Chart"] = (
        len(categorical_cols) > 0 and len(numeric_cols) > 0,
        "Kategorilere göre sayısal değişken ortalaması"
    )
    
    # Pie Chart
    recommendations["Pie Chart"] = (
        len(categorical_cols) > 0,
        "Kategori yüzde dağılımı (max 7 kategori önerilir)"
    )
    
    # Heatmap (Numeric)
    recommendations["Heatmap (Pivot Table)"] = (
        len(categorical_cols) >= 2 and len(numeric_cols) > 0,
        "İki kategoriye göre sayısal değerin heatmap'i"
    )
    
    return recommendations


def render_visualizations(df: pd.DataFrame, numeric_cols: list, categorical_cols: list):
    """
    Gelişmiş görselleştirmeler tabını render eder.
    
    Args:
        df: Pandas DataFrame
        numeric_cols: Sayısal sütunlar
        categorical_cols: Kategorik sütunlar
    """
    st.subheader("📉 Görselleştirmeler")
    
    # Akıllı öneri sistemi
    recommendations = get_recommended_charts(df, numeric_cols, categorical_cols)
    
    # Önerilen grafikleri göster
    with st.expander("💡 Bu Veri Seti İçin Önerilen Grafikler"):
        recommended = [name for name, (enabled, _) in recommendations.items() if enabled]
        if recommended:
            st.success(f"✅ **{len(recommended)} grafik** kullanılabilir:")
            for chart in recommended:
                reason = recommendations[chart][1]
                st.write(f"• **{chart}**: {reason}")
        else:
            st.warning("⚠️ Bu veri seti için uygun grafik bulunamadı.")
    
    # Dropdown - sadece uygun olanlar
    available_charts = [name for name, (enabled, _) in recommendations.items() if enabled]
    
    if not available_charts:
        st.error("❌ Görselleştirme için uygun veri bulunamadı.")
        return
    
    viz_type = st.selectbox(
        "📊 Grafik türü seçin:",
        available_charts,
        key="viz_type",
        help="Sadece veri setinize uygun grafikler gösteriliyor"
    )
    
    st.divider()
    
    # ═══════════════════════════════════════
    # GRAFİK RENDERİNG
    # ═══════════════════════════════════════
    
    if viz_type == "Histogram":
        render_histogram(df, numeric_cols)
    
    elif viz_type == "Box Plot":
        render_boxplot(df, numeric_cols)
    
    elif viz_type == "Violin Plot":
        render_violinplot(df, numeric_cols)
    
    elif viz_type == "KDE Plot":
        render_kdeplot(df, numeric_cols)
    
    elif viz_type == "Scatter Plot":
        render_scatterplot(df, numeric_cols)
    
    elif viz_type == "Pair Plot (Scatter Matrix)":
        render_pairplot(df, numeric_cols)
    
    elif viz_type == "Count Plot":
        render_countplot(df, categorical_cols)
    
    elif viz_type == "Grouped Bar Chart":
        render_grouped_bar(df, categorical_cols, numeric_cols)
    
    elif viz_type == "Pie Chart":
        render_piechart(df, categorical_cols)
    
    elif viz_type == "Heatmap (Pivot Table)":
        render_heatmap_pivot(df, categorical_cols, numeric_cols)


# ═══════════════════════════════════════════════════════
# AI ANALİZ FONKSİYONU - MERKEZI
# ═══════════════════════════════════════════════════════

def analyze_chart_with_ai(chart_type: str, column: str, data_summary: str, extra_info: str = ""):
    """
    Herhangi bir grafik için AI analizi yapar.
    
    Args:
        chart_type: Grafik türü (Histogram, Box Plot, vb.)
        column: Ana sütun adı
        data_summary: Veri özeti
        extra_info: Ekstra bilgi
    """
    with st.spinner("🤔 Grafik analiz ediliyor..."):
        load_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key or api_key == "your_api_key_here":
            st.error("⚠️ OpenAI API key bulunamadı!")
            return
        
        try:
            client = OpenAI(api_key=api_key)
            
            prompt = f"""
Sen bir veri analisti asistanısın. Kullanıcıya {chart_type} grafiğini kısa ve öz açıkla.

**GRAFİK TİPİ:** {chart_type}
**SÜTUN/VERİ:** {column}
**VERİ ÖZETİ:**
{data_summary}
{extra_info}

**GÖREV:**
Sadece şu formatı kullan:

📊 **Grafik Yorumu:**
- [1 cümle: Bu grafikte ne görüyoruz?]
- [1 cümle: En önemli pattern/trend]

💡 **AI Önerisi:**
- [1 cümle: Aksiyon önerisi veya tahmin]

SADECE bu formatı kullan. Ekstra açıklama yapma.
"""
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Sen kısa, öz ve net açıklamalar yapan bir veri analistisin. Tam olarak istenen formatı kullanırsın."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=250
            )
            
            analysis = response.choices[0].message.content
            
            st.success("✅ Analiz tamamlandı!")
            st.markdown(analysis)
            
        except Exception as e:
            st.error(f"❌ Analiz hatası: {str(e)}")


# ═══════════════════════════════════════════════════════
# YARDIMCI FONKSİYONLAR - HER GRAFİK TİPİ İÇİN
# ═══════════════════════════════════════════════════════

def render_histogram(df: pd.DataFrame, numeric_cols: list):
    """Histogram grafiği"""
    selected_col = st.selectbox("Sütun seçin:", numeric_cols, key="hist_col")
    bins = st.slider("Bin sayısı:", 10, 100, 30, key="hist_bins")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df[selected_col].dropna(), bins=bins, edgecolor='black', alpha=0.7, color='steelblue')
    ax.set_xlabel(selected_col, fontsize=12, fontweight='bold')
    ax.set_ylabel('Frekans', fontsize=12, fontweight='bold')
    ax.set_title(f'{selected_col} Dağılımı', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
    
    # AI ANALİZ BUTONU
    st.divider()
    if st.button("🤖 AI ile Bu Grafiği Analiz Et", key=f"ai_hist_{selected_col}"):
        data_summary = f"""
- Ortalama: {df[selected_col].mean():.2f}
- Medyan: {df[selected_col].median():.2f}
- Standart Sapma: {df[selected_col].std():.2f}
- Min: {df[selected_col].min():.2f}
- Max: {df[selected_col].max():.2f}
- Bin sayısı: {bins}
"""
        analyze_chart_with_ai("Histogram", selected_col, data_summary)


def render_boxplot(df: pd.DataFrame, numeric_cols: list):
    """Box plot grafiği"""
    selected_col = st.selectbox("Sütun seçin:", numeric_cols, key="box_col")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bp = ax.boxplot(df[selected_col].dropna(), vert=True, patch_artist=True)
    bp['boxes'][0].set_facecolor('lightblue')
    ax.set_ylabel(selected_col, fontsize=12, fontweight='bold')
    ax.set_title(f'{selected_col} Box Plot', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
    
    # AI ANALİZ BUTONU
    st.divider()
    if st.button("🤖 AI ile Bu Grafiği Analiz Et", key=f"ai_box_{selected_col}"):
        q1, q2, q3 = df[selected_col].quantile([0.25, 0.5, 0.75])
        iqr = q3 - q1
        outliers = df[(df[selected_col] < q1-1.5*iqr) | (df[selected_col] > q3+1.5*iqr)]
        
        data_summary = f"""
- Medyan (Q2): {q2:.2f}
- Q1 (25%): {q1:.2f}
- Q3 (75%): {q3:.2f}
- IQR: {iqr:.2f}
- Aykırı değer sayısı: {len(outliers)}
- Aykırı değer oranı: %{len(outliers)/len(df)*100:.1f}
"""
        analyze_chart_with_ai("Box Plot", selected_col, data_summary)


def render_violinplot(df: pd.DataFrame, numeric_cols: list):
    """Violin plot grafiği"""
    selected_col = st.selectbox("Sütun seçin:", numeric_cols, key="violin_col")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    parts = ax.violinplot([df[selected_col].dropna()], vert=True, showmeans=True, showmedians=True)
    ax.set_ylabel(selected_col, fontsize=12, fontweight='bold')
    ax.set_title(f'{selected_col} Violin Plot', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
    
    # AI ANALİZ BUTONU
    st.divider()
    if st.button("🤖 AI ile Bu Grafiği Analiz Et", key=f"ai_violin_{selected_col}"):
        data_summary = f"""
- Ortalama: {df[selected_col].mean():.2f}
- Medyan: {df[selected_col].median():.2f}
- Skewness (çarpıklık): {df[selected_col].skew():.2f}
- Veri sayısı: {len(df[selected_col].dropna())}
"""
        analyze_chart_with_ai("Violin Plot", selected_col, data_summary)


def render_kdeplot(df: pd.DataFrame, numeric_cols: list):
    """KDE (Kernel Density) plot"""
    selected_col = st.selectbox("Sütun seçin:", numeric_cols, key="kde_col")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    df[selected_col].dropna().plot(kind='density', ax=ax, linewidth=2, color='darkblue')
    ax.set_xlabel(selected_col, fontsize=12, fontweight='bold')
    ax.set_ylabel('Yoğunluk', fontsize=12, fontweight='bold')
    ax.set_title(f'{selected_col} KDE Plot', fontsize=14, fontweight='bold')
    ax.grid(alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
    
    # AI ANALİZ BUTONU
    st.divider()
    if st.button("🤖 AI ile Bu Grafiği Analiz Et", key=f"ai_kde_{selected_col}"):
        data_summary = f"""
- Ortalama: {df[selected_col].mean():.2f}
- Medyan: {df[selected_col].median():.2f}
- Mod (en sık değer): {df[selected_col].mode().values[0] if len(df[selected_col].mode()) > 0 else 'N/A'}
- Dağılım tipi: Smooth density curve
"""
        analyze_chart_with_ai("KDE Plot", selected_col, data_summary)


def render_scatterplot(df: pd.DataFrame, numeric_cols: list):
    """Scatter plot"""
    col1, col2 = st.columns(2)
    with col1:
        x_col = st.selectbox("X ekseni:", numeric_cols, key="scatter_x")
    with col2:
        y_col = st.selectbox("Y ekseni:", numeric_cols, key="scatter_y")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(df[x_col], df[y_col], alpha=0.6, s=50, color='steelblue', edgecolors='black', linewidth=0.5)
    ax.set_xlabel(x_col, fontsize=12, fontweight='bold')
    ax.set_ylabel(y_col, fontsize=12, fontweight='bold')
    ax.set_title(f'{x_col} vs {y_col}', fontsize=14, fontweight='bold')
    ax.grid(alpha=0.3)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
    
    # AI ANALİZ BUTONU
    st.divider()
    if st.button("🤖 AI ile Bu Grafiği Analiz Et", key=f"ai_scatter_{x_col}_{y_col}"):
        correlation = df[[x_col, y_col]].corr().iloc[0, 1]
        data_summary = f"""
- X değişkeni ({x_col}): Ort={df[x_col].mean():.2f}
- Y değişkeni ({y_col}): Ort={df[y_col].mean():.2f}
- Korelasyon: {correlation:.3f}
- İlişki yönü: {'Pozitif' if correlation > 0 else 'Negatif'}
- İlişki gücü: {'Güçlü' if abs(correlation) > 0.7 else 'Orta' if abs(correlation) > 0.3 else 'Zayıf'}
"""
        analyze_chart_with_ai("Scatter Plot", f"{x_col} vs {y_col}", data_summary)


def render_pairplot(df: pd.DataFrame, numeric_cols: list):
    """Pair plot (scatter matrix)"""
    st.info("📊 Tüm sayısal sütunlar arası scatter plot matrix oluşturuluyor...")
    
    # En fazla 6 sütun al (performans için)
    cols_to_plot = numeric_cols[:6]
    
    fig = sns.pairplot(df[cols_to_plot].dropna(), diag_kind='kde', plot_kws={'alpha': 0.6})
    fig.fig.suptitle('Pair Plot - Tüm Değişken İlişkileri', y=1.02, fontsize=14, fontweight='bold')
    st.pyplot(fig)
    plt.close()
    
    # AI ANALİZ BUTONU
    st.divider()
    if st.button("🤖 AI ile Bu Grafiği Analiz Et", key="ai_pairplot"):
        corr_matrix = df[cols_to_plot].corr()
        max_corr = corr_matrix.abs().unstack().sort_values(ascending=False).drop_duplicates()
        max_corr = max_corr[max_corr < 1.0].head(1)
        
        data_summary = f"""
- Analiz edilen değişkenler: {', '.join(cols_to_plot)}
- Toplam grafik sayısı: {len(cols_to_plot) * len(cols_to_plot)}
- En güçlü korelasyon: {max_corr.values[0]:.3f} ({max_corr.index[0][0]} vs {max_corr.index[0][1]})
"""
        analyze_chart_with_ai("Pair Plot (Scatter Matrix)", "Tüm değişkenler", data_summary)


def render_countplot(df: pd.DataFrame, categorical_cols: list):
    """Count plot (kategorik frekans)"""
    selected_cat = st.selectbox("Kategorik sütun:", categorical_cols, key="count_cat")
    max_categories = st.slider("Maksimum kategori sayısı:", 5, 20, 10, key="count_max")
    
    value_counts = df[selected_cat].value_counts().head(max_categories)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    value_counts.plot(kind='bar', ax=ax, color='steelblue', edgecolor='black')
    ax.set_xlabel(selected_cat, fontsize=12, fontweight='bold')
    ax.set_ylabel('Frekans', fontsize=12, fontweight='bold')
    ax.set_title(f'{selected_cat} Dağılımı (İlk {max_categories})', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    # Değerleri barların üstüne yaz
    for i, v in enumerate(value_counts):
        ax.text(i, v + max(value_counts)*0.01, str(v), ha='center', fontweight='bold')
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
    
    # AI ANALİZ BUTONU
    st.divider()
    if st.button("🤖 AI ile Bu Grafiği Analiz Et", key=f"ai_count_{selected_cat}"):
        top_category = value_counts.index[0]
        top_count = value_counts.iloc[0]
        total = value_counts.sum()
        
        data_summary = f"""
- Toplam benzersiz kategori: {df[selected_cat].nunique()}
- En sık kategori: {top_category} ({top_count} kez, %{top_count/total*100:.1f})
- Gösterilen kategori sayısı: {len(value_counts)}
- Dağılım: {', '.join([f"{k}={v}" for k, v in value_counts.head(3).items()])}
"""
        analyze_chart_with_ai("Count Plot (Bar Chart)", selected_cat, data_summary)


def render_grouped_bar(df: pd.DataFrame, categorical_cols: list, numeric_cols: list):
    """Grouped bar chart"""
    col1, col2 = st.columns(2)
    with col1:
        cat_col = st.selectbox("Kategorik sütun:", categorical_cols, key="group_cat")
    with col2:
        num_col = st.selectbox("Sayısal sütun (ortalama):", numeric_cols, key="group_num")
    
    # Kategoriye göre ortalama hesapla
    grouped = df.groupby(cat_col)[num_col].mean().sort_values(ascending=False).head(10)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    grouped.plot(kind='bar', ax=ax, color='coral', edgecolor='black')
    ax.set_xlabel(cat_col, fontsize=12, fontweight='bold')
    ax.set_ylabel(f'{num_col} (Ortalama)', fontsize=12, fontweight='bold')
    ax.set_title(f'{cat_col} Kategorilerine Göre Ortalama {num_col}', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    # Değerleri barların üstüne yaz
    for i, v in enumerate(grouped):
        ax.text(i, v + max(grouped)*0.01, f'{v:.2f}', ha='center', fontweight='bold')
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
    
    # AI ANALİZ BUTONU
    st.divider()
    if st.button("🤖 AI ile Bu Grafiği Analiz Et", key=f"ai_grouped_{cat_col}_{num_col}"):
        highest_cat = grouped.index[0]
        highest_val = grouped.iloc[0]
        lowest_cat = grouped.index[-1]
        lowest_val = grouped.iloc[-1]
        
        data_summary = f"""
- Kategorik değişken: {cat_col}
- Sayısal değişken: {num_col} (ortalama)
- En yüksek: {highest_cat} = {highest_val:.2f}
- En düşük: {lowest_cat} = {lowest_val:.2f}
- Fark: {highest_val - lowest_val:.2f}
"""
        analyze_chart_with_ai("Grouped Bar Chart", f"{cat_col} vs {num_col}", data_summary)


def render_piechart(df: pd.DataFrame, categorical_cols: list):
    """Pie chart"""
    selected_cat = st.selectbox("Kategorik sütun:", categorical_cols, key="pie_cat")
    max_slices = st.slider("Maksimum dilim sayısı:", 3, 10, 7, key="pie_max")
    
    value_counts = df[selected_cat].value_counts().head(max_slices)
    
    fig, ax = plt.subplots(figsize=(10, 7))
    colors = plt.cm.Set3(range(len(value_counts)))
    wedges, texts, autotexts = ax.pie(
        value_counts, 
        labels=value_counts.index, 
        autopct='%1.1f%%',
        startangle=90,
        colors=colors,
        textprops={'fontsize': 11, 'fontweight': 'bold'}
    )
    ax.set_title(f'{selected_cat} Dağılımı', fontsize=14, fontweight='bold')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
    
    # AI ANALİZ BUTONU
    st.divider()
    if st.button("🤖 AI ile Bu Grafiği Analiz Et", key=f"ai_pie_{selected_cat}"):
        percentages = (value_counts / value_counts.sum() * 100).round(1)
        dominant = percentages.index[0]
        dominant_pct = percentages.iloc[0]
        
        data_summary = f"""
- Kategori: {selected_cat}
- Toplam dilim: {len(value_counts)}
- Dominant kategori: {dominant} (%{dominant_pct})
- Dağılım: {', '.join([f"{k}={v}%" for k, v in percentages.head(3).items()])}
"""
        analyze_chart_with_ai("Pie Chart", selected_cat, data_summary)


def render_heatmap_pivot(df: pd.DataFrame, categorical_cols: list, numeric_cols: list):
    """Heatmap with pivot table"""
    col1, col2, col3 = st.columns(3)
    with col1:
        cat1 = st.selectbox("Kategorik 1 (satır):", categorical_cols, key="heat_cat1")
    with col2:
        cat2 = st.selectbox("Kategorik 2 (sütun):", categorical_cols, key="heat_cat2")
    with col3:
        num = st.selectbox("Sayısal (değer):", numeric_cols, key="heat_num")
    
    # Aynı sütun kontrolü
    if cat1 == cat2:
        st.warning("⚠️ Lütfen farklı kategorik sütunlar seçin!")
        return
    
    # Pivot table oluştur
    try:
        pivot = df.pivot_table(values=num, index=cat1, columns=cat2, aggfunc='mean')
    except Exception as e:
        st.error(f"❌ Heatmap oluşturulamadı: {str(e)}")
        st.warning("💡 **Olası sebepler:**\n- Aynı kategorik sütun seçilmiş olabilir\n- Farklı kategorik sütunlar seçin")
        return  # ← BURASI DÜZELDİ (try-except içinde)
    
    # Boş kontrol
    if pivot.empty:
        st.warning("⚠️ Bu kombinasyon için veri bulunamadı.")
        return
    
    # İlk 10x10'a sınırla (görsellik için)
    pivot = pivot.iloc[:10, :10]
    
    fig, ax = plt.subplots(figsize=(10, 7))
    sns.heatmap(pivot, annot=True, fmt='.2f', cmap='YlOrRd', ax=ax, linewidths=0.5)
    ax.set_title(f'{cat1} vs {cat2} - Ortalama {num}', fontsize=14, fontweight='bold')
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
    
    # AI ANALİZ BUTONU
    st.divider()
    if st.button("🤖 AI ile Bu Grafiği Analiz Et", key=f"ai_heat_{cat1}_{cat2}_{num}"):
        max_val = pivot.max().max()
        min_val = pivot.min().min()
        max_idx = pivot.stack().idxmax()
        
        data_summary = f"""
- Satır: {cat1}, Sütun: {cat2}, Değer: {num}
- En yüksek değer: {max_val:.2f} ({max_idx[0]} - {max_idx[1]})
- En düşük değer: {min_val:.2f}
- Ortalama: {pivot.mean().mean():.2f}
"""
        analyze_chart_with_ai("Heatmap (Pivot Table)", f"{cat1} vs {cat2}", data_summary)
def render_ai_insights(df: pd.DataFrame, numeric_cols: list, categorical_cols: list):
    """
    AI içgörüler tabını render eder.
    
    Args:
        df: Pandas DataFrame
        numeric_cols: Sayısal sütunlar
        categorical_cols: Kategorik sütunlar
    """
    st.subheader("💡 AI-Powered İçgörüler")
    st.write("GPT, veri setinizi analiz ederek otomatik içgörüler ve öneriler üretir.")
    
    if st.button("Analiz Et", type="primary", key="ai_insights"):
        with st.spinner("🔍 Veri seti analiz ediliyor..."):
            load_dotenv()
            api_key = os.getenv("OPENAI_API_KEY")
            
            if not api_key or api_key == "your_api_key_here":
                st.error("⚠️ OpenAI API key bulunamadı!")
            else:
                try:
                    client = OpenAI(api_key=api_key)
                    
                    summary = f"""
Veri Seti Özeti:
- Toplam satır: {len(df):,}
- Sütunlar: {', '.join(df.columns.tolist())}
- Sayısal sütunlar: {', '.join(numeric_cols) if numeric_cols else 'Yok'}
- Kategorik sütunlar: {', '.join(categorical_cols) if categorical_cols else 'Yok'}

Sayısal İstatistikler:
{df[numeric_cols].describe().to_string() if len(numeric_cols) > 0 else 'Yok'}

İlk 5 Satır:
{df.head(5).to_string()}
"""
                    
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system",
                                "content": "Sen profesyonel bir veri analisti asistanısın. Yanıtlarını Türkçe ver."
                            },
                            {
                                "role": "user",
                                "content": f"""Veri setini analiz et:

1. En önemli 5 içgörüyü belirle
2. İş/bilim açısından ne anlama geldiğini açıkla
3. 3 actionable öneri sun
4. Dikkat edilmesi gereken noktaları belirt
5- Açıklamalar kısa ve net olsun.
6- Yanıtı madde madde ver.
{summary}"""
                            }
                        ],
                        temperature=0.7,
                        max_tokens=1000
                    )
                    
                    insights = response.choices[0].message.content
                    st.success("✅ Analiz tamamlandı!")
                    st.markdown(insights)
                    
                    st.download_button(
                        label="📥 İçgörüleri İndir (TXT)",
                        data=insights,
                        file_name="ai_insights.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"❌ Hata: {str(e)}")
    else:
        st.info("👆 Butona tıklayarak analiz başlatın.")


def render_data_analysis(df: pd.DataFrame):
    """
    Ana veri analizi bölümünü render eder.
    
    Args:
        df: Pandas DataFrame
    """
    st.divider()
    st.header("📈 Veri Analizi")
    st.write("Veri setinizi detaylı olarak analiz edin ve içgörüler keşfedin.")
    
    numeric_cols, categorical_cols = get_column_types(df)
    
    tabs = st.tabs([
        "📊 İstatistiksel Özet",
        "🔗 Korelasyon Analizi",
        "📉 Görselleştirmeler",
        "💡 AI İçgörüler"
    ])
    
    with tabs[0]:
        render_statistical_summary(df, numeric_cols, categorical_cols)
    
    with tabs[1]:
        render_correlation_analysis(df, numeric_cols)
    
    with tabs[2]:
        render_visualizations(df, numeric_cols, categorical_cols)
    
    with tabs[3]:
        render_ai_insights(df, numeric_cols, categorical_cols)