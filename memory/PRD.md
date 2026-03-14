# Dynamic Sports & Bonus Authority Network (DSBN) - v24.0

## Original Problem Statement
Spor icerikleri ve deneme bonusu rehberlerini birlestiren, SEO uyumlu, AI destekli, multi-tenant icerik platformu. guncelgiris.ai sitesinin GG2026 SEO framework ile buyuk olcekli SEO buyumesine hazirlanmasi.

## What's Been Implemented

### v1-v22: Previous versions (see CHANGELOG.md for full history)

### v23.0: GG2026 SEO Framework - Phase 1 (Mar 2026)
- Company folder architecture: 10 alt sayfa tipi, 264 firma = ~2640 URL
- Two core clusters: Company Guide + Bonus Guide
- 5 Bonus hub + 8 Payment hub pages
- Navigation + footer + mobile nav guncelleme
- Sitemap scaffolding (sitemap-seo-pages.xml)

### v24.0: GG2026 SEO Framework - Phase 2 (Mar 2026) - CURRENT

**Company Guide Template Sections:**
- CompanyOverview: Firma istatistikleri (kategori, puan, bonus, lisans)
- AccessInstructions: Adim adim erisim talimatlari (sayfa tipine ozel)
- AddressChangeExplanation: Domain degisikligi aciklamasi
- MobileLoginInfo: Mobil uyumluluk detaylari (sadece mobil-giris)
- SecurityNotes: SSL, lisans, 2FA, GDPR bilgileri

**Bonus Guide Template Sections:**
- CompanySummary: Firma ozeti + istatistik kartlari
- BonusAvailability: Aktif bonus durumu gostergesi
- BonusTypesSection: Mevcut bonus turleri listesi
- WageringExplanation: Cevrim sarti aciklamasi (ornek dahil)
- AdvantagesDisadvantages: Avantaj/dezavantaj karsilastirmasi
- RecommendedProfile: Hedef kullanici profili

**Shared Sections:**
- FAQSection: Sayfa tipine ozel FAQ (accordion + FAQPage schema)
- RelatedPagesBlock: Cluster ici baglanti blogu
- LastUpdatedBlock: Son guncelleme zamani
- RelatedCompaniesBlock: Benzer firmalar + alt sayfa linkleri

**Internal Linking Engine:**
- Hub → Company pages (bonus hub → deneme-bonusu, hosgeldin-bonusu, bonus-sartlari, guncel-giris)
- Payment hub → Company payment + access pages (odeme-yontemleri, guncel-giris, deneme-bonusu, mobil-giris)
- Company bonus ↔ Company access cross-cluster links

**Schema Support:**
- BreadcrumbList JSON-LD
- FAQPage JSON-LD (per page type FAQ data)
- Article JSON-LD (dateModified, headline, publisher)

**Backend Enhancements:**
- PAGE_TYPE_FAQ: 10 page type x 3-4 FAQ = ~35 unique FAQ items
- Enhanced firma-sub response: faq, last_updated, hub_links, related_companies

## Architecture
```
/app/
├── backend/
│   └── server.py              // PAGE_TYPE_FAQ, HUB_COMPANY_PAGE_MAPPING, enhanced firma-sub endpoint
├── frontend/src/
│   ├── pages/
│   │   ├── CompanySubPage.jsx  // Rich templates: CompanyGuide + BonusGuide sections
│   │   ├── BonusHubPage.jsx    // Enhanced internal linking
│   │   ├── PaymentHubPage.jsx  // Enhanced internal linking
│   │   └── ...existing pages
│   └── components/
│       └── ...existing components
```

## Prioritized Backlog

### P0 - Critical
- Production domain (guncelgiris.ai) instability - BLOCKED on Emergent support

### P1 - High Priority
- GG2026 Phase 3+ (future phases as user requests)
- Telegram BotFather rate limit solution (multi-account rotation)

### P2 - Medium Priority
- AI Video Generation POC (Sora 2)
- Company Intelligence Score
- AMP pages fix

### P3 - Backlog
- Backend refactoring (server.py modular router structure)
- Full Company Intelligence with real API data
