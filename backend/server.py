from fastapi import FastAPI, APIRouter, HTTPException, Query, Request, Depends
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import httpx
import re
import json
import hashlib
import asyncio

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Environment variables
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')
FOOTBALL_API_KEY = os.environ.get('FOOTBALL_DATA_API_KEY', 'demo')
CLOUDFLARE_API_TOKEN = os.environ.get('CLOUDFLARE_API_TOKEN', '')
CLOUDFLARE_ACCOUNT_ID = os.environ.get('CLOUDFLARE_ACCOUNT_ID', '')

# Create the main app
app = FastAPI(title="Multi-Tenant Authority Platform API")
api_router = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============== PYDANTIC MODELS ==============

# DOMAIN / MULTI-TENANT MODELS
class Domain(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    domain_name: str  # example.com
    display_name: str  # Site display name
    focus: str = "bonus"  # bonus, spor, hibrit
    theme: Dict[str, str] = {}  # primary_color, secondary_color, etc.
    logo_url: str = ""
    favicon_url: str = ""
    # Cloudflare integration
    cloudflare_zone_id: Optional[str] = None
    cloudflare_status: str = "pending"  # pending, active, error
    nameservers: List[str] = []
    ssl_status: str = "pending"
    # Settings
    is_active: bool = True
    meta_title: str = ""
    meta_description: str = ""
    google_analytics_id: str = ""
    # Auto content settings
    auto_article_enabled: bool = True
    auto_news_enabled: bool = True
    content_language: str = "tr"
    # Timestamps
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class DomainCreate(BaseModel):
    domain_name: str
    display_name: str
    focus: str = "bonus"
    theme: Dict[str, str] = {}
    logo_url: str = ""
    meta_title: str = ""
    meta_description: str = ""

class DomainSite(BaseModel):
    """Links bonus sites to specific domains"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    domain_id: str
    site_id: str  # Reference to BonusSite
    custom_order: int = 0
    is_active: bool = True

class BonusSite(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    logo_url: str
    bonus_type: str
    bonus_amount: str
    bonus_value: int = 0
    affiliate_url: str
    rating: float = 4.5
    features: List[str] = []
    turnover_requirement: float = 10.0
    # Performance (per domain tracked separately)
    global_cta_clicks: int = 0
    global_affiliate_clicks: int = 0
    global_impressions: int = 0
    # Status
    is_active: bool = True
    is_global: bool = True  # Available to all domains
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class DomainPerformance(BaseModel):
    """Track performance per domain per site"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    domain_id: str
    site_id: str
    impressions: int = 0
    cta_clicks: int = 0
    affiliate_clicks: int = 0
    avg_time_on_page: float = 0.0
    avg_scroll_depth: float = 0.0
    performance_score: float = 0.0
    is_featured: bool = False
    rank: int = 0
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class Article(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    domain_id: Optional[str] = None  # None = global article
    title: str
    slug: str
    excerpt: str
    content: str
    category: str
    tags: List[str] = []
    image_url: str = ""
    author: str = "Admin"
    is_published: bool = True
    is_ai_generated: bool = False
    is_auto_generated: bool = False  # Auto article engine
    seo_title: str = ""
    seo_description: str = ""
    schema_type: str = "Article"  # Article, FAQ, NewsArticle
    internal_links: List[str] = []
    view_count: int = 0
    content_hash: str = ""
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    content_updated_at: Optional[str] = None

class AutoContentJob(BaseModel):
    """Scheduled auto content generation jobs"""
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    domain_id: Optional[str] = None
    job_type: str  # article, news, seo_update
    topic: str
    status: str = "pending"  # pending, running, completed, failed
    result: Dict[str, Any] = {}
    scheduled_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None

class Category(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    domain_id: Optional[str] = None
    name: str
    slug: str
    description: str = ""
    type: str
    order: int = 0

class PerformanceEventCreate(BaseModel):
    domain_id: str
    site_id: str
    event_type: str
    value: float = 1.0
    user_session: str = ""
    page_url: str = ""

class KeywordGapRequest(BaseModel):
    keywords: List[str]
    competitor_keywords: List[str] = []

# ============== HELPER FUNCTIONS ==============

def slugify(text: str) -> str:
    text = text.lower()
    for old, new in [('ı', 'i'), ('İ', 'i'), ('ş', 's'), ('Ş', 's'), ('ğ', 'g'), ('Ğ', 'g'), 
                     ('ü', 'u'), ('Ü', 'u'), ('ö', 'o'), ('Ö', 'o'), ('ç', 'c'), ('Ç', 'c')]:
        text = text.replace(old, new)
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-')

def extract_bonus_value(bonus_amount: str) -> int:
    numbers = re.findall(r'\d+', bonus_amount.replace('.', '').replace(',', ''))
    return int(numbers[0]) if numbers else 0

async def generate_ai_content(prompt: str, system_message: str = "Sen profesyonel bir Türkçe içerik yazarısın.") -> str:
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=str(uuid.uuid4()), system_message=system_message).with_model("openai", "gpt-5.2")
        return await chat.send_message(UserMessage(text=prompt))
    except Exception as e:
        logger.error(f"AI error: {e}")
        return f"AI hatası: {str(e)}"

def calculate_heuristic_score(site: dict) -> float:
    score = min(site.get('bonus_value', 0) / 25, 40)
    score += max(0, 20 - site.get('turnover_requirement', 10))
    score += site.get('rating', 4.0) * 4
    return score

def calculate_performance_score(perf: dict) -> float:
    impressions = max(perf.get('impressions', 0), 1)
    cta_clicks = perf.get('cta_clicks', 0)
    cta_rate = (cta_clicks / impressions) * 100
    score = min(cta_rate * 10, 30)
    score += min(perf.get('avg_time_on_page', 0) / 10, 20)
    score += min(perf.get('avg_scroll_depth', 0) / 4, 25)
    return score

# ============== CLOUDFLARE INTEGRATION ==============

async def cloudflare_create_zone(domain_name: str) -> Dict[str, Any]:
    """Create zone in Cloudflare"""
    if not CLOUDFLARE_API_TOKEN or not CLOUDFLARE_ACCOUNT_ID:
        return {"error": "Cloudflare credentials not configured", "status": "skipped"}
    
    try:
        async with httpx.AsyncClient() as http:
            response = await http.post(
                "https://api.cloudflare.com/client/v4/zones",
                headers={"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}", "Content-Type": "application/json"},
                json={"name": domain_name, "account": {"id": CLOUDFLARE_ACCOUNT_ID}, "type": "full"}
            )
            data = response.json()
            if data.get("success"):
                result = data["result"]
                return {
                    "zone_id": result["id"],
                    "nameservers": result.get("name_servers", []),
                    "status": result.get("status", "pending")
                }
            return {"error": data.get("errors", []), "status": "error"}
    except Exception as e:
        logger.error(f"Cloudflare error: {e}")
        return {"error": str(e), "status": "error"}

async def cloudflare_add_dns_records(zone_id: str, domain_name: str, target_ip: str = "76.76.21.21") -> Dict[str, Any]:
    """Add A and CNAME records"""
    if not CLOUDFLARE_API_TOKEN:
        return {"status": "skipped"}
    
    records = [
        {"type": "A", "name": domain_name, "content": target_ip, "proxied": True},
        {"type": "CNAME", "name": f"www.{domain_name}", "content": domain_name, "proxied": True}
    ]
    
    results = []
    async with httpx.AsyncClient() as http:
        for record in records:
            try:
                response = await http.post(
                    f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records",
                    headers={"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}", "Content-Type": "application/json"},
                    json=record
                )
                results.append(response.json())
            except Exception as e:
                results.append({"error": str(e)})
    
    return {"records_created": len(results), "results": results}

async def cloudflare_enable_ssl(zone_id: str) -> Dict[str, Any]:
    """Enable SSL for zone"""
    if not CLOUDFLARE_API_TOKEN:
        return {"status": "skipped"}
    
    try:
        async with httpx.AsyncClient() as http:
            # Set SSL mode to Full
            await http.patch(
                f"https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/ssl",
                headers={"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}", "Content-Type": "application/json"},
                json={"value": "full"}
            )
            # Enable HTTPS redirect
            await http.patch(
                f"https://api.cloudflare.com/client/v4/zones/{zone_id}/settings/always_use_https",
                headers={"Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}", "Content-Type": "application/json"},
                json={"value": "on"}
            )
            return {"ssl_mode": "full", "https_redirect": "on"}
    except Exception as e:
        return {"error": str(e)}

# ============== DOMAIN MANAGEMENT ENDPOINTS ==============

@api_router.get("/")
async def root():
    return {"message": "Multi-Tenant Authority Platform API", "version": "3.0.0"}

@api_router.post("/domains", response_model=Domain)
async def create_domain(domain: DomainCreate):
    """Create a new domain with Cloudflare automation"""
    # Check if domain exists
    existing = await db.domains.find_one({"domain_name": domain.domain_name})
    if existing:
        raise HTTPException(status_code=400, detail="Domain already exists")
    
    domain_obj = Domain(**domain.model_dump())
    
    # Create Cloudflare zone
    cf_result = await cloudflare_create_zone(domain.domain_name)
    if cf_result.get("zone_id"):
        domain_obj.cloudflare_zone_id = cf_result["zone_id"]
        domain_obj.nameservers = cf_result.get("nameservers", [])
        domain_obj.cloudflare_status = cf_result.get("status", "pending")
        
        # Add DNS records
        await cloudflare_add_dns_records(cf_result["zone_id"], domain.domain_name)
        
        # Enable SSL
        ssl_result = await cloudflare_enable_ssl(cf_result["zone_id"])
        domain_obj.ssl_status = "active" if not ssl_result.get("error") else "pending"
    
    await db.domains.insert_one(domain_obj.model_dump())
    
    # Copy global sites to this domain
    global_sites = await db.bonus_sites.find({"is_global": True, "is_active": True}, {"_id": 0}).to_list(100)
    for site in global_sites:
        domain_site = DomainSite(domain_id=domain_obj.id, site_id=site["id"])
        await db.domain_sites.insert_one(domain_site.model_dump())
        # Create performance record
        perf = DomainPerformance(domain_id=domain_obj.id, site_id=site["id"], performance_score=calculate_heuristic_score(site))
        await db.domain_performance.insert_one(perf.model_dump())
    
    return domain_obj

@api_router.get("/domains")
async def list_domains():
    """List all domains"""
    domains = await db.domains.find({}, {"_id": 0}).to_list(100)
    return domains

@api_router.get("/domains/{domain_id}")
async def get_domain(domain_id: str):
    """Get domain details"""
    domain = await db.domains.find_one({"id": domain_id}, {"_id": 0})
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    return domain

@api_router.get("/domains/by-name/{domain_name}")
async def get_domain_by_name(domain_name: str):
    """Get domain by domain name"""
    domain = await db.domains.find_one({"domain_name": domain_name}, {"_id": 0})
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    return domain

@api_router.delete("/domains/{domain_id}")
async def delete_domain(domain_id: str):
    """Delete a domain"""
    await db.domains.delete_one({"id": domain_id})
    await db.domain_sites.delete_many({"domain_id": domain_id})
    await db.domain_performance.delete_many({"domain_id": domain_id})
    await db.articles.delete_many({"domain_id": domain_id})
    return {"message": "Domain deleted"}

# ============== DOMAIN-SPECIFIC SITE MANAGEMENT ==============

@api_router.get("/domains/{domain_id}/sites")
async def get_domain_sites(domain_id: str):
    """Get sites for a specific domain, sorted by performance"""
    # Get domain site mappings
    domain_sites = await db.domain_sites.find({"domain_id": domain_id, "is_active": True}, {"_id": 0}).to_list(100)
    site_ids = [ds["site_id"] for ds in domain_sites]
    
    # Get performances
    performances = await db.domain_performance.find({"domain_id": domain_id}, {"_id": 0}).sort("performance_score", -1).to_list(100)
    perf_map = {p["site_id"]: p for p in performances}
    
    # Get sites
    sites = await db.bonus_sites.find({"id": {"$in": site_ids}, "is_active": True}, {"_id": 0}).to_list(100)
    
    # Merge and sort
    result = []
    for site in sites:
        perf = perf_map.get(site["id"], {})
        site["performance_score"] = perf.get("performance_score", 0)
        site["is_featured"] = perf.get("is_featured", False)
        site["rank"] = perf.get("rank", 99)
        result.append(site)
    
    result.sort(key=lambda x: x["performance_score"], reverse=True)
    for i, site in enumerate(result):
        site["rank"] = i + 1
        site["is_featured"] = i < 2
    
    return result

@api_router.post("/domains/{domain_id}/sites/{site_id}/add")
async def add_site_to_domain(domain_id: str, site_id: str):
    """Add a site to a domain"""
    existing = await db.domain_sites.find_one({"domain_id": domain_id, "site_id": site_id})
    if existing:
        await db.domain_sites.update_one({"domain_id": domain_id, "site_id": site_id}, {"$set": {"is_active": True}})
    else:
        domain_site = DomainSite(domain_id=domain_id, site_id=site_id)
        await db.domain_sites.insert_one(domain_site.model_dump())
        site = await db.bonus_sites.find_one({"id": site_id}, {"_id": 0})
        if site:
            perf = DomainPerformance(domain_id=domain_id, site_id=site_id, performance_score=calculate_heuristic_score(site))
            await db.domain_performance.insert_one(perf.model_dump())
    return {"message": "Site added to domain"}

@api_router.post("/domains/{domain_id}/sites/{site_id}/remove")
async def remove_site_from_domain(domain_id: str, site_id: str):
    """Remove a site from a domain"""
    await db.domain_sites.update_one({"domain_id": domain_id, "site_id": site_id}, {"$set": {"is_active": False}})
    return {"message": "Site removed from domain"}

# ============== PERFORMANCE TRACKING ==============

@api_router.post("/track/event")
async def track_event(event: PerformanceEventCreate):
    """Track performance event for domain-site pair"""
    update = {}
    if event.event_type == "cta_click":
        update = {"$inc": {"cta_clicks": 1}}
    elif event.event_type == "affiliate_click":
        update = {"$inc": {"affiliate_clicks": 1}}
    elif event.event_type == "impression":
        update = {"$inc": {"impressions": 1}}
    
    if update:
        await db.domain_performance.update_one(
            {"domain_id": event.domain_id, "site_id": event.site_id},
            {**update, "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}},
            upsert=True
        )
    
    return {"status": "tracked"}

@api_router.post("/domains/{domain_id}/update-rankings")
async def update_domain_rankings(domain_id: str):
    """Update site rankings for a domain based on performance"""
    performances = await db.domain_performance.find({"domain_id": domain_id}, {"_id": 0}).to_list(100)
    
    for perf in performances:
        site = await db.bonus_sites.find_one({"id": perf["site_id"]}, {"_id": 0})
        if not site:
            continue
        
        has_data = perf.get("impressions", 0) > 10
        if has_data:
            score = calculate_performance_score(perf)
        else:
            score = calculate_heuristic_score(site)
        
        await db.domain_performance.update_one(
            {"domain_id": domain_id, "site_id": perf["site_id"]},
            {"$set": {"performance_score": score}}
        )
    
    # Update ranks and featured status
    performances = await db.domain_performance.find({"domain_id": domain_id}, {"_id": 0}).sort("performance_score", -1).to_list(100)
    for i, perf in enumerate(performances):
        await db.domain_performance.update_one(
            {"domain_id": domain_id, "site_id": perf["site_id"]},
            {"$set": {"rank": i + 1, "is_featured": i < 2}}
        )
    
    return {"updated": len(performances)}

# ============== GLOBAL BONUS SITES ==============

@api_router.get("/bonus-sites")
async def get_all_bonus_sites(limit: int = 50):
    """Get all global bonus sites"""
    sites = await db.bonus_sites.find({"is_active": True}, {"_id": 0}).to_list(limit)
    return sites

@api_router.post("/bonus-sites")
async def create_bonus_site(site: Dict[str, Any]):
    """Create a new global bonus site"""
    site_obj = BonusSite(**site)
    site_obj.bonus_value = extract_bonus_value(site_obj.bonus_amount)
    await db.bonus_sites.insert_one(site_obj.model_dump())
    return site_obj

@api_router.delete("/bonus-sites/{site_id}")
async def delete_bonus_site(site_id: str):
    await db.bonus_sites.delete_one({"id": site_id})
    return {"message": "Site deleted"}

# ============== ARTICLES (DOMAIN-SPECIFIC) ==============

@api_router.get("/domains/{domain_id}/articles")
async def get_domain_articles(domain_id: str, limit: int = 20):
    """Get articles for a domain (including global articles)"""
    articles = await db.articles.find(
        {"$or": [{"domain_id": domain_id}, {"domain_id": None}], "is_published": True},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit).to_list(limit)
    return articles

@api_router.post("/domains/{domain_id}/articles")
async def create_domain_article(domain_id: str, article: Dict[str, Any]):
    """Create article for a domain"""
    article["domain_id"] = domain_id
    if not article.get("slug"):
        article["slug"] = slugify(article["title"])
    article["content_hash"] = hashlib.md5(article.get("content", "").encode()).hexdigest()
    article["content_updated_at"] = datetime.now(timezone.utc).isoformat()
    article_obj = Article(**article)
    await db.articles.insert_one(article_obj.model_dump())
    return article_obj

@api_router.get("/articles")
async def get_all_articles(limit: int = 50):
    articles = await db.articles.find({"is_published": True}, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return articles

# ============== AUTO CONTENT ENGINE ==============

@api_router.post("/auto-content/generate-article")
async def auto_generate_article(domain_id: Optional[str] = None, topic: str = "deneme bonusu rehberi"):
    """Auto generate SEO article"""
    # Check if similar article exists
    existing = await db.articles.find_one({"title": {"$regex": topic, "$options": "i"}, "domain_id": domain_id})
    if existing:
        return {"status": "skipped", "reason": "Similar article exists", "article_id": existing.get("id")}
    
    prompt = f"""
    Konu: {topic}
    
    SEO uyumlu, özgün bir makale yaz. Yapı:
    1. H2 başlıkları kullan
    2. Detaylı açıklamalar ekle
    3. Liste ve maddeler kullan
    4. 800-1000 kelime
    5. Doğal iç link yerleri için [İÇ_LİNK: konu] işaretle
    6. FAQ bölümü ekle (3-4 soru)
    
    İçeriğin %80'i bilgilendirici, %20'si doğal yönlendirme olsun.
    Spam CTA kullanma.
    
    HTML formatında yaz (<h2>, <p>, <ul>, <li> kullan).
    """
    
    content = await generate_ai_content(prompt, "Sen Türkçe SEO içerik uzmanısın. Google E-E-A-T kriterlerine uygun içerik üretirsin.")
    
    article = Article(
        domain_id=domain_id,
        title=topic.title(),
        slug=slugify(topic),
        excerpt=f"{topic} hakkında detaylı rehber ve güncel bilgiler.",
        content=content,
        category="bonus",
        tags=[slugify(t) for t in topic.split()],
        is_ai_generated=True,
        is_auto_generated=True,
        schema_type="Article",
        content_hash=hashlib.md5(content.encode()).hexdigest(),
        content_updated_at=datetime.now(timezone.utc).isoformat()
    )
    
    await db.articles.insert_one(article.model_dump())
    return {"status": "created", "article_id": article.id, "title": article.title}

@api_router.post("/auto-content/generate-news")
async def auto_generate_news(domain_id: Optional[str] = None):
    """Auto generate sports news from API data"""
    # Get match data
    matches = await get_demo_matches("PL")
    if not matches.get("matches"):
        return {"status": "no_data"}
    
    match = matches["matches"][0]
    topic = f"{match['home_team']} vs {match['away_team']} Maç Analizi"
    
    prompt = f"""
    Maç: {match['home_team']} {match.get('home_score', '?')} - {match.get('away_score', '?')} {match['away_team']}
    Lig: {match.get('league', 'Premier League')}
    
    Bu maç için kısa ve etkileyici bir haber/analiz yaz:
    1. Skor özeti
    2. Önemli anlar
    3. Oyuncu performansları
    4. Sonraki maç beklentisi
    
    200-300 kelime. Doğal bir şekilde "bahis analizleri için sitemizi ziyaret edin" gibi bir cümle ekle.
    HTML formatında yaz.
    """
    
    content = await generate_ai_content(prompt, "Sen spor gazetecisisin.")
    
    article = Article(
        domain_id=domain_id,
        title=topic,
        slug=slugify(topic),
        excerpt=f"{match['home_team']} - {match['away_team']} maç özeti ve analizi.",
        content=content,
        category="spor",
        tags=["futbol", slugify(match['home_team']), slugify(match['away_team'])],
        is_ai_generated=True,
        is_auto_generated=True,
        schema_type="NewsArticle",
        content_hash=hashlib.md5(content.encode()).hexdigest(),
        content_updated_at=datetime.now(timezone.utc).isoformat()
    )
    
    await db.articles.insert_one(article.model_dump())
    return {"status": "created", "article_id": article.id, "title": article.title}

@api_router.post("/auto-content/bulk-generate")
async def bulk_generate_content(domain_id: Optional[str] = None, count: int = 5):
    """Bulk generate content for a domain"""
    topics = [
        "Deneme Bonusu Nedir Nasıl Alınır 2026",
        "En Yüksek Hoşgeldin Bonusu Veren Siteler",
        "Çevrim Şartı Nedir Nasıl Hesaplanır",
        "Yatırımsız Bonus Fırsatları Rehberi",
        "Canlı Bahis Stratejileri ve Taktikleri",
        "Casino Kayıp Bonusu Nasıl Kullanılır",
        "Mobil Bahis Uygulamaları Karşılaştırma",
        "Bahis Sitesi Seçerken Dikkat Edilecekler"
    ]
    
    results = []
    for topic in topics[:count]:
        result = await auto_generate_article(domain_id, topic)
        results.append(result)
        await asyncio.sleep(1)  # Rate limiting
    
    return {"generated": len([r for r in results if r.get("status") == "created"]), "results": results}

# ============== AI & SEO TOOLS ==============

@api_router.post("/ai/generate-content")
async def generate_content(request: Dict[str, Any]):
    """Generate AI content"""
    topic = request.get("topic", "")
    content_type = request.get("content_type", "article")
    
    if content_type == "article":
        prompt = f"Konu: {topic}\n\nSEO uyumlu, 800 kelimelik makale yaz. HTML formatında."
    elif content_type == "faq":
        prompt = f"Konu: {topic}\n\n5 soru-cevap içeren FAQ bölümü yaz. Schema.org FAQ formatına uygun."
    else:
        prompt = topic
    
    content = await generate_ai_content(prompt)
    return {"content": content, "generated_at": datetime.now(timezone.utc).isoformat()}

@api_router.post("/ai/competitor-analysis")
async def competitor_analysis(request: Dict[str, Any]):
    """Analyze competitor domain"""
    url = request.get("competitor_url", "")
    prompt = f"""
    Rakip Site: {url}
    
    Analiz et:
    1. Site yapısı tahmini
    2. İçerik stratejisi
    3. SEO güçlü/zayıf yönler
    4. Bizim için fırsatlar
    5. Aksiyon önerileri
    
    Kopyalama önerme, özgün strateji sun.
    """
    
    content = await generate_ai_content(prompt, "Sen SEO analisti ve rakip araştırma uzmanısın.")
    return {"analysis": content, "url": url}

@api_router.post("/ai/keyword-gap-analysis")
async def keyword_gap_analysis(request: KeywordGapRequest):
    """Find keyword opportunities"""
    prompt = f"""
    Mevcut Kelimeler: {', '.join(request.keywords)}
    
    Türkçe bahis/bonus sektörü için:
    1. Kaçırılan fırsatlar
    2. Long-tail önerileri
    3. İçerik planı
    4. Öncelik sıralaması
    """
    
    content = await generate_ai_content(prompt, "Sen SEO anahtar kelime uzmanısın.")
    return {"analysis": content, "keywords": request.keywords}

@api_router.get("/ai/weekly-seo-report")
async def weekly_seo_report(domain_id: Optional[str] = None):
    """Generate weekly SEO report"""
    stats = {
        "total_articles": await db.articles.count_documents({"domain_id": domain_id} if domain_id else {}),
        "total_domains": await db.domains.count_documents({}),
        "total_sites": await db.bonus_sites.count_documents({"is_active": True})
    }
    
    prompt = f"""
    Haftalık SEO Raporu:
    - Toplam Makale: {stats['total_articles']}
    - Aktif Domain: {stats['total_domains']}
    - Bonus Sitesi: {stats['total_sites']}
    
    Özet ve öneriler sun:
    1. Performans değerlendirmesi
    2. İçerik önerileri
    3. Gelecek hafta aksiyonları
    """
    
    content = await generate_ai_content(prompt, "Sen SEO raporlama uzmanısın.")
    return {"report": content, "stats": stats}

# ============== SPORTS API ==============

@api_router.get("/sports/matches")
async def get_matches(league: str = "PL"):
    return await get_demo_matches(league)

async def get_demo_matches(league: str):
    return {
        "matches": [
            {"home_team": "Galatasaray", "away_team": "Fenerbahçe", "home_score": 2, "away_score": 1, "league": "Süper Lig", "status": "FINISHED"},
            {"home_team": "Beşiktaş", "away_team": "Trabzonspor", "home_score": 1, "away_score": 1, "league": "Süper Lig", "status": "FINISHED"},
            {"home_team": "Arsenal", "away_team": "Chelsea", "home_score": 3, "away_score": 1, "league": "Premier League", "status": "FINISHED"},
        ],
        "competition": league
    }

# ============== STATS ==============

@api_router.get("/stats/dashboard")
async def get_dashboard_stats(domain_id: Optional[str] = None):
    query = {"domain_id": domain_id} if domain_id else {}
    return {
        "total_domains": await db.domains.count_documents({}),
        "total_articles": await db.articles.count_documents(query if domain_id else {}),
        "total_bonus_sites": await db.bonus_sites.count_documents({"is_active": True}),
        "auto_generated_articles": await db.articles.count_documents({**query, "is_auto_generated": True} if domain_id else {"is_auto_generated": True})
    }

# ============== SCHEMA MARKUP HELPER ==============

@api_router.get("/schema/{article_id}")
async def get_article_schema(article_id: str):
    """Get JSON-LD schema for article"""
    article = await db.articles.find_one({"id": article_id}, {"_id": 0})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    schema = {
        "@context": "https://schema.org",
        "@type": article.get("schema_type", "Article"),
        "headline": article["title"],
        "description": article.get("seo_description") or article["excerpt"],
        "datePublished": article["created_at"],
        "dateModified": article.get("content_updated_at") or article["updated_at"],
        "author": {"@type": "Person", "name": article.get("author", "Admin")}
    }
    
    if article.get("image_url"):
        schema["image"] = article["image_url"]
    
    return schema

# ============== SEED DATA ==============

@api_router.post("/seed")
async def seed_database():
    """Seed with initial data"""
    await db.bonus_sites.delete_many({})
    await db.domains.delete_many({})
    await db.domain_sites.delete_many({})
    await db.domain_performance.delete_many({})
    await db.articles.delete_many({})
    
    # Global bonus sites
    sites = [
        {"name": "MAXWIN", "logo_url": "https://images.unsplash.com/photo-1709873582570-4f17d43921d4?w=100&h=100&fit=crop", "bonus_type": "deneme", "bonus_amount": "750 TL", "affiliate_url": "https://cutt.ly/glockmaxwn", "rating": 4.9, "features": ["Hızlı Ödeme", "7/24 Destek"], "turnover_requirement": 8.0},
        {"name": "HILTONBET", "logo_url": "https://images.unsplash.com/photo-1763089221979-ebb2a748358a?w=100&h=100&fit=crop", "bonus_type": "deneme", "bonus_amount": "500 TL", "affiliate_url": "https://hiltonbetortak.com/affiliates/?btag=2652418", "rating": 4.8, "features": ["Yüksek Oranlar", "Canlı Bahis"], "turnover_requirement": 10.0},
        {"name": "ELEXBET", "logo_url": "https://images.unsplash.com/photo-1678696419211-6e0fb533c95e?w=100&h=100&fit=crop", "bonus_type": "hosgeldin", "bonus_amount": "1000 TL", "affiliate_url": "https://go.aff.elexbetpro.com/syq46dzq", "rating": 4.7, "features": ["Yatırım Bonusu"], "turnover_requirement": 12.0},
        {"name": "FESTWIN", "logo_url": "https://images.unsplash.com/photo-1762278804798-dd7e493db051?w=100&h=100&fit=crop", "bonus_type": "kayip", "bonus_amount": "%15 Kayıp", "affiliate_url": "https://t2m.co/gmfest", "rating": 4.6, "features": ["Kayıp Bonusu"], "turnover_requirement": 5.0},
        {"name": "CASINO DIOR", "logo_url": "https://images.pexels.com/photos/7594162/pexels-photo-7594162.jpeg?w=100&h=100&fit=crop", "bonus_type": "hosgeldin", "bonus_amount": "2000 TL", "affiliate_url": "https://www.diorlink.com/links/?btag=2481426", "rating": 4.8, "features": ["Casino", "VIP"], "turnover_requirement": 15.0},
        {"name": "BETCI", "logo_url": "https://images.unsplash.com/photo-1741089731004-3c17efa3e381?w=100&h=100&fit=crop", "bonus_type": "deneme", "bonus_amount": "500 TL", "affiliate_url": "https://betcilink2.com/affiliates/?btag=2482990", "rating": 4.5, "features": ["Spor Bahisleri"], "turnover_requirement": 10.0},
        {"name": "ALFABAHIS", "logo_url": "https://images.pexels.com/photos/12616082/pexels-photo-12616082.jpeg?w=100&h=100&fit=crop", "bonus_type": "deneme", "bonus_amount": "600 TL", "affiliate_url": "https://alfabahisaff10.com/affiliates/?btag=2482989", "rating": 4.6, "features": ["Mobil Uygulama"], "turnover_requirement": 8.0},
        {"name": "TULIPBET", "logo_url": "https://images.pexels.com/photos/6203470/pexels-photo-6203470.jpeg?w=100&h=100&fit=crop", "bonus_type": "hosgeldin", "bonus_amount": "1500 TL", "affiliate_url": "https://tulipbetortaklik.com/upw8v0ar", "rating": 4.7, "features": ["Free Spin"], "turnover_requirement": 12.0},
    ]
    
    for site in sites:
        site_obj = BonusSite(**site)
        site_obj.bonus_value = extract_bonus_value(site_obj.bonus_amount)
        await db.bonus_sites.insert_one(site_obj.model_dump())
    
    return {"message": "Seeded", "sites": len(sites)}

# ============== APP SETUP ==============

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
