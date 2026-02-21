"""
Multi-Tenant Authority Platform API
Production-Ready Backend with Hardening
Version: 3.0.0
"""

from fastapi import FastAPI, APIRouter, HTTPException, Query, Request, Depends, status, BackgroundTasks
from fastapi.responses import JSONResponse, PlainTextResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
import os
import sys
import logging
import json
import time
import uuid
import hashlib
import subprocess
import asyncio
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any, Callable
from pydantic import BaseModel, Field, ConfigDict
from collections import defaultdict
import httpx
import re
from passlib.context import CryptContext
import jwt as pyjwt
from emergentintegrations.llm.chat import LlmChat, UserMessage

# ============== CONFIGURATION ==============

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Environment validation with fail-fast
def get_required_env(key: str, default: str = None) -> str:
    """Get required environment variable with fail-fast behavior"""
    value = os.environ.get(key, default)
    if value is None:
        print(f"[FATAL] Required environment variable '{key}' is not set.", file=sys.stderr)
        print(f"[FATAL] Please set {key} in your .env file or environment.", file=sys.stderr)
        sys.exit(1)
    return value

def get_optional_env(key: str, default: str = "") -> str:
    """Get optional environment variable with default"""
    return os.environ.get(key, default)

# Required environment variables
MONGO_URL = get_required_env("MONGO_URL")
DB_NAME = get_required_env("DB_NAME")

# Optional environment variables
EMERGENT_LLM_KEY = get_optional_env("EMERGENT_LLM_KEY")
FOOTBALL_API_KEY = get_optional_env("FOOTBALL_DATA_API_KEY", "demo")
CLOUDFLARE_API_TOKEN = get_optional_env("CLOUDFLARE_API_TOKEN")
CLOUDFLARE_ACCOUNT_ID = get_optional_env("CLOUDFLARE_ACCOUNT_ID")

# Admin auth config
ADMIN_USERNAME = get_optional_env("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = get_optional_env("ADMIN_PASSWORD_HASH", "")
JWT_SECRET = get_optional_env("JWT_SECRET", "changeme-set-in-env")
JWT_EXPIRE_HOURS = int(get_optional_env("JWT_EXPIRE_HOURS", "24"))
ODDS_API_KEY = get_optional_env("ODDS_API_KEY", "")
PERIGON_API_KEY = get_optional_env("PERIGON_API_KEY", "")

# ============== SPORTS CACHE ==============

_scores_cache: Dict[str, Any] = {"data": None, "ts": 0, "error_count": 0, "last_error": None}
_CACHE_TTL = 120  # seconds
_featured_match_override: Optional[str] = None  # match id override from admin
_ai_insight_enabled: bool = True

SPORT_KEYS = [
    "soccer_turkey_super_league",
    "soccer_epl",
    "soccer_spain_la_liga",
    "soccer_germany_bundesliga",
    "soccer_italy_serie_a",
    "soccer_uefa_champs_league",
]

# CORS configuration
CORS_ORIGINS = get_optional_env("CORS_ORIGINS", "*")
CORS_ALLOW_CREDENTIALS = get_optional_env("CORS_ALLOW_CREDENTIALS", "false").lower() == "true"

# Rate limiting configuration
RATE_LIMIT_REQUESTS = int(get_optional_env("RATE_LIMIT_REQUESTS", "60"))
RATE_LIMIT_WINDOW = int(get_optional_env("RATE_LIMIT_WINDOW", "60"))

# Build info
GIT_COMMIT = get_optional_env("GIT_COMMIT", "")
BUILD_TIME = get_optional_env("BUILD_TIME", datetime.now(timezone.utc).isoformat())

# Production mode
DEBUG_MODE = get_optional_env("DEBUG_MODE", "false").lower() == "true"

# ============== STRUCTURED LOGGING ==============

class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging"""
    def format(self, record):
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        if hasattr(record, 'request_id'):
            log_record["request_id"] = record.request_id
        if hasattr(record, 'extra_data'):
            log_record.update(record.extra_data)
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

# Configure logging
logger = logging.getLogger("api")
logger.setLevel(logging.INFO if not DEBUG_MODE else logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.handlers = [handler]

# ============== RATE LIMITER ==============

class InMemoryRateLimiter:
    """Simple in-memory rate limiter per IP"""
    def __init__(self, requests_per_window: int = 60, window_seconds: int = 60):
        self.requests_per_window = requests_per_window
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[float]] = defaultdict(list)
    
    def is_allowed(self, client_ip: str) -> tuple[bool, int]:
        """Check if request is allowed, returns (allowed, remaining)"""
        now = time.time()
        window_start = now - self.window_seconds
        
        # Clean old requests
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if req_time > window_start
        ]
        
        current_count = len(self.requests[client_ip])
        remaining = max(0, self.requests_per_window - current_count)
        
        if current_count >= self.requests_per_window:
            return False, 0
        
        self.requests[client_ip].append(now)
        return True, remaining - 1
    
    def get_retry_after(self, client_ip: str) -> int:
        """Get seconds until rate limit resets"""
        if not self.requests[client_ip]:
            return 0
        oldest = min(self.requests[client_ip])
        return max(0, int(self.window_seconds - (time.time() - oldest)))

rate_limiter = InMemoryRateLimiter(RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW)

# ============== DATABASE ==============

client: AsyncIOMotorClient = None
db = None

async def connect_to_mongo():
    """Connect to MongoDB with validation"""
    global client, db
    try:
        client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        # Ping to verify connection
        await client.admin.command('ping')
        db = client[DB_NAME]
        logger.info("MongoDB connection established", extra={"extra_data": {"database": DB_NAME}})
        return True
    except Exception as e:
        logger.error(f"MongoDB connection failed: {str(e)}")
        return False

async def disconnect_from_mongo():
    """Disconnect from MongoDB"""
    global client
    if client:
        client.close()
        logger.info("MongoDB connection closed")

async def ping_mongo() -> tuple[bool, float]:
    """Ping MongoDB and return status with latency"""
    if not client:
        return False, 0
    try:
        start = time.time()
        await client.admin.command('ping')
        latency = (time.time() - start) * 1000
        return True, latency
    except Exception as e:
        logger.error(f"MongoDB ping failed: {str(e)}")
        return False, 0

# ============== LIFESPAN ==============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler"""
    # Startup
    logger.info("Starting application...")
    
    connected = await connect_to_mongo()
    if not connected:
        logger.error("[FATAL] Cannot start without database connection")
        sys.exit(1)
    
    logger.info("Application started successfully", extra={
        "extra_data": {
            "version": get_git_commit(),
            "build_time": BUILD_TIME,
            "debug_mode": DEBUG_MODE
        }
    })
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await disconnect_from_mongo()
    logger.info("Application shutdown complete")

# ============== UTILITY FUNCTIONS ==============

def get_git_commit() -> str:
    """Get git commit hash"""
    if GIT_COMMIT:
        return GIT_COMMIT
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() if result.returncode == 0 else "unknown"
    except:
        return "unknown"

def get_client_ip(request: Request) -> str:
    """Extract client IP from request"""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def generate_request_id() -> str:
    """Generate unique request ID"""
    return str(uuid.uuid4())[:8]

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    text = text.lower()
    for old, new in [('ı', 'i'), ('İ', 'i'), ('ş', 's'), ('Ş', 's'), ('ğ', 'g'), ('Ğ', 'g'), 
                     ('ü', 'u'), ('Ü', 'u'), ('ö', 'o'), ('Ö', 'o'), ('ç', 'c'), ('Ç', 'c')]:
        text = text.replace(old, new)
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    return text.strip('-')

def extract_bonus_value(bonus_amount: str) -> int:
    """Extract numeric value from bonus amount string"""
    numbers = re.findall(r'\d+', bonus_amount.replace('.', '').replace(',', ''))
    return int(numbers[0]) if numbers else 0

# ============== APP INITIALIZATION ==============

app = FastAPI(
    title="Multi-Tenant Authority Platform API",
    version="3.0.0",
    docs_url="/docs" if DEBUG_MODE else None,
    redoc_url="/redoc" if DEBUG_MODE else None,
    lifespan=lifespan
)

api_router = APIRouter(prefix="/api")

# ============== MIDDLEWARE ==============

@app.middleware("http")
async def request_middleware(request: Request, call_next):
    """Add request ID, logging, and rate limiting"""
    request_id = generate_request_id()
    client_ip = get_client_ip(request)
    start_time = time.time()
    
    # Add request_id to state
    request.state.request_id = request_id
    
    # Rate limiting — tracking ve health endpoint'lerini dışla
    RATE_LIMIT_SKIP = ("/api/sports/", "/api/performance/", "/api/go/", "/health", "/version", "/db-check")
    rl_remaining: Optional[int] = None
    if request.url.path.startswith("/api") and not request.url.path.startswith(RATE_LIMIT_SKIP):
        allowed, rl_remaining = rate_limiter.is_allowed(client_ip)
        if not allowed:
            retry_after = rate_limiter.get_retry_after(client_ip)
            logger.warning("Rate limit exceeded", extra={
                "extra_data": {"client_ip": client_ip, "path": request.url.path},
                "request_id": request_id
            })
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "retry_after": retry_after,
                    "request_id": request_id
                },
                headers={
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Remaining": "0",
                    "X-Request-ID": request_id
                }
            )
    
    # Process request
    try:
        response = await call_next(request)
        
        # Add headers
        response.headers["X-Request-ID"] = request_id
        if rl_remaining is not None:
            response.headers["X-RateLimit-Remaining"] = str(rl_remaining)
        
        # Log request
        duration = (time.time() - start_time) * 1000
        logger.info("Request completed", extra={
            "extra_data": {
                "method": request.method,
                "path": request.url.path,
                "status": response.status_code,
                "duration_ms": round(duration, 2),
                "client_ip": client_ip
            },
            "request_id": request_id
        })
        
        return response
    except Exception as e:
        logger.error(f"Request failed: {str(e)}", extra={
            "extra_data": {"path": request.url.path},
            "request_id": request_id
        })
        raise

