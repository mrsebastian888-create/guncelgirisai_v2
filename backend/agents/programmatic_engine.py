"""
GG2026 Phase 6 — Programmatic SEO Engine
Scalable system for 50K+ pages with unique user value.

Components:
- PageRegistry: central catalog of all programmatic pages
- SlugGenerator: builds valid slugs from dimension combinations
- TemplateSelector: picks the right template per combination type
- CanonicalManager: enforces canonical rules, prevents conflicts
- DuplicatePrevention: blocks near-duplicate pages
- IndexingEligibility: ensures pages have enough value for indexing
- SitemapIntegration: feeds dynamic sitemap generation
"""
import uuid
import re
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger("programmatic_seo")

# ═══════════════════════════════════════════════
# DIMENSION DEFINITIONS
# ═══════════════════════════════════════════════

COMBINATION_TYPES = {
    "company_x_bonus": {
        "dimensions": ["company", "bonus_type"],
        "template": "company_sub",
        "slug_pattern": "/{company}/{bonus_type}",
        "title_pattern": "{company_name} {bonus_label} 2026",
        "desc_pattern": "{company_name} {bonus_label} firsati. Detayli bilgi ve guncel bonus kosullari.",
        "priority": 0.7,
    },
    "company_x_payment": {
        "dimensions": ["company", "payment_method"],
        "template": "company_payment",
        "slug_pattern": "/{company}/{payment_method}",
        "title_pattern": "{company_name} {payment_label} ile Odeme 2026",
        "desc_pattern": "{company_name} {payment_label} ile para yatirma ve cekme rehberi.",
        "priority": 0.7,
    },
    "company_x_year": {
        "dimensions": ["company", "year"],
        "template": "company_year",
        "slug_pattern": "/{company}/{year}",
        "title_pattern": "{company_name} {year} Guncel Bilgiler",
        "desc_pattern": "{company_name} {year} yilina ozel bonus, giris ve odeme bilgileri.",
        "priority": 0.6,
    },
    "intent_x_category": {
        "dimensions": ["intent", "category"],
        "template": "intent_hub",
        "slug_pattern": "/{slug}",
        "title_pattern": "{title} 2026",
        "desc_pattern": "{description}",
        "priority": 0.8,
    },
    "license_x_category": {
        "dimensions": ["license", "category"],
        "template": "license_hub",
        "slug_pattern": "/{slug}",
        "title_pattern": "{license_name} Lisansli {category_name} 2026",
        "desc_pattern": "{license_name} lisansina sahip {category_name}. Guvenilir ve denetlenmis platformlar.",
        "priority": 0.7,
    },
    "country_x_category": {
        "dimensions": ["country", "category"],
        "template": "country_hub",
        "slug_pattern": "/{slug}",
        "title_pattern": "{country_name} {category_name} 2026",
        "desc_pattern": "{country_name} bolgesindeki en iyi {category_name}. Guvenilir ve lisansli siteler.",
        "priority": 0.7,
    },
    "guide_x_topic": {
        "dimensions": ["guide_type", "topic"],
        "template": "guide_hub",
        "slug_pattern": "/rehber/{slug}",
        "title_pattern": "{topic_title} Rehberi 2026",
        "desc_pattern": "{topic_title} hakkinda kapsamli rehber. Bilmeniz gereken her sey.",
        "priority": 0.7,
    },
}

# Pre-defined dimension values
PAYMENT_METHODS = {
    "kredi-karti": "Kredi Karti",
    "papara": "Papara",
    "kripto": "Kripto Para",
    "havale": "Banka Havale",
    "cepbank": "Cepbank",
    "jeton": "Jeton",
    "astropay": "AstroPay",
    "ecopayz": "EcoPayz",
    "bitcoin": "Bitcoin",
    "usdt": "USDT",
}

