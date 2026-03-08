# PHASE 3 — URL Architecture, Rendering Audit & Sitemap Optimization

**Tarih:** 2026-03  
**Kapsam:** URL yapısı, canonical doğrulama, render analizi, sitemap, internal link grafiği, index önceliği, prerender adayları.  
**Kural:** Sistemi kırmadan analiz, doğrulama ve önerilen düzeltmeler.

---

## 1. SITE STRUCTURE OVERVIEW

### 1.1 Mevcut route yapısı (React Router — `App.js`)

| Path | Bileşen | Tip |
|------|---------|-----|
| `/` | HomePage | Ana sayfa |
| `/deneme-bonusu` | BonusGuidePage (deneme) | Kategori / pillar |
| `/hosgeldin-bonusu` | BonusGuidePage (hosgeldin) | Kategori / pillar |
| `/bonus/:type` | BonusGuidePage | Kategori (yatirim, kayip, …) |
| `/spor-haberleri` | SportsNewsPage | Kategori |
| `/companies` | CompaniesPage | Kategori / hub |
| `/companies/:slug` | CompanyProfilePage | Provider (company) |
| `/makale/:slug` | ArticlePage | Rehber / makale |
| `/mac/:slug` | MatchDetailPage | Maç sayfası |
| `/:slug/video` | FirmVideoPage | Firma video |
| `/:slug` | FirmPage | Firma (provider) sayfası |
| `*` | NotFoundPage | 404 |
| `/admin-login`, `/admin` | LoginPage, AdminPage | Admin (noindex) |

### 1.2 Beklenen SEO hiyerarşisi (referans)

- **Beklenen:** `/` → category → guide / provider / faq  
- **Örnek:** `/` → `/deneme-bonusu-veren-siteler`, `/hosgeldin-bonusu`, `/casino-bonuslari` → guide: `/deneme-bonusu-nedir`, `/bonus-cevrim-sarti-nedir` → provider: `/provider-name`

### 1.3 Sitemap kaynakları (backend)

- **Sitemap index:** `GET /api/sitemap.xml` → alt sitemaplere yönlendirir (API host üzerinde).
- **Alt sitemapler:**  
  `sitemap-pages.xml`, `sitemap-firms.xml`, `sitemap-companies.xml`, `sitemap-videos.xml`, `sitemap-articles.xml`, `sitemap-amp.xml`, `sitemap-amp-videos.xml`.
- **Frontend:** `public/sitemap.xml` → `<loc>https://api.guncelgiris.ai/api/sitemap.xml</loc>` (sitemap index API’de).
- **robots.txt:** `Sitemap: https://www.guncelgiris.ai/sitemap.xml` → Tarayıcı önce frontend’teki `sitemap.xml`’i alır, o da API’deki index’e işaret eder.

---

## 2. URL ARCHITECTURE STATUS

### 2.1 URL structure consistency

| Beklenen yapı | Mevcut | Durum |
|---------------|--------|--------|
| Category pages | `/deneme-bonusu`, `/hosgeldin-bonusu`, `/bonus/:type`, `/spor-haberleri`, `/companies` | ✅ Var |
| Guide pages | `/makale/:slug` (örn. deneme-bonusu-nedir, bonus-cekim-sartlari) | ✅ Tek pattern altında |
| Provider pages | `/:slug` (FirmPage), `/companies/:slug` (CompanyProfilePage) | ✅ Var |
| FAQ / rehber | Makaleler `/makale/:slug` ile; ayrı FAQ route yok | ✅ Makale ile çözülmüş |

**Tespit edilen tutarsızlıklar:**

