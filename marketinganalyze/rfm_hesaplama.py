"""
E-Ticaret RFM/CLV Projesi - RFM Hesaplama ve Segmentasyon Scripti
Girdi: online_retail_clean.csv (veri_temizleme.py'nin çıktısı)
"""

import pandas as pd
import datetime as dt

# ============================================
# 1. TEMİZ VERİYİ OKU
# ============================================
df = pd.read_csv('online_retail_clean.csv')
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
print(f"Temiz veri yüklendi: {df.shape[0]:,} satır, {df['Customer ID'].nunique():,} benzersiz müşteri")

# ============================================
# 2. REFERANS TARİHİ BELİRLE
# Veri setindeki son tarihten 1 gün sonrası = "bugün" gibi düşün
# ============================================
reference_date = df['InvoiceDate'].max() + dt.timedelta(days=1)
print(f"[Adım 1] Referans tarih: {reference_date}")

# ============================================
# 3. RFM METRİKLERİNİ HESAPLA
# Recency  = son alışverişten bu yana geçen gün (düşük = iyi)
# Frequency = benzersiz fatura (sipariş) sayısı
# Monetary  = toplam harcama
# ============================================
rfm = df.groupby('Customer ID').agg({
    'InvoiceDate': lambda x: (reference_date - x.max()).days,
    'Invoice': 'nunique',
    'TotalPrice': 'sum'
})
rfm.columns = ['Recency', 'Frequency', 'Monetary']
print(f"[Adım 2] RFM metrikleri hesaplandı: {rfm.shape[0]:,} müşteri için")

print("\n=== RFM İSTATİSTİKLERİ ===")
print(rfm.describe())

# ============================================
# 4. RFM SKORLARINI HESAPLA (1-5 ARASI, ÇEYREKLİK BAZLI)
# ============================================
# Recency: düşük gün = iyi -> skor ters çevrilir (5,4,3,2,1)
rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1]).astype(int)

# Frequency: çok sayıda eşit değer olduğu için rank(method='first') kullanılır
# (qcut, tekrar eden değerlerde çeyreklik sınırı çizemeyip hata verebilir)
rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5]).astype(int)

# Monetary: yüksek harcama = iyi -> normal sıralama (1,2,3,4,5)
rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1, 2, 3, 4, 5]).astype(int)

print("\n[Adım 3] R, F, M skorları (1-5) hesaplandı")

# ============================================
# 5. BİRLEŞİK RFM SKORU (örn: "555" = en iyi müşteri)
# ============================================
rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)
print("[Adım 4] Birleşik RFM_Score kolonu oluşturuldu")

# ============================================
# 6. SEGMENTASYON KURALLARI
# ============================================
def segment_customer(row):
    r, f, m = row['R_Score'], row['F_Score'], row['M_Score']

    if r >= 4 and f >= 4 and m >= 4:
        return 'Champions'
    elif r >= 3 and f >= 3 and m >= 3:
        return 'Loyal Customers'
    elif r <= 2 and f >= 4 and m >= 4:
        return 'At Risk'
    elif r >= 4 and f <= 2:
        return 'New Customers'
    elif r <= 2 and f <= 2 and m <= 2:
        return 'Hibernating'
    else:
        return 'Need Attention'

rfm['Segment'] = rfm.apply(segment_customer, axis=1)
print("[Adım 5] Segment isimleri atandı")

# ============================================
# 7. SEGMENT ÖZET TABLOSU
# ============================================
segment_summary = rfm.groupby('Segment').agg(
    Musteri_Sayisi=('Segment', 'count'),
    Ortalama_Recency=('Recency', 'mean'),
    Ortalama_Frequency=('Frequency', 'mean'),
    Ortalama_Monetary=('Monetary', 'mean'),
    Toplam_Gelir=('Monetary', 'sum')
).sort_values('Toplam_Gelir', ascending=False)

segment_summary['Gelir_Yuzdesi'] = (segment_summary['Toplam_Gelir'] / rfm['Monetary'].sum() * 100).round(1)
segment_summary['Musteri_Yuzdesi'] = (segment_summary['Musteri_Sayisi'] / rfm.shape[0] * 100).round(1)

print("\n=== SEGMENT DAĞILIMI ===")
print(segment_summary)

# ============================================
# 8. KAYDET
# ============================================
rfm.to_csv('rfm_segmented.csv')
segment_summary.to_csv('segment_summary.csv')
print("\nKaydedildi: rfm_segmented.csv, segment_summary.csv")