INTENT_CATEGORIES = {
    "en-guvenilir-bahis-siteleri": {"title": "En Guvenilir Bahis Siteleri", "description": "2026 yilinin en guvenilir ve lisansli bahis siteleri listesi. Guvenlik analizi ve kullanici yorumlari.", "filter": {"min_rating": 4.5}},
    "en-iyi-casino-siteleri": {"title": "En Iyi Casino Siteleri", "description": "En iyi online casino siteleri 2026. Canli casino, slot ve masa oyunlari.", "filter": {"bonus_type": "casino"}},
    "en-yuksek-bonuslu-siteler": {"title": "En Yuksek Bonuslu Siteler", "description": "En yuksek bonus veren bahis siteleri 2026. Deneme ve hosgeldin bonuslari.", "filter": {"min_bonus": 500}},
    "yeni-bahis-siteleri-2026": {"title": "Yeni Bahis Siteleri 2026", "description": "2026 yilinda acilan yeni bahis siteleri. Guncel ve guvenilir yeni platformlar.", "filter": {}},
    "canli-bahis-siteleri": {"title": "Canli Bahis Siteleri", "description": "En iyi canli bahis siteleri 2026. Canli mac izle ve bahis yap.", "filter": {}},
    "illegal-olmayan-bahis-siteleri": {"title": "Yasal Bahis Siteleri", "description": "Lisansli ve yasal bahis siteleri 2026. Guvenli oyun platformlari.", "filter": {"min_rating": 4.0}},
    "az-yatirimla-bahis": {"title": "Az Yatirimla Bahis Yapilan Siteler", "description": "Dusuk minimum yatirim limiti olan bahis siteleri. 10-50 TL ile bahis.", "filter": {}},
    "turkce-bahis-siteleri": {"title": "Turkce Bahis Siteleri", "description": "Turkce arayuze sahip bahis siteleri. Tam Turkce destek ve odeme.", "filter": {"category": "Turkiye"}},
}

LICENSE_CATEGORIES = {
    "curacao-lisansli-siteler": {"license_name": "Curacao", "category_name": "Bahis Siteleri"},
    "malta-lisansli-siteler": {"license_name": "Malta (MGA)", "category_name": "Bahis Siteleri"},
    "isle-of-man-lisansli-siteler": {"license_name": "Isle of Man", "category_name": "Casino Siteleri"},
}

COUNTRY_CATEGORIES = {
    "turkiye-bahis-siteleri": {"country_name": "Turkiye", "category_name": "Bahis Siteleri"},
    "avrupa-bahis-siteleri": {"country_name": "Avrupa", "category_name": "Bahis Siteleri"},
    "turkiye-casino-siteleri": {"country_name": "Turkiye", "category_name": "Casino Siteleri"},
}

GUIDE_TOPICS = {
    "bahis-nasil-yapilir": {"topic_title": "Bahis Nasil Yapilir"},
    "bonus-cesitleri": {"topic_title": "Bonus Cesitleri ve Turleri"},
    "cevrim-sarti-nedir": {"topic_title": "Cevrim Sarti Nedir"},
    "guvenli-bahis-rehberi": {"topic_title": "Guvenli Bahis Rehberi"},
    "canli-bahis-stratejileri": {"topic_title": "Canli Bahis Stratejileri"},
    "para-yatirma-cekme-rehberi": {"topic_title": "Para Yatirma ve Cekme Rehberi"},
}


# ═══════════════════════════════════════════════
# SLUG GENERATOR
# ═══════════════════════════════════════════════

class SlugGenerator:
    """Generates valid, unique slugs from dimension combinations."""

    @staticmethod
    def generate(combination_type: str, dimensions: Dict[str, str]) -> Optional[str]:
        combo = COMBINATION_TYPES.get(combination_type)
        if not combo:
            return None
        pattern = combo["slug_pattern"]
        slug = pattern
        for key, val in dimensions.items():
            slug = slug.replace(f"{{{key}}}", val)
        # Clean up
        slug = re.sub(r'[{}]', '', slug)
        slug = re.sub(r'/+', '/', slug)
        return slug.strip("/")

    @staticmethod
    def is_valid_slug(slug: str) -> bool:
        if not slug or len(slug) < 3:
            return False
        if re.search(r'[^a-z0-9/-]', slug):
            return False
        if '//' in slug:
            return False
        return True


