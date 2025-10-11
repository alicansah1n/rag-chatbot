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

def render_statistical_summary(df: pd.DataFrame, numeric_cols: list, categorical_cols: list):
    """
    İstatistiksel özet tabını render eder.
    
    Args:
        df: Pandas DataFrame
        numeric_cols: Sayısal sütunlar
        categorical_cols: Kategorik sütunlar
    """
    st.subheader("📊 İstatistiksel Özet")
    
    # Sayısal sütunlar
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
    Korelasyon analizi tabını render eder.
    
    Args:
        df: Pandas DataFrame
        numeric_cols: Sayısal sütunlar
    """
    st.subheader("🔗 Korelasyon Analizi")
    
    if len(numeric_cols) >= 2:
        corr_matrix = df[numeric_cols].corr()
        
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(
            corr_matrix, 
            annot=True, 
            fmt='.2f', 
            cmap='coolwarm', 
            center=0,
            square=True,
            linewidths=1,
            cbar_kws={"shrink": 0.8},
            ax=ax
        )
        plt.title('Korelasyon Matrisi', fontsize=16, pad=20)
        plt.tight_layout()
        st.pyplot(fig)
        
        st.write("### 🔍 En Güçlü Korelasyonlar")
        
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
        
        with st.expander("ℹ️ Korelasyon Nasıl Yorumlanır?"):
            st.write("""
            **Korelasyon Katsayısı (-1 ile +1 arası):**
            - **+1.0**: Mükemmel pozitif ilişki
            - **0.7 - 1.0**: Çok güçlü pozitif
            - **0.5 - 0.7**: Güçlü pozitif
            - **0.3 - 0.5**: Orta pozitif
            - **0.0 - 0.3**: Zayıf/Yok
            - **-1.0**: Mükemmel negatif ilişki
            """)
    else:
        st.warning("⚠️ Korelasyon analizi için en az 2 sayısal sütun gerekli.")


def render_visualizations(df: pd.DataFrame, numeric_cols: list, categorical_cols: list):
    """
    Görselleştirmeler tabını render eder.
    
    Args:
        df: Pandas DataFrame
        numeric_cols: Sayısal sütunlar
        categorical_cols: Kategorik sütunlar
    """
    st.subheader("📉 Görselleştirmeler")
    
    if len(numeric_cols) > 0:
        viz_type = st.selectbox(
            "Grafik türü seçin:",
            ["Histogram", "Box Plot", "Scatter Plot", "Bar Chart (Kategorik)"],
            key="viz_type"
        )
        
        if viz_type == "Histogram":
            selected_col = st.selectbox("Sütun seçin:", numeric_cols, key="hist_col")
            bins = st.slider("Bin sayısı:", 10, 100, 30)
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.hist(df[selected_col].dropna(), bins=bins, edgecolor='black', alpha=0.7)
            ax.set_xlabel(selected_col, fontsize=12)
            ax.set_ylabel('Frekans', fontsize=12)
            ax.set_title(f'{selected_col} Dağılımı', fontsize=14)
            ax.grid(axis='y', alpha=0.3)
            st.pyplot(fig)
        
        elif viz_type == "Box Plot":
            selected_col = st.selectbox("Sütun seçin:", numeric_cols, key="box_col")
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.boxplot(df[selected_col].dropna(), vert=True)
            ax.set_ylabel(selected_col, fontsize=12)
            ax.set_title(f'{selected_col} Box Plot', fontsize=14)
            ax.grid(axis='y', alpha=0.3)
            st.pyplot(fig)
        
        elif viz_type == "Scatter Plot":
            if len(numeric_cols) >= 2:
                col1, col2 = st.columns(2)
                with col1:
                    x_col = st.selectbox("X ekseni:", numeric_cols, key="scatter_x")
                with col2:
                    y_col = st.selectbox("Y ekseni:", numeric_cols, key="scatter_y")
                
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.scatter(df[x_col], df[y_col], alpha=0.5)
                ax.set_xlabel(x_col, fontsize=12)
                ax.set_ylabel(y_col, fontsize=12)
                ax.set_title(f'{x_col} vs {y_col}', fontsize=14)
                ax.grid(alpha=0.3)
                st.pyplot(fig)
            else:
                st.warning("Scatter plot için en az 2 sayısal sütun gerekli.")
        
        elif viz_type == "Bar Chart (Kategorik)":
            if len(categorical_cols) > 0:
                selected_cat = st.selectbox("Kategorik sütun:", categorical_cols, key="bar_cat")
                value_counts = df[selected_cat].value_counts().head(10)
                
                fig, ax = plt.subplots(figsize=(10, 6))
                value_counts.plot(kind='bar', ax=ax, edgecolor='black')
                ax.set_xlabel(selected_cat, fontsize=12)
                ax.set_ylabel('Frekans', fontsize=12)
                ax.set_title(f'{selected_cat} Dağılımı (İlk 10)', fontsize=14)
                ax.grid(axis='y', alpha=0.3)
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.warning("Bar chart için kategorik sütun bulunamadı.")
    else:
        st.warning("⚠️ Görselleştirme için sayısal sütun gerekli.")


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
    
    if st.button("🤖 Analiz Et", type="primary", key="ai_insights"):
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