# CORS middleware
cors_origins = [origin.strip() for origin in CORS_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ============== EXCEPTION HANDLER ==============

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler - no stack traces to client"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    
    # Log full error server-side
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True, extra={
        "request_id": request_id,
        "extra_data": {"path": request.url.path}
    })
    
    # Return safe error to client
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred" if not DEBUG_MODE else str(exc),
            "request_id": request_id
        },
        headers={"X-Request-ID": request_id}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP exception handler"""
    request_id = getattr(request.state, 'request_id', 'unknown')
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "request_id": request_id
        },
        headers={"X-Request-ID": request_id}
    )

# ============== HEALTH CHECK ENDPOINTS ==============

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}

@app.get("/version")
async def version_info():
    """Version information endpoint"""
    return {
        "commit": get_git_commit(),
        "buildTime": BUILD_TIME,
        "version": "3.0.0"
    }

@app.get("/db-check")
async def db_check():
    """Database connectivity check"""
    is_connected, latency = await ping_mongo()
    
    if is_connected:
        return {
            "status": "connected",
            "database": DB_NAME,
            "latency_ms": round(latency, 2)
        }
    else:
        return JSONResponse(
            status_code=503,
            content={
                "status": "disconnected",
                "database": DB_NAME,
                "error": "Database connection failed"
            }
        )

# ============== PYDANTIC MODELS ==============

class Domain(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    domain_name: str
    display_name: str
    focus: str = "bonus"
    theme: Dict[str, str] = {}
    logo_url: str = ""
    favicon_url: str = ""
    cloudflare_zone_id: Optional[str] = None
    cloudflare_status: str = "pending"
    nameservers: List[str] = []
    ssl_status: str = "pending"
    is_active: bool = True
    meta_title: str = ""
    meta_description: str = ""
    google_analytics_id: str = ""
    auto_article_enabled: bool = True
    auto_news_enabled: bool = True
    content_language: str = "tr"
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
    global_cta_clicks: int = 0
    global_affiliate_clicks: int = 0
    global_impressions: int = 0
    is_active: bool = True
    is_global: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class DomainPerformance(BaseModel):
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
    domain_id: Optional[str] = None
    title: str
    slug: str = ""
    excerpt: str = ""
    content: str = ""
    category: str = "bonus"
    tags: List[str] = []
    image_url: str = ""
    author: str = "Admin"
    is_published: bool = True
    is_ai_generated: bool = False
    is_auto_generated: bool = False
    seo_title: str = ""
    seo_description: str = ""
    schema_type: str = "Article"
    internal_links: List[str] = []
    view_count: int = 0
    content_hash: str = ""
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    content_updated_at: Optional[str] = None

class Category(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    domain_id: Optional[str] = None
    name: str
    slug: str
    description: str = ""
    type: str
    order: int = 0

class DomainSite(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    domain_id: str
    site_id: str
    custom_order: int = 0
    is_active: bool = True

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

def calculate_heuristic_score(site: dict) -> float:
    """Calculate heuristic score for ranking"""
    score = min(site.get('bonus_value', 0) / 25, 40)
    score += max(0, 20 - site.get('turnover_requirement', 10))
    score += site.get('rating', 4.0) * 4
    return score

def calculate_performance_score(perf: dict) -> float:
    """Calculate performance score from tracking data"""
    impressions = max(perf.get('impressions', 0), 1)
    cta_clicks = perf.get('cta_clicks', 0)
    cta_rate = (cta_clicks / impressions) * 100
    score = min(cta_rate * 10, 30)
    score += min(perf.get('avg_time_on_page', 0) / 10, 20)
    score += min(perf.get('avg_scroll_depth', 0) / 4, 25)
    return score

async def generate_ai_content(prompt: str, system_message: str = "Sen profesyonel bir Türkçe içerik yazarısın.") -> str:
    """Generate AI content using Emergent integrations"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=str(uuid.uuid4()), system_message=system_message).with_model("openai", "gpt-5.2")
        return await chat.send_message(UserMessage(text=prompt))
    except Exception as e:
        logger.error(f"AI content generation failed: {str(e)}")
        return f"AI içerik üretimi başarısız: {str(e)}"

# ============== API ROUTES ==============

@api_router.get("/")
async def api_root():
    """API root endpoint"""
    return {
        "message": "Multi-Tenant Authority Platform API",
        "version": "3.0.0",
        "status": "operational"
    }

# Domain Management
@api_router.post("/domains", response_model=Domain)
async def create_domain(domain: DomainCreate, background_tasks: BackgroundTasks):
    """Create a new domain with auto-generated content"""
    existing = await db.domains.find_one({"domain_name": domain.domain_name})
    if existing:
        raise HTTPException(status_code=400, detail="Domain already exists")
    
    domain_obj = Domain(**domain.model_dump())
    await db.domains.insert_one(domain_obj.model_dump())
    
    # Copy global sites to domain
    global_sites = await db.bonus_sites.find({"is_global": True, "is_active": True}, {"_id": 0}).to_list(100)
    for site in global_sites:
        domain_site = DomainSite(domain_id=domain_obj.id, site_id=site["id"])
        await db.domain_sites.insert_one(domain_site.model_dump())
        perf = DomainPerformance(domain_id=domain_obj.id, site_id=site["id"], performance_score=calculate_heuristic_score(site))
        await db.domain_performance.insert_one(perf.model_dump())
    
    # Auto-generate starter content in background
    background_tasks.add_task(auto_generate_domain_content, domain_obj.id, domain_obj.domain_name, domain_obj.focus)
    
    logger.info(f"Domain created: {domain.domain_name} - auto content generation started")
    return domain_obj

async def auto_generate_domain_content(domain_id: str, domain_name: str, focus: str):
    """Generate starter content for a new domain"""
    topic_map = {
        "bonus": [
            "Deneme Bonusu Veren Siteler 2026 Guncel Liste",
            "Hosgeldin Bonusu Rehberi En Yuksek Bonuslar",
            "Cevrim Sarti Nedir Nasil Hesaplanir",
            "Yatirimsiz Bonus Veren Siteler Tam Liste",
            "Canli Bahis Bonuslari ve Promosyonlar",
        ],
        "spor": [
            "Super Lig Haftalik Analiz ve Tahminler",
            "Canli Bahis Stratejileri Rehberi",
            "Futbol Istatistikleri Ile Kazanma Taktikleri",
            "Basketbol Bahis Rehberi NBA ve Euroleague",
            "Spor Bahislerinde Banko Maclar Nasil Bulunur",
        ],
        "hibrit": [
            "Deneme Bonusu Veren Siteler 2026 Guncel Liste",
            "Super Lig Haftalik Analiz ve Tahminler",
            "Hosgeldin Bonusu Rehberi En Yuksek Bonuslar",
            "Canli Bahis Stratejileri ve Bonuslari",
            "Spor Bahislerinde Kazanma Taktikleri",
        ],
    }
    topics = topic_map.get(focus, topic_map["bonus"])
    
    for topic in topics:
        try:
            existing = await db.articles.find_one({"domain_id": domain_id, "title": {"$regex": topic[:20], "$options": "i"}})
            if existing:
                continue
            
            prompt = f"""'{domain_name}' sitesi için '{topic}' konusunda profesyonel, SEO uyumlu ve özgün bir makale yaz.

KURALLAR:
- 1000-1500 kelime arası olmalı
- HTML formatında yaz (h2, h3, p, ul, li, strong etiketleri kullan)
- En az 3 adet h2 başlık kullan
- Her h2 altında en az 2 paragraf olsun
- Doğal, bilgilendirici ve otoriter bir ton kullan
- Anahtar kelimeyi ({topic}) ilk paragrafta, en az 1 h2 başlıkta ve son paragrafta doğal şekilde kullan
- Anahtar kelime yoğunluğu %1-2 arasında olsun
- En az 1 adet sıralı veya sırasız liste ekle
- İç bağlantı için uygun anchor text önerileri bırak
- Sonuç paragrafında kullanıcıya yönlendirme yap (CTA)
- Gerçekçi ve güncel bilgiler kullan (2026 yılı)
- Paragraflar kısa ve okunabilir olsun (3-4 cümle)
- Keyword stuffing yapma, doğal yaz"""
            
            content = await generate_ai_content(prompt)
            
            title_clean = topic.replace("Guncel", "Güncel").replace("Yuksek", "Yüksek").replace("Sarti", "Şartı").replace("Nasil", "Nasıl").replace("Hesaplanir", "Hesaplanır").replace("Yatirimsiz", "Yatırımsız").replace("Canli", "Canlı").replace("Istatistikleri", "İstatistikleri").replace("Ile", "İle").replace("Taktikleri", "Taktikleri")
            seo_title = f"{title_clean} - {domain_name} Rehberi"[:60]
            seo_desc = f"{title_clean} hakkında detaylı ve güncel rehber. En iyi fırsatlar, stratejiler ve uzman tavsiyeleri {domain_name}'da."[:160]
            
            article = Article(
                domain_id=domain_id,
                title=title_clean,
                slug=slugify(topic),
                excerpt=f"{title_clean} hakkında kapsamlı ve güncel rehber.",
                content=content,
                category="bonus" if "bonus" in topic.lower() or "cevrim" in topic.lower() else "spor",
                tags=[slugify(t) for t in topic.split()[:4]],
                seo_title=seo_title,
                seo_description=seo_desc,
                is_ai_generated=True,
                is_auto_generated=True,
                is_published=True,
                content_hash=hashlib.md5(content.encode()).hexdigest(),
                content_updated_at=datetime.now(timezone.utc).isoformat(),
            )
            await db.articles.insert_one(article.model_dump())
            logger.info(f"Auto article for {domain_name}: {topic}")
            await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"Auto content failed for {domain_name}/{topic}: {e}")

