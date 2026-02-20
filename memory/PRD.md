# Dynamic Sports & Bonus Authority Network (DSBN) - v3.0

## Original Problem Statement
Spor içerikleri ve deneme bonusu rehberlerini birleştiren, SEO uyumlu, AI destekli ve kendi kendini optimize eden içerik platformu.

## User Choices/Requirements
1. **AI Performansa Göre Otomatik Sıralama** - CTA tıklama, affiliate click, scroll depth, time on page metrikleri
2. **Gerçek Site Listesi** - MAXWIN, HILTONBET, ELEXBET, FESTWIN, CASINO DIOR, BETCI, ALFABAHIS, TULIPBET
3. **Freshness Engine** - Gerçek değişiklikte güncelleme, kampanya arşivleme
4. **SEO Asistanı** - Rakip analizi, anahtar kelime boşluğu, haftalık rapor, iç link önerileri
5. **Gelişmiş AI SEO Asistanı** - Kapsamlı SEO aracı seti (Dashboard, Keyword Research, Site Audit, Competitor Analysis, Meta Generator, Content Optimizer)

## Tech Stack
- **Frontend**: React 19, Tailwind CSS, Framer Motion, shadcn/ui
- **Backend**: FastAPI, Python, `motor` (MongoDB async driver)
- **Database**: MongoDB
- **AI**: OpenAI GPT-5.2 & Gemini-3-Flash via Emergent Integrations
- **APIs**: The Odds API (live scores), Perigon API (news)

## What's Been Implemented

### v1.0 - Base MVP
- Homepage, Bonus Guide Pages, Sports News, Article Pages
- Admin Panel with CRUD operations
- AI Content Generation

### v2.0 - Match Hub Module
- Robust Scores API (cache + retry + fallback)
- MatchHub component (cards, league badge, status, score, CTAs)
- AI Mini-Insight (Gemini-flash)
- Match Detail Page with SEO schema
- Partner Tracking endpoint
- Admin Controls (API status, AI toggle, featured match)

### v3.0 - Production Hardening
- Health checks, versioning, DB checks
- Structured logging (JSON formatter)
- Rate limiting (IP-based)
- CI/CD Pipeline (GitHub Actions)
- JWT Admin Authentication
- Domain-Based Access Control (admin-guncelgiris.co)

### v4.0 - Homepage Overhaul
- Hero section with neon grid
- Filterable bonus list
- Category slider
- FAQ accordion
- CTA banner

### v5.0 - Gelişmiş AI SEO Asistanı (February 2026) ✅ NEW
Backend Endpoints (10 new):
- `GET /api/seo/dashboard` - SEO health score, metrics, issues, recommendations
- `POST /api/seo/keyword-research` - AI keyword analysis with scoring, related keywords, content ideas
- `POST /api/seo/site-audit` - Comprehensive SEO audit with category scores and priority actions
- `POST /api/seo/content-score` - Article SEO quality scoring
- `POST /api/seo/competitor-deep` - Deep competitor analysis with action plans
- `POST /api/seo/meta-generator` - Generate meta titles/descriptions with SERP preview
- `POST /api/seo/internal-links` - Internal linking suggestions
- `POST /api/seo/content-optimizer` - Content optimization recommendations
- `GET /api/seo/reports` - Historical SEO reports
- `DELETE /api/seo/reports/{id}` - Delete reports

Frontend Component (SeoAssistant.jsx):
- SEO Score Dashboard with visual ring, stats cards, issues
- Keyword Research Tool (search volume, competition, difficulty, intent)
- Site Audit Tool (category scores, priority actions)
- Competitor Analysis (profile, keyword gaps, action plan)
- Meta Tag Generator (3 options with SERP preview)
- Content Optimizer (title improvements, content improvements, readability)
- Reports History (filter, expand, delete)

## Database Schema
```
bonus_sites: {id, name, logo_url, bonus_type, bonus_amount, bonus_value, affiliate_url, rating, features, turnover_requirement, is_active}
articles: {id, title, slug, content, content_hash, content_updated_at, seo_title, seo_description, tags, category}
domains: {id, domain_name, display_name, focus, theme, cloudflare_zone_id}
seo_reports: {id, type, input, result, created_at}
users: {username, hashed_password}
```

## API Endpoints
- POST /api/auth/login
- GET /api/bonus-sites, POST /api/bonus-sites
- GET /api/articles, POST /api/domains/{id}/articles
- GET /api/sports/scores, GET /api/sports/featured
- GET /api/sports/match/{id}
- GET /api/news (Perigon API)
- GET /api/seo/dashboard
- POST /api/seo/keyword-research
- POST /api/seo/site-audit
- POST /api/seo/content-score
- POST /api/seo/competitor-deep
- POST /api/seo/meta-generator
- POST /api/seo/internal-links
- POST /api/seo/content-optimizer
- GET /api/seo/reports
- DELETE /api/seo/reports/{id}

## Prioritized Backlog

### P0 (Done) ✅
- [x] AI performance ranking system
- [x] Real site list integration
- [x] SEO assistant tools (basic)
- [x] Performance tracking infrastructure
- [x] Match Hub with live scores
- [x] Admin authentication (JWT)
- [x] Gelişmiş AI SEO Asistanı

### P1 (Next Phase)
- [ ] Complete Perigon News API integration (SportsNewsPage)
- [ ] Deployment guidance (Atlas, Railway, Vercel)
- [ ] GoDaddy API Integration (DNS automation)
- [ ] AMP Implementation (mobile SEO)

### P2 (Future)
- [ ] Multi-language support
- [ ] Scheduled reports via email
- [ ] A/B testing for CTA buttons
- [ ] Mobile app (PWA)

## Testing Status
- Backend: 20/20 tests passed (SEO endpoints)
- Frontend: All tabs, admin login, homepage verified
- Test file: /app/backend/tests/test_seo_assistant.py
