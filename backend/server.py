from fastapi import FastAPI, APIRouter, HTTPException, Query
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import httpx
import re

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
    affiliate_url: str
    rating: float = 4.5
    features: List[str] = []
    is_featured: bool = False
    order: int = 0
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class BonusSiteCreate(BaseModel):
    name: str
    logo_url: str
    bonus_type: str
    bonus_amount: str
    affiliate_url: str
    rating: float = 4.5
    features: List[str] = []
    is_featured: bool = False
    order: int = 0

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
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

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
    article_id: Optional[str] = None
    url: Optional[str] = None
    keyword: str
    score: int = 0
    suggestions: List[str] = []
    competitor_insights: Dict[str, Any] = {}
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class AIContentRequest(BaseModel):
    topic: str
    content_type: str  # article, seo_analysis, match_summary
    language: str = "tr"
    keywords: List[str] = []
    tone: str = "professional"  # professional, casual, exciting
    word_count: int = 800

class MatchResult(BaseModel):
    home_team: str
    away_team: str
    home_score: int
    away_score: int
    league: str
    match_date: str
    status: str

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

# ============== ROOT ENDPOINT ==============

@api_router.get("/")
async def root():
    return {"message": "Dynamic Sports & Bonus Network API", "version": "1.0.0"}

# ============== BONUS SITES ENDPOINTS ==============

@api_router.get("/bonus-sites", response_model=List[BonusSite])
async def get_bonus_sites(
    bonus_type: Optional[str] = None,
    is_featured: Optional[bool] = None,
    limit: int = Query(default=20, le=100)
):
    """Get all bonus sites with optional filtering"""
    query = {}
    if bonus_type:
        query["bonus_type"] = bonus_type
    if is_featured is not None:
        query["is_featured"] = is_featured
    
    sites = await db.bonus_sites.find(query, {"_id": 0}).sort("order", 1).limit(limit).to_list(limit)
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
    site_obj = BonusSite(**site.model_dump())
    doc = site_obj.model_dump()
    await db.bonus_sites.insert_one(doc)
    return site_obj