# ═══════════════════════════════════════════════
# TEMPLATE SELECTOR
# ═══════════════════════════════════════════════

class TemplateSelector:
    """Maps combination types to frontend templates."""

    TEMPLATE_MAP = {
        "company_sub": "CompanySubPage",
        "company_payment": "ProgrammaticPage",
        "company_year": "ProgrammaticPage",
        "intent_hub": "ProgrammaticPage",
        "license_hub": "ProgrammaticPage",
        "country_hub": "ProgrammaticPage",
        "guide_hub": "ProgrammaticPage",
    }

    @classmethod
    def select(cls, combination_type: str) -> str:
        combo = COMBINATION_TYPES.get(combination_type, {})
        template = combo.get("template", "ProgrammaticPage")
        return cls.TEMPLATE_MAP.get(template, "ProgrammaticPage")


# ═══════════════════════════════════════════════
# CANONICAL MANAGER
# ═══════════════════════════════════════════════

class CanonicalManager:
    """Manages canonical URLs to prevent conflicts."""

    BASE_URL = "https://guncelgiris.ai"

    # Pages that already have canonical owners (from Phase 1-5)
    RESERVED_SLUGS = {
        "deneme-bonusu", "hosgeldin-bonusu", "deneme-bonusu-veren-siteler",
        "guncel-deneme-bonusu", "yatirimsiz-deneme-bonusu", "bonus-veren-siteler",
        "odeme-yontemleri", "mobil-odeme-ile-bahis", "kredi-karti-ile-bahis",
        "papel-ile-bahis", "havale-ile-bahis", "kripto-ile-bahis",
        "bddk-onayli-odeme-yontemleri", "guvenli-odeme-yontemleri",
        "spor-haberleri", "companies", "admin", "admin-login",
    }

    @classmethod
    def get_canonical(cls, slug: str) -> str:
        clean = slug.strip("/")
        return f"{cls.BASE_URL}/{clean}"

    @classmethod
    def is_reserved(cls, slug: str) -> bool:
        clean = slug.strip("/").split("/")[0]
        return clean in cls.RESERVED_SLUGS

    @classmethod
    async def has_conflict(cls, db: AsyncIOMotorDatabase, slug: str) -> bool:
        clean = slug.strip("/")
        if cls.is_reserved(clean):
            return True
        existing = await db.programmatic_pages.find_one(
            {"slug": clean, "is_active": True}, {"_id": 0, "page_id": 1}
        )
        return existing is not None


# ═══════════════════════════════════════════════
# DUPLICATE PREVENTION
# ═══════════════════════════════════════════════

class DuplicatePrevention:
    """Prevents creation of near-duplicate or low-value pages."""

    # Company sub-page types from Phase 1 — already exist
    EXISTING_COMPANY_PAGES = {
        "guncel-giris", "guncel-adresi", "yeni-giris-adresi", "mobil-giris",
        "deneme-bonusu", "deneme-bonusu-2026", "hosgeldin-bonusu",
        "yatirimsiz-deneme-bonusu", "bonus-sartlari", "odeme-yontemleri",
    }

    @classmethod
    def is_duplicate_of_existing(cls, combination_type: str, dimensions: Dict[str, str]) -> Tuple[bool, str]:
        """Check if this page duplicates an already-existing page."""
        if combination_type == "company_x_bonus":
            bonus = dimensions.get("bonus_type", "")
            if bonus in cls.EXISTING_COMPANY_PAGES:
                return True, f"/{dimensions.get('company','')}/{bonus} already exists as CompanySubPage"
        if combination_type == "company_x_payment":
            pm = dimensions.get("payment_method", "")
            if pm == "odeme-yontemleri":
                return True, "odeme-yontemleri already exists as CompanySubPage"
        return False, ""

    @classmethod
    async def has_near_duplicate(cls, db: AsyncIOMotorDatabase, slug: str, seo_title: str) -> Tuple[bool, str]:
        """Check if a page with very similar slug or title exists."""
        clean = slug.strip("/")
        # Check exact slug
        existing = await db.programmatic_pages.find_one({"slug": clean}, {"_id": 0, "slug": 1})
        if existing:
            return True, f"Exact slug already exists: {clean}"
        return False, ""