1. **İsimlendirme:** Strateji dokümanında “deneme-bonusu-veren-siteler” pillar örnek URL’i var; uygulama `/deneme-bonusu`. İçerik planındaki slug’lar (`deneme-bonusu-veren-siteler-2026` vb.) makale olarak `/makale/...` altında; kategori sayfası farklı. **Öneri:** Ya kategori URL’i `/deneme-bonusu-veren-siteler` yapılır (redirect ile eski URL korunur) ya da dokümantasyon mevcut URL’e göre güncellenir; aynı terminoloji kullanılsın.
2. **Guide URL’leri:** Rehber sayfalar tek segment: `/makale/deneme-bonusu-nedir`. Beklenen örnekte bazen `/deneme-bonusu-nedir` (root’ta) geçiyor. Mevcut yapı (tüm rehberler `/makale/`) hiyerarşik olarak tutarlı ve derinliği artırmıyor; **değişiklik zorunlu değil**.
3. **Casino bonusları:** Örnekte `/casino-bonuslari` var; route’ta yok. `/bonus/casino` veya ayrı bir kategori eklenebilir; şu an sadece `BonusGuidePage` ile `type` (deneme, hosgeldin, yatirim, kayip) var.

### 2.2 Özet

- Genel hiyerarşi: **Home → Category → Article/Provider** ile uyumlu.
- Küçük tutarsızlıklar: pillar/category isimlendirmesi ve casino-bonuslari eksikliği; doküman veya route ile giderilebilir.

---

## 3. URL DEPTH ANALYSIS

**Derinlik:** Home = 1. seviye, her `/` = +1.

| URL pattern | Örnek | Derinlik | Durum |
|-------------|--------|----------|--------|
| `/` | `/` | 1 | ✅ |
| `/deneme-bonusu` | `/deneme-bonusu` | 2 | ✅ |
| `/hosgeldin-bonusu` | `/hosgeldin-bonusu` | 2 | ✅ |
| `/bonus/:type` | `/bonus/yatirim` | 3 | ✅ |
| `/spor-haberleri` | `/spor-haberleri` | 2 | ✅ |
| `/companies` | `/companies` | 2 | ✅ |
| `/companies/:slug` | `/companies/acme` | 3 | ✅ |
| `/makale/:slug` | `/makale/deneme-bonusu-nedir` | 3 | ✅ |
| `/mac/:slug` | `/mac/maç-id` | 3 | ✅ |
| `/:slug` | `/betting-site` | 2 | ✅ |
| `/:slug/video` | `/betting-site/video` | 3 | ✅ |

**Sonuç:** Tüm sayfalar **3 veya daha az** seviyede. “Category/subcategory/page/article” gibi 4+ seviye yok. **Derinlik açısından sorun yok.**

---

## 4. CANONICAL VALIDATION

### 4.1 Sayfa bazında canonical

| Sayfa | Canonical kaynağı | Not |
|-------|-------------------|-----|
| HomePage | `canonical="https://guncelgiris.ai"` (sabit) | ⚠️ www yok; index.html’de `https://www.guncelgiris.ai/` |
| BonusGuidePage | `window.location.origin` + path (deneme-bonusu, hosgeldin-bonusu, bonus/type) | ✅ Dinamik, doğru |
| SportsNewsPage | `origin + /spor-haberleri` | ✅ |
| ArticlePage | `origin + /makale/${article.slug}` | ✅ |
| FirmPage | `https://guncelgiris.ai/${site.slug}` (sabit domain) | ⚠️ www yok; ortam değişirse hatalı olabilir |
| FirmVideoPage | API’den `canonical_url` | ✅ Backend kontrolü |
| CompaniesPage | `https://guncelgiris.ai/companies` (sabit) | ⚠️ www yok |
| CompanyProfilePage | API’den `canonical_url` | ✅ |
| MatchDetailPage | `origin + /mac/${slug}` | ✅ |
| NotFoundPage (404) | Yok (SEOHead’e canonical verilmiyor) | ⚠️ Fallback: `window.location.href` → 404 URL’i canonical olur |

### 4.2 Canonical kuralları

