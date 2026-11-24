# RCA Post-Mortem Simülasyonları (AIE 501 Dönem Bildirisi)

Bildiri: *Başarısız Yazılım Projelerinde Post-Mortem İncelemesi: Kök Neden Analizi (RCA) Metodolojisi ile Kurumsal Hafıza Oluşturma*
Yazar: Nuran Beyza Gökçe — Ankara Bilim Üniversitesi

## Deneyler
| # | Dosya | Amaç | Veri |
|---|-------|------|------|
| 1 | `src/exp1_evm_pert.py` | Vaka EVM/PERT hesaplarının yeniden üretimi; PERT kuyruk olasılığının dağılım varsayımına duyarlılığı (normal, beta-PERT, üçgen) | Simüle vaka |
| 2 | `src/exp2_kemerer.py` | Gerçek tahmin hatası (MMRE, gerçekleşen/tahmin oranı) ve K1 kuralının sınanması | **Halka açık** Kemerer (1987), 15 proje |
| 3 | `src/exp3_knoi.py` | KNÖİ (P = E·T·Y) puanlarının Monte Carlo duyarlılık analizi (10.000 deneme × 3 senaryo) | Simüle puanlar |
| 4 | `src/exp4_rca_sim.py` | Ishikawa, 5 Neden ve hibrit yaklaşımın sentetik nedensel graflar üzerinde karşılaştırması (5.000 ağaç + parametre taraması) | Sentetik |

## Çalıştırma
```bash
pip install -r requirements.txt
python tests/test_case_numbers.py   # temel sayıların denetimi
python run_all.py                   # tüm deneyler, çıktılar results/ içine yazılır
```
Rastgelelik için sabit tohum (`SEED = 42`) kullanılır; aynı sürümlerle sonuçlar tekrarlanabilir. Her deney bağımsız olarak da çalıştırılabilir (`python src/exp3_knoi.py`).

## Önemli notlar ve sınırlılıklar
* **Deney 1, 3 ve 4 simülasyondur.** Vaka ve puanlar kurgusaldır; Deney 4 parametrik bir model varsayar ve sonuçlar bu varsayımlara koşulludur (`results/exp4_rca_sweep.csv` parametre taramasını içerir).
* **Deney 2 gerçek veriyi kullanır** ancak tahminler *ex post* (SLOC proje sonunda sayılmıştır) ve tek bir kuruma aittir; teklif aşaması tahminlerini temsil etmez.
* Kemerer verisi, özgün kaynaktan değil ikincil kaynaktan aktarılmıştır; iki FPA satırı (proje 7 ve 10) yayımlanan MRE'den geri türetilmiştir. Ayrıntı: `data/README_data.md`. Özgün PROMISE dosyasıyla karşılaştırılması önerilir.

## Kaynak
Kemerer, C. F. (1987). An empirical validation of software cost estimation models. *Communications of the ACM, 30*(5), 416–429.
Arnuphaptrairong, T. (2016). A literature survey on the accuracy of software effort estimation models. *Proceedings of IMECS 2016* (Vol. 2, pp. 668–673).
