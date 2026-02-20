"""
Multi-Tenant Authority Platform API
Production-Ready Backend with Hardening
Version: 3.0.0
"""

from fastapi import FastAPI, APIRouter, HTTPException, Query, Request, Depends, status
from fastapi.responses import JSONResponse
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

# CORS configuration
CORS_ORIGINS = get_optional_env("CORS_ORIGINS", "https://guncelgiris.ai,https://www.guncelgiris.ai")
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
    
    # Rate limiting for /api routes
    if request.url.path.startswith("/api"):
        allowed, remaining = rate_limiter.is_allowed(client_ip)
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
        if request.url.path.startswith("/api"):
            _, remaining = rate_limiter.is_allowed(client_ip)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
        
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
    slug: str
    excerpt: str
    content: str
    category: str
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
async def create_domain(domain: DomainCreate):
    """Create a new domain"""
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
    
    logger.info(f"Domain created: {domain.domain_name}")
    return domain_obj

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
    """Get all global bonus sites"""
    sites = await db.bonus_sites.find({"is_active": True}, {"_id": 0}).to_list(limit)
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
async def get_articles(limit: int = 50):
    """Get all articles"""
    articles = await db.articles.find({"is_published": True}, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
    return articles

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
SEO uyumlu, özgün bir makale yaz. 800-1000 kelime. HTML formatında."""
    
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

# Sports
@api_router.get("/sports/matches")
async def get_matches(league: str = "PL"):
    """Get match data"""
    return {
        "matches": [
            {"home_team": "Galatasaray", "away_team": "Fenerbahçe", "home_score": 2, "away_score": 1, "league": "Süper Lig", "status": "FINISHED"},
            {"home_team": "Beşiktaş", "away_team": "Trabzonspor", "home_score": 1, "away_score": 1, "league": "Süper Lig", "status": "FINISHED"},
            {"home_team": "Arsenal", "away_team": "Chelsea", "home_score": 3, "away_score": 1, "league": "Premier League", "status": "FINISHED"},
        ],
        "competition": league
    }

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

# Seed
@api_router.post("/seed")
async def seed_database():
    """Seed database with initial data"""
    await db.bonus_sites.delete_many({})
    await db.domains.delete_many({})
    await db.domain_sites.delete_many({})
    await db.domain_performance.delete_many({})
    await db.articles.delete_many({})
    
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
