"""
E-Ticaret RFM/CLV Projesi - CLV Modelleme (lifetimes kütüphanesi)
BG/NBD modeli: gelecekte kaç alışveriş yapılacağını tahmin eder
Gamma-Gamma modeli: her alışverişte ortalama ne kadar harcanacağını tahmin eder

Girdi: online_retail_clean.csv
Çıktı: clv_final.csv
"""

import pandas as pd
from lifetimes.utils import summary_data_from_transaction_data
from lifetimes import BetaGeoFitter, GammaGammaFitter

# ============================================
# 1. VERİYİ lifetimes FORMATINA ÇEVİR
# frequency: TEKRAR eden sipariş sayısı (ilk alışveriş sayılmaz)
# recency  : ilk alışveriş ile son alışveriş arasındaki gün farkı
# T        : müşterinin gözlemlendiği toplam süre (ilk alışverişten referans tarihe kadar)
# monetary_value: tekrar eden alışverişlerin ortalama tutarı
# ============================================
df = pd.read_csv('online_retail_clean.csv')
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

summary = summary_data_from_transaction_data(
    df,
    customer_id_col='Customer ID',
    datetime_col='InvoiceDate',
    monetary_value_col='TotalPrice',
    observation_period_end=df['InvoiceDate'].max()
)
print(f"[Adım 1] lifetimes formatına çevrildi: {summary.shape[0]:,} müşteri")
print(f"   Hiç tekrar alışveriş yapmamış müşteri (frequency=0): "
      f"{(summary['frequency']==0).sum():,} ({(summary['frequency']==0).mean()*100:.1f}%)")

# ============================================
# 2. BG/NBD MODELİNİ EĞİT
# Müşterinin "hâlâ aktif" olma olasılığını ve gelecekteki
# alışveriş sayısını tahmin eder
# ============================================
bgf = BetaGeoFitter(penalizer_coef=0.001)
bgf.fit(summary['frequency'], summary['recency'], summary['T'])
print("\n[Adım 2] BG/NBD modeli eğitildi")
print(bgf.summary)

# Önümüzdeki 90 gün için beklenen alışveriş sayısı
summary['predicted_purchases_90d'] = bgf.conditional_expected_number_of_purchases_up_to_time(
    90, summary['frequency'], summary['recency'], summary['T']
)
# Müşterinin hâlâ "aktif" olma olasılığı
summary['prob_alive'] = bgf.conditional_probability_alive(
    summary['frequency'], summary['recency'], summary['T']
)

# ============================================
# 3. GAMMA-GAMMA MODELİNİ EĞİT
# Sadece tekrar eden müşteriler (frequency > 0) kullanılabilir,
# çünkü model harcama davranışını öğrenmek için en az 1 tekrar ister
# ============================================
repeat_customers = summary[summary['frequency'] > 0]

# Varsayım kontrolü: frequency ile monetary_value arasında korelasyon olmamalı
correlation = repeat_customers[['frequency', 'monetary_value']].corr().iloc[0, 1]
print(f"\n[Kontrol] Frequency-Monetary korelasyonu: {correlation:.4f} (0'a yakın olmalı)")

ggf = GammaGammaFitter(penalizer_coef=0.001)
ggf.fit(repeat_customers['frequency'], repeat_customers['monetary_value'])
print("\n[Adım 3] Gamma-Gamma modeli eğitildi")
print(ggf.summary)

# ============================================
# 4. 12 AYLIK CLV TAHMİNİ HESAPLA
# BG/NBD (kaç kez alışveriş) ile Gamma-Gamma (ne kadar harcar)
# modellerini birleştirip gelecekteki toplam beklenen geliri hesaplar
# ============================================
clv = ggf.customer_lifetime_value(
    bgf,
    repeat_customers['frequency'],
    repeat_customers['recency'],
    repeat_customers['T'],
    repeat_customers['monetary_value'],
    time=12,            # 12 ay ileriye tahmin
    freq='D',           # T, recency birim olarak gün cinsinden
    discount_rate=0.01  # aylık %1 iskonto oranı (paranın zaman değeri)
)
summary['predicted_CLV_12m'] = clv
summary['predicted_CLV_12m'] = summary['predicted_CLV_12m'].fillna(0)  # frequency=0 olanlar için 0
print("\n[Adım 4] 12 aylık CLV tahmini hesaplandı")

# ============================================
# 5. CLV TIER'LARINA AYIR
# ============================================
summary['CLV_Tier'] = pd.qcut(
    summary['predicted_CLV_12m'].rank(method='first'), 3,
    labels=['Düşük Potansiyel', 'Orta Potansiyel', 'Yüksek Potansiyel']
)

print("\n=== SONUÇ ÖZETİ ===")
print(f"Toplam portföy CLV (önümüzdeki 12 ay): £{summary['predicted_CLV_12m'].sum():,.2f}")
print(f"Ortalama müşteri CLV: £{summary['predicted_CLV_12m'].mean():,.2f}")
print(f"Medyan müşteri CLV: £{summary['predicted_CLV_12m'].median():,.2f}")
print("\nCLV Tier dağılımı:")
print(summary.groupby('CLV_Tier')['predicted_CLV_12m'].agg(['count', 'mean', 'sum']))

# NOT: En yüksek CLV'li müşterileri kontrol etmeyi unutma!
# Çok düşük frequency + çok yüksek tek seferlik harcaması olan müşteriler
# (muhtemelen B2B/toptan alıcılar) Gamma-Gamma modelinde aşırı şişirilmiş
# CLV tahminlerine yol açabilir. Bu müşterileri ayrı incelemek gerekir.
print("\n[Uyarı] En yüksek CLV'li 10 müşteriyi kontrol et - "
      "düşük frequency + çok yüksek monetary_value kombinasyonu "
      "aşırı tahmine işaret edebilir (muhtemelen B2B alıcı):")
print(summary.sort_values('predicted_CLV_12m', ascending=False)
      [['frequency', 'monetary_value', 'predicted_CLV_12m']].head(10))

summary.to_csv('clv_final.csv')
print("\nKaydedildi: clv_final.csv")
