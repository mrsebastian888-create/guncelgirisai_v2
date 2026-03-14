# Dynamic Sports & Bonus Authority Network (DSBN) - v28.0

## Original Problem Statement
guncelgiris.ai sitesinin GG2026 SEO framework ile buyuk olcekli SEO buyumesine hazirlanmasi.

## What's Been Implemented

### v23-v27: GG2026 Phase 1-5 (see CHANGELOG.md)

### v28.0: Phase 6 - Programmatic SEO Engine (Mar 2026) - CURRENT

**Engine Components:**
- **PageRegistry**: Central catalog for all programmatic pages (MongoDB `programmatic_pages`)
- **SlugGenerator**: Builds valid slugs from dimension combinations
- **TemplateSelector**: Maps 7 combination types to frontend templates
- **CanonicalManager**: Enforces canonical rules, blocks reserved Phase 1-5 slugs
- **DuplicatePrevention**: Blocks near-duplicate pages and existing route overlaps
- **IndexingEligibility**: Checks min title/desc length, min firms for hub pages (3+)
- **SitemapIntegration**: Dynamic `sitemap-programmatic.xml` for indexable pages

**7 Combination Types:**
- `company_x_bonus` — /{company}/{bonus_type}
- `company_x_payment` — /{company}/{payment_method} (10 payment methods)
- `company_x_year` — /{company}/{year}
- `intent_x_category` — /en-guvenilir-bahis-siteleri, /canli-bahis-siteleri etc. (8 intents)
- `license_x_category` — /curacao-lisansli-siteler etc. (3 licenses)
- `country_x_category` — /turkiye-bahis-siteleri etc. (3 countries)
- `guide_x_topic` — /rehber/bahis-nasil-yapilir etc. (6 topics)

**Scale Capacity:** 50,000+ pages
- 264 firms × 10 payments = 2,640
- 264 firms × 1 year = 264
- 8 intent + 3 license + 3 country + 6 guide = 20 hub pages
- Total potential: ~3,000+ unique pages with built-in deduplication

**New API Endpoints:**
- `GET /api/programmatic/stats` — Engine statistics
- `POST /api/programmatic/generate` — Generate combinations (dry_run or execute)
- `POST /api/programmatic/register` — Register single page
- `GET /api/programmatic/pages` — List pages (filterable)
- `GET /api/programmatic/page/{slug}` — Get page data for rendering
- `GET /api/sitemap-programmatic.xml` — Sitemap for indexable pages

**Frontend:**
- `ProgrammaticPage.jsx` — Generic renderer for all programmatic pages
- `SlugResolver.jsx` — Smart catch-all: checks programmatic first, falls back to FirmPage
- `/rehber/:slug` route for guide pages

## Architecture
```
/app/backend/
├── agents/
│   ├── programmatic_engine.py  # Core engine (7 components)
│   ├── serp/                   # SERP providers
│   └── ...agents
├── server.py                   # Programmatic API + sitemap endpoints
/app/frontend/src/pages/
├── ProgrammaticPage.jsx        # Generic renderer
├── SlugResolver.jsx            # Smart resolver
└── ...existing pages
```

## Total System Scale
- **264 firms** × 10 sub-pages = 2,640 company pages
- **264 firms** × articles = unlimited article pages
- **13 hub pages** (bonus + payment)
- **20+ programmatic pages** (intent, license, country, guide)
- **5 AI agents** with 21 endpoints
- **3 SERP providers** with 6 endpoints
- **10 sitemaps** in index

## Prioritized Backlog
### P1: Phase 7+ (as user requests), Bulk programmatic page generation
### P2: Admin UI, SERP provider keys, Telegram
### P3: Backend refactoring
