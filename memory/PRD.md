# Dynamic Sports & Bonus Authority Network (DSBN) - v25.0

## Original Problem Statement
guncelgiris.ai sitesinin GG2026 SEO framework ile buyuk olcekli SEO buyumesine hazirlanmasi. Spor icerikleri ve deneme bonusu rehberlerini birlestiren, SEO uyumlu, AI destekli platform.

## What's Been Implemented

### v1-v22: Previous versions (see CHANGELOG.md)
### v23.0: GG2026 Phase 1 - Company folder architecture, hub pages, navigation, sitemap
### v24.0: GG2026 Phase 2 - Page templates, internal linking engine, FAQ, schema support

### v25.0: GG2026 Phase 3 - AI Agent Infrastructure (Mar 2026) - CURRENT

**5 modular AI agents:**

1. **Keyword Intelligence Agent** (`keyword_agent.py`)
   - `cluster` — Keyword clustering by topic
   - `intent` — Search intent classification
   - `opportunities` — SERP gap/opportunity detection
   - `discover` — Topic discovery from seed

2. **Content Generator Agent** (`content_agent.py`)
   - `company_page` — Company sub-page content (stored in agent_generated_content)
   - `hub_page` — Hub page content generation
   - `guide` — Comprehensive guide articles
   - `article` — SEO articles with firm mentions

3. **Internal Linking Agent** (`linking_agent.py`)
   - `suggest` — AI-powered link suggestions for any page
   - `audit_clusters` — Topical cluster health/coverage audit
   - `orphans` — Orphan page detection

4. **Update Agent** (`update_agent.py`)
   - `scan` — Detect outdated content by days threshold
   - `refresh` — AI-refresh specific company page content
   - `timestamps` — Bulk timestamp updates

5. **Technical SEO Agent** (`seo_agent.py`)
   - `titles` — AI-generated page titles (max 60 char)
   - `descriptions` — AI-generated meta descriptions (max 160 char)
   - `canonicals` — Canonical tag audit (2388 pages audited)
   - `sitemap_audit` — Sitemap completeness check

**Infrastructure:**
- BaseAgent class with MongoDB job tracking (agent_jobs collection)
- Generated content stored in agent_generated_content collection
- 21 API endpoints under /api/agents/*
- 12 LLM-powered + 9 non-LLM endpoints
- Each operation creates a tracked job with status, duration_ms

## Architecture
```
/app/backend/
├── agents/
│   ├── __init__.py          # Package exports
│   ├── base.py              # BaseAgent, AgentJob, AgentResult
│   ├── keyword_agent.py     # Agent 1: Keyword Intelligence
│   ├── content_agent.py     # Agent 2: Content Generator
│   ├── linking_agent.py     # Agent 3: Internal Linking
│   ├── update_agent.py      # Agent 4: Update Agent
│   ├── seo_agent.py         # Agent 5: Technical SEO
│   └── router.py            # FastAPI router (21 endpoints)
├── server.py                # Main app (includes agents_router)
└── ...existing files
```

## Key API Endpoints
```
GET  /api/agents/status              # All agents health
GET  /api/agents/jobs                # Job list (filter by agent/status)
GET  /api/agents/jobs/{job_id}       # Job details
POST /api/agents/keyword/cluster     # Keyword clustering
POST /api/agents/keyword/intent      # Intent classification
POST /api/agents/keyword/opportunities # SERP gaps
POST /api/agents/keyword/discover    # Topic discovery
POST /api/agents/content/company-page # Company page content
POST /api/agents/content/hub-page    # Hub page content
POST /api/agents/content/guide       # Guide generation
POST /api/agents/content/article     # Article generation
POST /api/agents/linking/suggest     # Link suggestions
POST /api/agents/linking/audit       # Cluster audit
POST /api/agents/linking/orphans     # Orphan detection
POST /api/agents/update/scan         # Outdated scan
POST /api/agents/update/refresh      # Page refresh
POST /api/agents/update/timestamps   # Bulk timestamps
POST /api/agents/seo/titles          # Title generation
POST /api/agents/seo/descriptions    # Meta desc generation
POST /api/agents/seo/canonicals      # Canonical audit
POST /api/agents/seo/sitemap-audit   # Sitemap audit
```

## DB Collections (new)
- `agent_jobs` — Job tracking (job_id, agent, action, status, params, result, duration_ms)
- `agent_generated_content` — AI-generated page content (company_slug, page_type, title, sections, faq)

## Prioritized Backlog

### P0 - Critical
- Production domain (guncelgiris.ai) - BLOCKED on Emergent support

### P1 - High Priority
- GG2026 Phase 4+ (as user requests)
- Admin UI for agent management (trigger, monitor, review)
- Telegram BotFather rate limit solution

### P2 - Medium Priority
- AI Video Generation, Company Intelligence Score
- AMP pages fix

### P3 - Backlog
- Backend refactoring (server.py modular structure)