- **Canonical olmalı:** Tüm indexlenebilir sayfalarda var (SEOHead ile); 404’te açık canonical yok, fallback mevcut URL.
- **Indexlenebilir URL ile eşleşmeli:** Dinamik sayfalarda genelde `origin + path` kullanılıyor; sabit kullanılan sayfalarda domain (www vs non-www) tutarsızlığı var.
- **Redirect sayfasına işaret etmemeli:** Kod incelemesinde canonical’ın redirect URL’ine işaret ettiği bir durum yok.

### 4.3 Rapor: canonical sorunları

| Sorun | Sayfa(lar) | Öneri |
|-------|------------|--------|
| **canonical_conflict (www vs non-www)** | HomePage, CompaniesPage, FirmPage | Canonical’da tek format seçin (tercihen `https://www.guncelgiris.ai`). `FRONTEND_BASE_URL` veya `window.location.origin` ile tek kaynaktan üretin. |
| **missing_canonical (anlamlı)** | NotFoundPage | 404’te canonical vermeyin veya canonical’ı ana sayfaya verin (best practice: 404’te canonical yok veya mevcut 404 URL’i; noindex zaten var). |
| **duplicate_canonical** | Tespit yok | Aynı sayfada iki canonical yok. |

**Özet:** Asıl risk www / non-www tutarsızlığı ve sabit domain kullanımı; canonical’ların indexlenebilir URL ile eşleşmesi için tek “base URL” (env veya origin) kullanılması önerilir.

---

## 5. RENDERING ANALYSIS

### 5.1 Mimari

- **Frontend:** SPA (Create React App / Craco). İlk istekte sunucu **tek bir `index.html`** döner; içerik **JavaScript ile** render edilir.
- **SSR:** Yok. Tüm sayfa içeriği (title, meta, H1, ana metin, linkler, JSON-LD) **client-side** oluşturuluyor.

### 5.2 İlk HTML (index.html)