# Public Site API - domain bazlı içerik sunma
@api_router.get("/site/{domain_name}")
async def get_site_data(domain_name: str):
    """Get complete site data for a domain - used by frontend to render the site"""
    domain = await db.domains.find_one({"domain_name": domain_name}, {"_id": 0})
    if not domain:
        raise HTTPException(status_code=404, detail="Site bulunamadı")
    
    domain_id = domain["id"]
    
    # Bonus sites for this domain
    domain_site_links = await db.domain_sites.find({"domain_id": domain_id, "is_active": True}, {"_id": 0}).to_list(100)
    site_ids = [ds["site_id"] for ds in domain_site_links]
    bonus_sites = await db.bonus_sites.find({"id": {"$in": site_ids}, "is_active": True}, {"_id": 0}).to_list(100)
    
    # Articles for this domain
    articles = await db.articles.find(
        {"domain_id": domain_id, "is_published": True},
        {"_id": 0, "content": 0}
    ).sort("created_at", -1).limit(20).to_list(20)
    
    # Stats
    article_count = await db.articles.count_documents({"domain_id": domain_id, "is_published": True})
    generating = await db.articles.count_documents({"domain_id": domain_id, "is_auto_generated": True})
    
    return {
        "domain": domain,
        "bonus_sites": bonus_sites,
        "articles": articles,
        "stats": {
            "total_articles": article_count,
            "auto_generated": generating,
            "total_bonus_sites": len(bonus_sites),
        },
        "is_ready": article_count > 0,
    }

@api_router.get("/domains")
async def list_domains():
    """List all domains"""
    domains = await db.domains.find({}, {"_id": 0}).to_list(100)
    return domains

@api_router.get("/domains/{domain_id}")
async def get_domain(domain_id: str):
    """Get domain by ID"""
    domain = await db.domains.find_one({"id": domain_id}, {"_id": 0})
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    return domain

@api_router.get("/domains/by-name/{domain_name}")
async def get_domain_by_name(domain_name: str):
    """Get domain by name"""
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
    logger.info(f"Domain deleted: {domain_id}")
    return {"message": "Domain deleted"}

@api_router.put("/domains/{domain_id}")
async def update_domain(domain_id: str, data: Dict[str, Any]):
    """Update a domain"""
    data.pop("id", None)
    data.pop("_id", None)
    await db.domains.update_one({"id": domain_id}, {"$set": data})
    updated = await db.domains.find_one({"id": domain_id}, {"_id": 0})
    return updated

# Domain Sites
@api_router.get("/domains/{domain_id}/sites")
async def get_domain_sites(domain_id: str):
    """Get sites for a domain sorted by performance"""
    domain_sites = await db.domain_sites.find({"domain_id": domain_id, "is_active": True}, {"_id": 0}).to_list(100)
    site_ids = [ds["site_id"] for ds in domain_sites]
    
    performances = await db.domain_performance.find({"domain_id": domain_id}, {"_id": 0}).sort("performance_score", -1).to_list(100)
    perf_map = {p["site_id"]: p for p in performances}
    
    sites = await db.bonus_sites.find({"id": {"$in": site_ids}, "is_active": True}, {"_id": 0}).to_list(100)
    
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

# Bonus Sites
@api_router.get("/bonus-sites")
async def get_all_bonus_sites(limit: int = 50):
    """Get all global bonus sites sorted by sort_order"""
    sites = await db.bonus_sites.find({"is_active": True}, {"_id": 0}).sort("sort_order", 1).limit(limit).to_list(limit)
    return sites

@api_router.post("/bonus-sites")
async def create_bonus_site(site: Dict[str, Any]):
    """Create a new bonus site"""
    site_obj = BonusSite(**site)
    site_obj.bonus_value = extract_bonus_value(site_obj.bonus_amount)
    await db.bonus_sites.insert_one(site_obj.model_dump())
    logger.info(f"Bonus site created: {site_obj.name}")
    return site_obj

@api_router.delete("/bonus-sites/{site_id}")
async def delete_bonus_site(site_id: str):
    """Delete a bonus site"""
    await db.bonus_sites.delete_one({"id": site_id})
    return {"message": "Site deleted"}

@api_router.put("/bonus-sites/{site_id}")
async def update_bonus_site(site_id: str, data: Dict[str, Any]):
    """Update a bonus site"""
    data.pop("id", None)
    data.pop("_id", None)
    if "bonus_amount" in data:
        data["bonus_value"] = extract_bonus_value(data["bonus_amount"])
    if "features" in data and isinstance(data["features"], str):
        data["features"] = [f.strip() for f in data["features"].split(",") if f.strip()]
    await db.bonus_sites.update_one({"id": site_id}, {"$set": data})
    updated = await db.bonus_sites.find_one({"id": site_id}, {"_id": 0})
    return updated

# Performance Tracking
@api_router.post("/track/event")
async def track_event(event: PerformanceEventCreate):
    """Track performance event"""
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
    """Update site rankings for a domain"""
    performances = await db.domain_performance.find({"domain_id": domain_id}, {"_id": 0}).to_list(100)
    
    for perf in performances:
        site = await db.bonus_sites.find_one({"id": perf["site_id"]}, {"_id": 0})
        if not site:
            continue
        
        has_data = perf.get("impressions", 0) > 10
        score = calculate_performance_score(perf) if has_data else calculate_heuristic_score(site)
        
        await db.domain_performance.update_one(
            {"domain_id": domain_id, "site_id": perf["site_id"]},
            {"$set": {"performance_score": score}}
        )
    
    performances = await db.domain_performance.find({"domain_id": domain_id}, {"_id": 0}).sort("performance_score", -1).to_list(100)
    for i, perf in enumerate(performances):
        await db.domain_performance.update_one(
            {"domain_id": domain_id, "site_id": perf["site_id"]},
            {"$set": {"rank": i + 1, "is_featured": i < 2}}
        )
    
    return {"updated": len(performances)}

# Articles
@api_router.get("/articles")
async def get_articles(limit: int = 50, search: Optional[str] = None, category: Optional[str] = None):
    """Get all articles with optional search and filter"""
    query: Dict[str, Any] = {}
    if search:
        query["$or"] = [
            {"title": {"$regex": search, "$options": "i"}},
            {"content": {"$regex": search, "$options": "i"}},
        ]
    if category:
        query["category"] = category
    articles = await db.articles.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return articles

@api_router.post("/articles")
async def create_article(article: Dict[str, Any]):
    """Create a new article"""
    if not article.get("title"):
        raise HTTPException(status_code=400, detail="Başlık gerekli")
    if not article.get("slug"):
        article["slug"] = slugify(article["title"])
    # Auto-generate excerpt from content if not provided
    if not article.get("excerpt") and article.get("content"):
        excerpt_text = article["content"][:200].strip()
        article["excerpt"] = excerpt_text + "..." if len(article["content"]) > 200 else excerpt_text
    article["content_hash"] = hashlib.md5(article.get("content", "").encode()).hexdigest()
    article["content_updated_at"] = datetime.now(timezone.utc).isoformat()
    article_obj = Article(**article)
    await db.articles.insert_one(article_obj.model_dump())
    logger.info(f"Article created: {article_obj.title}")
    return article_obj.model_dump()

@api_router.put("/articles/{article_id}")
async def update_article(article_id: str, data: Dict[str, Any]):
    """Update an article"""
    data.pop("id", None)
    data.pop("_id", None)
    if "content" in data:
        data["content_hash"] = hashlib.md5(data["content"].encode()).hexdigest()
        data["content_updated_at"] = datetime.now(timezone.utc).isoformat()
    if "title" in data and "slug" not in data:
        data["slug"] = slugify(data["title"])
    await db.articles.update_one({"id": article_id}, {"$set": data})
    updated = await db.articles.find_one({"id": article_id}, {"_id": 0})
    return updated

@api_router.delete("/articles/{article_id}")
async def delete_article(article_id: str):
    """Delete an article"""
    await db.articles.delete_one({"id": article_id})
    return {"message": "Makale silindi"}

@api_router.get("/articles/slug/{slug}")
async def get_article_by_slug(slug: str):
    """Get article by slug and increment view count"""
    article = await db.articles.find_one({"slug": slug, "is_published": True}, {"_id": 0})
    if not article:
        raise HTTPException(status_code=404, detail="Makale bulunamadı")
    await db.articles.update_one({"slug": slug}, {"$inc": {"view_count": 1}})
    article["view_count"] = article.get("view_count", 0) + 1
    return article

