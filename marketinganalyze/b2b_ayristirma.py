

import pandas as pd

merged = pd.read_csv('rfm_clv_merged.csv', index_col='Customer ID')


merged['Avg_Order_Value'] = merged['Monetary'] / merged['Frequency']
print("=== AOV DAĞILIMI ===")
print(merged['Avg_Order_Value'].describe())


threshold = merged['Avg_Order_Value'].quantile(0.99)
print(f"\n99. persentil eşiği: £{threshold:,.2f}")


merged['Customer_Type'] = 'B2C (Bireysel)'
merged.loc[merged['Avg_Order_Value'] > threshold, 'Customer_Type'] = 'B2B/Outlier (Ayrı İncelenmeli)'

b2c = merged[merged['Customer_Type'] == 'B2C (Bireysel)']
b2b = merged[merged['Customer_Type'] == 'B2B/Outlier (Ayrı İncelenmeli)']


comparison = pd.DataFrame({
    'B2C (Bireysel)': [
        b2c.shape[0], b2c['Monetary'].sum(),
        b2c['predicted_CLV_12m'].sum(), b2c['predicted_CLV_12m'].mean()
    ],
    'B2B/Outlier': [
        b2b.shape[0], b2b['Monetary'].sum(),
        b2b['predicted_CLV_12m'].sum(), b2b['predicted_CLV_12m'].mean()
    ]
}, index=['Müşteri Sayısı', 'Geçmiş Toplam Ciro (£)', 'Toplam Gelecek CLV (£)', 'Ortalama Gelecek CLV (£)'])

print("\n=== B2C vs B2B/OUTLIER KARŞILAŞTIRMASI ===")
print(comparison.to_string(float_format=lambda x: f'{x:,.1f}'))

print(f"\nB2C grubunun payı: {b2c.shape[0]/merged.shape[0]*100:.1f}% müşteri, "
      f"toplam CLV'nin %{b2c['predicted_CLV_12m'].sum()/merged['predicted_CLV_12m'].sum()*100:.1f}'i")


merged.to_csv('rfm_clv_final_with_type.csv')
b2c.to_csv('b2c_clean_portfolio.csv')
b2b.to_csv('b2b_outliers.csv')
print("\nKaydedildi: rfm_clv_final_with_type.csv (tümü), "
      "b2c_clean_portfolio.csv (güvenilir CLV), b2b_outliers.csv (ayrı incelenecek)")

print("\n[Not] B2B/Outlier grubu için CLV tahminleri istatistiksel olarak güvenilmez "
      "(az veriden büyük tahmin). Bu grup için gerçek B2B analiz yöntemleri "
      "(kontrat değeri, sipariş trendi, account manager değerlendirmesi) önerilir.")
