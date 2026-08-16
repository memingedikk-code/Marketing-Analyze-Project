"""
E-Ticaret RFM/CLV Projesi - Görselleştirme Scripti
Girdi: rfm_segmented.csv (rfm_hesaplama.py'nin çıktısı)
Çıktı: segment_overview.png, rfm_scatter.png
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

rfm = pd.read_csv('rfm_segmented.csv', index_col='Customer ID')

sns.set_style("whitegrid")
colors = {
    'Champions': '#2E7D32', 'Loyal Customers': '#66BB6A',
    'Need Attention': '#FFA726', 'At Risk': '#EF5350',
    'New Customers': '#42A5F5', 'Hibernating': '#9E9E9E'
}
segment_order = rfm.groupby('Segment')['Monetary'].sum().sort_values(ascending=False).index.tolist()
seg_colors = [colors[s] for s in segment_order]

# ============================================
# GRAFİK 1: 4 Panelli Segment Özeti
# (müşteri sayısı, gelir, gelir payı pastası, müşteri payı pastası)
# ============================================
fig, axes = plt.subplots(2, 2, figsize=(15, 12))

# Panel 1: Segment başına müşteri sayısı
ax1 = axes[0, 0]
seg_counts = rfm['Segment'].value_counts().reindex(segment_order)
bars1 = ax1.bar(seg_counts.index, seg_counts.values, color=seg_colors)
ax1.set_title('Segment Başına Müşteri Sayısı', fontsize=13, fontweight='bold')
ax1.set_ylabel('Müşteri Sayısı')
ax1.tick_params(axis='x', rotation=30)
for bar in bars1:
    height = bar.get_height()
    ax1.annotate(f'{int(height):,}', xy=(bar.get_x() + bar.get_width()/2, height),
                 xytext=(0, 3), textcoords="offset points", ha='center', fontsize=9)

# Panel 2: Segment başına toplam gelir
ax2 = axes[0, 1]
seg_revenue = rfm.groupby('Segment')['Monetary'].sum().reindex(segment_order)
bars2 = ax2.bar(seg_revenue.index, seg_revenue.values / 1000, color=seg_colors)
ax2.set_title('Segment Başına Toplam Gelir (£000)', fontsize=13, fontweight='bold')
ax2.set_ylabel('Gelir (£000)')
ax2.tick_params(axis='x', rotation=30)
for bar in bars2:
    height = bar.get_height()
    ax2.annotate(f'£{height:,.0f}K', xy=(bar.get_x() + bar.get_width()/2, height),
                 xytext=(0, 3), textcoords="offset points", ha='center', fontsize=9)

# Panel 3: Gelir payı pasta grafik
ax3 = axes[1, 0]
ax3.pie(seg_revenue.values, labels=seg_revenue.index, autopct='%1.1f%%',
        colors=seg_colors, startangle=90, textprops={'fontsize': 9})
ax3.set_title('Toplam Gelirin Segmentlere Göre Dağılımı', fontsize=13, fontweight='bold')

# Panel 4: Müşteri payı pasta grafik
ax4 = axes[1, 1]
ax4.pie(seg_counts.values, labels=seg_counts.index, autopct='%1.1f%%',
        colors=seg_colors, startangle=90, textprops={'fontsize': 9})
ax4.set_title('Müşteri Sayısının Segmentlere Göre Dağılımı', fontsize=13, fontweight='bold')

plt.tight_layout()
plt.savefig('segment_overview.png', dpi=150, bbox_inches='tight')
plt.close()
print("Kaydedildi: segment_overview.png")

# ============================================
# GRAFİK 2: RFM Scatter Plot (Segment Haritası)
# X: Recency, Y: Frequency, Nokta boyutu: Monetary
# ============================================
fig, ax = plt.subplots(figsize=(11, 7))

for segment, color in colors.items():
    subset = rfm[rfm['Segment'] == segment]
    ax.scatter(subset['Recency'], subset['Frequency'],
               s=subset['Monetary'].clip(upper=20000) / 100,  # aşırı uçları kırp (görsel okunabilirlik için)
               alpha=0.5, color=color, label=segment, edgecolors='white', linewidth=0.3)

ax.set_xlabel('Recency (gün) — Düşük = Yakın Zamanda Alışveriş', fontsize=11)
ax.set_ylabel('Frequency (sipariş sayısı)', fontsize=11)
ax.set_title('RFM Segment Haritası\n(Nokta boyutu = Monetary değeri)', fontsize=13, fontweight='bold')
ax.set_ylim(0, 60)
ax.legend(title='Segment', loc='upper right', framealpha=0.9)
plt.tight_layout()
plt.savefig('rfm_scatter.png', dpi=150, bbox_inches='tight')
plt.close()
print("Kaydedildi: rfm_scatter.png")