- **İçerik:** `title`, `meta description`, `og:*`, `canonical` (https://www.guncelgiris.ai/), `noscript` mesajı, `<div id="root"></div>`.
- **Eksik (ilk HTML’de):** Sayfa bazlı title/description, H1, ana metin, internal linkler, sayfa özelinde JSON-LD. Bunlar sadece React mount sonrası var.

### 5.3 Kritik SEO öğeleri

| Öğe | İlk HTML | JS sonrası |
|-----|----------|------------|
| title | Genel (sadece ana sayfa için anlamlı) | ✅ Sayfa bazlı |
| meta description | Genel | ✅ Sayfa bazlı |
| H1 | ❌ | ✅ |
| Ana içerik metni | ❌ | ✅ |
| Internal linkler | ❌ | ✅ (Navbar, Footer, sayfa içi) |
| JSON-LD | ❌ | ✅ (SEOHead useEffect) |

**Sonuç:** Önemli SEO içeriği (title, description, H1, içerik, linkler, yapısal veri) **tamamen JS render sonrasında** görünüyor. İlk HTML’de sadece genel meta ve boş root var; bot JS çalıştırmazsa içerik “zayıf” kalır.

### 5.4 Sayfa bazlı kısa değerlendirme

- **Tüm public sayfalar:** İçerik JS sonrası yükleniyor → **candidate_for_prerender** veya **must_fix_in_app** (SSR/ prerender yoksa “in app” = bot’a anlamlı ilk HTML sağlama) kapsamına girer.
- **Admin:** noindex; render önceliği düşük.

---

## 6. PRERENDER RISK DETECTION

### 6.1 Sınıflandırma

| Sınıf | Açıklama | Bu sitedeki sayfalar |
|-------|----------|----------------------|
| **safe_without_prerender** | İlk HTML yeterli, JS gerekmez | Yok (SPA, ilk HTML zayıf) |
| **candidate_for_prerender** | İlk HTML zayıf, içerik JS ile; önemli sayfalar | Ana sayfa, deneme-bonusu, hosgeldin-bonusu, spor-haberleri, companies, makale/*, firm /*, companies/* |
| **must_fix_in_app** | 404, redirect, noindex, bozuk canonical, ince içerik, placeholder | 404 (noindex var, canonical belirsiz); diğerleri “candidate” |

### 6.2 must_fix_in_app detay

- **404:** noindex doğru; canonical açıkça tanımlı değil (fallback mevcut URL). İsteğe bağlı: 404’te canonical’ı kaldırın veya ana sayfaya yönlendirin.
- **Redirect / noindex / broken canonical:** Kod tarafında ciddi bir redirect/canonical hatası yok.
- **Thin content / placeholder:** İçerik yönetimine bağlı; bu raporda URL/teknik tarafta “thin” tespiti yapılmadı.

**Özet:** Çoğu sayfa **candidate_for_prerender**. 404 için küçük canonical iyileştirmesi yeterli; “must_fix_in_app” ağırlıklı olarak 404 ve (varsa) ince içerikli sayfalar.

---

## 7. INTERNAL LINK GRAPH

### 7.1 Link kaynakları (kod bazlı)

- **Navbar:** `/`, `/companies`, `/deneme-bonusu`, `/hosgeldin-bonusu`, `/bonus/deneme`, `/#firma-rehberi`, `/bonus/guncel-giris-adresleri`, `/spor-haberleri`.
- **Footer:** `/`, `/deneme-bonusu`, `/hosgeldin-bonusu`, `/bonus/yatirim`, `/bonus/kayip`, `/spor-haberleri`, `/makale/deneme-bonusu-nedir`, `/makale/hosgeldin-bonusu-nedir`, `/makale/cevrim-sarti-nedir`, `/makale/guvenilir-bonus-siteleri`, `/makale/bonus-cekim-sartlari`, Gizlilik/Kullanım (`/`).
- **BonusGuidePage:** “İlgili Rehberler” ile `/makale/*` linkleri (deneme/hosgeldin/yatirim/kayip’e göre değişiyor).
- **ArticlePage:** İlgili makaleler, “Geri Dön” (kategori sayfasına).
- **HomePage:** Slider, kategoriler, firmalar (harici/affiliate linkler + muhtemelen bazı internal).
- **FirmPage / CompanyProfilePage:** Muhtemelen ana sayfa veya liste sayfalarına linkler.

### 7.2 Orphan / düşük linkli sayfalar

- **Orphan (hiç internal link yok):** Sadece sitemap veya harici kaynaktan gelen sayfalar. Örn. bazı `/makale/*` slug’ları sadece sitemap’te; Footer’da 5 rehber, BonusGuidePage’de birkaç rehber var. Diğer makaleler **orphan** olabilir.
- **Düşük linkli:** Çoğu `/companies/:slug`, `/:slug`, `/:slug/video`, `/mac/:slug` sadece liste/sayfa içi linklerle; Navbar/Footer’da yok. Pillar (deneme-bonusu, hosgeldin-bonusu) Navbar + Footer’da olduğu için **yüksek otorite**.
- **Yüksek otorite:** `/`, `/deneme-bonusu`, `/hosgeldin-bonusu`, `/spor-haberleri`, `/companies` — tüm kullanıcılar bunlara maruz.

**Öneri:** Pillar sayfaları zaten iyi link alıyor. Rehber makaleleri için Footer + BonusGuidePage’deki “İlgili Rehberler” genişletilebilir; yeni rehberler eklendikçe internal link ile bağlanmalı. Sitemap’te olup sitede hiç link olmayan makaleler “orphan” adayıdır; listelenip linklenmeli.

---

## 8. SITEMAP VALIDATION

### 8.1 Mevcut sitemap yapısı

- **Index:** `GET /api/sitemap.xml` (backend).  
- **Frontend:** `public/sitemap.xml` → tek `<sitemap>` ile `https://api.guncelgiris.ai/api/sitemap.xml`.
- **robots.txt:** `Sitemap: https://www.guncelgiris.ai/sitemap.xml` → Frontend’teki statik sitemap’i işaret ediyor; o da API index’e yönlendiriyor.

### 8.2 Doğrulanacak kurallar

| Kural | Durum |
|-------|--------|
| URL’ler 200 döner | Backend sitemap’teki URL’ler `FRONTEND_BASE_URL` ile üretiliyor; canlı istek yapılmadığı için bu raporda **doğrulanamadı**; production’da kontrol önerilir. |
| URL’ler canonical | Sitemap’teki loc = frontend sayfa URL’i; canonical’lar (www hariç) aynı path’i kullanıyor. |
| Indexlenebilir | Sadece public sayfalar; admin sitemap’te yok. |
| Redirect değil | Kodda sitemap URL’lerinin redirect’e işaret ettiği yok. |
| Duplicate yok | Her sitemap türü kendi kümesini veriyor; çakışma beklenmez. |

### 8.3 Olası sitemap sorunları

1. **Domain tutarlılığı:** Sitemap’te `FRONTEND_BASE_URL` (varsayılan `https://www.guncelgiris.ai`) kullanılıyor. Canonical’da bazı sayfalar `https://guncelgiris.ai` (www’suz). **Sitemap ile canonical aynı domain formatında olmalı.**
2. **Sitemap konumu:** Google `https://www.guncelgiris.ai/sitemap.xml` istiyor → statik dosya API’ye yönlendiriyor. Statik dosya her zaman API’yi işaret etmeli; API erişilebilir olmalı.
3. **AMP sitemapleri:** `sitemap-amp.xml` ve `sitemap-amp-videos.xml` `request.base_url` (API host) kullanıyor. Yani AMP URL’leri `https://api.guncelgiris.ai/api/amp/...` formatında. Bu, AMP sayfalarının API’de sunulduğu varsayımıyla tutarlı; frontend domain’de AMP bekleniyorsa çakışma olabilir.

**Özet:** Sitemap yapısı mantıklı; asıl risk **www vs non-www** ve **AMP URL’lerinin hangi domain’de sunulduğu**; production’da URL’lerin 200 ve indexlenebilir olduğu manuel/otomatik kontrol edilmeli.

---

## 9. CLEAN SITEMAP GENERATION (Öneriler)

### 9.1 Dahil edilmesi önerilenler

- 200 dönen sayfalar.
- Tek (canonical) URL formatında olanlar (tercihen www ile).
- Indexlenebilir (noindex olmayan) sayfalar.
- İnce içerik (thin) olmayan sayfalar — tespit için içerik/kelime sayısı kriteri ayrı tanımlanabilir.

### 9.2 Hariç tutulması önerilenler

- Mock / test route’ları: Kodda görünmüyor; admin zaten sitemap’te yok.
- Redirect URL’leri: Sitemap’te bilinçli olarak yok.
- 404: Zaten sitemap’te yok.
- İnce içerik: Backend’de “thin” işareti yok; ileride eklenirse sitemap üretiminde filtrelenebilir.

**Mevcut backend sitemap mantığı** (pages, firms, companies, videos, articles, amp, amp-videos) bu kurallarla uyumlu. Ek yapılacaklar: (1) Base URL’i tek kaynaktan (env) alıp www/non-www tutarlılığı, (2) isteğe bağlı “thin” / “noindex” filtreleri.

---

## 10. INDEX PRIORITY MAP

Önerilen tarama önceliği:

| Öncelik | Sayfa türü | Örnekler |
|---------|------------|----------|
| **HIGH** | Pillar / kategori | `/`, `/deneme-bonusu`, `/hosgeldin-bonusu`, `/spor-haberleri`, `/companies`, `/bonus/:type` |
| **MEDIUM** | Rehber makaleleri, provider | `/makale/*`, `/:slug` (FirmPage), `/companies/:slug` |
| **LOW** | FAQ, arşiv, video, maç | `/makale/*` (FAQ amaçlı olanlar), `/:slug/video`, `/mac/:slug` |

Sitemap’te `<priority>` ve `<changefreq>` zaten kullanılıyor; yukarıdaki sıra mevcut priority değerleriyle (1.0, 0.9, 0.8, 0.7) uyumlu. İstenirse HIGH sayfalar 0.9–1.0, MEDIUM 0.7–0.8, LOW 0.6–0.7 olarak netleştirilebilir.

---

## 11. SEARCH CONSOLE RISK ANALYSIS

“Discovered – currently not indexed” / “Crawled – currently not indexed” için olası nedenler:

| Risk | Açıklama | Bu sitede |
|------|-----------|-----------|
| Thin content | Az metin, düşük değer | İçerik yönetimine bağlı; teknik olarak tespit edilmedi. |
| Düşük internal linking | Az link alan sayfalar | Orphan veya sadece sitemap’ten gelen makaleler; bazı firm/company sayfaları. |
| JS rendering | İçerik sadece JS ile | Tüm SPA sayfaları; bot JS çalıştırmazsa zayıf. |
| Duplicate canonical | Aynı canonical’a işaret eden farklı URL’ler | www vs non-www farkı var; gerçek duplicate yok. |
| Sitemap mismatch | Sitemap’teki URL erişilemiyor / farklı | Domain (www) ve AMP host (API) tutarlılığı kontrol edilmeli. |

**Öneri:** Domain ve canonical’ı sabitleyin; internal linkleri (özellikle rehber makalelere) artırın; gerekirse prerender/SSR ile ilk HTML’i güçlendirin.

---

## 12. PRERENDER PILOT LIST

Aşağıdaki 10–20 URL, SEO açısından kritik, render riski yüksek ve (mevcut yapıda) güçlü içerik / internal link potansiyeli olan sayfalar. Prerender (veya SSR) pilotu için aday.

1. `https://www.guncelgiris.ai/`
2. `https://www.guncelgiris.ai/deneme-bonusu`
3. `https://www.guncelgiris.ai/hosgeldin-bonusu`
4. `https://www.guncelgiris.ai/spor-haberleri`
5. `https://www.guncelgiris.ai/companies`
6. `https://www.guncelgiris.ai/bonus/yatirim`
7. `https://www.guncelgiris.ai/bonus/kayip`
8. `https://www.guncelgiris.ai/makale/deneme-bonusu-nedir`
9. `https://www.guncelgiris.ai/makale/hosgeldin-bonusu-nedir`
10. `https://www.guncelgiris.ai/makale/cevrim-sarti-nedir`
11. `https://www.guncelgiris.ai/makale/guvenilir-bonus-siteleri`
12. `https://www.guncelgiris.ai/makale/bonus-cekim-sartlari`

(12 URL listelendi; toplam 20’ye çıkarmak için en çok trafik alan veya stratejik `/:slug` / `/companies/:slug` sayfaları eklenebilir.)

**Kriterler:** SEO kritik, JS’e bağımlı içerik, güçlü içerik ve internal link (Footer/Navbar/BonusGuide’da geçenler). İnce veya duplicate sayfalar hariç.

---

## 13. FINAL REPORT — ÖZET BÖLÜMLER

### SITE STRUCTURE OVERVIEW

- SPA; route’lar: `/`, kategori (`/deneme-bonusu`, `/hosgeldin-bonusu`, `/bonus/:type`, `/spor-haberleri`, `/companies`), rehber (`/makale/:slug`), provider (`/:slug`, `/companies/:slug`), video (`/:slug/video`), maç (`/mac/:slug`), 404.
- Hiyerarşi: Home → Category → Article/Provider; mantıklı.

### URL ARCHITECTURE STATUS

- Tutarlı; küçük tutarsızlıklar: pillar isimlendirmesi (deneme-bonusu vs deneme-bonusu-veren-siteler), casino-bonuslari route eksikliği.

### CANONICAL ISSUES

- www vs non-www: HomePage, CompaniesPage, FirmPage sabit `https://guncelgiris.ai` kullanıyor; index.html ve sitemap `www` ile. Tek format (tercihen www) ve tek kaynak (env veya origin) kullanılmalı.
- 404: Açık canonical yok; noindex var. İsteğe bağlı: 404’te canonical’ı kaldır veya ana sayfaya yönlendir.

### RENDERING ANALYSIS

- Tüm önemli SEO içeriği JS sonrası; ilk HTML zayıf. Tüm public sayfalar **candidate_for_prerender** (veya SSR ile must_fix_in_app).

### PRERENDER CANDIDATES

- Yukarıdaki 12 URL pilot için uygun; isteğe bağlı 8 URL daha eklenebilir.

### INTERNAL LINK GRAPH

- Pillar sayfalar yüksek otorite; bazı makaleler ve firm/company sayfaları orphan veya düşük linkli. Rehber makalelere Footer/BonusGuide ve ilgili makalelerden link artırılmalı.

### SITEMAP ISSUES

- Yapı doğru; domain (www) ve canonical tutarlılığı sağlanmalı; AMP URL’leri API host’ta; production’da sitemap URL’lerinin 200 ve indexlenebilir olduğu doğrulanmalı.

### INDEXABILITY STATUS

- Admin noindex; public sayfalar indexlenebilir. Risk: JS rendering, www tutarsızlığı, düşük/orphan linkler.

### PRIORITY FIX LIST

1. **Canonical ve base URL:** Tüm sayfalarda tek canonical formatı (tercihen `https://www.guncelgiris.ai`). HomePage, CompaniesPage, FirmPage için `FRONTEND_BASE_URL` veya `window.location.origin` kullanın; sabit domain kaldırın.
2. **404 canonical:** NotFoundPage’te canonical’ı açıkça tanımlayın (yok veya ana sayfa).
3. **Sitemap vs canonical:** Sitemap’teki base URL ile canonical aynı olsun (www dahil).
4. **Internal links:** Sitemap’te olup sitede linki olmayan makaleleri tespit edip en az bir internal link verin; rehber kümelerini genişletin.
5. **Rendering:** Prerender veya SSR ile kritik sayfaların ilk HTML’inde title, description, H1 ve kısa içerik verin; veya en azından pilot URL’ler için prerender kullanın.

### OPTIMIZED URL MAP

| Tip | Önerilen URL pattern | Örnek | Sitemap | Öncelik |
|-----|----------------------|--------|---------|---------|
| Ana sayfa | `/` | `https://www.guncelgiris.ai/` | sitemap-pages | HIGH |
| Kategori (pillar) | `/deneme-bonusu`, `/hosgeldin-bonusu` | Aynı | sitemap-pages | HIGH |
| Kategori | `/bonus/:type` | `/bonus/yatirim`, `/bonus/kayip` | sitemap-pages | HIGH |
| Kategori | `/spor-haberleri`, `/companies` | Aynı | sitemap-pages | HIGH |
| Rehber | `/makale/:slug` | `/makale/deneme-bonusu-nedir` | sitemap-articles | MEDIUM |
| Firma | `/:slug` | `/:firma-slug` | sitemap-firms | MEDIUM |
| Şirket profili | `/companies/:slug` | `/companies/acme` | sitemap-companies | MEDIUM |
| Video | `/:slug/video` | `/:firma-slug/video` | sitemap-videos | LOW |
| Maç | `/mac/:slug` | `/mac/match-id` | (ayrı sitemap yok) | LOW |
| 404 | — | noindex, canonical opsiyonel | Hariç | — |

Tüm indexlenebilir URL’ler tek base domain üzerinden (tercihen `https://www.guncelgiris.ai`) canonical ve sitemap’te tutarlı olmalı. AMP sayfaları API host’ta kalabilir.

---

*Rapor sonu. Değişiklikler analiz ve öneri düzeyindedir; çalışan sistem bozulmamalıdır.*