@api_router.get("/articles/{article_id}")
async def get_article(article_id: str):
    """Get single article by ID"""
    article = await db.articles.find_one({"id": article_id}, {"_id": 0})
    if not article:
        raise HTTPException(status_code=404, detail="Makale bulunamadı")
    return article

@api_router.get("/domains/{domain_id}/articles")
async def get_domain_articles(domain_id: str, limit: int = 20):
    """Get articles for a domain"""
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
    logger.info(f"Article created: {article_obj.title}")
    return article_obj

# Auto Content
@api_router.post("/auto-content/generate-article")
async def auto_generate_article(domain_id: Optional[str] = None, topic: str = "deneme bonusu rehberi"):
    """Auto generate SEO article"""
    existing = await db.articles.find_one({"title": {"$regex": topic, "$options": "i"}, "domain_id": domain_id})
    if existing:
        return {"status": "skipped", "reason": "Similar article exists", "article_id": existing.get("id")}
    
    prompt = f"""Konu: {topic}

Profesyonel, SEO uyumlu ve özgün bir makale yaz.

KURALLAR:
- 1000-1500 kelime arası
- HTML formatında (h2, h3, p, ul, li, strong etiketleri)
- En az 3 adet h2 başlık
- Doğal, bilgilendirici ve otoriter ton
- Anahtar kelimeyi ilk paragrafta ve en az 1 h2'de kullan
- En az 1 liste ekle
- Sonuçta CTA paragrafı olsun
- 2026 yılına uygun güncel bilgiler
- Keyword stuffing yapma"""
    
    content = await generate_ai_content(prompt)
    
    article = Article(
        domain_id=domain_id,
        title=topic.title(),
        slug=slugify(topic),
        excerpt=f"{topic} hakkında detaylı rehber.",
        content=content,
        category="bonus",
        tags=[slugify(t) for t in topic.split()],
        is_ai_generated=True,
        is_auto_generated=True,
        content_hash=hashlib.md5(content.encode()).hexdigest(),
        content_updated_at=datetime.now(timezone.utc).isoformat()
    )
    
    await db.articles.insert_one(article.model_dump())
    logger.info(f"Auto article generated: {article.title}")
    return {"status": "created", "article_id": article.id, "title": article.title}

@api_router.post("/auto-content/bulk-generate")
async def bulk_generate_content(domain_id: Optional[str] = None, count: int = 5):
    """Bulk generate content"""
    topics = [
        "Deneme Bonusu Nedir Nasıl Alınır 2026",
        "En Yüksek Hoşgeldin Bonusu Veren Siteler",
        "Çevrim Şartı Nedir Nasıl Hesaplanır",
        "Yatırımsız Bonus Fırsatları Rehberi",
        "Canlı Bahis Stratejileri ve Taktikleri"
    ]
    
    results = []
    for topic in topics[:count]:
        result = await auto_generate_article(domain_id, topic)
        results.append(result)
        await asyncio.sleep(1)
    
    return {"generated": len([r for r in results if r.get("status") == "created"]), "results": results}

# AI Tools
@api_router.post("/ai/generate-content")
async def generate_content(request: Dict[str, Any]):
    """Generate AI content"""
    topic = request.get("topic", "")
    content = await generate_ai_content(f"Konu: {topic}\nSEO uyumlu makale yaz.")
    return {"content": content, "generated_at": datetime.now(timezone.utc).isoformat()}

@api_router.post("/ai/competitor-analysis")
async def competitor_analysis(request: Dict[str, Any]):
    """Analyze competitor"""
    url = request.get("competitor_url", "")
    content = await generate_ai_content(f"Rakip site analizi: {url}")
    return {"analysis": content, "url": url}

@api_router.post("/ai/keyword-gap-analysis")
async def keyword_gap_analysis(request: KeywordGapRequest):
    """Keyword gap analysis"""
    content = await generate_ai_content(f"Anahtar kelime analizi: {', '.join(request.keywords)}")
    return {"analysis": content, "keywords": request.keywords}

@api_router.get("/ai/weekly-seo-report")
async def weekly_seo_report(domain_id: Optional[str] = None):
    """Generate weekly SEO report"""
    stats = {
        "total_articles": await db.articles.count_documents({"domain_id": domain_id} if domain_id else {}),
        "total_domains": await db.domains.count_documents({}),
        "total_sites": await db.bonus_sites.count_documents({"is_active": True})
    }
    content = await generate_ai_content(f"Haftalık SEO raporu: {json.dumps(stats)}")
    return {"report": content, "stats": stats}

# ============== ADVANCED SEO ASSISTANT ==============

class SeoKeywordRequest(BaseModel):
    keywords: List[str]
    language: str = "tr"
    niche: str = "bonus"

class SeoAuditRequest(BaseModel):
    url: Optional[str] = None
    domain_id: Optional[str] = None

class SeoContentScoreRequest(BaseModel):
    article_id: Optional[str] = None
    title: str = ""
    content: str = ""
    target_keyword: str = ""

class SeoCompetitorRequest(BaseModel):
    competitor_url: str
    our_domain: str = ""

class SeoMetaRequest(BaseModel):
    topic: str
    page_type: str = "article"
    keywords: List[str] = []

class SeoInternalLinkRequest(BaseModel):
    article_id: Optional[str] = None
    content: str = ""

class SeoContentOptimizeRequest(BaseModel):
    article_id: Optional[str] = None
    content: str = ""
    title: str = ""
    target_keyword: str = ""

@api_router.get("/seo/dashboard")
async def seo_dashboard(domain_id: Optional[str] = None):
    """Comprehensive SEO dashboard with metrics"""
    query = {"domain_id": domain_id} if domain_id else {}

    total_articles = await db.articles.count_documents(query if domain_id else {})
    published = await db.articles.count_documents({**query, "is_published": True} if domain_id else {"is_published": True})
    ai_generated = await db.articles.count_documents({**query, "is_ai_generated": True} if domain_id else {"is_ai_generated": True})
    total_sites = await db.bonus_sites.count_documents({"is_active": True})
    total_domains = await db.domains.count_documents({})
    total_reports = await db.seo_reports.count_documents(query if domain_id else {})

    articles = await db.articles.find(
        query if domain_id else {},
        {"_id": 0, "title": 1, "seo_title": 1, "seo_description": 1, "content": 1, "slug": 1, "tags": 1, "view_count": 1}
    ).to_list(200)

    missing_meta = sum(1 for a in articles if not a.get("seo_title") or not a.get("seo_description"))
    short_content = sum(1 for a in articles if len((a.get("content") or "").split()) < 300)
    no_tags = sum(1 for a in articles if not a.get("tags"))
    total_views = sum(a.get("view_count", 0) for a in articles)

    health_score = 100
    if total_articles > 0:
        health_score -= int((missing_meta / total_articles) * 30)
        health_score -= int((short_content / total_articles) * 25)
        health_score -= int((no_tags / total_articles) * 15)
    if total_articles < 10:
        health_score -= 15
    if total_sites < 5:
        health_score -= 10
    health_score = max(0, min(100, health_score))

    return {
        "health_score": health_score,
        "total_articles": total_articles,
        "published_articles": published,
        "ai_generated_articles": ai_generated,
        "total_bonus_sites": total_sites,
        "total_domains": total_domains,
        "total_reports": total_reports,
        "total_views": total_views,
        "issues": {
            "missing_meta": missing_meta,
            "short_content": short_content,
            "no_tags": no_tags,
        },
        "recommendations": [
            f"{missing_meta} makale eksik meta başlık/açıklama" if missing_meta else None,
            f"{short_content} makale 300 kelimeden kısa" if short_content else None,
            f"{no_tags} makale etiketsiz" if no_tags else None,
            "Daha fazla içerik üretilmeli" if total_articles < 10 else None,
        ],
    }

