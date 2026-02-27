# Dynamic Sports & Bonus Authority Network (DSBN) - v9.0

## Original Problem Statement
Spor içerikleri ve deneme bonusu rehberlerini birleştiren, SEO uyumlu, AI destekli, multi-tenant içerik platformu.

## What's Been Implemented

### v1-v6: Base MVP, Match Hub, Production Hardening, Admin CRUD, Auto-Site Generation, Categories
### v7.0: SEO Infrastructure (Sitemap, Robots.txt, JSON-LD, Canonical, OG Tags, Twitter Cards)
### v8.0: Otomatik İçerik Zamanlayıcı Sistemi (Feb 2026)
### v9.0: GoDaddy API Entegrasyonu (Feb 2026)
### v10.0: Otomatik İçerik Hızlandırma (Feb 2026)
### v11.0: Firma Rehberi + Affiliate URL Güncellemesi (Feb 2026)
### v12.0: Ana Sayfa Kapsamlı Güncelleme (Feb 2026)
### v13.0: Production Cleanup - Emergent Badge Kaldırma (Feb 2026)
### v13.1: Kapsamlı Sistem Kontrolü & Test (Feb 2026)
### v14.0: Firma URL Yapısı Güncelleme (Feb 2026)
### v15.0: AMP Sayfaları (Feb 2026)
### v16.0: Google Search Console SEO Optimizasyonu (Feb 2026)
### v17.0: Firma Detay Hero Taşıma + Test Stabilizasyonu (Feb 2026)
### v18.0: Firma Özel Video Sayfaları + Video Sitemap/AMP Sitemap (Feb 2026)
### v19.0: Sora 2 AI Video Üretim MVP (Tek Firma Pilot) (Feb 2026)
### v20.0: Company Intelligence Module Faz-1 (Fallback Mod) (Feb 2026)
### v21.0: AI Company Intelligence Navigation + Hero Yönlendirme (Feb 2026) - CURRENT

