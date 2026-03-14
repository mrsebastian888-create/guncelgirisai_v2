# Dynamic Sports & Bonus Authority Network (DSBN) - v30.0

## Original Problem Statement
guncelgiris.ai sitesinin GG2026 SEO framework ile buyuk olcekli SEO buyumesine hazirlanmasi.

## What's Been Implemented

### v23-v29: GG2026 Phase 1-7 (see CHANGELOG.md)

### v30.0: Phase 8 - Admin Control System (Mar 2026) - CURRENT

**8 Monitoring Subsystems:**
1. **Page Type Toggles**: Enable/disable company sub-pages, hubs, articles, programmatic pages, guides (with counts)
2. **AI Agent Toggles**: Enable/disable 5 agents with job stats and success rates
3. **Publish Queue Visibility**: Queue status, today's activity, 7-day forecast, recent published
4. **Company Priority Lists**: Sort order, coverage score (articles×10 + programmatic×5 + 10), per-firm stats
5. **SERP Sync Status**: Provider configuration, fallback mode, recent SERP jobs
6. **Article Generation Status**: Company vs general articles, AI generation coverage (firms with articles %)
7. **Sitemap Health**: 10 sitemaps, total URL count, health status, warnings
8. **Indexing Status**: Programmatic page indexable %, non-indexable reasons, recommendations

**Settings System:**
- MongoDB `admin_settings` collection (singleton _id='global')
- Dot-path updates: `agents.keyword_intelligence`, `publishing.max_per_day`, etc.
- Default settings seeded on first access

**12 Admin API Endpoints (JWT protected):**
- `GET /api/admin/seo/dashboard` — Full dashboard (all 8 sections)
- `GET/POST /api/admin/seo/settings` — Get/update toggles
- `GET /api/admin/seo/page-types` — Page type status
- `GET /api/admin/seo/agents` — Agent status
- `GET /api/admin/seo/publishing` — Publish queue
- `GET /api/admin/seo/companies` — Company priorities
- `POST /api/admin/seo/companies/priority` — Update priority
- `GET /api/admin/seo/serp` — SERP status
- `GET /api/admin/seo/articles` — Article status
- `GET /api/admin/seo/sitemap` — Sitemap health
- `GET /api/admin/seo/indexing` — Indexing status

## Full GG2026 Architecture Summary
```
Phase 1: URL structure (2,640 company sub-pages)
Phase 2: Page templates + internal linking + FAQ + schemas
Phase 3: 5 AI agents (21 endpoints)
Phase 4: SERP Intelligence — 3 providers (6 endpoints)
Phase 5: Company Articles (4 endpoints)
Phase 6: Programmatic SEO Engine (6 endpoints)
Phase 7: Controlled Publishing (9 endpoints)
Phase 8: Admin Control System (12 endpoints)
─────────────────────────────────────────────────
Total: 58+ API endpoints, 10 sitemaps, 4,500+ URLs, 50K+ capacity
```

## Prioritized Backlog
### P1: Phase 9+ (as user requests), Admin UI dashboard
### P2: SERP provider keys, bulk content generation
### P3: Telegram, AI Video, Backend refactoring
