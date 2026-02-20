# Dynamic Sports & Bonus Authority Network (DSBN) - v2.0

## Original Problem Statement
Spor içerikleri ve deneme bonusu rehberlerini birleştiren, SEO uyumlu, AI destekli ve kendi kendini optimize eden içerik platformu.

## User Choices/Requirements
1. **AI Performansa Göre Otomatik Sıralama** - CTA tıklama, affiliate click, scroll depth, time on page metrikleri
2. **Gerçek Site Listesi** - MAXWIN, HILTONBET, ELEXBET, FESTWIN, CASINO DIOR, BETCI, ALFABAHIS, TULIPBET
3. **Freshness Engine** - Gerçek değişiklikte güncelleme, kampanya arşivleme
4. **SEO Asistanı** - Rakip analizi, anahtar kelime boşluğu, haftalık rapor, iç link önerileri

## Tech Stack
- **Frontend**: React 19, Tailwind CSS, Framer Motion, shadcn/ui
- **Backend**: FastAPI, Motor (MongoDB async driver)
- **Database**: MongoDB
- **AI**: OpenAI GPT-5.2 via Emergent Integrations

## What's Been Implemented (February 2026)

### v1.0 - Base MVP ✅
- Homepage, Bonus Guide Pages, Sports News, Article Pages
- Admin Panel with CRUD operations
- AI Content Generation

### v5.0 - Match Hub Module ✅
1. **Robust Scores API** — cache (120s TTL) + retry + fallback (upcoming fixtures)
2. **MatchHub component** — structured cards, league badge, status (Live/Upcoming/Finished), score, 2 CTAs
3. **AI Mini-Insight** — featured match'e Gemini-flash ile tarafsız Türkçe analiz
4. **Match Detail Page** `/mac/:slug` — SEO schema (SportsEvent JSON-LD), AI analiz (ReactMarkdown), partner CTA + disclaimer
5. **Partner Tracking** `/api/go/{partner_id}/{match_id}` — MongoDB click log + redirect
6. **Admin Controls** — API status, AI toggle, featured match selection, cache refresh
7. **Rate limiter** — sports/tracking endpoint'leri limit dışı tutuldu
8. **Seed** — sessionStorage ile tek seferlik çalıştırma


1. **BonusRow.jsx** — Ranked horizontal list card (screenshot tasarımına uygun)
2. **HomePage.jsx** — Tam yeniden tasarım:
   - Compact hero + stadyum arka plan + neon grid
   - Canlı skor ticker (maçlar gösteriliyor)
   - Filtre tab'lı ranked bonus listesi (Tüm/Deneme/Hoşgeldin/Kayıp)
   - Görsel kategori slider (6 kategori, gerçek fotoğraflar)
   - Neden Bizi Seç bölümü
   - FAQ accordion + CTA banner
3. **Backend** — `/api/categories` endpoint eklendi (hardcoded 6 kategori)


1. **Bug Fixes (server.py)**
   - Rate limiter çift sayım sorunu düzeltildi
   - `ping_mongo()` guard clause eklendi
2. **CI/CD Pipeline** — `.github/workflows/` altında backend + frontend workflows
3. **Admin Authentication (JWT)**
   - `/api/auth/login` ve `/api/auth/verify` endpoint'leri
   - `bcrypt` ile hash'lenmiş şifre — `.env`'de saklı
   - Frontend: `LoginPage.js`, `ProtectedRoute.js`
   - `/admin` rotası korumalı, `/admin-login` yeni giriş sayfası
   - Admin sayfalarında navbar/footer/popup gizlendi


1. **AI Performance Ranking System**
   - Performance tracking (impressions, clicks, scroll, time)
   - Heuristic scoring when no data (bonus_value, turnover_req, rating)
   - Auto-update featured status for top 2 sites
   - Daily micro / weekly macro optimization ready

2. **Real Site List Integration**
   - 8 real affiliate sites with URLs
   - Turnover requirements displayed
   - Campaign start/end tracking
   - Archive functionality for ended campaigns

3. **SEO Assistant Tools**
   - Competitor domain analysis
   - Keyword gap analysis
   - Internal link suggestions
   - Weekly SEO report generation

4. **Content Freshness System**
   - content_updated_at only changes on real content updates
   - Content hash for change detection
   - Campaign archive system

## Database Schema
```
bonus_sites: {id, name, logo_url, bonus_type, bonus_amount, bonus_value, affiliate_url, 
              rating, features, turnover_requirement, campaign_start/end,
              cta_clicks, affiliate_clicks, impressions, avg_time_on_page, avg_scroll_depth,
              performance_score, is_featured, order, is_active, is_archived}

performance_events: {id, site_id, event_type, value, user_session, page_url, timestamp}

articles: {id, title, slug, content, content_hash, content_updated_at, ...}

seo_analysis: {id, analysis_type, target_url, keyword, results, suggestions}
```

## API Endpoints

### Performance Tracking
- POST /api/track/event - Track single event
- POST /api/track/batch - Track multiple events
- POST /api/ai/update-rankings - Trigger ranking update
- GET /api/ai/ranking-report - Get detailed ranking report

### SEO Tools
- POST /api/ai/competitor-analysis - Analyze competitor site
- POST /api/ai/keyword-gap-analysis - Find keyword opportunities
- GET /api/ai/weekly-seo-report - Generate weekly report
- POST /api/ai/internal-link-suggestions - Get link suggestions

## Prioritized Backlog

### P0 (Done) ✅
- [x] AI performance ranking system
- [x] Real site list integration
- [x] SEO assistant tools
- [x] Performance tracking infrastructure

### P1 (Next Phase)
- [ ] Real Football-Data.org API key for live data
- [ ] Automated daily content generation from sports data
- [ ] Email notification for ranking changes
- [ ] A/B testing for CTA buttons

### P2 (Future)
- [ ] Multi-language support
- [ ] User authentication for admin
- [ ] Scheduled reports via email
- [ ] Mobile app (PWA)

## Next Tasks
1. Collect real performance data to improve rankings
2. Set up scheduled ranking updates (cron job)
3. Integrate real sports API for automated content
4. Add Google Analytics integration for deeper insights
