# Site Haritası (Sitemap) Referansı

Site haritası **backend API** tarafından dinamik üretilir. Frontend’teki `public/sitemap.xml` tüm alt sitemaplere doğrudan link verir (son güncelleme: 2026-03-06).

---

## Ana index (Google’ın çektiği adres)

- **Canlı:** https://www.guncelgiris.ai/sitemap.xml  
  → `frontend/public/sitemap.xml` — 7 alt sitemap’in listesi (pages, firms, companies, videos, articles, amp, amp-videos).
- **API üzerinden index (yedek):** https://api.guncelgiris.ai/api/sitemap.xml  
- **Lokal API:** http://localhost:8000/api/sitemap.xml  

---

## Alt sitemap adresleri

`www.guncelgiris.ai/sitemap.xml` açıldığında aşağıdaki 7 sitemap listelenir; her biri API’de üretilir:

| Sitemap | İçerik | Örnek URL (canlı) |
|--------|--------|--------------------|
| **sitemap-pages.xml** | Ana sayfa, deneme/hosgeldin, spor-haberleri, companies, bonus kategorileri | https://api.guncelgiris.ai/api/sitemap-pages.xml |
| **sitemap-firms.xml** | Tüm aktif firma sayfaları (`/{slug}`) | https://api.guncelgiris.ai/api/sitemap-firms.xml |
| **sitemap-companies.xml** | Tüm onaylı şirket profilleri (`/companies/{slug}`) | https://api.guncelgiris.ai/api/sitemap-companies.xml |
| **sitemap-videos.xml** | Firma video sayfaları (`/{slug}/video`) | https://api.guncelgiris.ai/api/sitemap-videos.xml |
| **sitemap-articles.xml** | Yayında olan tüm makaleler (`/makale/{slug}`) | https://api.guncelgiris.ai/api/sitemap-articles.xml |
| **sitemap-amp.xml** | AMP firma sayfaları (API host’ta) | https://api.guncelgiris.ai/api/sitemap-amp.xml |
| **sitemap-amp-videos.xml** | AMP video sayfaları (API host’ta) | https://api.guncelgiris.ai/api/sitemap-amp-videos.xml |

Tüm `<loc>` değerleri `FRONTEND_BASE_URL` (varsayılan: https://www.guncelgiris.ai) ile başlar; AMP sitemapleri API base URL kullanır.

---

## Sabit sayfalar (sitemap-pages’teki URL’ler)

- /
- /deneme-bonusu
- /hosgeldin-bonusu
- /spor-haberleri
- /companies
- /bonus/{kategori_slug}  (kategoriler DB’den gelir)

---

## robots.txt

- **Frontend:** `https://www.guncelgiris.ai/robots.txt` → `public/robots.txt`  
  İçinde: `Sitemap: https://www.guncelgiris.ai/sitemap.xml`
- **Backend:** `https://api.guncelgiris.ai/robots.txt` → API’de üretilen robots (isteğe bağlı)

---

## Hızlı test

1. Tarayıcıda aç: https://www.guncelgiris.ai/sitemap.xml  
   → Tek `<sitemap>` görünmeli, `loc` içinde API sitemap index olmalı.
2. O `loc` URL’sini aç (örn. https://api.guncelgiris.ai/api/sitemap.xml)  
   → 7 adet `<sitemap>` (pages, firms, companies, videos, articles, amp, amp-videos) görünmeli.
3. Örn. https://api.guncelgiris.ai/api/sitemap-pages.xml  
   → `https://www.guncelgiris.ai/...` ile başlayan `<url>` listesi görünmeli.

**Not:** `frontend/public/sitemap.xml` içindeki `lastmod` tarihini yayın tarihine göre güncelleyebilirsin. Alt sitemaplerdeki URL listesi ve `lastmod` değerleri backend’de her istekte dinamik üretilir.
