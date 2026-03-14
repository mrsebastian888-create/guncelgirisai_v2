# Dynamic Sports & Bonus Authority Network (DSBN) - v29.0

## Original Problem Statement
guncelgiris.ai sitesinin GG2026 SEO framework ile buyuk olcekli SEO buyumesine hazirlanmasi.

## What's Been Implemented

### v23-v28: GG2026 Phase 1-6 (see CHANGELOG.md)

### v29.0: Phase 7 - Controlled Publishing System (Mar 2026) - CURRENT

**Queue-Based Publishing:**
- `publish_queue` MongoDB collection: pending → scheduled → publishing → published/failed
- Rate limiting: 8-15 pages per day (configurable)
- Priority system: 1=highest, 10=lowest
- Slug dedup: blocks pending/scheduled duplicates
- Manual override: immediately publish any item

**Day-of-Week Content Schedule:**
| Day | Content Type |
|-----|-------------|
| Monday | Hub pages (intent, license, country) |
| Tuesday | Company pages (sub-pages, payment, year) |
| Wednesday | Guides (rehber, guide topics) |
| Thursday | Comparison pages (karsilastirma, intent×category) |
| Friday | Bonus pages (deneme, hosgeldin, bonus rehberi) |
| Saturday | Articles (makale, inceleme, giris rehberi) |
| Sunday | Content updates (refresh, timestamp updates) |

**Background Daemon:**
- Auto-runs every 30 min
- Auto-schedules pending items by day rules
- Auto-publishes due items for today
- Lifecycle integrated with FastAPI lifespan

**9 API Endpoints:**
- `GET /api/publish/status` — Queue stats + 7-day forecast + daemon status
- `POST /api/publish/enqueue` — Add items to queue
- `POST /api/publish/schedule` — Schedule pending items
- `POST /api/publish/run` — Manually trigger today's publishing
- `POST /api/publish/manual` — Override: publish specific items immediately
- `GET /api/publish/queue` — List items with status filter + pagination
- `POST /api/publish/remove` — Remove pending/scheduled items
- `POST /api/publish/reschedule-failed` — Move failed → pending
- `GET /api/publish/schedule-map` — Day content mapping

## Full GG2026 Architecture Summary
```
Phase 1: URL structure (264 firms × 10 sub-pages = 2,640 URLs)
Phase 2: Page templates + internal linking engine + FAQ + schemas
Phase 3: 5 AI agents (keyword, content, linking, update, SEO) = 21 endpoints
Phase 4: SERP Intelligence (Ahrefs/Semrush/DataForSEO) = 6 endpoints
Phase 5: Company Articles (/{company}/makaleler/{slug}) = 4 endpoints
Phase 6: Programmatic SEO Engine (7 combination types) = 6 endpoints
Phase 7: Controlled Publishing (queue + scheduler + daemon) = 9 endpoints
─────────────────────────────────────────────────────────
Total: 46+ API endpoints, 50K+ page capacity, 10 sitemaps
```

## Prioritized Backlog
### P1: Phase 8+ (as user requests)
### P2: Admin UI for publishing dashboard, SERP provider keys
### P3: Telegram, AI Video, Backend refactoring
