"""
E-Ticaret Müşteri Segmentasyonu ve CLV Dashboard'u
RFM Analizi + BG/NBD & Gamma-Gamma CLV Modeli

Çalıştırmak için:
    pip install streamlit pandas plotly
    streamlit run dashboard.py

Girdi dosyası: rfm_clv_final_with_type.csv (script ile aynı klasörde olmalı)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ============================================
# SAYFA AYARLARI
# ============================================
st.set_page_config(
    page_title="E-Ticaret CLV & Segmentasyon Dashboard",
    page_icon="📊",
    layout="wide"
)

SEGMENT_COLORS = {
    'Champions': '#2E7D32', 'Loyal Customers': '#66BB6A',
    'Need Attention': '#FFA726', 'At Risk': '#EF5350',
    'New Customers': '#42A5F5', 'Hibernating': '#9E9E9E'
}

SEGMENT_STRATEGY = {
    'Champions': {
        'amac': 'Elde tut, savun, marka elçisine dönüştür',
        'kanal': 'E-posta (VIP), doğrudan hesap yöneticisi',
        'kampanya': 'Erken erişim/özel lansmanlar, sadakat programı, yıl dönümü teklifleri, referral programı',
        'kacinilmasi_gereken': 'Genel/kitlesel indirim e-postaları — marj eritir',
        'butce_onceligi': 'Orta'
    },
    'Loyal Customers': {
        'amac': "Champions'a terfi ettir",
        'kanal': 'E-posta otomasyonu, retargeting',
        'kampanya': 'Cross-sell/upsell önerileri, bundle kampanyaları, ücretsiz kargo eşiği',
        'kacinilmasi_gereken': 'Segmenti Champions ile aynı muameleyle karıştırmak',
        'butce_onceligi': 'Orta-Yüksek'
    },
    'New Customers': {
        'amac': 'İkinci alışverişi tetikle',
        'kanal': 'Otomatik onboarding e-posta serisi, sosyal retargeting',
        'kampanya': "'Hoş geldin' serisi, kullanım ipuçları, ikinci siparişe özel indirim",
        'kacinilmasi_gereken': 'Onboarding sürecini atlamak',
        'butce_onceligi': 'Yüksek'
    },
    'Need Attention': {
        'amac': "Hibernating'e kaymayı önle, yukarı it",
        'kanal': 'E-posta, düşük maliyetli retargeting',
        'kampanya': "'Sizi özledik' hatırlatmaları, sınırlı süreli düşük maliyetli indirim",
        'kacinilmasi_gereken': 'Yüksek maliyetli kanallara bütçe ayırmak',
        'butce_onceligi': 'Düşük-Orta'
    },
    'At Risk': {
        'amac': 'Acil win-back — yüksek değerli, kaybedilme riski yüksek',
        'kanal': 'Kişiselleştirilmiş e-posta + doğrudan temas',
        'kampanya': 'Agresif geri kazanım indirimi, churn nedeni anketi, VIP destek hattı',
        'kacinilmasi_gereken': 'Bu segmenti Need Attention ile aynı düşük öncelikte görmek',
        'butce_onceligi': 'Yüksek (öncelikli)'
    },
    'Hibernating': {
        'amac': 'Düşük maliyetli son deneme',
        'kanal': 'Yalnızca otomatik/ücretsiz e-posta',
        'kampanya': "Tek seferlik 'hoş geldin geri' e-postası, liste temizliği",
        'kacinilmasi_gereken': 'Ücretli reklam bütçesi ayırmak',
        'butce_onceligi': 'Çok Düşük'
    }
}


# ============================================
# VERİ YÜKLEME
# ============================================
@st.cache_data
def load_data():
    df = pd.read_csv('rfm_clv_final_with_type.csv')
    return df


try:
    df = load_data()
except FileNotFoundError:
    st.error(
        "⚠️ 'rfm_clv_final_with_type.csv' dosyası bulunamadı. "
        "Bu dosyayı dashboard.py ile aynı klasöre koyduğundan emin ol."
    )
    st.stop()

# ============================================
# BAŞLIK
# ============================================
st.title("📊 E-Ticaret Müşteri Segmentasyonu ve CLV Dashboard'u")
st.caption("RFM Analizi + BG/NBD & Gamma-Gamma Modeli ile Müşteri Yaşam Boyu Değeri Tahmini")

# ============================================
# ÜST ÖZET METRİKLER
# ============================================
col1, col2, col3, col4 = st.columns(4)
col1.metric("Toplam Müşteri", f"{df.shape[0]:,}")
col2.metric("Toplam Geçmiş Ciro", f"£{df['Monetary'].sum():,.0f}")
col3.metric("Toplam Gelecek CLV (12 Ay)", f"£{df['predicted_CLV_12m'].sum():,.0f}")
top_segment_share = df.groupby('Segment')['Monetary'].sum().max() / df['Monetary'].sum() * 100
col4.metric("En Büyük Segmentin Gelir Payı", f"%{top_segment_share:.1f}", "Champions")

st.divider()

# ============================================
# SEKMELER
# ============================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🧩 Segment Genel Bakış", "🗺️ RFM Haritası", "💰 CLV Risk-Değer Analizi",
    "📣 Pazarlama Stratejisi", "🔍 Müşteri Arama"
])

# ------------------------------------------------
# TAB 1: SEGMENT GENEL BAKIŞ
# ------------------------------------------------
with tab1:
    st.subheader("Segment Dağılımı")

    segment_summary = df.groupby('Segment').agg(
        Musteri_Sayisi=('Segment', 'count'),
        Toplam_Gelir=('Monetary', 'sum'),
        Toplam_Gelecek_CLV=('predicted_CLV_12m', 'sum'),
        Ort_Prob_Alive=('prob_alive', 'mean')
    ).reset_index().sort_values('Toplam_Gelir', ascending=False)

    c1, c2 = st.columns(2)

    with c1:
        fig_bar = px.bar(
            segment_summary, x='Segment', y='Musteri_Sayisi',
            color='Segment', color_discrete_map=SEGMENT_COLORS,
            title='Segment Başına Müşteri Sayısı', text='Musteri_Sayisi'
        )
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        fig_pie = px.pie(
            segment_summary, values='Toplam_Gelir', names='Segment',
            color='Segment', color_discrete_map=SEGMENT_COLORS,
            title='Toplam Gelirin Segmentlere Göre Dağılımı'
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("Segment Detay Tablosu")
    display_summary = segment_summary.copy()
    display_summary['Toplam_Gelir'] = display_summary['Toplam_Gelir'].apply(lambda x: f"£{x:,.0f}")
    display_summary['Toplam_Gelecek_CLV'] = display_summary['Toplam_Gelecek_CLV'].apply(lambda x: f"£{x:,.0f}")
    display_summary['Ort_Prob_Alive'] = display_summary['Ort_Prob_Alive'].apply(lambda x: f"%{x*100:.0f}")
    display_summary.columns = ['Segment', 'Müşteri Sayısı', 'Toplam Geçmiş Gelir', 'Toplam Gelecek CLV', 'Ort. Aktif Kalma Olasılığı']
    st.dataframe(display_summary, use_container_width=True, hide_index=True)

# ------------------------------------------------
# TAB 2: RFM HARİTASI
# ------------------------------------------------
with tab2:
    st.subheader("RFM Segment Haritası")
    st.caption("Nokta boyutu = Monetary (toplam harcama) değeri")

    selected_segments = st.multiselect(
        "Görüntülenecek segmentler:",
        options=list(SEGMENT_COLORS.keys()),
        default=list(SEGMENT_COLORS.keys())
    )
    filtered = df[df['Segment'].isin(selected_segments)]

    fig_scatter = px.scatter(
        filtered, x='Recency', y='Frequency', size='Monetary', color='Segment',
        color_discrete_map=SEGMENT_COLORS, hover_data=['Monetary', 'predicted_CLV_12m'],
        opacity=0.6, size_max=40,
        labels={'Recency': 'Recency (gün) — düşük = yakın zamanda alışveriş',
                'Frequency': 'Frequency (sipariş sayısı)'}
    )
    fig_scatter.update_layout(height=600)
    st.plotly_chart(fig_scatter, use_container_width=True)

# ------------------------------------------------
# TAB 3: CLV RİSK-DEĞER ANALİZİ
# ------------------------------------------------
with tab3:
    st.subheader("Segment Risk-Değer Haritası")
    st.caption("X ekseni: Aktif kalma olasılığı | Y ekseni: Ortalama gelecek CLV | Baloncuk boyutu: Müşteri sayısı")

    risk_summary = df.groupby('Segment').agg(
        Musteri_Sayisi=('Segment', 'count'),
        Ort_Prob_Alive=('prob_alive', 'mean'),
        Ort_Gelecek_CLV=('predicted_CLV_12m', 'mean'),
        Toplam_Gelecek_CLV=('predicted_CLV_12m', 'sum')
    ).reset_index()

    fig_risk = px.scatter(
        risk_summary, x='Ort_Prob_Alive', y='Ort_Gelecek_CLV', size='Musteri_Sayisi',
        color='Segment', color_discrete_map=SEGMENT_COLORS, text='Segment', size_max=80,
        labels={'Ort_Prob_Alive': 'Ortalama Aktif Kalma Olasılığı', 'Ort_Gelecek_CLV': 'Ortalama Gelecek CLV (£)'}
    )
    fig_risk.update_traces(textposition='top center')
    fig_risk.add_vline(x=0.7, line_dash="dash", line_color="red", opacity=0.4,
                        annotation_text="Risk Bölgesi Eşiği")
    fig_risk.update_layout(height=550, showlegend=False)
    st.plotly_chart(fig_risk, use_container_width=True)

    st.warning(
        "⚠️ **At Risk segmenti**, geçmişte yüksek harcama yapmış ancak aktif kalma olasılığı "
        "düşük müşterilerden oluşuyor — bu segment acil win-back kampanyası gerektirir."
    )

    st.subheader("B2B / Outlier Müşteriler")
    st.caption("Ortalama sipariş değeri (AOV) 99. persentilin üzerinde olan, CLV tahmini istatistiksel olarak daha az güvenilir müşteriler")
    b2b_df = df[df['Customer_Type'].str.contains('B2B', na=False)]
    st.dataframe(
        b2b_df[['Customer ID', 'Recency', 'Frequency', 'Monetary', 'predicted_CLV_12m']].sort_values(
            'predicted_CLV_12m', ascending=False
        ) if 'Customer ID' in b2b_df.columns else b2b_df[['Recency', 'Frequency', 'Monetary', 'predicted_CLV_12m']].sort_values(
            'predicted_CLV_12m', ascending=False
        ),
        use_container_width=True, hide_index=True
    )

# ------------------------------------------------
# TAB 4: PAZARLAMA STRATEJİSİ
# ------------------------------------------------
with tab4:
    st.subheader("Segment Bazlı Pazarlama Stratejisi")

    selected_segment = st.selectbox("Segment seç:", options=list(SEGMENT_STRATEGY.keys()))
    strategy = SEGMENT_STRATEGY[selected_segment]

    seg_data = df[df['Segment'] == selected_segment]

    c1, c2, c3 = st.columns(3)
    c1.metric("Müşteri Sayısı", f"{seg_data.shape[0]:,}")
    c2.metric("Toplam Geçmiş Ciro", f"£{seg_data['Monetary'].sum():,.0f}")
    c3.metric("Toplam Gelecek CLV", f"£{seg_data['predicted_CLV_12m'].sum():,.0f}")

    st.markdown(f"""
    | Alan | Detay |
    |---|---|
    | 🎯 **Amaç** | {strategy['amac']} |
    | 📢 **Ana Kanal** | {strategy['kanal']} |
    | 💡 **Kampanya Fikirleri** | {strategy['kampanya']} |
    | 🚫 **Kaçınılması Gereken** | {strategy['kacinilmasi_gereken']} |
    | 💵 **Bütçe Önceliği** | {strategy['butce_onceligi']} |
    """)

# ------------------------------------------------
# TAB 5: MÜŞTERİ ARAMA
# ------------------------------------------------
with tab5:
    st.subheader("Müşteri Bazlı Arama")

    id_col = 'Customer ID' if 'Customer ID' in df.columns else df.columns[0]
    customer_ids = df[id_col].unique().tolist()
    selected_id = st.selectbox("Müşteri ID seç:", options=sorted(customer_ids))

    customer_row = df[df[id_col] == selected_id].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Segment", customer_row['Segment'])
    c2.metric("Recency (gün)", int(customer_row['Recency']))
    c3.metric("Frequency (sipariş)", int(customer_row['Frequency']))
    c4.metric("Geçmiş Harcama", f"£{customer_row['Monetary']:,.2f}")

    c5, c6 = st.columns(2)
    c5.metric("Aktif Kalma Olasılığı", f"%{customer_row['prob_alive']*100:.1f}")
    c6.metric("12 Ay Gelecek CLV Tahmini", f"£{customer_row['predicted_CLV_12m']:,.2f}")

    if customer_row['Segment'] in SEGMENT_STRATEGY:
        st.info(f"**Önerilen strateji:** {SEGMENT_STRATEGY[customer_row['Segment']]['amac']}")

st.divider()
st.caption("Veri kaynağı: Online Retail II Dataset (UCI Machine Learning Repository)")
