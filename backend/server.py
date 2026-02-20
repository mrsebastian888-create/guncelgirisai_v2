from fastapi import FastAPI, APIRouter, HTTPException, Query, Request
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

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Environment variables
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY', '')
FOOTBALL_API_KEY = os.environ.get('FOOTBALL_DATA_API_KEY', 'demo')

# Create the main app
app = FastAPI(title="Dynamic Sports & Bonus Network API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============== PYDANTIC MODELS ==============

class BonusSite(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    logo_url: str
    bonus_type: str  # deneme, hosgeldin, yatirim, kayip
    bonus_amount: str  # "1000 TL", "500 TL"
    bonus_value: int = 0  # Numeric value for sorting (e.g., 1000)
    affiliate_url: str
    rating: float = 4.5
    features: List[str] = []
    is_featured: bool = False
    order: int = 0
    # Performance metrics
    cta_clicks: int = 0
    affiliate_clicks: int = 0
    impressions: int = 0
    avg_time_on_page: float = 0.0  # seconds
    avg_scroll_depth: float = 0.0  # percentage
    conversion_score: float = 0.0
    performance_score: float = 0.0
    # Campaign info
    campaign_start: Optional[str] = None
    campaign_end: Optional[str] = None
    turnover_requirement: float = 10.0  # Çevrim şartı (x times)
    is_active: bool = True
    is_archived: bool = False
    # Timestamps
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    content_updated_at: Optional[str] = None  # Only updates when real content changes

class BonusSiteCreate(BaseModel):
    name: str
    logo_url: str
    bonus_type: str
    bonus_amount: str
    bonus_value: int = 0
    affiliate_url: str
    rating: float = 4.5
    features: List[str] = []
    is_featured: bool = False
    order: int = 0
    turnover_requirement: float = 10.0
    campaign_start: Optional[str] = None
    campaign_end: Optional[str] = None

class PerformanceEvent(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    site_id: str
    event_type: str  # cta_click, affiliate_click, impression, scroll, time_on_page
    value: float = 1.0  # For scroll depth (0-100) or time (seconds)
    user_session: str = ""
    page_url: str = ""
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class Article(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    slug: str
    excerpt: str
    content: str
    category: str  # spor, bonus, analiz
    tags: List[str] = []
    image_url: str = ""
    author: str = "Admin"
    is_published: bool = True
    is_ai_generated: bool = False
    seo_title: str = ""
    seo_description: str = ""
    internal_links: List[str] = []
    view_count: int = 0
    # Content freshness
    content_hash: str = ""  # To detect real content changes
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    content_updated_at: Optional[str] = None

class ArticleCreate(BaseModel):
    title: str
    slug: Optional[str] = None
    excerpt: str
    content: str
    category: str
    tags: List[str] = []
    image_url: str = ""
    author: str = "Admin"
    is_published: bool = True
    seo_title: str = ""
    seo_description: str = ""

class Category(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    slug: str
    description: str = ""
    type: str  # bonus, spor
    order: int = 0

class CategoryCreate(BaseModel):
    name: str
    slug: str
    description: str = ""
    type: str
    order: int = 0

class SEOAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    analysis_type: str  # competitor, keyword_gap, internal_link, weekly_report
    target_url: Optional[str] = None
    keyword: Optional[str] = None
    results: Dict[str, Any] = {}
    suggestions: List[str] = []
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class AIContentRequest(BaseModel):
    topic: str
    content_type: str  # article, seo_analysis, match_summary, competitor_analysis
    language: str = "tr"
    keywords: List[str] = []
    tone: str = "professional"  # professional, casual, exciting
    word_count: int = 800
    target_url: Optional[str] = None  # For competitor analysis

class CompetitorAnalysisRequest(BaseModel):
    competitor_url: str
    analysis_depth: str = "basic"  # basic, detailed

class PerformanceEventCreate(BaseModel):
    site_id: str
    event_type: str
    value: float = 1.0
    user_session: str = ""
    page_url: str = ""

# ============== HELPER FUNCTIONS ==============

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    text = text.lower()
    text = re.sub(r'[ıİ]', 'i', text)
    text = re.sub(r'[şŞ]', 's', text)
    text = re.sub(r'[ğĞ]', 'g', text)
    text = re.sub(r'[üÜ]', 'u', text)
    text = re.sub(r'[öÖ]', 'o', text)
    text = re.sub(r'[çÇ]', 'c', text)
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')

def extract_bonus_value(bonus_amount: str) -> int:
    """Extract numeric value from bonus amount string"""
    numbers = re.findall(r'\d+', bonus_amount.replace('.', '').replace(',', ''))
    return int(numbers[0]) if numbers else 0

def calculate_heuristic_score(site: dict) -> float:
    """Calculate heuristic score when no performance data available"""
    score = 0.0
    
    # Bonus value score (max 40 points)
    bonus_value = site.get('bonus_value', 0)
    score += min(bonus_value / 25, 40)  # 1000 TL = 40 points
    
    # Turnover requirement score (lower is better, max 20 points)
    turnover = site.get('turnover_requirement', 10)
    score += max(0, 20 - turnover)
    
    # Campaign freshness score (max 20 points)
    if site.get('campaign_start'):
        try:
            start = datetime.fromisoformat(site['campaign_start'].replace('Z', '+00:00'))
            days_old = (datetime.now(timezone.utc) - start).days
            score += max(0, 20 - days_old)
        except:
            score += 10
    else:
        score += 10
    
    # Rating score (max 20 points)
    score += site.get('rating', 4.0) * 4
    
    return score

def calculate_performance_score(site: dict) -> float:
    """Calculate performance score from tracking data"""
    impressions = max(site.get('impressions', 0), 1)
    cta_clicks = site.get('cta_clicks', 0)
    affiliate_clicks = site.get('affiliate_clicks', 0)
    
    # CTR calculation
    cta_rate = (cta_clicks / impressions) * 100
    affiliate_rate = (affiliate_clicks / max(cta_clicks, 1)) * 100
    
    # Time and scroll engagement
    avg_time = site.get('avg_time_on_page', 0)
    avg_scroll = site.get('avg_scroll_depth', 0)
    
    # Weighted score calculation
    score = 0.0
    score += min(cta_rate * 10, 30)  # Max 30 points for CTR
    score += min(affiliate_rate * 5, 25)  # Max 25 points for conversion
    score += min(avg_time / 10, 20)  # Max 20 points for time (200+ seconds)
    score += min(avg_scroll / 4, 25)  # Max 25 points for scroll depth
    
    return score

async def generate_ai_content(prompt: str, system_message: str = "Sen profesyonel bir Türkçe içerik yazarısın.") -> str:
    """Generate content using GPT-5.2 via Emergent Integrations"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=str(uuid.uuid4()),
            system_message=system_message
        ).with_model("openai", "gpt-5.2")
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        return response
    except Exception as e:
        logger.error(f"AI content generation error: {e}")
        return f"AI içerik üretimi sırasında hata oluştu: {str(e)}"

async def update_site_rankings():
    """Update site rankings based on performance or heuristic scores"""
    sites = await db.bonus_sites.find({"is_active": True, "is_archived": False}, {"_id": 0}).to_list(100)
    
    for site in sites:
        # Check if we have enough performance data
        has_performance_data = site.get('impressions', 0) > 10
        
        if has_performance_data:
            score = calculate_performance_score(site)
        else:
            score = calculate_heuristic_score(site)
        
        await db.bonus_sites.update_one(
            {"id": site['id']},
            {"$set": {"performance_score": score}}
        )
    
    # Update rankings based on score
    sites = await db.bonus_sites.find(
        {"is_active": True, "is_archived": False}, 
        {"_id": 0}
    ).sort("performance_score", -1).to_list(100)
    
    # Update order and featured status
    for i, site in enumerate(sites):
        is_featured = i < 2  # Top 2 sites are featured
        await db.bonus_sites.update_one(
            {"id": site['id']},
            {"$set": {"order": i + 1, "is_featured": is_featured}}
        )
    
    return len(sites)

# ============== ROOT ENDPOINT ==============

@api_router.get("/")
async def root():
    return {"message": "Dynamic Sports & Bonus Network API", "version": "2.0.0"}

# ============== PERFORMANCE TRACKING ENDPOINTS ==============

@api_router.post("/track/event")
async def track_event(event: PerformanceEventCreate):
    """Track user interaction events for AI ranking"""
    event_obj = PerformanceEvent(**event.model_dump())
    await db.performance_events.insert_one(event_obj.model_dump())
    
    # Update site metrics
    update_field = {}
    if event.event_type == "cta_click":
        update_field = {"$inc": {"cta_clicks": 1}}
    elif event.event_type == "affiliate_click":
        update_field = {"$inc": {"affiliate_clicks": 1}}
    elif event.event_type == "impression":
        update_field = {"$inc": {"impressions": 1}}
    elif event.event_type == "scroll":
        # Update average scroll depth
        site = await db.bonus_sites.find_one({"id": event.site_id}, {"_id": 0})
        if site:
            current_avg = site.get('avg_scroll_depth', 0)
            impressions = site.get('impressions', 1)
            new_avg = ((current_avg * impressions) + event.value) / (impressions + 1)
            update_field = {"$set": {"avg_scroll_depth": new_avg}}
    elif event.event_type == "time_on_page":
        site = await db.bonus_sites.find_one({"id": event.site_id}, {"_id": 0})
        if site:
            current_avg = site.get('avg_time_on_page', 0)
            impressions = site.get('impressions', 1)
            new_avg = ((current_avg * impressions) + event.value) / (impressions + 1)
            update_field = {"$set": {"avg_time_on_page": new_avg}}
    
    if update_field:
        await db.bonus_sites.update_one({"id": event.site_id}, update_field)
    
    return {"status": "tracked", "event_id": event_obj.id}

@api_router.post("/track/batch")
async def track_batch_events(events: List[PerformanceEventCreate]):
    """Track multiple events at once"""
    for event in events:
        await track_event(event)
    return {"status": "tracked", "count": len(events)}

# ============== AI RANKING ENDPOINTS ==============

@api_router.post("/ai/update-rankings")
async def trigger_ranking_update():
    """Manually trigger AI ranking update"""
    updated_count = await update_site_rankings()
    return {
        "status": "success",
        "sites_updated": updated_count,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@api_router.get("/ai/ranking-report")
async def get_ranking_report():
    """Get detailed ranking report with performance metrics"""
    sites = await db.bonus_sites.find(
        {"is_active": True, "is_archived": False},
        {"_id": 0}
    ).sort("performance_score", -1).to_list(100)
    
    report = []
    for site in sites:
        has_data = site.get('impressions', 0) > 10
        report.append({
            "name": site['name'],
            "rank": site.get('order', 0),
            "performance_score": round(site.get('performance_score', 0), 2),
            "is_featured": site.get('is_featured', False),
            "data_source": "performance" if has_data else "heuristic",
            "metrics": {
                "impressions": site.get('impressions', 0),
                "cta_clicks": site.get('cta_clicks', 0),
                "affiliate_clicks": site.get('affiliate_clicks', 0),
                "ctr": round((site.get('cta_clicks', 0) / max(site.get('impressions', 1), 1)) * 100, 2),
                "avg_time": round(site.get('avg_time_on_page', 0), 1),
                "avg_scroll": round(site.get('avg_scroll_depth', 0), 1)
            }
        })
    
    return {"report": report, "generated_at": datetime.now(timezone.utc).isoformat()}

# ============== BONUS SITES ENDPOINTS ==============

@api_router.get("/bonus-sites", response_model=List[BonusSite])
async def get_bonus_sites(
    bonus_type: Optional[str] = None,
    is_featured: Optional[bool] = None,
    include_archived: bool = False,
    limit: int = Query(default=20, le=100)
):
    """Get all bonus sites sorted by AI performance score"""
    query = {"is_active": True}
    if not include_archived:
        query["is_archived"] = False
    if bonus_type:
        query["bonus_type"] = bonus_type
    if is_featured is not None:
        query["is_featured"] = is_featured
    
    # Sort by performance_score (AI ranking) then by order
    sites = await db.bonus_sites.find(query, {"_id": 0}).sort([
        ("performance_score", -1),
        ("order", 1)
    ]).limit(limit).to_list(limit)
    
    return sites

@api_router.get("/bonus-sites/{site_id}", response_model=BonusSite)
async def get_bonus_site(site_id: str):
    """Get a single bonus site by ID"""
    site = await db.bonus_sites.find_one({"id": site_id}, {"_id": 0})
    if not site:
        raise HTTPException(status_code=404, detail="Bonus site not found")
    return site

@api_router.post("/bonus-sites", response_model=BonusSite)
async def create_bonus_site(site: BonusSiteCreate):
    """Create a new bonus site"""
    site_data = site.model_dump()
    
    # Extract numeric bonus value
    if not site_data.get('bonus_value'):
        site_data['bonus_value'] = extract_bonus_value(site_data['bonus_amount'])
    
    site_obj = BonusSite(**site_data)
    
    # Calculate initial heuristic score
    site_obj.performance_score = calculate_heuristic_score(site_obj.model_dump())
    
    doc = site_obj.model_dump()
    await db.bonus_sites.insert_one(doc)
    
    # Trigger ranking update
    await update_site_rankings()
    
    return site_obj

@api_router.put("/bonus-sites/{site_id}", response_model=BonusSite)
async def update_bonus_site(site_id: str, site: BonusSiteCreate):
    """Update an existing bonus site"""
    existing = await db.bonus_sites.find_one({"id": site_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Bonus site not found")
    
    update_data = site.model_dump()
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Check if content actually changed
    content_fields = ['bonus_amount', 'bonus_type', 'features']
    content_changed = any(
        update_data.get(f) != existing.get(f) for f in content_fields
    )
    
    if content_changed:
        update_data["content_updated_at"] = datetime.now(timezone.utc).isoformat()
        update_data["bonus_value"] = extract_bonus_value(update_data['bonus_amount'])
    
    await db.bonus_sites.update_one({"id": site_id}, {"$set": update_data})
    
    # Recalculate rankings
    await update_site_rankings()
    
    updated = await db.bonus_sites.find_one({"id": site_id}, {"_id": 0})
    return updated

@api_router.post("/bonus-sites/{site_id}/archive")
async def archive_bonus_site(site_id: str):
    """Archive a bonus site (for ended campaigns)"""
    result = await db.bonus_sites.update_one(
        {"id": site_id},
        {"$set": {
            "is_archived": True,
            "is_active": False,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Bonus site not found")
    
    await update_site_rankings()
    return {"message": "Site archived successfully"}

@api_router.delete("/bonus-sites/{site_id}")
async def delete_bonus_site(site_id: str):
    """Delete a bonus site"""
    result = await db.bonus_sites.delete_one({"id": site_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Bonus site not found")
    return {"message": "Bonus site deleted successfully"}

# ============== ARTICLES ENDPOINTS ==============

@api_router.get("/articles", response_model=List[Article])
async def get_articles(
    category: Optional[str] = None,
    tag: Optional[str] = None,
    is_published: bool = True,
    limit: int = Query(default=20, le=100),
    skip: int = 0
):
    """Get all articles with optional filtering"""
    query = {"is_published": is_published}
    if category:
        query["category"] = category
    if tag:
        query["tags"] = tag
    
    articles = await db.articles.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    return articles

@api_router.get("/articles/slug/{slug}", response_model=Article)
async def get_article_by_slug(slug: str):
    """Get a single article by slug"""
    article = await db.articles.find_one({"slug": slug}, {"_id": 0})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Increment view count
    await db.articles.update_one({"slug": slug}, {"$inc": {"view_count": 1}})
    return article

@api_router.get("/articles/{article_id}", response_model=Article)
async def get_article(article_id: str):
    """Get a single article by ID"""
    article = await db.articles.find_one({"id": article_id}, {"_id": 0})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@api_router.post("/articles", response_model=Article)
async def create_article(article: ArticleCreate):
    """Create a new article"""
    article_data = article.model_dump()
    
    # Auto-generate slug if not provided
    if not article_data.get("slug"):
        article_data["slug"] = slugify(article_data["title"])
    
    # Auto-generate SEO fields if not provided
    if not article_data.get("seo_title"):
        article_data["seo_title"] = article_data["title"]
    if not article_data.get("seo_description"):
        article_data["seo_description"] = article_data["excerpt"][:160]
    
    # Generate content hash for change detection
    import hashlib
    content_hash = hashlib.md5(article_data["content"].encode()).hexdigest()
    article_data["content_hash"] = content_hash
    article_data["content_updated_at"] = datetime.now(timezone.utc).isoformat()
    
    article_obj = Article(**article_data)
    doc = article_obj.model_dump()
    await db.articles.insert_one(doc)
    return article_obj

@api_router.put("/articles/{article_id}", response_model=Article)
async def update_article(article_id: str, article: ArticleCreate):
    """Update an existing article"""
    existing = await db.articles.find_one({"id": article_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Article not found")
    
    update_data = article.model_dump()
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    # Check if content actually changed
    import hashlib
    new_hash = hashlib.md5(update_data["content"].encode()).hexdigest()
    if new_hash != existing.get("content_hash", ""):
        update_data["content_hash"] = new_hash
        update_data["content_updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.articles.update_one({"id": article_id}, {"$set": update_data})
    updated = await db.articles.find_one({"id": article_id}, {"_id": 0})
    return updated

@api_router.delete("/articles/{article_id}")
async def delete_article(article_id: str):
    """Delete an article"""
    result = await db.articles.delete_one({"id": article_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"message": "Article deleted successfully"}

# ============== CATEGORIES ENDPOINTS ==============

@api_router.get("/categories", response_model=List[Category])
async def get_categories(type: Optional[str] = None):
    """Get all categories"""
    query = {}
    if type:
        query["type"] = type
    
    categories = await db.categories.find(query, {"_id": 0}).sort("order", 1).to_list(100)
    return categories

@api_router.post("/categories", response_model=Category)
async def create_category(category: CategoryCreate):
    """Create a new category"""
    category_obj = Category(**category.model_dump())
    doc = category_obj.model_dump()
    await db.categories.insert_one(doc)
    return category_obj

# ============== AI CONTENT GENERATION ==============

@api_router.post("/ai/generate-content")
async def generate_content(request: AIContentRequest):
    """Generate AI-powered content"""
    
    if request.content_type == "article":
        prompt = f"""
        Konu: {request.topic}
        Anahtar Kelimeler: {', '.join(request.keywords)}
        Kelime Sayısı: yaklaşık {request.word_count} kelime
        Ton: {request.tone}
        
        Lütfen SEO uyumlu, özgün ve bilgilendirici bir makale yaz.
        Başlık, giriş, ana bölümler ve sonuç içermeli.
        
        ÖNEMLİ: İçeriğin %80'i bilgilendirici/analiz odaklı olmalı, %20'si doğal affiliate yönlendirme içermeli.
        Spam CTA kullanma, doğal geçişler yap.
        
        Doğal iç link önerileri için uygun yerleri [İÇ_LİNK: konu] şeklinde işaretle.
        """
        system_msg = "Sen spor bahisleri ve bonus rehberleri konusunda uzman bir Türkçe içerik yazarısın. SEO uyumlu, özgün ve değerli içerikler üretiyorsun. İçeriklerin %80'i bilgilendirici, %20'si doğal affiliate yönlendirme içermeli."
    
    elif request.content_type == "match_summary":
        prompt = f"""
        Maç/Konu: {request.topic}
        
        Bu maç için kısa ve etkileyici bir özet yaz.
        Sonuç, önemli anlar ve oyuncu performanslarını içer.
        150-200 kelime olmalı.
        
        Sonunda doğal bir şekilde "Bu maçla ilgili bahis analizi için bonus rehberimize göz atabilirsiniz" gibi 
        bir geçiş cümlesi ekle ama spam yapma.
        """
        system_msg = "Sen spor gazetecisisin. Maç özetleri yazıyorsun. İçerik bilgilendirici olmalı, hafif affiliate yönlendirme doğal olmalı."
    
    elif request.content_type == "seo_analysis":
        prompt = f"""
        Anahtar Kelime: {request.topic}
        Mevcut Anahtar Kelimeler: {', '.join(request.keywords)}
        
        Bu anahtar kelime için detaylı SEO analizi yap:
        1. Rekabet durumu değerlendirmesi
        2. İçerik önerileri (hangi konular işlenmeli)
        3. İç link stratejisi (hangi sayfalar birbirine bağlanmalı)
        4. Başlık önerileri (5 adet)
        5. Meta açıklama önerileri (3 adet)
        6. Anahtar kelime boşlukları (rakiplerin kullandığı ama bizim kullanmadığımız kelimeler)
        
        JSON formatında yanıt ver.
        """
        system_msg = "Sen SEO uzmanısın. Türkçe bahis ve spor siteleri için optimizasyon önerileri sunuyorsun."
    
    elif request.content_type == "competitor_analysis":
        prompt = f"""
        Rakip Site: {request.target_url or request.topic}
        
        Bu rakip site için yapısal analiz yap:
        1. Site yapısı değerlendirmesi
        2. İçerik stratejisi analizi
        3. Anahtar kelime kullanımı
        4. Güçlü yönler
        5. Zayıf yönler
        6. Bizim için fırsatlar
        7. Önerilen aksiyon planı
        
        NOT: Kopyalama önerisi yapma, sadece yapısal analiz ve özgün üretim stratejisi sun.
        
        JSON formatında yanıt ver.
        """
        system_msg = "Sen SEO ve dijital pazarlama uzmanısın. Rakip analizi yapıyorsun ama kopyalama değil, özgün strateji öneriyorsun."
    
    else:
        prompt = request.topic
        system_msg = "Sen profesyonel bir Türkçe içerik yazarısın."
    
    content = await generate_ai_content(prompt, system_msg)
    
    return {
        "content": content,
        "content_type": request.content_type,
        "topic": request.topic,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

@api_router.post("/ai/competitor-analysis")
async def analyze_competitor(request: CompetitorAnalysisRequest):
    """Analyze a competitor website"""
    prompt = f"""
    Rakip Site URL: {request.competitor_url}
    Analiz Derinliği: {request.analysis_depth}
    
    Bu rakip bahis/bonus sitesi için detaylı analiz yap:
    
    1. **Yapısal Analiz**
       - Site mimarisi
       - Sayfa hiyerarşisi
       - Navigasyon yapısı
    
    2. **İçerik Stratejisi**
       - Kullandıkları içerik türleri
       - Güncelleme sıklığı
       - Ton ve stil
    
    3. **SEO Analizi**
       - Hedef anahtar kelimeler (tahmin)
       - Meta yapısı
       - İç link stratejisi
    
    4. **Anahtar Kelime Boşlukları**
       - Rakibin güçlü olduğu kelimeler
       - Kaçırdığımız fırsatlar
    
    5. **Aksiyon Önerileri**
       - Hemen yapılabilecekler
       - Orta vadeli stratejiler
       - Uzun vadeli hedefler
    
    JSON formatında yanıt ver. Kopyalama değil, özgün strateji öner.
    """
    
    content = await generate_ai_content(
        prompt, 
        "Sen SEO ve dijital pazarlama uzmanısın. Rakip analizi yapıyorsun. Kopyalama önermiyorsun, özgün stratejiler sunuyorsun."
    )
    
    # Save analysis
    analysis = SEOAnalysis(
        analysis_type="competitor",
        target_url=request.competitor_url,
        results={"raw_analysis": content},
        suggestions=[]
    )
    await db.seo_analysis.insert_one(analysis.model_dump())
    
    return {
        "analysis": content,
        "competitor_url": request.competitor_url,
        "analyzed_at": datetime.now(timezone.utc).isoformat()
    }

class KeywordGapRequest(BaseModel):
    keywords: List[str]
    competitor_keywords: List[str] = []

@api_router.post("/ai/keyword-gap-analysis")
async def keyword_gap_analysis(request: KeywordGapRequest):
    """Find keyword gaps and opportunities"""
    prompt = f"""
    Mevcut Anahtar Kelimelerimiz: {', '.join(request.keywords)}
    Rakip Anahtar Kelimeleri: {', '.join(request.competitor_keywords) if request.competitor_keywords else 'Belirtilmedi'}
    
    Türkçe bahis ve bonus sektörü için anahtar kelime boşluk analizi yap:
    
    1. **Kaçırılan Fırsatlar**
       - Yüksek hacimli ama rekabeti düşük kelimeler
       - Long-tail fırsatları
    
    2. **İçerik Önerileri**
       - Her kelime için içerik türü önerisi
       - Öncelik sıralaması
    
    3. **Semantik Kelime Grupları**
       - İlgili kelime kümeleri
       - Topic cluster önerileri
    
    4. **Haftalık İçerik Planı**
       - Hangi kelimeler için içerik üretilmeli
       - Önerilen içerik takvimi
    
    JSON formatında yanıt ver.
    """
    
    content = await generate_ai_content(
        prompt,
        "Sen SEO uzmanısın. Türkçe bahis sektörü için anahtar kelime analizi yapıyorsun."
    )
    
    return {
        "analysis": content,
        "input_keywords": request.keywords,
        "analyzed_at": datetime.now(timezone.utc).isoformat()
    }

@api_router.post("/ai/internal-link-suggestions")
async def get_internal_link_suggestions(article_id: str):
    """Get AI-powered internal link suggestions for an article"""
    article = await db.articles.find_one({"id": article_id}, {"_id": 0})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Get all other articles for context
    other_articles = await db.articles.find(
        {"id": {"$ne": article_id}, "is_published": True},
        {"_id": 0, "id": 1, "title": 1, "slug": 1, "category": 1, "tags": 1}
    ).to_list(50)
    
    # Get bonus sites
    bonus_sites = await db.bonus_sites.find(
        {"is_active": True},
        {"_id": 0, "id": 1, "name": 1, "bonus_type": 1}
    ).to_list(20)
    
    prompt = f"""
    Makale Başlığı: {article['title']}
    Makale Kategorisi: {article['category']}
    Makale İçeriği Özeti: {article['excerpt']}
    
    Mevcut Diğer Makaleler:
    {json.dumps([{"title": a['title'], "slug": a['slug'], "category": a['category']} for a in other_articles], ensure_ascii=False)}
    
    Mevcut Bonus Siteleri:
    {json.dumps([{"name": s['name'], "type": s['bonus_type']} for s in bonus_sites], ensure_ascii=False)}
    
    Bu makale için iç link stratejisi öner:
    
    1. **Doğal Link Fırsatları**
       - Hangi kelimelerde hangi makaleye link verilmeli
       - Bonus sayfalarına yönlendirme noktaları
    
    2. **Link Anchor Textleri**
       - Önerilen anchor text'ler
       - Doğal görünümlü alternatifler
    
    3. **Link Önceliği**
       - En önemli linkler
       - Sayfa başına maksimum link sayısı önerisi
    
    JSON formatında yanıt ver. Spam link değil, kullanıcıya değer katan doğal linkler öner.
    """
    
    content = await generate_ai_content(
        prompt,
        "Sen SEO uzmanısın. Doğal ve kullanıcı odaklı iç link stratejileri öneriyorsun."
    )
    
    return {
        "article_id": article_id,
        "suggestions": content,
        "analyzed_at": datetime.now(timezone.utc).isoformat()
    }

@api_router.get("/ai/weekly-seo-report")
async def generate_weekly_seo_report():
    """Generate weekly SEO performance report"""
    # Get site stats
    total_articles = await db.articles.count_documents({"is_published": True})
    total_views = await db.articles.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$view_count"}}}
    ]).to_list(1)
    
    # Get bonus site performance
    sites = await db.bonus_sites.find({"is_active": True}, {"_id": 0}).to_list(50)
    
    # Get top performing content
    top_articles = await db.articles.find(
        {"is_published": True},
        {"_id": 0, "title": 1, "view_count": 1, "category": 1}
    ).sort("view_count", -1).limit(5).to_list(5)
    
    prompt = f"""
    Haftalık SEO Raporu Oluştur:
    
    **Site İstatistikleri:**
    - Toplam Makale: {total_articles}
    - Toplam Görüntülenme: {total_views[0]['total'] if total_views else 0}
    - Aktif Bonus Sitesi: {len(sites)}
    
    **En İyi Performans Gösteren İçerikler:**
    {json.dumps(top_articles, ensure_ascii=False)}
    
    **Bonus Site Performansları:**
    {json.dumps([{
        "name": s['name'],
        "impressions": s.get('impressions', 0),
        "clicks": s.get('cta_clicks', 0),
        "score": s.get('performance_score', 0)
    } for s in sites[:10]], ensure_ascii=False)}
    
    Şunları içeren bir rapor oluştur:
    
    1. **Haftalık Özet**
       - Öne çıkan metrikler
       - Geçen haftaya göre değişim (tahmin)
    
    2. **İçerik Performansı**
       - En başarılı içerikler
       - Düşük performanslı içerikler
       - İyileştirme önerileri
    
    3. **Bonus Site Performansı**
       - Sıralama değişiklikleri
       - CTR analizi
       - Önerilen optimizasyonlar
    
    4. **Gelecek Hafta İçin Öneriler**
       - Yazılması gereken içerikler
       - Güncellenmesi gereken sayfalar
       - SEO aksiyonları
    
    5. **Rakip Hareketleri** (genel sektör tahmini)
       - Dikkat edilmesi gereken trendler
       - Fırsat alanları
    
    Markdown formatında, okunabilir ve aksiyon odaklı bir rapor oluştur.
    """
    
    content = await generate_ai_content(
        prompt,
        "Sen SEO analisti ve içerik stratejistisin. Haftalık performans raporları hazırlıyorsun."
    )
    
    # Save report
    report = SEOAnalysis(
        analysis_type="weekly_report",
        results={
            "total_articles": total_articles,
            "total_views": total_views[0]['total'] if total_views else 0,
            "active_sites": len(sites)
        },
        suggestions=[content]
    )
    await db.seo_analysis.insert_one(report.model_dump())
    
    return {
        "report": content,
        "stats": {
            "total_articles": total_articles,
            "total_views": total_views[0]['total'] if total_views else 0,
            "active_bonus_sites": len(sites)
        },
        "generated_at": datetime.now(timezone.utc).isoformat()
    }

# ============== FOOTBALL DATA API ==============

@api_router.get("/sports/matches")
async def get_matches(
    league: str = "PL",  # PL, SA, BL1, etc.
    status: Optional[str] = None  # SCHEDULED, LIVE, FINISHED
):
    """Get matches from Football Data API"""
    try:
        async with httpx.AsyncClient() as http_client:
            headers = {"X-Auth-Token": FOOTBALL_API_KEY}
            url = f"https://api.football-data.org/v4/competitions/{league}/matches"
            params = {}
            if status:
                params["status"] = status
            
            response = await http_client.get(url, headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                matches = []
                for match in data.get("matches", [])[:10]:
                    matches.append({
                        "home_team": match.get("homeTeam", {}).get("name", ""),
                        "away_team": match.get("awayTeam", {}).get("name", ""),
                        "home_score": match.get("score", {}).get("fullTime", {}).get("home"),
                        "away_score": match.get("score", {}).get("fullTime", {}).get("away"),
                        "league": data.get("competition", {}).get("name", league),
                        "match_date": match.get("utcDate", ""),
                        "status": match.get("status", "")
                    })
                return {"matches": matches, "competition": data.get("competition", {}).get("name", league)}
            else:
                # Return mock data for demo
                return get_demo_matches(league)
    except Exception as e:
        logger.error(f"Football API error: {e}")
        return get_demo_matches(league)

def get_demo_matches(league: str):
    """Return demo match data"""
    return {
        "matches": [
            {"home_team": "Galatasaray", "away_team": "Fenerbahçe", "home_score": 2, "away_score": 1, "league": "Süper Lig", "match_date": "2026-01-18", "status": "FINISHED"},
            {"home_team": "Beşiktaş", "away_team": "Trabzonspor", "home_score": 1, "away_score": 1, "league": "Süper Lig", "match_date": "2026-01-17", "status": "FINISHED"},
            {"home_team": "Manchester United", "away_team": "Liverpool", "home_score": 2, "away_score": 2, "league": "Premier League", "match_date": "2026-01-16", "status": "FINISHED"},
            {"home_team": "Arsenal", "away_team": "Chelsea", "home_score": 3, "away_score": 1, "league": "Premier League", "match_date": "2026-01-15", "status": "FINISHED"},
            {"home_team": "Real Madrid", "away_team": "Barcelona", "home_score": 2, "away_score": 2, "league": "La Liga", "match_date": "2026-01-14", "status": "FINISHED"}
        ],
        "competition": league,
        "note": "Demo data - API key required for live data"
    }

@api_router.get("/sports/standings")
async def get_standings(league: str = "PL"):
    """Get league standings"""
    try:
        async with httpx.AsyncClient() as http_client:
            headers = {"X-Auth-Token": FOOTBALL_API_KEY}
            url = f"https://api.football-data.org/v4/competitions/{league}/standings"
            
            response = await http_client.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                return {
                    "standings": [
                        {"position": 1, "team": "Galatasaray", "points": 48, "won": 15, "draw": 3, "lost": 2},
                        {"position": 2, "team": "Fenerbahçe", "points": 45, "won": 14, "draw": 3, "lost": 3},
                        {"position": 3, "team": "Beşiktaş", "points": 40, "won": 12, "draw": 4, "lost": 4},
                        {"position": 4, "team": "Trabzonspor", "points": 35, "won": 10, "draw": 5, "lost": 5}
                    ],
                    "note": "Demo data"
                }
    except Exception as e:
        logger.error(f"Standings API error: {e}")
        return {"standings": [], "error": str(e)}

# ============== STATS ENDPOINTS ==============

@api_router.get("/stats/dashboard")
async def get_dashboard_stats():
    """Get dashboard statistics"""
    total_articles = await db.articles.count_documents({})
    total_bonus_sites = await db.bonus_sites.count_documents({"is_active": True})
    published_articles = await db.articles.count_documents({"is_published": True})
    archived_sites = await db.bonus_sites.count_documents({"is_archived": True})
    total_views = await db.articles.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$view_count"}}}
    ]).to_list(1)
    
    # Performance stats
    total_impressions = await db.bonus_sites.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$impressions"}}}
    ]).to_list(1)
    total_clicks = await db.bonus_sites.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$cta_clicks"}}}
    ]).to_list(1)
    
    return {
        "total_articles": total_articles,
        "total_bonus_sites": total_bonus_sites,
        "published_articles": published_articles,
        "archived_sites": archived_sites,
        "total_views": total_views[0]["total"] if total_views else 0,
        "total_impressions": total_impressions[0]["total"] if total_impressions else 0,
        "total_clicks": total_clicks[0]["total"] if total_clicks else 0
    }

# ============== SEED DATA ==============

@api_router.post("/seed")
async def seed_database():
    """Seed database with initial data including real site list"""
    
    # Clear existing data
    await db.bonus_sites.delete_many({})
    await db.categories.delete_many({})
    await db.articles.delete_many({})
    
    # Seed categories
    categories = [
        {"name": "Deneme Bonusu Veren Siteler", "slug": "deneme-bonusu-veren-siteler", "type": "bonus", "order": 1},
        {"name": "Hoşgeldin Bonusları", "slug": "hosgeldin-bonuslari", "type": "bonus", "order": 2},
        {"name": "Yatırım Bonusları", "slug": "yatirim-bonuslari", "type": "bonus", "order": 3},
        {"name": "Kayıp Bonusları", "slug": "kayip-bonuslari", "type": "bonus", "order": 4},
        {"name": "Süper Lig", "slug": "super-lig", "type": "spor", "order": 1},
        {"name": "Premier Lig", "slug": "premier-lig", "type": "spor", "order": 2},
        {"name": "Şampiyonlar Ligi", "slug": "sampiyonlar-ligi", "type": "spor", "order": 3}
    ]
    
    for cat in categories:
        cat_obj = Category(**cat)
        await db.categories.insert_one(cat_obj.model_dump())
    
    # Seed REAL bonus sites from user's list
    bonus_sites = [
        {
            "name": "MAXWIN",
            "logo_url": "https://images.unsplash.com/photo-1709873582570-4f17d43921d4?w=100&h=100&fit=crop",
            "bonus_type": "deneme",
            "bonus_amount": "750 TL",
            "bonus_value": 750,
            "affiliate_url": "https://cutt.ly/glockmaxwn",
            "rating": 4.9,
            "features": ["Hızlı Ödeme", "7/24 Destek", "Mobil Uyumlu"],
            "turnover_requirement": 8.0,
            "campaign_start": datetime.now(timezone.utc).isoformat()
        },
        {
            "name": "HILTONBET",
            "logo_url": "https://images.unsplash.com/photo-1763089221979-ebb2a748358a?w=100&h=100&fit=crop",
            "bonus_type": "deneme",
            "bonus_amount": "500 TL",
            "bonus_value": 500,
            "affiliate_url": "https://hiltonbetortak.com/affiliates/?btag=2652418",
            "rating": 4.8,
            "features": ["Yüksek Oranlar", "Canlı Bahis", "Casino"],
            "turnover_requirement": 10.0,
            "campaign_start": datetime.now(timezone.utc).isoformat()
        },
        {
            "name": "ELEXBET",
            "logo_url": "https://images.unsplash.com/photo-1678696419211-6e0fb533c95e?w=100&h=100&fit=crop",
            "bonus_type": "hosgeldin",
            "bonus_amount": "1000 TL",
            "bonus_value": 1000,
            "affiliate_url": "https://go.aff.elexbetpro.com/syq46dzq",
            "rating": 4.7,
            "features": ["Yatırım Bonusu", "Geniş Bahis Seçenekleri"],
            "turnover_requirement": 12.0,
            "campaign_start": datetime.now(timezone.utc).isoformat()
        },
        {
            "name": "FESTWIN",
            "logo_url": "https://images.unsplash.com/photo-1762278804798-dd7e493db051?w=100&h=100&fit=crop",
            "bonus_type": "kayip",
            "bonus_amount": "%15 Kayıp",
            "bonus_value": 15,
            "affiliate_url": "https://t2m.co/gmfest",
            "rating": 4.6,
            "features": ["Kayıp Bonusu", "Hızlı Çekim"],
            "turnover_requirement": 5.0,
            "campaign_start": datetime.now(timezone.utc).isoformat()
        },
        {
            "name": "CASINO DIOR",
            "logo_url": "https://images.pexels.com/photos/7594162/pexels-photo-7594162.jpeg?w=100&h=100&fit=crop",
            "bonus_type": "hosgeldin",
            "bonus_amount": "2000 TL",
            "bonus_value": 2000,
            "affiliate_url": "https://www.diorlink.com/links/?btag=2481426",
            "rating": 4.8,
            "features": ["Casino Oyunları", "VIP Program", "Slot Çeşitliliği"],
            "turnover_requirement": 15.0,
            "campaign_start": datetime.now(timezone.utc).isoformat()
        },
        {
            "name": "BETCI",
            "logo_url": "https://images.unsplash.com/photo-1741089731004-3c17efa3e381?w=100&h=100&fit=crop",
            "bonus_type": "deneme",
            "bonus_amount": "500 TL",
            "bonus_value": 500,
            "affiliate_url": "https://betcilink2.com/affiliates/?btag=2482990",
            "rating": 4.5,
            "features": ["Spor Bahisleri", "Canlı Casino"],
            "turnover_requirement": 10.0,
            "campaign_start": datetime.now(timezone.utc).isoformat()
        },
        {
            "name": "ALFABAHIS",
            "logo_url": "https://images.pexels.com/photos/12616082/pexels-photo-12616082.jpeg?w=100&h=100&fit=crop",
            "bonus_type": "deneme",
            "bonus_amount": "600 TL",
            "bonus_value": 600,
            "affiliate_url": "https://alfabahisaff10.com/affiliates/?btag=2482989",
            "rating": 4.6,
            "features": ["Hızlı Kayıt", "Mobil Uygulama"],
            "turnover_requirement": 8.0,
            "campaign_start": datetime.now(timezone.utc).isoformat()
        },
        {
            "name": "TULIPBET",
            "logo_url": "https://images.pexels.com/photos/6203470/pexels-photo-6203470.jpeg?w=100&h=100&fit=crop",
            "bonus_type": "hosgeldin",
            "bonus_amount": "1500 TL",
            "bonus_value": 1500,
            "affiliate_url": "https://tulipbetortaklik.com/upw8v0ar",
            "rating": 4.7,
            "features": ["Hoşgeldin Paketi", "Free Spin"],
            "turnover_requirement": 12.0,
            "campaign_start": datetime.now(timezone.utc).isoformat()
        }
    ]
    
    for i, site in enumerate(bonus_sites):
        site_obj = BonusSite(**site)
        site_obj.order = i + 1
        # Calculate initial heuristic score
        site_obj.performance_score = calculate_heuristic_score(site_obj.model_dump())
        await db.bonus_sites.insert_one(site_obj.model_dump())
    
    # Update rankings (set featured status for top 2)
    await update_site_rankings()
    
    # Seed articles
    articles = [
        {
            "title": "2026 Deneme Bonusu Veren Siteler - Güncel Liste",
            "slug": "2026-deneme-bonusu-veren-siteler",
            "excerpt": "2026 yılında deneme bonusu veren en güvenilir bahis sitelerinin güncel listesi. Yatırımsız bonus fırsatları ve detaylı incelemeler.",
            "content": """<h2>2026 Deneme Bonusu Nedir?</h2>
<p>Deneme bonusu, bahis sitelerinin yeni üyelerine sunduğu yatırımsız bonus fırsatıdır. Bu bonus sayesinde hiç para yatırmadan bahis yapabilir ve kazanç elde edebilirsiniz.</p>

<h2>En İyi Deneme Bonusu Veren Siteler</h2>
<p>2026 yılında en yüksek deneme bonusu veren siteleri sizler için derledik. Güvenilirlik, ödeme hızı ve bonus miktarı kriterlerine göre AI sistemimiz tarafından sıralanmaktadır.</p>

<h3>AI Destekli Sıralama Sistemi</h3>
<p>Sitemizde bonus siteleri performans verilerine göre otomatik olarak sıralanmaktadır:</p>
<ul>
<li>Kullanıcı tıklama oranları</li>
<li>Dönüşüm performansı</li>
<li>Kullanıcı memnuniyeti</li>
<li>Ödeme hızı</li>
</ul>

<h3>Bonus Kullanım Şartları</h3>
<ul>
<li>Minimum çevrim şartı kontrolü</li>
<li>Maksimum kazanç limitleri</li>
<li>Geçerlilik süreleri</li>
</ul>

<p>Detaylı bonus karşılaştırması ve güncel fırsatlar için sayfamızı takip edin.</p>""",
            "category": "bonus",
            "tags": ["deneme bonusu", "yatırımsız bonus", "2026"],
            "image_url": "https://images.unsplash.com/photo-1678696419211-6e0fb533c95e?w=800",
            "seo_title": "2026 Deneme Bonusu Veren Siteler | Güncel Liste",
            "seo_description": "2026 yılının en güncel deneme bonusu veren site listesi. Yatırımsız bonus fırsatları ve detaylı site incelemeleri."
        },
        {
            "title": "Galatasaray-Fenerbahçe Derbisi Analizi: Taktiksel İnceleme",
            "slug": "galatasaray-fenerbahce-derbisi-analizi",
            "excerpt": "Süper Lig'in en büyük derbisi için detaylı taktiksel analiz. Takım kadroları, form durumları ve maç tahmini.",
            "content": """<h2>Derbi Öncesi Takım Durumları</h2>
<p>Süper Lig'de zirve mücadelesi veren iki ezeli rakip, sezonun en kritik maçına çıkıyor.</p>

<h3>Galatasaray</h3>
<p>Son 5 maçta 4 galibiyet alan Galatasaray, formda bir grafik çiziyor. Hücum hattındaki etkinlik dikkat çekici. Icardi'nin sakatlanmasıyla forvet hattında değişiklik bekleniyor.</p>

<h3>Fenerbahçe</h3>
<p>Deplasman performansı ile öne çıkan Fenerbahçe, derbi öncesi moralli. Mourinho'nun taktik hamleleri merakla bekleniyor.</p>

<h2>Taktiksel Beklentiler</h2>
<p>Her iki takımın da yüksek tempolu oynayacağı bir maç bekleniyor. Orta saha mücadelesi belirleyici olacak.</p>

<h2>Maç Tahmini</h2>
<p>Skor tahmini: 2-1 (Ev sahibi avantajı göz önüne alındığında Galatasaray lehine)</p>

<p>Bu maçla ilgili bahis analizleri ve bonus fırsatları için ana sayfamızı ziyaret edebilirsiniz.</p>""",
            "category": "spor",
            "tags": ["galatasaray", "fenerbahce", "super lig", "derbi"],
            "image_url": "https://images.unsplash.com/photo-1762013315117-1c8005ad2b41?w=800",
            "seo_title": "Galatasaray-Fenerbahçe Derbisi Analizi 2026",
            "seo_description": "Galatasaray-Fenerbahçe derbisi için detaylı taktiksel analiz ve maç tahmini."
        },
        {
            "title": "Premier Lig Hafta Sonu Maç Özetleri",
            "slug": "premier-lig-hafta-sonu-mac-ozetleri",
            "excerpt": "Premier Lig'de haftanın öne çıkan maçları ve sonuçları. Manchester derbisi, Arsenal'in galibiyet serisi ve daha fazlası.",
            "content": """<h2>Haftanın Öne Çıkan Maçları</h2>

<h3>Manchester United 2-2 Liverpool</h3>
<p>Old Trafford'da oynanan zorlu mücadelede iki takım da sahadan beraberlikle ayrıldı. Bruno Fernandes ve Salah'ın golleri öne çıktı.</p>

<h3>Arsenal 3-1 Chelsea</h3>
<p>Kuzey Londra'da Arsenal üstünlüğü ele geçirdi. Saka, Rice ve Havertz'in golleriyle 3-1'lik net skorla sahadan galip ayrıldı.</p>

<h2>Puan Durumu Güncellemesi</h2>
<p>Arsenal zirvede yerini koruyor, Manchester City takipte. Liverpool ise düşüşe geçti.</p>

<h2>Gelecek Hafta Beklentileri</h2>
<p>Arsenal'in zorlayıcı deplasman maçı ve City'nin kolay fikstürü ile puan durumu değişebilir.</p>

<p>Premier Lig maçları için bahis oranları ve bonus fırsatları sitemizde güncel olarak paylaşılmaktadır.</p>""",
            "category": "spor",
            "tags": ["premier lig", "manchester united", "arsenal", "mac ozeti"],
            "image_url": "https://images.unsplash.com/photo-1706675780107-7c43cc487928?w=800",
            "seo_title": "Premier Lig Hafta Sonu Maç Özetleri | Ocak 2026",
            "seo_description": "Premier Lig'de haftanın tüm maç özetleri ve sonuçları. Manchester derbisi, Arsenal galibiyeti ve puan durumu."
        }
    ]
    
    for article in articles:
        import hashlib
        article["content_hash"] = hashlib.md5(article["content"].encode()).hexdigest()
        article["content_updated_at"] = datetime.now(timezone.utc).isoformat()
        article_obj = Article(**article)
        await db.articles.insert_one(article_obj.model_dump())
    
    return {
        "message": "Database seeded successfully with real site data",
        "categories": len(categories),
        "bonus_sites": len(bonus_sites),
        "articles": len(articles),
        "sites_list": [s["name"] for s in bonus_sites]
    }

# Include the router in the main app
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
