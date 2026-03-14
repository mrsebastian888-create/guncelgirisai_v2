# Dynamic Sports & Bonus Authority Network (DSBN) - v27.0

## Original Problem Statement
guncelgiris.ai sitesinin GG2026 SEO framework ile buyuk olcekli SEO buyumesine hazirlanmasi.

## What's Been Implemented

### v1-v22: Previous versions (see CHANGELOG.md)
### v23.0: Phase 1 - Company folder architecture, hub pages, navigation, sitemap
### v24.0: Phase 2 - Page templates, internal linking engine, FAQ, schema support
### v25.0: Phase 3 - AI Agent Infrastructure (5 agents, 21 endpoints)
### v26.0: Phase 4 - SERP Intelligence (Ahrefs/Semrush/DataForSEO abstraction)

### v27.0: Phase 5 - Company Article System (Mar 2026) - CURRENT

**Company Article Layer:**
- URL: `/{company}/makaleler/{article-slug}` (e.g., `/onwin/makaleler/onwin-deneme-bonusu-rehberi`)
- Listing: `/{company}/makaleler` — all articles for a company
- 9 article taxonomy types: deneme-bonusu-rehberi, hosgeldin-bonusu-rehberi, bonus-sartlari, giris-rehberi, mobil-giris-rehberi, odeme-rehberi, inceleme, karsilastirma, guvenilirlik-analizi
- Cluster-based relationships: bonus-guide articles → bonus sub-pages + bonus hubs, company-guide articles → company sub-pages + payment hubs

**Article Relationships (topical authority strengthening):**
- Article → Company sub-pages (related_sub_pages filtered by cluster)
- Article → Hub pages (related_hubs based on cluster)
- Company sub-page → Company articles (sidebar "Makaleler" link)
- Article listing → General articles mentioning the company
- Cross-company: Similar firms' article listing links

**New API Endpoints:**
- `POST /api/company-articles` — Create company article
- `GET /api/company-articles/{base_slug}` — List company articles
- `GET /api/company-articles/{base_slug}/{article_slug}` — Article detail
- `GET /api/sitemap-company-articles.xml` — Sitemap for articles + listing pages

**New Frontend Pages:**
- `CompanyArticlesListPage.jsx` — `/:companySlug/makaleler`
- `CompanyArticlePage.jsx` — `/:companySlug/makaleler/:articleSlug`

**DB Collection:**
- `company_articles`: id, company_slug, title, slug, content, article_type, tags, related_company_pages, related_hub_pages, internal_links, view_count

## Architecture
```
/app/backend/
├── server.py              // COMPANY_ARTICLE_TYPES, article CRUD, sitemap
├── agents/
│   ├── serp/              // SERP providers
│   ├── keyword_agent.py
│   ├── content_agent.py
│   └── ...
/app/frontend/src/
├── pages/
│   ├── CompanyArticlesListPage.jsx  // NEW
│   ├── CompanyArticlePage.jsx       // NEW
│   ├── CompanySubPage.jsx           // Updated: Makaleler sidebar link
│   └── ...
```

## Total Pages & Endpoints
- **Frontend pages:** ~15 page components
- **API endpoints:** ~35+ (CRUD + SEO + agents + SERP + articles)
- **URL patterns:** /{company}/{page-type}, /{company}/makaleler/{slug}, /hub-pages, /api/agents/*

## Prioritized Backlog

### P1
- GG2026 Phase 6+ (as user requests)
- Bulk article generation using Content Generator Agent
- Configure SERP provider API keys

### P2
- Admin UI for article management
- Telegram multi-account rotation
- Production domain fix

### P3
- Backend refactoring (server.py modular structure)
