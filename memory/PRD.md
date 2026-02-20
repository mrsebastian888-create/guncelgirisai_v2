# Dynamic Sports & Bonus Authority Network (DSBN) - v5.0

## Original Problem Statement
Spor içerikleri ve deneme bonusu rehberlerini birleştiren, SEO uyumlu, AI destekli ve kendi kendini optimize eden içerik platformu.

## Tech Stack
- **Frontend**: React 19, Tailwind CSS, Framer Motion, shadcn/ui
- **Backend**: FastAPI, Python, `motor` (MongoDB async driver)
- **Database**: MongoDB
- **AI**: OpenAI GPT-5.2 & Gemini-3-Flash via Emergent Integrations
- **APIs**: The Odds API (live scores), Perigon API (news)

## What's Been Implemented

### v1-v3: Base MVP + Match Hub + Production Hardening
- Homepage, Bonus Guide Pages, Sports News, Article Pages
- Admin Panel with JWT Authentication
- AI Content Generation, Match Hub with live scores
- Health checks, rate limiting, CI/CD, domain-based admin access

### v4: Homepage Overhaul
- Hero section, filterable bonus list, category slider, FAQ, CTA banner

### v5.0: Gelişmiş AI SEO Asistanı (Feb 2026)
- 10 new /api/seo/* endpoints (dashboard, keyword-research, site-audit, competitor-deep, meta-generator, content-optimizer, content-score, internal-links, reports CRUD)
- SeoAssistant.jsx component with 6 sub-tabs + reports history

### v5.1: Admin Panel Tamamlama (Feb 2026) - CURRENT
**Siteler Tab:**
- Inline edit mode (name, bonus_type, amount, URL, features, rating)
- Delete with confirmation
- PUT /api/bonus-sites/{id} endpoint

**Makaleler Tab:**
- New article creation form (title, category, SEO title, description, tags, content)
- Inline edit with publish/draft toggle
- Delete with confirmation  
- Search by title/content + category filter
- Content preview (expand/collapse)
- POST /api/articles, PUT /api/articles/{id}, DELETE /api/articles/{id}, GET /api/articles/{id}

**Domainler Tab:**
- Inline edit (display_name, focus, meta_title)
- PUT /api/domains/{id} endpoint

**Admin Domain:** adminguncelgiris.company

## API Endpoints
### Auth
- POST /api/auth/login

### Domains CRUD
- GET /api/domains, POST /api/domains, PUT /api/domains/{id}, DELETE /api/domains/{id}

### Bonus Sites CRUD  
- GET /api/bonus-sites, POST /api/bonus-sites, PUT /api/bonus-sites/{id}, DELETE /api/bonus-sites/{id}

### Articles CRUD
- GET /api/articles, POST /api/articles, PUT /api/articles/{id}, DELETE /api/articles/{id}, GET /api/articles/{id}
- GET /api/articles?search=term&category=bonus

### SEO Assistant
- GET /api/seo/dashboard, POST /api/seo/keyword-research, POST /api/seo/site-audit
- POST /api/seo/competitor-deep, POST /api/seo/meta-generator, POST /api/seo/content-optimizer
- POST /api/seo/content-score, POST /api/seo/internal-links
- GET /api/seo/reports, DELETE /api/seo/reports/{id}

### Sports & Auto Content
- GET /api/sports/scores, GET /api/sports/match/{id}
- POST /api/auto-content/generate-article, POST /api/auto-content/bulk-generate
- GET /api/news

## Database Schema
- bonus_sites, articles, domains, seo_reports, domain_sites, domain_performance, users

## Prioritized Backlog
### P0 (Done)
- [x] Admin panel full CRUD (sites, articles, domains)
- [x] AI SEO Assistant
- [x] Match Hub with live scores
- [x] Admin JWT authentication + domain isolation

### P1 (Next)
- [ ] Complete Perigon News API integration (/spor-haberleri)
- [ ] Deployment to production (Vercel + Railway + Atlas)
- [ ] GoDaddy API Integration (DNS automation)
- [ ] AMP Implementation

### P2 (Future)
- [ ] Multi-language support
- [ ] Scheduled SEO reports
- [ ] A/B testing for CTAs
- [ ] server.py modular refactoring

## Testing
- iteration_4.json: SEO Assistant - 20/20 backend, all frontend passed
- iteration_5.json: Admin CRUD - 19/19 backend, all frontend passed
- Test file: /app/backend/tests/test_admin_crud.py
