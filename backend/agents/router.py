"""
GG2026 AI Agent API Router
Exposes all 5 agents as /api/agents/* endpoints.
"""
from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from .keyword_agent import KeywordIntelligenceAgent
from .content_agent import ContentGeneratorAgent
from .linking_agent import InternalLinkingAgent
from .update_agent import UpdateAgent
from .seo_agent import TechnicalSEOAgent

router = APIRouter(prefix="/agents", tags=["AI Agents"])

# ── Request models ───────────────────────────

class KeywordClusterRequest(BaseModel):
    keywords: List[str]
    niche: str = "bahis"

class KeywordIntentRequest(BaseModel):
    keywords: List[str]

class SERPOpportunityRequest(BaseModel):
    domain: str = "guncelgiris.ai"
    niche: str = "bahis"

class TopicDiscoverRequest(BaseModel):
    seed_topic: str
    depth: int = 2

class CompanyPageRequest(BaseModel):
    company_slug: str
    page_type: str

class HubPageRequest(BaseModel):
    hub_slug: str
    hub_type: str = "bonus"

class GuideRequest(BaseModel):
    topic: str
    target_keyword: str

class ArticleRequest(BaseModel):
    topic: str
    firms: Optional[List[str]] = None
    word_count: int = 600

class LinkSuggestRequest(BaseModel):
    page_url: str
    page_content: str = ""
    limit: int = 10

class RefreshPageRequest(BaseModel):
    company_slug: str
    page_type: str

class BulkTimestampRequest(BaseModel):
    company_slugs: Optional[List[str]] = None

class TitleGenRequest(BaseModel):
    pages: List[Dict[str, str]]

class DescGenRequest(BaseModel):
    pages: List[Dict[str, str]]

class ScanOutdatedRequest(BaseModel):
    days_threshold: int = 30


# ── Helper to get agent instances ────────────

def _get_db_and_key(request: Request):
    from server import db, EMERGENT_LLM_KEY
    return db, EMERGENT_LLM_KEY


# ── Agent Status ─────────────────────────────

@router.get("/status")
async def agents_status(request: Request):
    """Health check for all agents."""
    db, llm_key = _get_db_and_key(request)
    agents = [
        {"name": "keyword_intelligence", "actions": ["cluster", "intent", "opportunities", "discover"]},
        {"name": "content_generator", "actions": ["company_page", "hub_page", "guide", "article"]},
        {"name": "internal_linking", "actions": ["suggest", "audit_clusters", "orphans"]},
        {"name": "update", "actions": ["scan", "refresh", "timestamps"]},
        {"name": "technical_seo", "actions": ["titles", "descriptions", "canonicals", "sitemap_audit"]},
    ]
    total_jobs = await db.agent_jobs.count_documents({})
    completed = await db.agent_jobs.count_documents({"status": "completed"})
    failed = await db.agent_jobs.count_documents({"status": "failed"})
    return {
        "status": "operational",
        "llm_configured": bool(llm_key),
        "agents": agents,
        "jobs": {"total": total_jobs, "completed": completed, "failed": failed},
    }


@router.get("/jobs")
async def list_jobs(request: Request, limit: int = 20, agent: str = None, status: str = None):
    """List recent agent jobs."""
    db, _ = _get_db_and_key(request)
    query = {}
    if agent:
        query["agent"] = agent
    if status:
        query["status"] = status
    jobs = await db.agent_jobs.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return {"jobs": jobs, "count": len(jobs)}


@router.get("/jobs/{job_id}")
async def get_job(job_id: str, request: Request):
    """Get a specific job by ID."""
    db, _ = _get_db_and_key(request)
    job = await db.agent_jobs.find_one({"job_id": job_id}, {"_id": 0})
    if not job:
        raise HTTPException(status_code=404, detail="Job bulunamadi")
    return job


# ── Agent 1: Keyword Intelligence ────────────

@router.post("/keyword/cluster")
async def keyword_cluster(req: KeywordClusterRequest, request: Request):
    db, key = _get_db_and_key(request)
    agent = KeywordIntelligenceAgent(db, key)
    return await agent.cluster_keywords(req.keywords, req.niche)