@api_router.put("/bonus-sites/{site_id}", response_model=BonusSite)
async def update_bonus_site(site_id: str, site: BonusSiteCreate):
    """Update an existing bonus site"""
    existing = await db.bonus_sites.find_one({"id": site_id})
    if not existing:
        raise HTTPException(status_code=404, detail="Bonus site not found")
    
    update_data = site.model_dump()
    update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    await db.bonus_sites.update_one({"id": site_id}, {"$set": update_data})
    updated = await db.bonus_sites.find_one({"id": site_id}, {"_id": 0})
    return updated

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
        Doğal iç link önerileri için uygun yerleri [İÇ_LİNK: konu] şeklinde işaretle.
        """
        system_msg = "Sen spor bahisleri ve bonus rehberleri konusunda uzman bir Türkçe içerik yazarısın. SEO uyumlu, özgün ve değerli içerikler üretiyorsun."
    
    elif request.content_type == "match_summary":
        prompt = f"""
        Maç/Konu: {request.topic}
        
        Bu maç için kısa ve etkileyici bir özet yaz.
        Sonuç, önemli anlar ve oyuncu performanslarını içer.
        150-200 kelime olmalı.
        """
        system_msg = "Sen spor gazetecisisin. Maç özetleri yazıyorsun."
    
    elif request.content_type == "seo_analysis":
        prompt = f"""
        Anahtar Kelime: {request.topic}
        Mevcut Anahtar Kelimeler: {', '.join(request.keywords)}
        
        Bu anahtar kelime için SEO analizi yap:
        1. Rekabet durumu
        2. İçerik önerileri
        3. İç link stratejisi
        4. Başlık önerileri
        5. Meta açıklama önerileri
        """
        system_msg = "Sen SEO uzmanısın. Türkçe bahis ve spor siteleri için optimizasyon önerileri sunuyorsun."
    
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

@api_router.post("/ai/seo-suggestions")
async def get_seo_suggestions(article_id: str):
    """Get AI-powered SEO suggestions for an article"""
    article = await db.articles.find_one({"id": article_id}, {"_id": 0})
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    prompt = f"""
    Makale Başlığı: {article['title']}
    Kategori: {article['category']}
    Mevcut İçerik Özeti: {article['excerpt']}
    
    Bu makale için detaylı SEO önerileri sun:
    1. Başlık iyileştirmesi
    2. Meta açıklama önerisi
    3. İç link önerileri (bonus sayfalarına ve spor haberlerine)
    4. Anahtar kelime önerileri
    5. İçerik genişletme fırsatları
    6. Rakip analizi notları
    
    JSON formatında yanıt ver.
    """
    
    content = await generate_ai_content(prompt, "Sen SEO uzmanısın. JSON formatında yanıt ver.")
    
    # Save analysis
    analysis = SEOAnalysis(
        article_id=article_id,
        keyword=article['title'],
        suggestions=[content]
    )
    await db.seo_analysis.insert_one(analysis.model_dump())
    
    return {
        "article_id": article_id,
        "suggestions": content,
        "analyzed_at": datetime.now(timezone.utc).isoformat()
    }

# ============== FOOTBALL DATA API ==============

@api_router.get("/sports/matches")
async def get_matches(
    league: str = "PL",  # PL, SA, BL1, etc.
    status: Optional[str] = None  # SCHEDULED, LIVE, FINISHED
):
    """Get matches from Football Data API"""
    try:
        async with httpx.AsyncClient() as client:
            headers = {"X-Auth-Token": FOOTBALL_API_KEY}
            url = f"https://api.football-data.org/v4/competitions/{league}/matches"
            params = {}
            if status:
                params["status"] = status
            
            response = await client.get(url, headers=headers, params=params, timeout=30)
            
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
                return {
                    "matches": [
                        {"home_team": "Manchester United", "away_team": "Liverpool", "home_score": 2, "away_score": 1, "league": "Premier League", "match_date": "2026-01-15", "status": "FINISHED"},
                        {"home_team": "Arsenal", "away_team": "Chelsea", "home_score": 3, "away_score": 2, "league": "Premier League", "match_date": "2026-01-14", "status": "FINISHED"},
                        {"home_team": "Galatasaray", "away_team": "Fenerbahce", "home_score": 1, "away_score": 1, "league": "Super Lig", "match_date": "2026-01-13", "status": "FINISHED"}
                    ],
                    "competition": league,
                    "note": "Demo data - API key required for live data"
                }
    except Exception as e:
        logger.error(f"Football API error: {e}")
        return {
            "matches": [
                {"home_team": "Galatasaray", "away_team": "Besiktas", "home_score": 2, "away_score": 0, "league": "Süper Lig", "match_date": "2026-01-15", "status": "FINISHED"},
                {"home_team": "Fenerbahce", "away_team": "Trabzonspor", "home_score": 3, "away_score": 1, "league": "Süper Lig", "match_date": "2026-01-14", "status": "FINISHED"}
            ],
            "competition": "Demo League"
        }

@api_router.get("/sports/standings")
async def get_standings(league: str = "PL"):
    """Get league standings"""
    try:
        async with httpx.AsyncClient() as client:
            headers = {"X-Auth-Token": FOOTBALL_API_KEY}
            url = f"https://api.football-data.org/v4/competitions/{league}/standings"
            
            response = await client.get(url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                return {
                    "standings": [
                        {"position": 1, "team": "Galatasaray", "points": 45, "won": 14, "draw": 3, "lost": 2},
                        {"position": 2, "team": "Fenerbahce", "points": 42, "won": 13, "draw": 3, "lost": 3},
                        {"position": 3, "team": "Besiktas", "points": 38, "won": 11, "draw": 5, "lost": 3}
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
    total_bonus_sites = await db.bonus_sites.count_documents({})
    published_articles = await db.articles.count_documents({"is_published": True})
    total_views = await db.articles.aggregate([
        {"$group": {"_id": None, "total": {"$sum": "$view_count"}}}
    ]).to_list(1)
    
    return {
        "total_articles": total_articles,
        "total_bonus_sites": total_bonus_sites,
        "published_articles": published_articles,
        "total_views": total_views[0]["total"] if total_views else 0
    }

# ============== SEED DATA ==============

@api_router.post("/seed")
async def seed_database():
    """Seed database with initial data"""
    
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
        existing = await db.categories.find_one({"slug": cat["slug"]})
        if not existing:
            cat_obj = Category(**cat)
            await db.categories.insert_one(cat_obj.model_dump())
    
    # Seed bonus sites
    bonus_sites = [
        {
            "name": "BetStar", "logo_url": "https://images.unsplash.com/photo-1709873582570-4f17d43921d4?w=100&h=100&fit=crop",
            "bonus_type": "deneme", "bonus_amount": "500 TL", "affiliate_url": "#",
            "rating": 4.8, "features": ["Hızlı Ödeme", "7/24 Destek", "Mobil Uyumlu"], "is_featured": True, "order": 1
        },
        {
            "name": "WinMax", "logo_url": "https://images.unsplash.com/photo-1763089221979-ebb2a748358a?w=100&h=100&fit=crop",
            "bonus_type": "deneme", "bonus_amount": "1000 TL", "affiliate_url": "#",
            "rating": 4.9, "features": ["Yüksek Oranlar", "Canlı Bahis", "Casino"], "is_featured": True, "order": 2
        },
        {
            "name": "LuckBet", "logo_url": "https://images.unsplash.com/photo-1678696419211-6e0fb533c95e?w=100&h=100&fit=crop",
            "bonus_type": "hosgeldin", "bonus_amount": "2000 TL", "affiliate_url": "#",
            "rating": 4.7, "features": ["Geniş Bahis Seçenekleri", "Kripto Ödeme"], "is_featured": True, "order": 3
        },
        {
            "name": "SportKing", "logo_url": "https://images.unsplash.com/photo-1762278804798-dd7e493db051?w=100&h=100&fit=crop",
            "bonus_type": "yatirim", "bonus_amount": "%100 Bonus", "affiliate_url": "#",
            "rating": 4.6, "features": ["Spor Odaklı", "Yüksek Limitler"], "is_featured": False, "order": 4
        },
        {
            "name": "CasinoPlus", "logo_url": "https://images.pexels.com/photos/7594162/pexels-photo-7594162.jpeg?w=100&h=100&fit=crop",
            "bonus_type": "kayip", "bonus_amount": "%15 Kayıp Bonusu", "affiliate_url": "#",
            "rating": 4.5, "features": ["Casino Oyunları", "Slot Çeşitliliği"], "is_featured": False, "order": 5
        }
    ]
    
    for site in bonus_sites:
        existing = await db.bonus_sites.find_one({"name": site["name"]})
        if not existing:
            site_obj = BonusSite(**site)
            await db.bonus_sites.insert_one(site_obj.model_dump())
    
    # Seed articles
    articles = [
        {
            "title": "2026 Deneme Bonusu Veren Siteler - Güncel Liste",
            "slug": "2026-deneme-bonusu-veren-siteler",
            "excerpt": "2026 yılında deneme bonusu veren en güvenilir bahis sitelerinin güncel listesi. Yatırımsız bonus fırsatları ve detaylı incelemeler.",
            "content": """<h2>2026 Deneme Bonusu Nedir?</h2>