@api_router.post("/seo/keyword-research")
async def seo_keyword_research(req: SeoKeywordRequest):
    """AI-powered keyword research with scoring and suggestions"""
    prompt = f"""Sen bir SEO uzmanısın. Aşağıdaki anahtar kelimeler için detaylı bir analiz yap.

Anahtar Kelimeler: {', '.join(req.keywords)}
Niş: {req.niche}
Dil: {req.language}

Şu JSON formatında yanıt ver (sadece JSON, başka bir şey yazma):
{{
  "keywords": [
    {{
      "keyword": "anahtar kelime",
      "search_volume_estimate": "yüksek/orta/düşük",
      "competition": "yüksek/orta/düşük",
      "difficulty_score": 65,
      "cpc_estimate": "düşük/orta/yüksek",
      "intent": "bilgilendirme/ticari/navigasyonel",
      "recommendation": "kısa açıklama"
    }}
  ],
  "related_keywords": ["ilgili1", "ilgili2", "ilgili3", "ilgili4", "ilgili5"],
  "long_tail_suggestions": ["uzun kuyruk 1", "uzun kuyruk 2", "uzun kuyruk 3"],
  "content_ideas": ["içerik fikri 1", "içerik fikri 2", "içerik fikri 3"],
  "summary": "genel değerlendirme"
}}"""

    result = await generate_ai_content(prompt, "Sen bir SEO ve dijital pazarlama uzmanısın. Sadece JSON formatında yanıt ver.")

    # Try to parse JSON from response
    parsed = None
    try:
        cleaned = result.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0].strip()
        parsed = json.loads(cleaned)
    except Exception:
        parsed = {"raw_analysis": result, "keywords": req.keywords}

    # Save report
    report = {
        "id": str(uuid.uuid4()),
        "type": "keyword_research",
        "input": {"keywords": req.keywords, "niche": req.niche},
        "result": parsed,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.seo_reports.insert_one({**report})
    report.pop("_id", None)

    return parsed

@api_router.post("/seo/site-audit")
async def seo_site_audit(req: SeoAuditRequest):
    """Comprehensive SEO audit of current site content"""
    articles = await db.articles.find(
        {"domain_id": req.domain_id} if req.domain_id else {},
        {"_id": 0, "title": 1, "seo_title": 1, "seo_description": 1, "content": 1, "slug": 1, "tags": 1, "category": 1}
    ).to_list(50)

    sites = await db.bonus_sites.find({"is_active": True}, {"_id": 0, "name": 1, "bonus_type": 1}).to_list(50)

    article_summaries = []
    for a in articles[:20]:
        word_count = len((a.get("content") or "").split())
        article_summaries.append({
            "title": a.get("title", ""),
            "has_seo_title": bool(a.get("seo_title")),
            "has_seo_desc": bool(a.get("seo_description")),
            "word_count": word_count,
            "has_tags": bool(a.get("tags")),
            "category": a.get("category", ""),
        })

    prompt = f"""Sen bir SEO denetçisisin. Aşağıdaki site verilerini analiz et ve kapsamlı bir SEO denetim raporu oluştur.

Site Verileri:
- Toplam Makale: {len(articles)}
- Bonus Siteleri: {len(sites)}
- Makale Özetleri: {json.dumps(article_summaries[:10], ensure_ascii=False)}

Şu JSON formatında yanıt ver (sadece JSON):
{{
  "overall_score": 72,
  "categories": [
    {{
      "name": "Teknik SEO",
      "score": 75,
      "issues": ["sorun 1", "sorun 2"],
      "fixes": ["çözüm 1", "çözüm 2"]
    }},
    {{
      "name": "İçerik Kalitesi",
      "score": 68,
      "issues": ["sorun 1"],
      "fixes": ["çözüm 1"]
    }},
    {{
      "name": "On-Page SEO",
      "score": 70,
      "issues": ["sorun 1"],
      "fixes": ["çözüm 1"]
    }},
    {{
      "name": "Kullanıcı Deneyimi",
      "score": 80,
      "issues": [],
      "fixes": []
    }}
  ],
  "priority_actions": ["öncelikli aksiyon 1", "öncelikli aksiyon 2", "öncelikli aksiyon 3"],
  "summary": "genel değerlendirme"
}}"""

    result = await generate_ai_content(prompt, "Sen bir SEO denetçisi ve teknik SEO uzmanısın. Sadece JSON formatında yanıt ver.")

    parsed = None
    try:
        cleaned = result.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0].strip()
        parsed = json.loads(cleaned)
    except Exception:
        parsed = {"raw_analysis": result, "overall_score": 0}

    report = {
        "id": str(uuid.uuid4()),
        "type": "site_audit",
        "input": {"domain_id": req.domain_id, "url": req.url},
        "result": parsed,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.seo_reports.insert_one({**report})
    report.pop("_id", None)

    return parsed

@api_router.post("/seo/content-score")
async def seo_content_score(req: SeoContentScoreRequest):
    """Score content for SEO quality"""
    content = req.content
    title = req.title

    if req.article_id and not content:
        article = await db.articles.find_one({"id": req.article_id}, {"_id": 0})
        if article:
            content = article.get("content", "")
            title = article.get("title", "")

    if not content:
        raise HTTPException(status_code=400, detail="İçerik gerekli")

    word_count = len(content.split())

    prompt = f"""Sen bir SEO içerik analisti olarak bu makaleyi değerlendir.

Başlık: {title}
Hedef Anahtar Kelime: {req.target_keyword or 'belirtilmedi'}
Kelime Sayısı: {word_count}
İçerik (ilk 500 kelime): {' '.join(content.split()[:500])}

Şu JSON formatında yanıt ver (sadece JSON):
{{
  "overall_score": 75,
  "scores": {{
    "keyword_usage": 70,
    "readability": 80,
    "structure": 65,
    "meta_quality": 60,
    "content_depth": 75
  }},
  "strengths": ["güçlü yön 1", "güçlü yön 2"],
  "weaknesses": ["zayıf yön 1", "zayıf yön 2"],
  "improvements": ["iyileştirme 1", "iyileştirme 2", "iyileştirme 3"],
  "keyword_density": "yüzde tahmini",
  "recommended_word_count": 1200,
  "summary": "özet değerlendirme"
}}"""

    result = await generate_ai_content(prompt, "Sen bir SEO içerik analisti ve editörüsün. Sadece JSON formatında yanıt ver.")

    parsed = None
    try:
        cleaned = result.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0].strip()
        parsed = json.loads(cleaned)
    except Exception:
        parsed = {"raw_analysis": result, "overall_score": 0}

    return {**parsed, "word_count": word_count, "title": title}

@api_router.post("/seo/competitor-deep")
async def seo_competitor_deep(req: SeoCompetitorRequest):
    """Deep competitor analysis with structured insights"""
    prompt = f"""Sen bir SEO rakip analiz uzmanısın. Aşağıdaki rakip siteyi analiz et.

Rakip Site: {req.competitor_url}
Bizim Sitemiz: {req.our_domain or 'belirtilmedi'}
Niş: Bonus/Bahis/Spor içerik sitesi

Şu JSON formatında yanıt ver (sadece JSON):
{{
  "competitor_profile": {{
    "domain": "{req.competitor_url}",
    "estimated_authority": "yüksek/orta/düşük",
    "content_strategy": "açıklama",
    "strengths": ["güçlü yön 1", "güçlü yön 2"],
    "weaknesses": ["zayıf yön 1", "zayıf yön 2"]
  }},
  "keyword_gaps": ["anahtar kelime 1", "anahtar kelime 2", "anahtar kelime 3", "anahtar kelime 4", "anahtar kelime 5"],
  "content_opportunities": ["fırsat 1", "fırsat 2", "fırsat 3"],
  "backlink_strategies": ["strateji 1", "strateji 2"],
  "action_plan": [
    {{"priority": "yüksek", "action": "aksiyon 1", "impact": "beklenen etki"}},
    {{"priority": "orta", "action": "aksiyon 2", "impact": "beklenen etki"}},
    {{"priority": "düşük", "action": "aksiyon 3", "impact": "beklenen etki"}}
  ],
  "summary": "genel değerlendirme"
}}"""

    result = await generate_ai_content(prompt, "Sen bir SEO ve dijital pazarlama rakip analiz uzmanısın. Sadece JSON formatında yanıt ver.")

    parsed = None
    try:
        cleaned = result.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0].strip()
        parsed = json.loads(cleaned)
    except Exception:
        parsed = {"raw_analysis": result}

    report = {
        "id": str(uuid.uuid4()),
        "type": "competitor_analysis",
        "input": {"competitor_url": req.competitor_url, "our_domain": req.our_domain},
        "result": parsed,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.seo_reports.insert_one({**report})
    report.pop("_id", None)

    return parsed

@api_router.post("/seo/meta-generator")
async def seo_meta_generator(req: SeoMetaRequest):
    """Generate SEO-optimized meta titles and descriptions"""
    prompt = f"""Sen bir SEO meta etiket uzmanısın. Aşağıdaki konu için optimize edilmiş meta etiketler oluştur.

Konu: {req.topic}
Sayfa Tipi: {req.page_type}
Hedef Anahtar Kelimeler: {', '.join(req.keywords) if req.keywords else 'belirtilmedi'}
Niş: Bonus/Bahis/Spor

Şu JSON formatında yanıt ver (sadece JSON):
{{
  "options": [
    {{
      "meta_title": "başlık (max 60 karakter)",
      "meta_description": "açıklama (max 160 karakter)",
      "focus_keyword": "odak kelime"
    }},
    {{
      "meta_title": "alternatif başlık",
      "meta_description": "alternatif açıklama",
      "focus_keyword": "odak kelime"
    }},
    {{
      "meta_title": "üçüncü alternatif",
      "meta_description": "üçüncü açıklama",
      "focus_keyword": "odak kelime"
    }}
  ],
  "og_title": "Open Graph başlık",
  "og_description": "Open Graph açıklama",
  "schema_suggestion": "Article/FAQPage/HowTo"
}}"""

    result = await generate_ai_content(prompt, "Sen bir SEO ve meta etiket optimizasyon uzmanısın. Sadece JSON formatında yanıt ver.")

    parsed = None
    try:
        cleaned = result.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0].strip()
        parsed = json.loads(cleaned)
    except Exception:
        parsed = {"raw_result": result}

    return parsed