@router.post("/keyword/intent")
async def keyword_intent(req: KeywordIntentRequest, request: Request):
    db, key = _get_db_and_key(request)
    agent = KeywordIntelligenceAgent(db, key)
    return await agent.detect_search_intent(req.keywords)

@router.post("/keyword/opportunities")
async def keyword_opportunities(req: SERPOpportunityRequest, request: Request):
    db, key = _get_db_and_key(request)
    agent = KeywordIntelligenceAgent(db, key)
    return await agent.detect_serp_opportunities(req.domain, req.niche)

@router.post("/keyword/discover")
async def keyword_discover(req: TopicDiscoverRequest, request: Request):
    db, key = _get_db_and_key(request)
    agent = KeywordIntelligenceAgent(db, key)
    return await agent.discover_topics(req.seed_topic, req.depth)


# ── Agent 2: Content Generator ───────────────

@router.post("/content/company-page")
async def content_company_page(req: CompanyPageRequest, request: Request):
    db, key = _get_db_and_key(request)
    agent = ContentGeneratorAgent(db, key)
    return await agent.generate_company_page(req.company_slug, req.page_type)

@router.post("/content/hub-page")
async def content_hub_page(req: HubPageRequest, request: Request):
    db, key = _get_db_and_key(request)
    agent = ContentGeneratorAgent(db, key)
    return await agent.generate_hub_page(req.hub_slug, req.hub_type)

@router.post("/content/guide")
async def content_guide(req: GuideRequest, request: Request):
    db, key = _get_db_and_key(request)
    agent = ContentGeneratorAgent(db, key)
    return await agent.generate_guide(req.topic, req.target_keyword)

@router.post("/content/article")
async def content_article(req: ArticleRequest, request: Request):
    db, key = _get_db_and_key(request)
    agent = ContentGeneratorAgent(db, key)
    return await agent.generate_article(req.topic, req.firms, req.word_count)


# ── Agent 3: Internal Linking ────────────────

@router.post("/linking/suggest")
async def linking_suggest(req: LinkSuggestRequest, request: Request):
    db, key = _get_db_and_key(request)
    agent = InternalLinkingAgent(db, key)
    return await agent.suggest_links(req.page_url, req.page_content, req.limit)

@router.post("/linking/audit")
async def linking_audit(request: Request):
    db, key = _get_db_and_key(request)
    agent = InternalLinkingAgent(db, key)
    return await agent.audit_clusters()

@router.post("/linking/orphans")
async def linking_orphans(request: Request):
    db, key = _get_db_and_key(request)
    agent = InternalLinkingAgent(db, key)
    return await agent.detect_orphans()


# ── Agent 4: Update Agent ────────────────────

@router.post("/update/scan")
async def update_scan(req: ScanOutdatedRequest, request: Request):
    db, key = _get_db_and_key(request)
    agent = UpdateAgent(db, key)
    return await agent.scan_outdated(req.days_threshold)

@router.post("/update/refresh")
async def update_refresh(req: RefreshPageRequest, request: Request):
    db, key = _get_db_and_key(request)
    agent = UpdateAgent(db, key)
    return await agent.refresh_page(req.company_slug, req.page_type)

@router.post("/update/timestamps")
async def update_timestamps(req: BulkTimestampRequest, request: Request):
    db, key = _get_db_and_key(request)
    agent = UpdateAgent(db, key)
    return await agent.bulk_update_timestamps(req.company_slugs)


# ── Agent 5: Technical SEO ───────────────────

@router.post("/seo/titles")
async def seo_titles(req: TitleGenRequest, request: Request):
    db, key = _get_db_and_key(request)
    agent = TechnicalSEOAgent(db, key)
    return await agent.generate_titles(req.pages)

@router.post("/seo/descriptions")
async def seo_descriptions(req: DescGenRequest, request: Request):
    db, key = _get_db_and_key(request)
    agent = TechnicalSEOAgent(db, key)
    return await agent.generate_descriptions(req.pages)

@router.post("/seo/canonicals")
async def seo_canonicals(request: Request):
    db, key = _get_db_and_key(request)
    agent = TechnicalSEOAgent(db, key)
    return await agent.audit_canonicals()

@router.post("/seo/sitemap-audit")
async def seo_sitemap_audit(request: Request):
    db, key = _get_db_and_key(request)
    agent = TechnicalSEOAgent(db, key)
    return await agent.audit_sitemap()