<p>Deneme bonusu, bahis sitelerinin yeni üyelerine sunduğu yatırımsız bonus fırsatıdır. Bu bonus sayesinde hiç para yatırmadan bahis yapabilir ve kazanç elde edebilirsiniz.</p>

<h2>En İyi Deneme Bonusu Veren Siteler</h2>
<p>2026 yılında en yüksek deneme bonusu veren siteleri sizler için derledik. Güvenilirlik, ödeme hızı ve bonus miktarı kriterlerine göre sıraladık.</p>

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
<p>Son 5 maçta 4 galibiyet alan Galatasaray, formda bir grafik çiziyor. Hücum hattındaki etkinlik dikkat çekici.</p>

<h3>Fenerbahçe</h3>
<p>Deplasman performansı ile öne çıkan Fenerbahçe, derbi öncesi moralli.</p>

<h2>Taktiksel Beklentiler</h2>
<p>Her iki takımın da yüksek tempolu oynayacağı bir maç bekleniyor. Orta saha mücadelesi belirleyici olacak.</p>

<p>[İÇ_LİNK: Süper Lig puan durumu için tıklayın]</p>""",
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

<h3>Manchester United 2-1 Liverpool</h3>
<p>Old Trafford'da oynanan zorlu mücadelede ev sahibi Manchester United, 2-1 galip geldi. Rashford'un 78. dakikada attığı gol maçın kaderini belirledi.</p>

<h3>Arsenal 3-0 Tottenham</h3>
<p>Kuzey Londra derbisinde Arsenal üstünlüğü ele geçirdi. Saka, Rice ve Havertz'in golleriyle 3-0'lık net skorla sahadan galip ayrıldı.</p>

<h2>Puan Durumu Güncellemesi</h2>
<p>Arsenal zirvede yerini koruyor, Manchester City takipte. Liverpool ise düşüşe geçti.</p>

<p>[İÇ_LİNK: Premier Lig bahis oranları için deneme bonusu sayfamıza göz atın]</p>""",
            "category": "spor",
            "tags": ["premier lig", "manchester united", "arsenal", "mac ozeti"],
            "image_url": "https://images.unsplash.com/photo-1706675780107-7c43cc487928?w=800",
            "seo_title": "Premier Lig Hafta Sonu Maç Özetleri | Ocak 2026",
            "seo_description": "Premier Lig'de haftanın tüm maç özetleri ve sonuçları. Manchester derbisi, Arsenal galibiyeti ve puan durumu."
        }
    ]
    
    for article in articles:
        existing = await db.articles.find_one({"slug": article["slug"]})
        if not existing:
            article_obj = Article(**article)
            await db.articles.insert_one(article_obj.model_dump())
    
    return {"message": "Database seeded successfully", "categories": len(categories), "bonus_sites": len(bonus_sites), "articles": len(articles)}

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
