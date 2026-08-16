"""
E-Ticaret RFM/CLV Projesi - RFM + CLV Birleştirme ve Segment Risk-Değer Analizi
Girdi: rfm_segmented.csv, clv_final.csv
Çıktı: rfm_clv_merged.csv, segment_clv_analysis.png
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ============================================
# 1. RFM VE CLV TABLOLARINI BİRLEŞTİR
# ============================================
rfm = pd.read_csv('rfm_segmented.csv', index_col='Customer ID')
clv = pd.read_csv('clv_final.csv', index_col='Customer ID')

merged = rfm.join(
    clv[['frequency', 'recency', 'T', 'monetary_value',
         'predicted_purchases_90d', 'prob_alive',
         'predicted_CLV_12m', 'CLV_Tier']],
    how='left'
)
print(f"[Adım 1] Birleştirilmiş tablo: {merged.shape[0]:,} müşteri, {merged.shape[1]} kolon")

# ============================================
# 2. SEGMENT BAZINDA CLV ÖZETİ
# ============================================
segment_clv = merged.groupby('Segment').agg(
    Musteri_Sayisi=('Segment', 'count'),
    Ort_Gecmis_Harcama=('Monetary', 'mean'),
    Ort_Prob_Alive=('prob_alive', 'mean'),
    Ort_Gelecek_CLV=('predicted_CLV_12m', 'mean'),
    Toplam_Gelecek_CLV=('predicted_CLV_12m', 'sum')
).sort_values('Toplam_Gelecek_CLV', ascending=False)

segment_clv['Gelecek_CLV_Payi_%'] = (
    segment_clv['Toplam_Gelecek_CLV'] / segment_clv['Toplam_Gelecek_CLV'].sum() * 100
).round(1)

print("\n=== SEGMENT BAZINDA CLV ÖZETİ ===")
print(segment_clv.to_string(float_format=lambda x: f'{x:,.1f}'))

merged.to_csv('rfm_clv_merged.csv')
segment_clv.to_csv('segment_clv_summary.csv')
print("\nKaydedildi: rfm_clv_merged.csv, segment_clv_summary.csv")

# ============================================
# 3. GÖRSELLEŞTİRME: RİSK-DEĞER HARİTASI + BAR CHART
# ============================================
sns.set_style("whitegrid")
colors = {
    'Champions': '#2E7D32', 'Loyal Customers': '#66BB6A',
    'Need Attention': '#FFA726', 'At Risk': '#EF5350',
    'New Customers': '#42A5F5', 'Hibernating': '#9E9E9E'
}
segment_order = segment_clv.index.tolist()
seg_colors = [colors[s] for s in segment_order]

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Panel 1: Risk-Değer Haritası (bubble chart)
# X: aktif kalma olasılığı, Y: ortalama gelecek CLV, boyut: müşteri sayısı
ax1 = axes[0]
for seg in segment_order:
    row = segment_clv.loc[seg]
    ax1.scatter(row['Ort_Prob_Alive'] * 100, row['Ort_Gelecek_CLV'],
                s=row['Musteri_Sayisi'] * 1.5, color=colors[seg], alpha=0.7,
                edgecolors='black', linewidth=1, label=seg)
    ax1.annotate(seg, (row['Ort_Prob_Alive'] * 100, row['Ort_Gelecek_CLV']),
                 textcoords="offset points", xytext=(10, 5), fontsize=9, fontweight='bold')

ax1.set_xlabel('Ortalama Aktif Kalma Olasılığı (%)', fontsize=11)
ax1.set_ylabel('Ortalama Gelecek CLV - 12 ay (£)', fontsize=11)
ax1.set_title('Segment Risk-Değer Haritası\n(Baloncuk boyutu = müşteri sayısı)', fontsize=13, fontweight='bold')
ax1.axvline(x=70, color='red', linestyle='--', alpha=0.3, linewidth=1)
ax1.text(71, ax1.get_ylim()[1] * 0.95, 'Risk Bölgesi', color='red', fontsize=9, alpha=0.7)

# Panel 2: Segment başına toplam gelecek CLV (bar chart)
ax2 = axes[1]
bars = ax2.bar(segment_order, segment_clv['Toplam_Gelecek_CLV'].values / 1000, color=seg_colors)
ax2.set_title('Segment Başına Toplam Gelecek CLV (£000, 12 ay)', fontsize=13, fontweight='bold')
ax2.set_ylabel('Gelecek CLV (£000)')
ax2.tick_params(axis='x', rotation=30)
for bar in bars:
    height = bar.get_height()
    ax2.annotate(f'£{height:,.0f}K', xy=(bar.get_x() + bar.get_width() / 2, height),
                 xytext=(0, 3), textcoords="offset points", ha='center', fontsize=9)

plt.tight_layout()
plt.savefig('segment_clv_analysis.png', dpi=150, bbox_inches='tight')
plt.close()
print("Kaydedildi: segment_clv_analysis.png")