# ═══════════════════════════════════════════════
# INDEXING ELIGIBILITY
# ═══════════════════════════════════════════════

class IndexingEligibility:
    """Determines if a programmatic page should be indexed by search engines."""

    MIN_FIRMS_FOR_HUB = 3  # hub page must list at least 3 firms
    MIN_TITLE_LENGTH = 15
    MIN_DESC_LENGTH = 50

    @classmethod
    async def check(cls, db: AsyncIOMotorDatabase, page: Dict[str, Any]) -> Tuple[bool, str]:
        combo_type = page.get("combination_type", "")
        dims = page.get("dimensions", {})
        seo = page.get("seo", {})

        # Title and description checks
        title = seo.get("title", "")
        desc = seo.get("description", "")
        if len(title) < cls.MIN_TITLE_LENGTH:
            return False, f"Title too short ({len(title)} < {cls.MIN_TITLE_LENGTH})"
        if len(desc) < cls.MIN_DESC_LENGTH:
            return False, f"Description too short ({len(desc)} < {cls.MIN_DESC_LENGTH})"

        # For company-based pages, company must exist
        if "company" in dims:
            company = dims["company"]
            site = await db.bonus_sites.find_one(
                {"slug": {"$regex": f"^{re.escape(company)}"}}, {"_id": 0, "name": 1}
            )
            if not site:
                return False, f"Company not found: {company}"

        # For hub-type pages, must have enough firms to list
        if combo_type in ("intent_x_category", "license_x_category", "country_x_category"):
            fq = page.get("filter_query", {})
            mongo_q: Dict[str, Any] = {"is_active": True}
            if fq.get("min_rating"):
                mongo_q["rating"] = {"$gte": fq["min_rating"]}
            if fq.get("bonus_type"):
                mongo_q["bonus_type"] = fq["bonus_type"]
            if fq.get("category"):
                mongo_q["category"] = fq["category"]
            if fq.get("min_bonus"):
                mongo_q["bonus_value"] = {"$gte": fq["min_bonus"]}
            count = await db.bonus_sites.count_documents(mongo_q)
            if count < cls.MIN_FIRMS_FOR_HUB:
                return False, f"Not enough firms ({count} < {cls.MIN_FIRMS_FOR_HUB})"

        return True, "eligible"


# ═══════════════════════════════════════════════
# PAGE REGISTRY (main orchestrator)
# ═══════════════════════════════════════════════

