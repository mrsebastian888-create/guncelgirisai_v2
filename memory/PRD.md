# Dynamic Sports & Bonus Authority Network (DSBN)

## Original Problem Statement
Spor içerikleri ve deneme bonusu rehberlerini birleştiren, SEO uyumlu, yapay zeka destekli ve kendi kendini güncelleyebilen bir içerik ağı. Sistem 3 ana içerik katmanından oluşur:
1. Ana Rehber Sayfalar (Money Pages) - Deneme Bonusu, 1000 TL Deneme Bonusu, Casino Bonusları
2. Güncel Spor İçerikleri (Freshness Engine) - Maç sonuçları, lig analizleri, transfer haberleri
3. İç Bağlantı Güç Aktarımı - Spor haberleri → Bonus rehberlerine link

## User Personas
- **Bonus Arayanlar**: Deneme ve hoşgeldin bonusu arayan yeni kullanıcılar
- **Spor Takipçileri**: Güncel maç sonuçları ve analizleri takip edenler
- **SEO Profesyonelleri**: İçerik optimizasyonu yapan site yöneticileri

## Core Requirements (Static)
- Türkçe dil desteği
- Dark mode neon yeşil tasarım
- Football-Data.org API entegrasyonu
- OpenAI GPT-5.2 ile AI içerik üretimi
- Admin paneli ile içerik yönetimi
- SEO uyumlu yapı

## Tech Stack
- **Frontend**: React 19, Tailwind CSS, Framer Motion, shadcn/ui
- **Backend**: FastAPI, Motor (MongoDB async driver)
- **Database**: MongoDB
- **AI**: OpenAI GPT-5.2 via Emergent Integrations

## What's Been Implemented (January 2026)

### MVP - Completed ✅
1. **Backend API** (server.py)
   - Bonus Sites CRUD endpoints
   - Articles CRUD endpoints
   - Categories system
   - AI Content Generation endpoint
   - SEO Analysis endpoint
   - Football Data API integration (demo mode)
   - Dashboard stats endpoint
   - Database seeding

2. **Frontend Pages**
   - Homepage with hero, bonus cards, live scores, FAQ
   - Bonus Guide Pages (/deneme-bonusu, /hosgeldin-bonusu)
   - Sports News Page with league selector
   - Article Detail Page
   - Admin Panel with tabs (Sites, Articles, AI Tools, SEO)

3. **Components**
   - Navbar with dropdown menu
   - Footer with links
   - BonusCard component
   - NewsCard component

4. **Database Seed Data**
   - 5 Bonus Sites (BetStar, WinMax, LuckBet, SportKing, CasinoPlus)
   - 3 Articles (Deneme Bonusu Rehberi, Derbi Analizi, Premier Lig Özet)
   - 7 Categories (4 bonus, 3 spor)

## Prioritized Backlog

### P0 (Critical)
- [x] Core bonus listing functionality
- [x] Sports news integration
- [x] AI content generation
- [x] Admin panel

### P1 (Important)
- [ ] User authentication system
- [ ] Real Football-Data.org API key integration
- [ ] Schema.org markup for SEO
- [ ] Article scheduling system

### P2 (Nice to Have)
- [ ] Multi-language support (English)
- [ ] Email newsletter integration
- [ ] Social media sharing buttons
- [ ] Analytics dashboard
- [ ] Competitor domain analysis
- [ ] Automatic SEO reports

## Next Tasks
1. Get real Football-Data.org API key for live match data
2. Implement schema.org structured data
3. Add user authentication for admin
4. Build automatic content scheduling system
5. Integrate competitor analysis feature