**Değişiklikler:**
- Sitemap Index yapısı: 4 alt sitemap (pages, firms, articles, amp)
- 264 firma + 545 makale + 264 AMP sayfası + 18 statik sayfa sitemap'e eklendi
- Tüm URL'ler guncelgiris.ai domain'ini kullanıyor
- robots.txt düzeltildi (AMP ve sitemap'lere izin verildi)
- public/robots.txt eklendi (frontend statik dosya)
- Homepage JSON-LD: WebSite + Organization + ItemList + FAQPage
- FirmPage JSON-LD: BreadcrumbList + Organization + Review
- Canonical URL'ler guncelgiris.ai'ye yönlendirildi
- SEO title'lar 2026 yılı ve bonus miktarı ile zenginleştirildi
- Twitter Card ve OG meta tagları güncellendi

**Değişiklikler:**
- 264 firma için AMP HTML sayfaları: `/api/amp/{slug}` endpoint'i
- Her AMP sayfasında: SEO meta, Schema.org JSON-LD, OG tagleri, affiliate CTA, makaleler, benzer siteler
- AMP endpoint rate limiter'dan hariç tutuldu
- SEOHead bileşenine amphtml prop desteği eklendi
- FirmPage'e amphtml link tag'i eklendi
- Google AMP validasyonu geçecek yapıda
- 264/264 firma başarılı test edildi

**Değişiklikler:**
- 264 firmaya `slug` alanı eklendi: `firmaismi-guncelgiris` formatı
- Backend `/api/firma/{slug}` endpoint'i slug alanından eşleşecek şekilde güncellendi (backward compatible)
- Homepage getFirmSlug fonksiyonu Türkçe karakter desteğiyle güncellendi
- FirmPage benzer siteler linkleri yeni formata güncellendi
- Örnek URL'ler: /maxwin-guncelgiris, /hiltonbet-guncelgiris, /casino-dior-guncelgiris

**Test Sonuçları (iteration_10):**
- Backend: 14/14 test geçti (%100)
- Frontend: Tüm akışlar doğrulandı (%100)
- .gitignore temizlendi, .env dosyaları git'e dahil edildi
- Tüm API'ler, admin panel, firma sayfaları, makale sayfaları çalışıyor
- Mobil özellikler (bottom nav, responsive, popuplar) doğrulandı

**Değişiklikler:**
- "Made with Emergent" badge tamamen kaldırıldı (index.html)
- emergent-main.js script kaldırıldı
- debug-monitor.js iframe script kaldırıldı
- Visual Edits tailwind CDN injection kaldırıldı
- Tüm codebase'de sıfır Emergent branding referansı

**Değişiklikler:**
- "BONUS SİTELERİ" → "YILIN EN İYİ SİTELERİ" (5 firma, altın tema)
- "EN GÜVENİLİR SİTELER" yeni bölüm (5 firma, yeşil tema)
- Firma Rehberi üste taşındı (Hero altı)
- Buton renkleri düzeltildi (okunaklı)
- BONUS AL navbar butonu random popüler firmaya yönlendiriyor
- Sayfa sırası: Hero → Firma Rehberi → Yılın En İyi → En Güvenilir → Kategoriler → MatchHub → Makaleler → FAQ → CTA

**Affiliate URL Güncellemesi:**
- 256 firma xlinks.art/firma-adi formatında özel URL aldı
- Hiçbir firma generic URL'de kalmadı

**Firma Rehberi (Ana Sayfa):**
- 3'lü grid layout tüm 264 firma
- Arama çubuğu (firma filtreleme)
- İlk 30 firma gösterimi + "Tümünü Gör" butonu
- Her kart: logo, isim, bonus, bonus tipi, "Giriş Yap" CTA
- Firma adına tıklayınca detay sayfasına yönlendirme

**Scheduler Güncellemesi:**
- Batch boyutu: 5 makale paralel (eski: 1)
- Aralık: 2 dakika (eski: 5 dakika)
- Bulk generate endpoint: /api/scheduler/bulk-generate (arka plan, timeout yok)
- AI retry mekanizması: 3 deneme, gpt-4o → gpt-4o-mini fallback
- Rate limiter: /api/track/ endpoint'leri hariç tutuldu (dakika 200 istek)
- Tahmini 1055 konu tamamlanma: ~7 saat

**Backend - GoDaddy API Endpoints:**
- GET /api/godaddy/domains - GoDaddy hesabındaki tüm domainleri listeler (2311+ domain, pagination destekli)
- POST /api/godaddy/import - GoDaddy domain'ini platforma tek tıkla ekler (bonus site kopyalama + AI içerik üretimi)
- Credentials: Production API Key/Secret (.env'de)
- already_added flag: Platformda mevcut domainleri işaretler

**Frontend - Admin Panel Domainler Sekmesi Güncellemesi:**
- GoDaddy Domainleri bölümü (cyan border accent)
- "GoDaddy Domainlerini Getir" butonu
- Domain kartları: ad, durum badge, son kullanma tarihi, oto-yenileme, gizlilik
- Arama/filtreleme input'u
- "Platforma Ekle" butonu (import)
- "Platformda Mevcut" durumu (zaten eklenmiş domainler)
- Manuel Domain Ekle bölümü (mevcut fonksiyonalite korundu)
- Tarih ve yazar bilgileri

**"En İyi Firmalar" Kategorisi:**
- Uygulama başlangıcında otomatik oluşturma
- Scheduler ile üretilen makaleler bu kategoride

**v17.0 Değişiklikler (Bu fork):**
- Yeni 3 kolonlu hero tasarımı `FirmPage.jsx` üzerinde aktif ve dinamik firma verileriyle çalışır hale getirildi
- Ana sayfanın mevcut hero slider yapısının korunduğu doğrulandı (hero yanlış sayfada değil)
- FirmPage üzerinde kritik etkileşimler/ana içerikler için ek `data-testid` etiketleri eklendi
- Admin login akışı preview ortamında test edildi: `/admin-login` → `/admin` başarılı

**v18.0 Değişiklikler (Bu fork):**
- Tüm firmalar için yeni video route eklendi: `/{slug}/video` (firma özel video sayfası)
- Yeni backend endpointi: `/api/firma/{slug}/video` (site + video + canonical + amp url)
- Yeni AMP video endpointi: `/api/amp-video/{slug}` (VideoObject schema ile)
- Yeni sitemapler: `/api/sitemap-videos.xml` ve `/api/sitemap-amp-videos.xml`
- `sitemap.xml` index ve `robots.txt` video sitemap/AMP video yollarını kapsayacak şekilde güncellendi
- Admin Sites tabına firma bazlı `video_url` ve `video_title` alanları eklendi

**v19.0 Değişiklikler (Bu fork):**
- Sora 2 ile firma bazlı AI video üretim endpointi eklendi: `POST /api/firma/{slug}/video/generate` (admin token zorunlu)
- Üretilen MP4 dosyaları servis endpointi: `GET /api/generated-videos/{filename}`
- Video durum modeli genişletildi: `ai_video_status`, `ai_video_error`, `ai_video_model`, `ai_video_generated_at`, `ai_video_url`
- `FirmVideoPage.jsx` artık video tipine göre otomatik render yapıyor (YouTube embed veya HTML5 MP4 player)
- AMP video sayfası, dosya tabanlı video varsa `amp-video` ile oynatım destekliyor
- Pilot firma: `grandpashabet-guncelgiris` için Sora 2 üretimi tetiklendi ve MP4 servis doğrulandı

**v20.0 Değişiklikler (Bu fork):**
- Company taxonomy eklendi: ana kategoriler + alt kategoriler (`company_categories`, `company_subcategories`)
- Yeni `companies` veri modeli ve Company Intelligence API katmanı eklendi
- Discovery pipeline aktif: `POST /api/admin/companies/discovery` (async queue + fallback mode)
- Public company endpoints: `GET /api/companies`, `GET /api/companies/featured/list`, `GET /api/companies/slug/{slug}`
- Admin company yönetimi: listele / onayla / featured / refresh / sil
- Dinamik profil sayfası route’u eklendi: `/companies/:slug`
- Homepage’e Featured Companies Slider eklendi (auto-rotate + 20dk auto-refresh)
- Sitemap entegrasyonu: `/api/sitemap-companies.xml` + sitemap index + robots allow
- Cron benzeri scheduler eklendi: metrics refresh 24h, feature refresh 20m, discovery 20m
- Modül dokümantasyonu: `/app/backend/modules/company-discovery/README.md`

**v21.0 Değişiklikler (Bu fork):**
- Üst menüye ana kategori olarak sabit `AI Company Intelligence` linki eklendi (`/companies`)
- Mobil alt menüde `AI Intel` kısa yolu eklendi (`/companies`)
- Yeni liste sayfası eklendi: `/companies` (arama + kategori filtreleri + company grid)
- Ana hero slider’a AI Company Intelligence odaklı yeni slide eklendi (primary CTA `/companies`, secondary CTA `#ai-company-intelligence-section`)
- Homepage Featured Companies bölümüne `Tümünü Gör` yönlendirmesi eklendi (`/companies`)
- Route genişletmesi: `/companies` + `/companies/:slug` akışı korunarak birlikte çalışır hale getirildi

## Architecture
```
/app/
├── backend/server.py
│   ├── ContentScheduler (asyncio loop)
│   ├── content_queue collection
│   ├── SEO endpoints (sitemap, robots, seo-data)
│   └── articles/latest endpoint
├── frontend/src/
│   ├── components/SEOHead.jsx
│   ├── pages/AdminPage.jsx (AutoContentScheduler component)
│   └── pages/HomePage.jsx (Latest articles section)
```

## Testing
- iteration_7: SEO Infrastructure 21/23
- iteration_8: Content Scheduler 16/18 backend + 100% frontend
- iteration_9: GoDaddy API Integration 100% backend + 100% frontend
- iteration_11: Firm hero taşıma + homepage koruma + admin login doğrulama = 100% backend + 100% frontend
- iteration_12: Firma video route + AMP video + video sitemapler = 100% backend + 100% frontend
- iteration_13: Sora 2 AI video generation MVP + admin-protected generate endpoint + MP4 serving doğrulama = 100% backend + 100% frontend
- iteration_14: Company Intelligence Faz-1 (discovery, admin controls, profile page, featured slider, sitemap) = 100% backend + 100% frontend
- iteration_15: AI Company Intelligence üst menü + hero slider yönlendirme + /companies liste sayfası = 100% backend + 100% frontend

## Production Readiness
- MongoDB indexes (17 index across 8 collections)
- Procfile + runtime.txt for Railway
- vercel.json for Vercel
- DEPLOYMENT.md rehberi
- GoDaddy domain kategorileme (Bosta/Farkli Sunucu/Platformda)

## Prioritized Backlog
### P0 (Resolved)
- [x] Admin login fix
- [x] Admin login preview doğrulaması (/admin-login -> /admin) (Feb 2026)
- [x] SEO altyapi
- [x] Otomatik icerik zamanlayici
- [x] GoDaddy API entegrasyonu
- [x] GoDaddy domain kategorileme
- [x] MongoDB indexleri
- [x] Production deployment hazirliklari
- [x] Firma detay sayfalari (FirmPage) - /firma-adi URL'leri calisiyor (Feb 2026)
- [x] Yeni 3-kolon hero tasariminin FirmPage'e tasinmasi ve dogrulanmasi (Feb 2026)
- [x] Firma özel video sayfalari + video sitemap + AMP video sitemap (Feb 2026)
- [x] Sora 2 ile tek firma pilot AI video üretim akışı (Grandpashabet) (Feb 2026)
- [x] Company Intelligence Module Faz-1 (fallback mod): şirket keşfi + company profile + featured slider + sitemap-companies (Feb 2026)
- [x] AI Company Intelligence navigasyon sabitleme + hero slider yönlendirme + /companies liste sayfası (Feb 2026)

### P1 (Next)
- [ ] Production admin login canli domainde kullanici dogrulamasi (adminguncelgiris.company)
- [ ] Sponsors tabanli dinamik GIF hero slider sistemi (DB + admin CRUD + oncelik + auto-refresh)
- [ ] AI video üretimi otomatik scheduler + batch üretim + admin onay akışı (tüm firmalar)
- [ ] External API keyleriyle gerçek discovery/enrichment aktif etme (Serper/Brave/Bing/SerpAPI/Similarweb/BuiltWith)
- [ ] Deep analysis modu (1200+ kelime AI içerik) ve otomatik SEO internal linking tuning
- [ ] Backend moduler refactoring (server.py bolunmesi)
- [ ] AMP kapsam/genisleme ve validasyon

### P2 (Future)
- [ ] Gelismis AI Style Engine
- [ ] Coklu dil destegi (i18n)
- [ ] Zamanlanmis SEO raporlari

## Key Credentials
- Admin: username=admin, password=123123..