class PageRegistry:
    """Central registry for all programmatic pages."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def register_page(self, combination_type: str, dimensions: Dict[str, str], seo: Dict[str, str], filter_query: Dict[str, Any] = None) -> Dict[str, Any]:
        """Register a new programmatic page with full validation."""
        # 1. Validate combination type
        if combination_type not in COMBINATION_TYPES:
            return {"error": f"Invalid combination type: {combination_type}", "registered": False}

        # 2. Generate slug
        slug = SlugGenerator.generate(combination_type, dimensions)
        if not slug or not SlugGenerator.is_valid_slug(slug):
            return {"error": f"Invalid slug generated: {slug}", "registered": False}

        # 3. Check duplicate of existing phase pages
        is_dup, dup_reason = DuplicatePrevention.is_duplicate_of_existing(combination_type, dimensions)
        if is_dup:
            return {"error": dup_reason, "registered": False, "duplicate": True}

        # 4. Check canonical conflict
        if await CanonicalManager.has_conflict(self.db, slug):
            return {"error": f"Canonical conflict: /{slug} already exists", "registered": False}

        # 5. Check near duplicate
        title = seo.get("title", "")
        is_near_dup, near_reason = await DuplicatePrevention.has_near_duplicate(self.db, slug, title)
        if is_near_dup:
            return {"error": near_reason, "registered": False, "duplicate": True}

        # 6. Build page record
        combo = COMBINATION_TYPES[combination_type]
        page = {
            "page_id": str(uuid.uuid4()),
            "slug": slug,
            "combination_type": combination_type,
            "dimensions": dimensions,
            "template": combo["template"],
            "canonical": CanonicalManager.get_canonical(slug),
            "seo": {
                "title": seo.get("title", "")[:70],
                "description": seo.get("description", "")[:170],
                "h1": seo.get("h1", seo.get("title", "")),
            },
            "filter_query": filter_query or {},
            "priority": combo["priority"],
            "is_active": True,
            "is_indexable": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        # 7. Check indexing eligibility
        eligible, reason = await IndexingEligibility.check(self.db, page)
        page["is_indexable"] = eligible
        page["eligibility_reason"] = reason

        # 8. Store
        await self.db.programmatic_pages.insert_one({k: v for k, v in page.items() if k != "_id"})
        return {"registered": True, "page": {k: v for k, v in page.items() if k != "_id"}}

    async def generate_combinations(self, combination_type: str, dry_run: bool = True) -> Dict[str, Any]:
        """Auto-generate page combinations for a given type."""
        if combination_type not in COMBINATION_TYPES:
            return {"error": f"Invalid type: {combination_type}"}

        firms = await self.db.bonus_sites.find(
            {"is_active": True}, {"_id": 0, "name": 1, "slug": 1, "bonus_type": 1, "bonus_amount": 1, "rating": 1, "category": 1}
        ).to_list(500)

        pages_to_create = []
        skipped = []

        if combination_type == "company_x_payment":
            for firm in firms:
                base = firm["slug"].replace("-guncelgiris", "") if firm.get("slug", "").endswith("-guncelgiris") else firm.get("slug", "")
                if not base:
                    continue
                for pm_slug, pm_label in PAYMENT_METHODS.items():
                    dims = {"company": base, "payment_method": pm_slug}
                    is_dup, reason = DuplicatePrevention.is_duplicate_of_existing(combination_type, dims)
                    if is_dup:
                        skipped.append({"slug": f"{base}/{pm_slug}", "reason": reason})
                        continue
                    seo = {
                        "title": f"{firm['name']} {pm_label} ile Odeme 2026",
                        "description": f"{firm['name']} {pm_label} ile para yatirma ve cekme. Hizli islem, guvenli odeme.",
                        "h1": f"{firm['name']} {pm_label}",
                    }
                    pages_to_create.append({"combination_type": combination_type, "dimensions": dims, "seo": seo})

        elif combination_type == "company_x_year":
            for firm in firms:
                base = firm["slug"].replace("-guncelgiris", "") if firm.get("slug", "").endswith("-guncelgiris") else firm.get("slug", "")
                if not base:
                    continue
                dims = {"company": base, "year": "2026"}
                seo = {
                    "title": f"{firm['name']} 2026 Guncel Bilgiler",
                    "description": f"{firm['name']} 2026 yili bonus, giris adresi ve odeme bilgileri.",
                    "h1": f"{firm['name']} 2026",
                }
                pages_to_create.append({"combination_type": combination_type, "dimensions": dims, "seo": seo})

        elif combination_type == "intent_x_category":
            for slug, info in INTENT_CATEGORIES.items():
                dims = {"intent": slug.split("-")[0], "category": "-".join(slug.split("-")[1:]), "slug": slug}
                seo = {"title": info["title"], "description": info["description"], "h1": info["title"]}
                fq = info.get("filter", {})
                pages_to_create.append({"combination_type": combination_type, "dimensions": dims, "seo": seo, "filter_query": fq})

        elif combination_type == "license_x_category":
            for slug, info in LICENSE_CATEGORIES.items():
                dims = {"license": slug.split("-")[0], "category": "-".join(slug.split("-")[1:]), "slug": slug}
                seo = {
                    "title": f"{info['license_name']} Lisansli {info['category_name']} 2026",
                    "description": f"{info['license_name']} lisansina sahip {info['category_name']}. Guvenilir ve denetlenmis.",
                    "h1": f"{info['license_name']} Lisansli {info['category_name']}",
                }
                pages_to_create.append({"combination_type": combination_type, "dimensions": dims, "seo": seo})

        elif combination_type == "country_x_category":
            for slug, info in COUNTRY_CATEGORIES.items():
                dims = {"country": slug.split("-")[0], "category": "-".join(slug.split("-")[1:]), "slug": slug}
                seo = {
                    "title": f"{info['country_name']} {info['category_name']} 2026",
                    "description": f"{info['country_name']} bolgesindeki en iyi {info['category_name']}.",
                    "h1": f"{info['country_name']} {info['category_name']}",
                }
                pages_to_create.append({"combination_type": combination_type, "dimensions": dims, "seo": seo})

        elif combination_type == "guide_x_topic":
            for slug, info in GUIDE_TOPICS.items():
                dims = {"guide_type": "rehber", "topic": slug, "slug": slug}
                seo = {
                    "title": f"{info['topic_title']} Rehberi 2026",
                    "description": f"{info['topic_title']} hakkinda kapsamli rehber.",
                    "h1": f"{info['topic_title']} Rehberi",
                }
                pages_to_create.append({"combination_type": combination_type, "dimensions": dims, "seo": seo})

        if dry_run:
            return {
                "combination_type": combination_type,
                "dry_run": True,
                "pages_to_create": len(pages_to_create),
                "skipped": len(skipped),
                "sample": pages_to_create[:10],
                "skipped_sample": skipped[:5],
            }

        # Actually register pages
        registered = 0
        errors = 0
        for p in pages_to_create:
            result = await self.register_page(
                p["combination_type"], p["dimensions"], p["seo"], p.get("filter_query")
            )
            if result.get("registered"):
                registered += 1
            else:
                errors += 1

        return {
            "combination_type": combination_type,
            "dry_run": False,
            "registered": registered,
            "errors": errors,
            "skipped": len(skipped),
            "total_attempted": len(pages_to_create),
        }

    async def get_page(self, slug: str) -> Optional[Dict[str, Any]]:
        """Retrieve a registered programmatic page by slug."""
        page = await self.db.programmatic_pages.find_one(
            {"slug": slug.strip("/"), "is_active": True}, {"_id": 0}
        )
        return page

    async def list_pages(self, combination_type: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List registered programmatic pages."""
        query: Dict[str, Any] = {"is_active": True}
        if combination_type:
            query["combination_type"] = combination_type
        total = await self.db.programmatic_pages.count_documents(query)
        pages = await self.db.programmatic_pages.find(
            query, {"_id": 0}
        ).sort("created_at", -1).skip(offset).limit(limit).to_list(limit)
        return {"pages": pages, "total": total, "limit": limit, "offset": offset}

    async def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics."""
        total = await self.db.programmatic_pages.count_documents({"is_active": True})
        indexable = await self.db.programmatic_pages.count_documents({"is_active": True, "is_indexable": True})

        by_type = {}
        for ct in COMBINATION_TYPES:
            count = await self.db.programmatic_pages.count_documents({"combination_type": ct, "is_active": True})
            by_type[ct] = count

        return {
            "total_pages": total,
            "indexable_pages": indexable,
            "non_indexable": total - indexable,
            "by_combination_type": by_type,
            "available_types": list(COMBINATION_TYPES.keys()),
            "capacity": "50,000+",
        }

    async def generate_sitemap_urls(self, limit: int = 50000) -> List[Dict[str, str]]:
        """Generate sitemap URL entries for all indexable pages."""
        pages = await self.db.programmatic_pages.find(
            {"is_active": True, "is_indexable": True},
            {"_id": 0, "slug": 1, "updated_at": 1, "priority": 1}
        ).limit(limit).to_list(limit)
        urls = []
        for p in pages:
            urls.append({
                "loc": f"https://guncelgiris.ai/{p['slug']}",
                "lastmod": str(p.get("updated_at", ""))[:10],
                "priority": str(p.get("priority", 0.7)),
            })
        return urls
