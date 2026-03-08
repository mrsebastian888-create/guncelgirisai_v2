# Google’a Dizine Ekleme Rehberi

Sitenizi ve site haritanızı Google’da dizine eklemek için aşağıdaki adımları uygulayın.

---

## 1. Google Search Console’a giriş

1. Tarayıcıda aç: **https://search.google.com/search-console**
2. Sitenin sahibi olan Google hesabıyla giriş yapın.
3. Henüz özellik eklemediyseniz **“Özellik Ekle”** ile devam edin.

---

## 2. Özellik (site) ekleme

- **Alan adı** ile eklemek (önerilen):
  - “Alan adı” seçin.
  - `guncelgiris.ai` yazın (www’suz).
  - Devam edin; mülkiyet doğrulaması istenir (aşağıda).
- **URL öneki** ile eklemek:
  - “URL öneki” seçin.
  - `https://www.guncelgiris.ai` yazın.
  - Devam edin; mülkiyet doğrulaması istenir.

---

## 3. Mülkiyet doğrulama

Google’ın önerdiği yöntemlerden birini kullanın.

### Seçenek A: HTML dosyası (kolay)

1. Search Console’da “HTML dosyası” yöntemini seçin.
2. İndirilen dosyayı (örn. `google123abc.html`) sitenizin **kök dizinine** koyun.
   - Frontend’te: `frontend/public/google123abc.html` (build sonrası sitenin kökünde erişilebilir olur).
3. Canlıya deploy edin.
4. Tarayıcıda kontrol edin: `https://www.guncelgiris.ai/google123abc.html` açılmalı.
5. Search Console’da **“Doğrula”** butonuna tıklayın.

### Seçenek B: DNS kaydı (alan adı özelliği için)

1. “DNS kaydı” yöntemini seçin.
2. Verilen TXT kaydını alan adı sağlayıcınıza (GoDaddy, Cloudflare vb.) ekleyin.
3. Yayılması birkaç dakika–saat sürebilir.
4. Search Console’da **“Doğrula”** deyin.

### Seçenek C: HTML etiketi (meta tag)

1. “HTML etiketi” yöntemini seçin.
2. Verilen `<meta name="google-site-verification" content="..." />` etiketini sitenizin `<head>` bölümüne ekleyin.
   - Örnek: `frontend/public/index.html` içinde `</head>` öncesine yapıştırın.
3. Canlıya deploy edin.
4. Search Console’da **“Doğrula”** deyin.

---

## 4. Site haritası (sitemap) gönderme

Mülkiyet doğrulandıktan sonra:

1. Sol menüden **“Site haritaları”** (Sitemaps) bölümüne girin.
2. **“Yeni site haritası ekle”** alanına şunu yazın:
   ```text
   sitemap.xml
   ```
   (Tam URL de kullanılabilir: `https://www.guncelgiris.ai/sitemap.xml`)
3. **“Gönder”** butonuna tıklayın.
4. Bir süre sonra durum “Başarılı” olarak görünür; URL sayısı artabilir.

---

## 5. URL’leri manuel dizine ekleme (isteğe bağlı)

Özellikle önemli sayfaları hemen taratmak için:

1. Sol menüden **“URL denetleme”** (URL Inspection) bölümüne girin.
2. Üstteki arama kutusuna tam URL’i yazın (örn. `https://www.guncelgiris.ai/deneme-bonusu`).
3. Enter’a basın.
4. Sayfa bilgisi geldikten sonra **“Dizine eklenmesini iste”** (Request indexing) butonuna tıklayın.

Ana sayfa, deneme-bonusu, hosgeldin-bonusu, companies gibi önemli sayfaları bu şekilde tek tek isteyebilirsiniz.

---

## 6. Özet — Kopyala yapıştır

- **Search Console:** https://search.google.com/search-console  
- **Eklenecek site:** `https://www.guncelgiris.ai` (veya alan adı: `guncelgiris.ai`)  
- **Gönderilecek site haritası:**  
  `https://www.guncelgiris.ai/sitemap.xml`  
  (Search Console’da sadece `sitemap.xml` yazmanız yeterli.)

---

## 7. robots.txt kontrolü

Sitemap adresi zaten `robots.txt` içinde tanımlı. Kontrol için:

- Tarayıcıda aç: **https://www.guncelgiris.ai/robots.txt**

Şu satır görünmeli:

```text
Sitemap: https://www.guncelgiris.ai/sitemap.xml
```

Google, bu dosyayı okuyup site haritanızı da bulabilir; yine de Search Console’dan site haritası göndermeniz önerilir.

---

## Notlar

- Dizine ekleme ve sıralama birkaç gün veya hafta sürebilir; sabırlı olun.
- “Site haritaları” bölümünde hata görürseniz, sitemap’in gerçekten `https://www.guncelgiris.ai/sitemap.xml` adresinde açıldığını tarayıcıda kontrol edin.
- Yeni sayfalar için tekrar “URL denetleme” ile “Dizine eklenmesini iste” kullanabilirsiniz; tüm site için site haritası göndermek yeterli olur.