@api_router.post("/seo/internal-links")
async def seo_internal_links(req: SeoInternalLinkRequest):
    """Suggest internal links based on content and existing articles"""
    content = req.content
    if req.article_id and not content:
        article = await db.articles.find_one({"id": req.article_id}, {"_id": 0})
        if article:
            content = article.get("content", "")

    all_articles = await db.articles.find(
        {"is_published": True},
        {"_id": 0, "title": 1, "slug": 1, "category": 1, "tags": 1}
    ).to_list(50)

    article_list = [{"title": a["title"], "slug": a["slug"], "category": a.get("category", "")} for a in all_articles]

    prompt = f"""Sen bir SEO iç link uzmanısın. Aşağıdaki içerik için iç bağlantı önerileri yap.

İçerik (ilk 300 kelime): {' '.join((content or '').split()[:300])}

Mevcut Makaleler:
{json.dumps(article_list[:20], ensure_ascii=False)}

Şu JSON formatında yanıt ver (sadece JSON):
{{
  "suggestions": [
    {{
      "anchor_text": "bağlantı metni",
      "target_slug": "hedef-makale-slug",
      "target_title": "hedef makale başlığı",
      "reason": "neden bu bağlantı öneriliyor"
    }}
  ],
  "missing_content": ["bu konuda makale yazılmalı 1", "bu konuda makale yazılmalı 2"],
  "link_strategy": "genel iç bağlantı stratejisi önerisi"
}}"""

    result = await generate_ai_content(prompt, "Sen bir SEO iç bağlantı ve site mimarisi uzmanısın. Sadece JSON formatında yanıt ver.")

    parsed = None
    try:
        cleaned = result.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0].strip()
        parsed = json.loads(cleaned)
    except Exception:
        parsed = {"raw_result": result}

    return parsed

@api_router.post("/seo/content-optimizer")
async def seo_content_optimizer(req: SeoContentOptimizeRequest):
    """AI-powered content optimization suggestions"""
    content = req.content
    title = req.title
    if req.article_id and not content:
        article = await db.articles.find_one({"id": req.article_id}, {"_id": 0})
        if article:
            content = article.get("content", "")
            title = article.get("title", "")

    if not content:
        raise HTTPException(status_code=400, detail="İçerik gerekli")

    prompt = f"""Sen bir SEO içerik optimizasyon uzmanısın. Bu makaleyi analiz et ve somut iyileştirme önerileri ver.

Başlık: {title}
Hedef Anahtar Kelime: {req.target_keyword or 'belirtilmedi'}
İçerik (ilk 600 kelime): {' '.join(content.split()[:600])}

Şu JSON formatında yanıt ver (sadece JSON):
{{
  "optimized_title": "optimize edilmiş başlık önerisi",
  "title_improvements": ["başlık iyileştirme 1", "başlık iyileştirme 2"],
  "content_improvements": [
    {{"section": "Giriş", "current_issue": "mevcut sorun", "suggestion": "iyileştirme önerisi"}},
    {{"section": "Ana İçerik", "current_issue": "mevcut sorun", "suggestion": "iyileştirme önerisi"}},
    {{"section": "Sonuç", "current_issue": "mevcut sorun", "suggestion": "iyileştirme önerisi"}}
  ],
  "keyword_suggestions": ["eklenecek anahtar kelime 1", "eklenecek anahtar kelime 2"],
  "structural_suggestions": ["yapısal öneri 1", "yapısal öneri 2"],
  "readability_tips": ["okunabilirlik ipucu 1", "okunabilirlik ipucu 2"],
  "estimated_improvement": "tahmini SEO etkisi açıklaması"
}}"""

    result = await generate_ai_content(prompt, "Sen bir SEO içerik optimizasyon uzmanısın. Sadece JSON formatında yanıt ver.")

    parsed = None
    try:
        cleaned = result.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0].strip()
        parsed = json.loads(cleaned)
    except Exception:
        parsed = {"raw_result": result}

    return parsed

@api_router.get("/seo/reports")
async def get_seo_reports(report_type: Optional[str] = None, limit: int = 20):
    """Get saved SEO reports"""
    query: Dict[str, Any] = {}
    if report_type:
        query["type"] = report_type
    reports = await db.seo_reports.find(query, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return {"reports": reports, "count": len(reports)}

@api_router.delete("/seo/reports/{report_id}")
async def delete_seo_report(report_id: str):
    """Delete a SEO report"""
    await db.seo_reports.delete_one({"id": report_id})
    return {"message": "Rapor silindi"}

# Sports
@api_router.get("/sports/matches")
async def get_matches(league: str = "PL"):
    """Legacy endpoint — redirects to /sports/scores"""
    return await get_live_scores()

# ── helpers ──────────────────────────────────────────────────────────

def _normalize_match(m: dict, sport_key: str) -> dict:
    scores = m.get("scores") or []
    home_score = next((s["score"] for s in scores if s["name"] == m["home_team"]), None)
    away_score = next((s["score"] for s in scores if s["name"] == m["away_team"]), None)
    slug_date = m["commence_time"][:10]
    home_slug = re.sub(r"[^a-z0-9]+", "-", m["home_team"].lower()).strip("-")
    away_slug = re.sub(r"[^a-z0-9]+", "-", m["away_team"].lower()).strip("-")
    return {
        "id": m["id"],
        "sport_key": sport_key,
        "sport_title": m.get("sport_title", ""),
        "home_team": m["home_team"],
        "away_team": m["away_team"],
        "commence_time": m["commence_time"],
        "completed": m.get("completed", False),
        "home_score": home_score,
        "away_score": away_score,
        "last_update": m.get("last_update"),
        "slug": f"{home_slug}-vs-{away_slug}-{slug_date}",
    }

async def _fetch_scores_from_api() -> list:
    """Fetch scores from Odds API with retry"""
    all_matches = []
    async with httpx.AsyncClient(timeout=12) as client:
        for sport_key in SPORT_KEYS:
            for attempt in range(2):
                try:
                    resp = await client.get(
                        f"https://api.the-odds-api.com/v4/sports/{sport_key}/scores",
                        params={"apiKey": ODDS_API_KEY, "daysFrom": "1", "dateFormat": "iso"},
                    )
                    if resp.status_code == 200:
                        for m in resp.json():
                            all_matches.append(_normalize_match(m, sport_key))
                    break
                except Exception as e:
                    if attempt == 1:
                        logger.warning(f"Odds API score error {sport_key}: {e}")
    return all_matches

async def _fetch_upcoming_fallback() -> list:
    """Fallback: fetch upcoming fixtures (next 24h)"""
    all_matches = []
    async with httpx.AsyncClient(timeout=12) as client:
        for sport_key in SPORT_KEYS[:3]:  # limit to top 3 leagues for fallback
            try:
                resp = await client.get(
                    f"https://api.the-odds-api.com/v4/sports/{sport_key}/events",
                    params={"apiKey": ODDS_API_KEY, "dateFormat": "iso"},
                )
                if resp.status_code == 200:
                    for m in resp.json()[:5]:
                        slug_date = m["commence_time"][:10]
                        home_slug = re.sub(r"[^a-z0-9]+", "-", m["home_team"].lower()).strip("-")
                        away_slug = re.sub(r"[^a-z0-9]+", "-", m["away_team"].lower()).strip("-")
                        all_matches.append({
                            "id": m["id"],
                            "sport_key": sport_key,
                            "sport_title": m.get("sport_title", ""),
                            "home_team": m["home_team"],
                            "away_team": m["away_team"],
                            "commence_time": m["commence_time"],
                            "completed": False,
                            "home_score": None,
                            "away_score": None,
                            "last_update": None,
                            "slug": f"{home_slug}-vs-{away_slug}-{slug_date}",
                        })
            except Exception as e:
                logger.warning(f"Odds API upcoming error {sport_key}: {e}")
    return all_matches

def _sort_matches(matches: list) -> list:
    now = datetime.now(timezone.utc).isoformat()
    live = [m for m in matches if not m["completed"] and m["commence_time"] <= now]
    completed = sorted([m for m in matches if m["completed"]], key=lambda x: x["commence_time"], reverse=True)
    upcoming = sorted([m for m in matches if not m["completed"] and m["commence_time"] > now], key=lambda x: x["commence_time"])
    return live + completed + upcoming

async def _get_scores_cached() -> tuple[list, bool]:
    """Returns (matches, is_cached). Populates / refreshes cache."""
    now_ts = time.time()
    # Cache still fresh
    if _scores_cache["data"] is not None and (now_ts - _scores_cache["ts"]) < _CACHE_TTL:
        return _scores_cache["data"], True

    try:
        matches = await _fetch_scores_from_api()
        if not matches:
            matches = await _fetch_upcoming_fallback()
        _scores_cache["data"] = _sort_matches(matches)[:10]
        _scores_cache["ts"] = now_ts
        _scores_cache["error_count"] = 0
        _scores_cache["last_error"] = None
        return _scores_cache["data"], False
    except Exception as e:
        _scores_cache["error_count"] = _scores_cache.get("error_count", 0) + 1
        _scores_cache["last_error"] = str(e)
        logger.error(f"Scores fetch failed: {e}")
        # Return stale cache if available
        if _scores_cache["data"]:
            return _scores_cache["data"], True
        return [], False

async def _generate_ai_insight(home_team: str, away_team: str, league: str) -> str:
    """Generate 2-3 line neutral AI match insight in Turkish"""
    if not _ai_insight_enabled or not EMERGENT_LLM_KEY:
        return ""
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"insight-{home_team}-{away_team}",
            system_message=(
                "Sen bir spor analisti asistanısın. Kısa, tarafsız ve bilgilendirici maç analizleri yazıyorsun. "
                "Kesinlikle 'kesin gol atar', 'garantili kazanır' gibi ifadeler kullanma. "
                "Sadece genel olası senaryoları, dikkat edilmesi gereken faktörleri belirt."
            )
        ).with_model("gemini", "gemini-3-flash-preview")

        msg = UserMessage(text=(
            f"'{home_team}' - '{away_team}' ({league}) maçı için 2-3 cümlelik "
            f"Türkçe, kısa ve tarafsız bir analiz yaz. "
            f"Form durumunu, güçlü yönleri ve olası senaryoları belirt. "
            f"'Bu yazı bilgi amaçlıdır' şeklinde başla."
        ))
        response = await chat.send_message(msg)
        return response[:300] if response else ""
    except Exception as e:
        logger.warning(f"AI insight error: {e}")
        return ""

