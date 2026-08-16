# 📊 E-Ticaret Müşteri Segmentasyonu ve CLV Tahmin Modeli

RFM analizi ve olasılıksal CLV modellemesi (BG/NBD & Gamma-Gamma) kullanarak bir e-ticaret şirketinin müşteri portföyünü segmentlere ayıran, gelecekteki müşteri değerini tahmin eden ve her segment için veri odaklı pazarlama stratejileri öneren uçtan uca bir data analitiği projesi.

**🔗 [Canlı Dashboard'u Görüntüle](STREAMLIT_LINKINI_BURAYA_KOY)**

![Segment Genel Bakış](images/segment_overview.png)



## 🎯 Proje Özeti

Bu proje, 1 milyondan fazla işlem içeren gerçek bir İngiltere merkezli online perakende veri setini kullanarak şu iş sorusuna cevap arıyor:

> **Hangi müşteriler en değerli, hangileri kaybedilme riskinde, ve pazarlama bütçesi nereye yönlendirilmeli?**

**Öne çıkan bulgular:**
- Müşterilerin yalnızca **%22'si (Champions segmenti)**, toplam gelirin **%68'ini** ve gelecek 12 aylık tahmini CLV'nin **%70'ini** oluşturuyor
- **At Risk** segmentindeki 223 müşteri geçmişte ortalama £4.404 harcamış olmasına rağmen aktif kalma olasılıkları **%50'ye** düşmüş — hedefli bir win-back kampanyası ~**£165.000**'lık gelecek gelir riskini azaltabilir
- Düşük sipariş sıklığına sahip ama çok yüksek tutarlı müşterilerin (muhtemelen B2B alıcılar) CLV tahminini istatistiksel olarak şişirdiği tespit edilip bu grup ayrı analiz edildi



## 🛠️ Kullanılan Teknolojiler

| Kategori | Araçlar |
|---|---|
| Veri işleme | Python, pandas, numpy |
| İstatistiksel modelleme | `lifetimes` (BG/NBD, Gamma-Gamma) |
| Görselleştirme | matplotlib, seaborn, plotly |
| Dashboard | Streamlit |
| Raporlama | Excel (openpyxl) |



## 📁 Veri Seti

[Online Retail II Dataset](https://archive.ics.uci.edu/dataset/502/online+retail+ii) (UCI Machine Learning Repository) — İngiltere merkezli bir hediyelik eşya perakendecisinin 01.12.2009 – 09.12.2011 tarihleri arasındaki 1.067.371 işlemi.

> Ham veri dosyası boyutu nedeniyle bu repoda yer almıyor. `notebooks/01_veri_temizleme.py` scriptini çalıştırmadan önce veri setini yukarıdaki linkten indirip `data/` klasörüne ekleyin.



## 🔬 Metodoloji

| Aşama | Açıklama |
|---|---|
| **1. Veri Temizleme** | İptal edilen faturalar, negatif/sıfır değerler, eksik Customer ID'ler ve duplicate kayıtlar temizlendi (1.067.371 → 779.425 satır) |
| **2. RFM Segmentasyonu** | Recency, Frequency, Monetary metrikleri hesaplanıp çeyreklik bazlı skorlamayla 6 segmente ayrıldı (Champions, Loyal Customers, Need Attention, At Risk, New Customers, Hibernating) |
| **3. CLV Modelleme** | BG/NBD modeli ile gelecekteki alışveriş sayısı, Gamma-Gamma modeli ile ortalama harcama tahmin edilip 12 aylık CLV hesaplandı |
| **4. Model Doğrulama** | Gamma-Gamma modelinin varsayımı (frequency-monetary korelasyonu ≈ 0, ölçülen: 0.02) kontrol edildi |
| **5. Outlier Ayrıştırma** | Ortalama sipariş değeri (AOV) 99. persentilin üzerindeki müşteriler (muhtemelen B2B) istatistiksel güvenilirlik için ayrı segmentlendi |
| **6. Stratejik Öneriler** | Her segment için kanal, mesaj tonu ve bütçe önceliği içeren somut pazarlama planı oluşturuldu |


## 📈 Sonuçlar

![RFM Segment Haritası](images/rfm_scatter.png)

![Segment Risk-Değer Analizi](images/segment_clv_analysis.png)

| Segment | Müşteri Sayısı | Gelir Payı | 12 Ay CLV Payı | Aktif Kalma Olasılığı |
|---|---|---|---|---|
| Champions | 1.297 (%22,1) | %68,3 | %69,6 | %100 |
| Loyal Customers | 1.138 (%19,4) | %14,8 | %17,1 | %100 |
| Need Attention | 1.497 (%25,5) | %7,2 | %4,7 | %80 |
| At Risk | 223 (%3,8) | %5,7 | %2,0 | %50 |
| New Customers | 443 (%7,5) | %2,3 | %6,3 | %100 |
| Hibernating | 1.280 (%21,8) | %1,9 | %0,3 | %90 |

Detaylı segment bazlı pazarlama stratejisi için: [`docs/pazarlama_strateji.md`](docs/pazarlama_strateji.md)



## 🚀 Nasıl Çalıştırılır

```bash
# Repoyu klonla
git clone https://github.com/KULLANICI_ADIN/ecommerce-clv-segmentation.git
cd ecommerce-clv-segmentation

# Gerekli paketleri kur
pip install -r requirements.txt

# Veri setini data/ klasörüne indir (yukarıdaki linkten)

# Scriptleri sırayla çalıştır
python notebooks/01_veri_temizleme.py
python notebooks/02_rfm_hesaplama.py
python notebooks/03_gorsellestirme.py
python notebooks/04_clv_modelleme.py
python notebooks/05_rfm_clv_birlestirme.py
python notebooks/06_b2b_ayristirma.py

# Dashboard'u başlat
streamlit run dashboard.py
```



## 📂 Proje Yapısı

```
├── README.md
├── requirements.txt
├── .gitignore
├── dashboard.py                          # Streamlit interaktif dashboard
│
├── notebooks/                            # Analiz scriptleri (sırayla çalıştırılır)
│   ├── 01_veri_temizleme.py
│   ├── 02_rfm_hesaplama.py
│   ├── 03_gorsellestirme.py
│   ├── 04_clv_modelleme.py
│   ├── 05_rfm_clv_birlestirme.py
│   └── 06_b2b_ayristirma.py
│
├── docs/
│   └── pazarlama_strateji.md             # Segment bazlı pazarlama stratejisi
│
├── images/                               # Görselleştirmeler
│   ├── segment_overview.png
│   ├── rfm_scatter.png
│   └── segment_clv_analysis.png
│
├── reports/
│   └── musteri_segmentasyon_CLV.xlsx     # Sekmelere bölünmüş, formüllü Excel raporu
│
└── data/
    └── rfm_clv_final_with_type.csv       # İşlenmiş final veri (ham veri hariç)
```



 📊 Dashboard Özellikleri

İnteraktif Streamlit dashboard'u 5 sekmeden oluşuyor:

1. **Segment Genel Bakış** — müşteri/gelir dağılımı, detay tablosu
2. **RFM Haritası** — segment filtrelenebilir interaktif scatter plot
3. **CLV Risk-Değer Analizi** — risk-değer haritası + B2B outlier listesi
4. **Pazarlama Stratejisi** — segment seçimine göre kampanya önerisi, KPI ve gerçek rakamlar
5. **Müşteri Arama** — tekil müşteri ID'sine göre RFM/CLV profili ve önerilen strateji



 ⚠️ Sınırlılıklar ve Geliştirme Alanları

Bu proje bir analitik/growth-marketing vaka çalışması olarak tasarlandı; production-grade bir ML sistemi değildir. Şeffaflık için bilinen sınırlılıklar:

- Segmentasyon eşikleri (R/F/M skor kombinasyonları) kural bazlıdır, veriden optimize edilmemiştir (alternatif: k-means kümeleme)
- Model, zaman bazlı train/test ayrımıyla backtest edilmemiştir — tahminlerin gerçekleşenlerle karşılaştırılması yapılmamıştır
- İskonto oranı ve projeksiyon süresi gibi varsayımlar için duyarlılık analizi yapılmamıştır



👤 İletişim

Muhammet Emin Gedik
www.linkedin.com/in/muhammet-emin-gedik-612515384 · m.emingedikk@gmail.com
