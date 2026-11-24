# Veri kaynağı: Kemerer (1987) veri seti

15 tamamlanmış kurumsal (çoğunlukla COBOL) yazılım projesi; gerçekleşen efor ve iki model tahmini (FPA, COCOMO), kişi-ay.

* Özgün kaynak: Kemerer, C. F. (1987). An empirical validation of software cost estimation models. *Communications of the ACM, 30*(5), 416–429.
* Veri, özgün makaleden/PROMISE deposundan doğrudan indirilmemiştir. Tablolar, Arnuphaptrairong (2016) IMECS bildirisinin Tablo II (FPA) ve Tablo XII (COCOMO) bölümlerinden aktarılmıştır (ağ erişimi olmayan ortamda).
* Doğrulama: COCOMO MMRE = %583,82 yayımlanan değerle birebir eşleşir. FPA MMRE'si yayımlanan %102,74 değerini ancak iki satır düzeltildiğinde verir:
  * Proje 7: ikincil kaynaktaki 52,60 değeri, bildirilen MRE (%326,73) ile çelişir; MRE'den geri türetilen 99,00 kullanılmıştır.
  * Proje 10: ikincil kaynaktaki 2,83 değeri, bildirilen MRE (%103,93) ile çelişir; geri türetilen 146,83 kullanılmıştır.
  * Bu iki satır `fpa_estimate_derived = 1` ile işaretlidir; analizler bunlar dışarıda bırakılarak da tekrarlanmıştır.
* Kullanmadan önce PROMISE/tera-PROMISE deposundaki özgün `kemerer` dosyasıyla karşılaştırılması önerilir.