# ── endpoints ────────────────────────────────────────────────────────

@api_router.get("/sports/scores")
async def get_live_scores():
    """Fetch live & recent scores with cache + fallback"""
    if not ODDS_API_KEY:
        raise HTTPException(status_code=503, detail="Odds API key not configured")
    matches, from_cache = await _get_scores_cached()
    return {"matches": matches, "from_cache": from_cache, "count": len(matches)}

@api_router.get("/sports/featured")
async def get_featured_match():
    """Returns featured match + AI mini-insight"""
    global _featured_match_override
    matches, _ = await _get_scores_cached()
    if not matches:
        return None

    # Pick featured: manual override > live Turkish match > first match
    featured = None
    if _featured_match_override:
        featured = next((m for m in matches if m["id"] == _featured_match_override), None)
    if not featured:
        featured = next((m for m in matches if m["sport_key"] == "soccer_turkey_super_league"), None)
    if not featured:
        featured = matches[0]

    insight = ""
    if _ai_insight_enabled:
        insight = await _generate_ai_insight(
            featured["home_team"], featured["away_team"], featured["sport_title"]
        )

    return {**featured, "ai_insight": insight}

@api_router.get("/sports/match/{match_id}")
async def get_match_detail(match_id: str):
    """Returns match details with AI analysis + recommended partner"""
    matches, _ = await _get_scores_cached()
    match = next((m for m in matches if m["id"] == match_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    # AI analysis (longer, for detail page)
    analysis = ""
    if _ai_insight_enabled and EMERGENT_LLM_KEY:
        try:
            chat = LlmChat(
                api_key=EMERGENT_LLM_KEY,
                session_id=f"analysis-{match_id}",
                system_message="Sen bir spor analisti asistanısın. Yapılandırılmış, tarafsız Türkçe maç analizleri yazıyorsun."
            ).with_model("gemini", "gemini-3-flash-preview")
            msg = UserMessage(text=(
                f"'{match['home_team']}' - '{match['away_team']}' ({match['sport_title']}) maçı için "
                f"yapılandırılmış bir Türkçe analiz yaz. "
                f"Şu başlıkları kullan: 1) Genel Bakış 2) Dikkat Edilmesi Gerekenler 3) Olası Senaryolar. "
                f"Her bölüm 2-3 cümle. Tarafsız ol, garanti ifade kullanma. "
                f"Sonunda: 'Bu analiz yalnızca bilgi amaçlıdır.' ekle."
            ))
            analysis = await chat.send_message(msg)
        except Exception as e:
            logger.warning(f"Match detail AI error: {e}")

    # Recommended partner (top rated bonus site)
    partner = None
    try:
        top_site = await db.bonus_sites.find_one(
            {"is_active": True},
            {"_id": 0, "id": 1, "name": 1, "affiliate_url": 1, "bonus_amount": 1},
            sort=[("performance_score", -1)]
        )
        if top_site:
            partner = top_site
    except Exception:
        pass

    return {**match, "ai_analysis": analysis, "recommended_partner": partner}

@api_router.get("/sports/match-by-slug/{slug}")
async def get_match_by_slug(slug: str):
    """Find match by URL slug"""
    matches, _ = await _get_scores_cached()
    match = next((m for m in matches if m.get("slug") == slug), None)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return await get_match_detail(match["id"])

@api_router.get("/go/{partner_id}/{match_id}")
async def tracking_redirect(partner_id: str, match_id: str, request: Request):
    """Tracking redirect for partner CTAs"""
    from fastapi.responses import RedirectResponse
    # Log the click
    try:
        await db.clicks.insert_one({
            "partner_id": partner_id,
            "match_id": match_id,
            "ip": request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown"),
            "user_agent": request.headers.get("User-Agent", ""),
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        # Get partner affiliate URL
        partner = await db.bonus_sites.find_one({"id": partner_id}, {"_id": 0, "affiliate_url": 1})
        url = partner["affiliate_url"] if partner else "/"
    except Exception as e:
        logger.warning(f"Tracking redirect error: {e}")
        url = "/"
    return RedirectResponse(url=url, status_code=302)

@api_router.get("/admin/api-status")
async def get_api_status():
    """Admin: API health and cache info"""
    age = time.time() - _scores_cache.get("ts", 0)
    return {
        "odds_api_configured": bool(ODDS_API_KEY),
        "cache_age_seconds": round(age),
        "cache_ttl_seconds": _CACHE_TTL,
        "is_stale": age > _CACHE_TTL,
        "cached_match_count": len(_scores_cache.get("data") or []),
        "error_count": _scores_cache.get("error_count", 0),
        "last_error": _scores_cache.get("last_error"),
        "ai_insight_enabled": _ai_insight_enabled,
        "featured_match_override": _featured_match_override,
        "last_fetch_time": datetime.fromtimestamp(_scores_cache["ts"], tz=timezone.utc).isoformat() if _scores_cache["ts"] else None,
    }

class FeaturedMatchRequest(BaseModel):
    match_id: Optional[str] = None

class AiToggleRequest(BaseModel):
    enabled: bool

@api_router.post("/admin/featured-match")
async def set_featured_match(req: FeaturedMatchRequest):
    global _featured_match_override
    _featured_match_override = req.match_id
    return {"ok": True, "featured_match_id": _featured_match_override}

@api_router.post("/admin/ai-toggle")
async def toggle_ai_insight(req: AiToggleRequest):
    global _ai_insight_enabled
    _ai_insight_enabled = req.enabled
    return {"ok": True, "ai_insight_enabled": _ai_insight_enabled}

@api_router.post("/admin/refresh-scores")
async def refresh_scores():
    """Force refresh scores cache"""
    _scores_cache["ts"] = 0  # invalidate cache
    matches, _ = await _get_scores_cached()
    return {"ok": True, "count": len(matches)}

# Stats
@api_router.get("/stats/dashboard")
async def get_dashboard_stats(domain_id: Optional[str] = None):
    """Get dashboard statistics"""
    query = {"domain_id": domain_id} if domain_id else {}
    return {
        "total_domains": await db.domains.count_documents({}),
        "total_articles": await db.articles.count_documents(query if domain_id else {}),
        "total_bonus_sites": await db.bonus_sites.count_documents({"is_active": True}),
        "auto_generated_articles": await db.articles.count_documents({**query, "is_auto_generated": True} if domain_id else {"is_auto_generated": True})
    }

# ============== AUTH ==============

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginRequest(BaseModel):
    username: str
    password: str

def create_jwt_token(username: str) -> str:
    payload = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return pyjwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_jwt_token(token: str) -> Optional[str]:
    try:
        payload = pyjwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload.get("sub")
    except pyjwt.ExpiredSignatureError:
        return None
    except pyjwt.InvalidTokenError:
        return None

@api_router.post("/auth/login")
async def admin_login(req: LoginRequest):
    """Admin login - returns JWT token"""
    if req.username != ADMIN_USERNAME:
        raise HTTPException(status_code=401, detail="Geçersiz kullanıcı adı veya şifre")
    if not ADMIN_PASSWORD_HASH or not pwd_context.verify(req.password, ADMIN_PASSWORD_HASH):
        raise HTTPException(status_code=401, detail="Geçersiz kullanıcı adı veya şifre")
    token = create_jwt_token(req.username)
    logger.info(f"Admin login successful: {req.username}")
    return {"token": token, "username": req.username, "expires_in": JWT_EXPIRE_HOURS * 3600}

@api_router.get("/auth/verify")
async def verify_token(request: Request):
    """Verify JWT token from Authorization header"""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token eksik")
    token = auth.removeprefix("Bearer ").strip()
    username = verify_jwt_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Token geçersiz veya süresi dolmuş")
    return {"valid": True, "username": username}

# ============== PERIGON NEWS ==============

_news_cache: Dict[str, Any] = {"data": None, "ts": 0}
_NEWS_TTL = 600  # 10 dakika cache

async def _fetch_perigon_news(size: int = 20, topic: Optional[str] = None) -> list:
    params: Dict[str, Any] = {
        "apiKey": PERIGON_API_KEY,
        "category": "Sports",
        "language": "en",
        "sortBy": "date",
        "showReprints": "false",
        "hasImage": "true",
        "size": size,
    }
    if topic:
        params["topic"] = topic

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get("https://api.goperigon.com/v1/all", params=params)
        resp.raise_for_status()
        articles = resp.json().get("articles", [])

    return [
        {
            "id": a.get("articleId", ""),
            "title": a.get("title", ""),
            "description": a.get("shortSummary") or a.get("description", ""),
            "content": a.get("content", ""),
            "image": a.get("imageUrl", ""),
            "url": a.get("url", ""),
            "source": (a.get("source") or {}).get("domain", ""),
            "published_at": a.get("pubDate", ""),
            "topics": [t["name"] for t in (a.get("topics") or [])],
            "slug": re.sub(r"[^a-z0-9]+", "-", (a.get("title") or "").lower()).strip("-")[:80],
            "category": "sports",
        }
        for a in articles
        if a.get("title") and a.get("imageUrl")
    ]

@api_router.get("/news")
async def get_news(size: int = 20, topic: Optional[str] = None, refresh: bool = False):
    """Get sports news from Perigon API with caching"""
    if not PERIGON_API_KEY:
        raise HTTPException(status_code=503, detail="Perigon API key not configured")

    now_ts = time.time()
    cache_key = f"{topic or 'all'}-{size}"

    # Serve from cache if fresh
    if (
        not refresh
        and _news_cache.get("data")
        and _news_cache.get("cache_key") == cache_key
        and (now_ts - _news_cache.get("ts", 0)) < _NEWS_TTL
    ):
        return {"articles": _news_cache["data"], "from_cache": True, "count": len(_news_cache["data"])}

    try:
        articles = await _fetch_perigon_news(size=size, topic=topic)
        _news_cache["data"] = articles
        _news_cache["ts"] = now_ts
        _news_cache["cache_key"] = cache_key
        return {"articles": articles, "from_cache": False, "count": len(articles)}
    except Exception as e:
        logger.error(f"Perigon API error: {e}")
        if _news_cache.get("data"):
            return {"articles": _news_cache["data"], "from_cache": True, "stale": True, "count": len(_news_cache["data"])}
        raise HTTPException(status_code=503, detail=f"News API unavailable: {str(e)}")

@api_router.get("/categories")
async def get_categories():
    """Get categories from DB, fallback to defaults"""
    cats = await db.categories.find({}, {"_id": 0}).sort("order", 1).to_list(50)
    if not cats:
        # Seed default categories
        defaults = [
            {"id": str(uuid.uuid4()), "name": "Deneme Bonusu", "slug": "deneme-bonusu", "type": "bonus", "image": "https://images.unsplash.com/photo-1566563255308-753861417000?w=600&q=80", "description": "Yatırımsız ücretsiz bonus", "order": 1, "is_active": True},
            {"id": str(uuid.uuid4()), "name": "Hoşgeldin Bonusu", "slug": "hosgeldin-bonusu", "type": "bonus", "image": "https://images.pexels.com/photos/7594382/pexels-photo-7594382.jpeg?w=600&q=80", "description": "Yeni üye bonusları", "order": 2, "is_active": True},
            {"id": str(uuid.uuid4()), "name": "Kayıp Bonusu", "slug": "kayip-bonusu", "type": "bonus", "image": "https://images.pexels.com/photos/7594162/pexels-photo-7594162.jpeg?w=600&q=80", "description": "Kayıplarını geri kazan", "order": 3, "is_active": True},
            {"id": str(uuid.uuid4()), "name": "Spor Bahisleri", "slug": "spor-bahisleri", "type": "spor", "image": "https://images.pexels.com/photos/12201296/pexels-photo-12201296.jpeg?w=600&q=80", "description": "Canlı bahis fırsatları", "order": 4, "is_active": True},
            {"id": str(uuid.uuid4()), "name": "Canlı Casino", "slug": "canli-casino", "type": "bonus", "image": "https://images.pexels.com/photos/7594615/pexels-photo-7594615.jpeg?w=600&q=80", "description": "Gerçek krupiyerler", "order": 5, "is_active": True},
            {"id": str(uuid.uuid4()), "name": "Free Spin", "slug": "free-spin", "type": "bonus", "image": "https://images.unsplash.com/photo-1511512578047-dfb367046420?w=600&q=80", "description": "Ücretsiz döndürme hakkı", "order": 6, "is_active": True},
        ]
        await db.categories.insert_many(defaults)
        cats = defaults
    return [c for c in cats if c.get("is_active", True)]

@api_router.post("/categories")
async def create_category(data: Dict[str, Any]):
    """Create a new category"""
    cat_count = await db.categories.count_documents({})
    cat = {
        "id": str(uuid.uuid4()),
        "name": data.get("name", ""),
        "slug": slugify(data.get("name", "")),
        "type": data.get("type", "bonus"),
        "image": data.get("image", ""),
        "description": data.get("description", ""),
        "order": data.get("order", cat_count + 1),
        "is_active": True,
    }
    await db.categories.insert_one(cat)
    cat.pop("_id", None)
    return cat

@api_router.put("/categories/{cat_id}")
async def update_category(cat_id: str, data: Dict[str, Any]):
    """Update a category"""
    data.pop("id", None)
    data.pop("_id", None)
    await db.categories.update_one({"id": cat_id}, {"$set": data})
    updated = await db.categories.find_one({"id": cat_id}, {"_id": 0})
    return updated

@api_router.delete("/categories/{cat_id}")
async def delete_category(cat_id: str):
    """Delete a category"""
    await db.categories.delete_one({"id": cat_id})
    return {"message": "Kategori silindi"}

@api_router.post("/categories/reorder")
async def reorder_categories(data: Dict[str, Any]):
    """Reorder categories"""
    order_list = data.get("order", [])
    for i, cat_id in enumerate(order_list):
        await db.categories.update_one({"id": cat_id}, {"$set": {"order": i + 1}})
    return {"message": "Sıralama güncellendi"}

# Bonus Sites Reorder
@api_router.post("/bonus-sites/reorder")
async def reorder_bonus_sites(data: Dict[str, Any]):
    """Reorder bonus sites"""
    order_list = data.get("order", [])
    for i, site_id in enumerate(order_list):
        await db.bonus_sites.update_one({"id": site_id}, {"$set": {"sort_order": i + 1}})
    return {"message": "Site sıralaması güncellendi"}

# ============== SEO ENDPOINTS ==============

@api_router.get("/sitemap.xml")
async def sitemap_xml(request: Request, domain: Optional[str] = None):
    """Generate dynamic sitemap.xml for all domains and articles"""
    # Use X-Forwarded headers or domain param for proper URL
    forwarded_proto = request.headers.get("x-forwarded-proto", "https")
    forwarded_host = request.headers.get("x-forwarded-host") or request.headers.get("host", "")
    if domain:
        base_url = f"https://{domain}"
    elif forwarded_host:
        base_url = f"{forwarded_proto}://{forwarded_host}"
    else:
        base_url = str(request.base_url).rstrip("/")
    
    # Collect all domains
    domains = await db.domains.find({}, {"_id": 0, "domain_name": 1}).to_list(100)
    # Collect all published articles
    articles = await db.articles.find(
        {"is_published": True},
        {"_id": 0, "slug": 1, "domain_id": 1, "updated_at": 1, "created_at": 1, "category": 1}
    ).to_list(5000)
    # Collect all categories
    categories = await db.categories.find({}, {"_id": 0, "slug": 1}).to_list(100)

    urls = []
    
    # Static pages
    static_pages = [
        {"loc": "/", "priority": "1.0", "changefreq": "daily"},
        {"loc": "/deneme-bonusu", "priority": "0.9", "changefreq": "daily"},
        {"loc": "/hosgeldin-bonusu", "priority": "0.9", "changefreq": "daily"},
        {"loc": "/spor-haberleri", "priority": "0.8", "changefreq": "hourly"},
    ]
    for page in static_pages:
        urls.append(f"""  <url>
    <loc>{base_url}{page["loc"]}</loc>
    <changefreq>{page["changefreq"]}</changefreq>
    <priority>{page["priority"]}</priority>
  </url>""")
    
    # Category pages
    for cat in categories:
        urls.append(f"""  <url>
    <loc>{base_url}/bonus/{cat["slug"]}</loc>
    <changefreq>daily</changefreq>
    <priority>0.7</priority>
  </url>""")

    # Article pages
    for article in articles:
        lastmod = article.get("updated_at") or article.get("created_at", "")
        if lastmod:
            lastmod_tag = f"\n    <lastmod>{lastmod[:10]}</lastmod>"
        else:
            lastmod_tag = ""
        urls.append(f"""  <url>
    <loc>{base_url}/makale/{article["slug"]}</loc>{lastmod_tag}
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""")

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{chr(10).join(urls)}
</urlset>"""
    
    return Response(content=xml, media_type="application/xml")

@api_router.get("/robots.txt")
async def robots_txt(request: Request):
    """Generate robots.txt"""
    base_url = str(request.base_url).rstrip("/")
    content = f"""User-agent: *
Allow: /
Disallow: /admin
Disallow: /admin-login
Disallow: /api/

User-agent: Googlebot
Allow: /api/sitemap.xml

Sitemap: {base_url}/api/sitemap.xml
"""
    return PlainTextResponse(content=content)

@api_router.get("/seo-data/{slug}")
async def get_seo_data(slug: str):
    """Get SEO metadata for a page - used by frontend for meta tags"""
    # Check if it's an article slug
    article = await db.articles.find_one({"slug": slug, "is_published": True}, {"_id": 0})
    if article:
        return {
            "type": "article",
            "title": article.get("seo_title") or article.get("title", ""),
            "description": article.get("seo_description") or article.get("excerpt", ""),
            "image": article.get("image_url", ""),
            "author": article.get("author", "Admin"),
            "published_time": article.get("created_at", ""),
            "modified_time": article.get("updated_at", ""),
            "category": article.get("category", ""),
            "tags": article.get("tags", []),
            "schema_type": article.get("schema_type", "Article"),
        }
    return {"type": "page", "title": "", "description": ""}

# Seed
@api_router.post("/seed")
async def seed_database():
    """Seed database with initial data - SADECE boş DB'de çalışır"""
    existing_count = await db.bonus_sites.count_documents({})
    if existing_count > 0:
        return {"message": "Database already seeded", "sites": existing_count}
    
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
    
    logger.info("Database seeded successfully")
    return {"message": "Seeded", "sites": len(sites)}

# Include router
app.include_router(api_router)
