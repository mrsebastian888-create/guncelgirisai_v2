# Dynamic Sports & Bonus Authority Network (DSBN) - v24.0

## Original Problem Statement
Spor icerikleri ve deneme bonusu rehberlerini birlestiren, SEO uyumlu, AI destekli, multi-tenant icerik platformu. guncelgiris.ai sitesinin GG2026 SEO framework ile buyuk olcekli SEO buyumesine hazirlanmasi.

## What's Been Implemented

### v1-v22: Previous versions (see CHANGELOG.md for full history)
### v23.0: GG2026 SEO Framework - Phase 1 (Mar 2026)
- Company folder architecture: Her firma icin 10 alt sayfa tipi
- Two core clusters: Company Guide ve Bonus Guide
- 5 Bonus hub + 8 Payment hub pages
- Navigation menu guncelleme
- Technical SEO: Dynamic titles, meta descriptions, canonical URLs, breadcrumbs
- Sitemap scaffolding

### v24.0: GG2026 SEO Framework - Phase 2 (Mar 2026) - CURRENT
**Page Template System:**
- CompanyGuideTemplate: overview, access instructions, address change, mobile login, safety notes, cross-cluster links, hub links, FAQ, last updated
- BonusGuideTemplate: overview, bonus availability, bonus types, wagering requirements, pros/cons, who it suits, cross-cluster links, hub links, FAQ, last updated
- Internal linking system: hub→company, bonus→access, access→bonus, payment hub→company payment
- Schema support: BreadcrumbList, FAQPage, Article JSON-LD

**New Backend Functions:**
- `build_company_guide_sections()` - Template sections for access pages
- `build_bonus_guide_sections()` - Template sections for bonus pages
- `build_faq()` - FAQ generation per page type
- `build_hub_links_for_company()` - Hub cross-references

**Enhanced API Response:**
- `GET /api/firma-sub/{slug}/{page_type}` now returns: template, sections, faq, hub_links, cross_cluster_links, last_updated
- `GET /api/hub/bonus/{slug}` now returns: hosgeldin_bonusu_url, odeme_url, bonus_sartlari_url per company
- `GET /api/hub/payment/{slug}` now returns: deneme_bonusu_url per company

**New Frontend Components:**
- `CompanyGuideTemplate.jsx` - 8 section template for access pages
- `BonusGuideTemplate.jsx` - 9 section template for bonus pages

## Architecture
```
/app/
├── backend/
│   ├── server.py              // Phase 2 template generators + enhanced endpoints
│   └── tests/
│       └── test_gg2026_phase2_templates.py
├── frontend/src/
│   ├── App.js
│   ├── components/
│   │   ├── templates/
│   │   │   ├── CompanyGuideTemplate.jsx  // NEW Phase 2
│   │   │   └── BonusGuideTemplate.jsx    // NEW Phase 2
│   │   ├── Navbar.jsx
│   │   ├── Footer.jsx
│   │   └── MobileBottomNav.jsx
│   └── pages/
│       ├── CompanySubPage.jsx   // Updated: uses templates + schemas
│       ├── BonusHubPage.jsx     // Updated: enhanced internal linking
│       ├── PaymentHubPage.jsx   // Updated: enhanced internal linking
│       ├── HomePage.jsx
│       ├── FirmPage.jsx
│       ├── BonusGuidePage.jsx
│       └── AdminPage.jsx
```

## Prioritized Backlog

### P0 - Critical
- Production domain (guncelgiris.ai) instability - BLOCKED on Emergent support

### P1 - High Priority
- GG2026 Phase 3: Content enrichment (AI-generated SEO content for sub-pages)
- Telegram BotFather rate limit solution (multi-account rotation)
- Company Intelligence API keys integration

### P2 - Medium Priority
- AI Video Generation POC (Sora 2)
- Company Intelligence Score implementation
- Admin Panel for company management
- AMP pages fix (blocked on production stability)

### P3 - Backlog
- Backend refactoring (server.py modular router structure)
- Full Company Intelligence module with real API data
