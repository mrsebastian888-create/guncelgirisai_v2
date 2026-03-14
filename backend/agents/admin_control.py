"""
GG2026 Phase 8 — Admin Control System
Unified monitoring and control backend for the SEO engine.

Provides:
- Page type toggles
- AI agent toggles
- Publish queue visibility
- Company priority lists
- SERP sync status
- Article generation status
- Sitemap health monitoring
- Indexing status monitoring
"""
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger("admin_control")

# Default toggle states stored in DB collection: admin_settings
DEFAULT_SETTINGS = {
    # Page type toggles
    "page_types": {
        "company_sub_pages": True,
        "bonus_hub_pages": True,
        "payment_hub_pages": True,
        "company_articles": True,
        "programmatic_pages": True,
        "guide_pages": True,
    },
    # AI agent toggles
    "agents": {
        "keyword_intelligence": True,
        "content_generator": True,
        "internal_linking": True,
        "update_agent": True,
        "technical_seo": True,
    },
    # Publishing settings
    "publishing": {
        "auto_publish_enabled": True,
        "min_per_day": 8,
        "max_per_day": 15,
        "daemon_interval_minutes": 30,
    },
    # SERP settings
    "serp": {
        "auto_sync_enabled": False,
        "sync_interval_hours": 24,
        "preferred_provider": "auto",
    },
}


class AdminControlSystem:
    """Unified admin control and monitoring system."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    # ─── Settings Management ─────────────────────

    async def get_settings(self) -> Dict[str, Any]:
        """Get all admin settings, initializing defaults if needed."""
        settings = await self.db.admin_settings.find_one({"_id": "global"})
        if not settings:
            await self.db.admin_settings.insert_one({"_id": "global", **DEFAULT_SETTINGS, "updated_at": datetime.now(timezone.utc).isoformat()})
            return DEFAULT_SETTINGS
        settings.pop("_id", None)
        return settings

    async def update_settings(self, path: str, value: Any) -> Dict[str, Any]:
        """Update a specific setting by dot-path (e.g., 'agents.keyword_intelligence')."""
        await self.db.admin_settings.update_one(
            {"_id": "global"},
            {"$set": {path: value, "updated_at": datetime.now(timezone.utc).isoformat()}},
            upsert=True,
        )
        return await self.get_settings()

    async def is_enabled(self, path: str) -> bool:
        """Check if a specific toggle is enabled."""
        settings = await self.get_settings()
        parts = path.split(".")
        val = settings
        for p in parts:
            if isinstance(val, dict):
                val = val.get(p)
            else:
                return True
        return bool(val) if val is not None else True

    # ─── Page Type Toggles ───────────────────────

    async def get_page_type_status(self) -> Dict[str, Any]:
        """Get status of all page types with counts."""
        settings = await self.get_settings()
        toggles = settings.get("page_types", DEFAULT_SETTINGS["page_types"])

        counts = {
            "company_sub_pages": await self.db.bonus_sites.count_documents({"is_active": True}) * 10,
            "bonus_hub_pages": 5,
            "payment_hub_pages": 8,
            "company_articles": await self.db.company_articles.count_documents({"is_published": True}),
            "programmatic_pages": await self.db.programmatic_pages.count_documents({"is_active": True}),
            "guide_pages": await self.db.programmatic_pages.count_documents({"combination_type": "guide_x_topic", "is_active": True}),
        }

        return {
            "toggles": toggles,
            "counts": counts,
            "total_active_pages": sum(c for k, c in counts.items() if toggles.get(k, True)),
        }

    # ─── AI Agent Toggles ────────────────────────

    async def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all AI agents with job stats."""
        settings = await self.get_settings()
        toggles = settings.get("agents", DEFAULT_SETTINGS["agents"])

        agent_names = ["keyword_intelligence", "content_generator", "internal_linking", "update", "technical_seo"]
        agents = []
        for name in agent_names:
            toggle_key = name if name != "update" else "update_agent"
            total = await self.db.agent_jobs.count_documents({"agent": name})
            completed = await self.db.agent_jobs.count_documents({"agent": name, "status": "completed"})
            failed = await self.db.agent_jobs.count_documents({"agent": name, "status": "failed"})
            last_job = await self.db.agent_jobs.find_one(
                {"agent": name}, {"_id": 0, "created_at": 1, "status": 1, "action": 1}
            , sort=[("created_at", -1)])
            agents.append({
                "name": name,
                "enabled": toggles.get(toggle_key, True),
                "total_jobs": total,
                "completed": completed,
                "failed": failed,
                "success_rate": round(completed / max(total, 1) * 100, 1),
                "last_job": last_job,
            })

        return {"agents": agents, "toggles": toggles}

    # ─── Publish Queue Visibility ────────────────

    async def get_publish_overview(self) -> Dict[str, Any]:
        """Get publish queue overview with detailed breakdown."""
        settings = await self.get_settings()
        pub_settings = settings.get("publishing", DEFAULT_SETTINGS["publishing"])

        total = await self.db.publish_queue.count_documents({})
        by_status = {}
        for status in ["pending", "scheduled", "publishing", "published", "failed"]:
            by_status[status] = await self.db.publish_queue.count_documents({"status": status})

        # Today's activity
        today = datetime.now(timezone.utc).date().isoformat()
        today_published = await self.db.publish_queue.count_documents({"scheduled_date": today, "status": "published"})
        today_scheduled = await self.db.publish_queue.count_documents({"scheduled_date": today, "status": "scheduled"})

        # Recent published items
        recent = await self.db.publish_queue.find(
            {"status": "published"}, {"_id": 0, "slug": 1, "title": 1, "published_at": 1, "content_type": 1}
        ).sort("published_at", -1).limit(10).to_list(10)

        return {
            "settings": pub_settings,
            "total": total,
            "by_status": by_status,
            "today": {"published": today_published, "scheduled": today_scheduled, "limit": pub_settings["max_per_day"]},
            "recent_published": recent,
        }

    # ─── Company Priority Lists ──────────────────

    async def get_company_priorities(self, limit: int = 30) -> Dict[str, Any]:
        """Get company priority list with content coverage."""
        firms = await self.db.bonus_sites.find(
            {"is_active": True},
            {"_id": 0, "name": 1, "slug": 1, "bonus_amount": 1, "rating": 1, "sort_order": 1}
        ).sort("sort_order", 1).limit(limit).to_list(limit)

        priorities = []
        for firm in firms:
            slug = firm.get("slug", "")
            base = slug.replace("-guncelgiris", "") if slug.endswith("-guncelgiris") else slug
            article_count = await self.db.company_articles.count_documents({"company_slug": base})
            prog_count = await self.db.programmatic_pages.count_documents({"dimensions.company": base, "is_active": True})
            queue_count = await self.db.publish_queue.count_documents({"slug": {"$regex": f"^{base}/"}})

            priorities.append({
                "name": firm["name"],
                "base_slug": base,
                "sort_order": firm.get("sort_order", 999),
                "rating": firm.get("rating", 0),
                "bonus_amount": firm.get("bonus_amount", ""),
                "articles": article_count,
                "programmatic_pages": prog_count,
                "queue_items": queue_count,
                "coverage_score": min(100, (article_count * 10) + (prog_count * 5) + 10),
            })

        return {
            "companies": priorities,
            "total_firms": await self.db.bonus_sites.count_documents({"is_active": True}),
        }

    async def update_company_priority(self, base_slug: str, sort_order: int) -> Dict[str, Any]:
        """Update a company's priority (sort_order)."""
        result = await self.db.bonus_sites.update_one(
            {"slug": {"$regex": f"^{base_slug}"}},
            {"$set": {"sort_order": sort_order}}
        )
        return {"updated": result.modified_count > 0, "base_slug": base_slug, "sort_order": sort_order}

    # ─── SERP Sync Status ────────────────────────

    async def get_serp_status(self) -> Dict[str, Any]:
        """Get SERP provider sync status."""
        import os
        settings = await self.get_settings()
        serp_settings = settings.get("serp", DEFAULT_SETTINGS["serp"])

        providers = [
            {"name": "ahrefs", "configured": bool(os.environ.get("AHREFS_API_KEY", ""))},
            {"name": "semrush", "configured": bool(os.environ.get("SEMRUSH_API_KEY", ""))},
            {"name": "dataforseo", "configured": bool(os.environ.get("DATAFORSEO_LOGIN", "")) and bool(os.environ.get("DATAFORSEO_PASSWORD", ""))},
        ]

        # SERP-related agent jobs
        serp_jobs = await self.db.agent_jobs.find(
            {"agent": "keyword_intelligence"},
            {"_id": 0, "action": 1, "status": 1, "created_at": 1}
        ).sort("created_at", -1).limit(5).to_list(5)

        return {
            "settings": serp_settings,
            "providers": providers,
            "any_configured": any(p["configured"] for p in providers),
            "fallback_mode": not any(p["configured"] for p in providers),
            "recent_jobs": serp_jobs,
        }

    # ─── Article Generation Status ───────────────

    async def get_article_status(self) -> Dict[str, Any]:
        """Get article generation and coverage status."""
        total_articles = await self.db.company_articles.count_documents({})
        published_articles = await self.db.company_articles.count_documents({"is_published": True})
        general_articles = await self.db.articles.count_documents({"is_published": True})

        # AI-generated content stats
        generated_content = await self.db.agent_generated_content.count_documents({})

        # Content generator jobs
        gen_jobs = await self.db.agent_jobs.count_documents({"agent": "content_generator"})
        gen_completed = await self.db.agent_jobs.count_documents({"agent": "content_generator", "status": "completed"})

        # Companies with articles
        firms_with_articles = len(await self.db.company_articles.distinct("company_slug"))
        total_firms = await self.db.bonus_sites.count_documents({"is_active": True})

        return {
            "company_articles": {"total": total_articles, "published": published_articles},
            "general_articles": {"total": general_articles},
            "ai_generated_content": generated_content,
            "generation_jobs": {"total": gen_jobs, "completed": gen_completed},
            "coverage": {
                "firms_with_articles": firms_with_articles,
                "total_firms": total_firms,
                "coverage_pct": round(firms_with_articles / max(total_firms, 1) * 100, 1),
            },
        }

    # ─── Sitemap Health ──────────────────────────

    async def get_sitemap_health(self) -> Dict[str, Any]:
        """Monitor sitemap health and completeness."""
        firms_count = await self.db.bonus_sites.count_documents({"is_active": True})
        articles_count = await self.db.articles.count_documents({"is_published": True})
        company_articles_count = await self.db.company_articles.count_documents({"is_published": True})
        prog_indexable = await self.db.programmatic_pages.count_documents({"is_active": True, "is_indexable": True})

        page_types_count = 10
        hub_pages = 13
        static_pages = 4

        sitemaps = [
            {"name": "sitemap-pages.xml", "type": "Static + categories", "est_urls": static_pages, "status": "active"},
            {"name": "sitemap-firms.xml", "type": "Firm pages", "est_urls": firms_count, "status": "active"},
            {"name": "sitemap-seo-pages.xml", "type": "Hub + sub-pages", "est_urls": hub_pages + firms_count * page_types_count, "status": "active"},
            {"name": "sitemap-articles.xml", "type": "General articles", "est_urls": articles_count, "status": "active"},
            {"name": "sitemap-company-articles.xml", "type": "Company articles + listings", "est_urls": company_articles_count + firms_count, "status": "active"},
            {"name": "sitemap-programmatic.xml", "type": "Programmatic pages", "est_urls": prog_indexable, "status": "active"},
            {"name": "sitemap-videos.xml", "type": "Video pages", "est_urls": firms_count, "status": "active"},
            {"name": "sitemap-companies.xml", "type": "Company profiles", "est_urls": 0, "status": "active"},
            {"name": "sitemap-amp.xml", "type": "AMP pages", "est_urls": firms_count, "status": "active"},
            {"name": "sitemap-amp-videos.xml", "type": "AMP video pages", "est_urls": firms_count, "status": "active"},
        ]

        total_urls = sum(s["est_urls"] for s in sitemaps)

        return {
            "sitemaps": sitemaps,
            "total_sitemaps": len(sitemaps),
            "total_urls": total_urls,
            "health": "healthy" if total_urls > 0 else "empty",
            "warnings": [
                w for w in [
                    "Sitemap 50K URL sinirini asmak uzere" if total_urls > 45000 else None,
                    "Company articles coverage dusuk" if company_articles_count < 10 else None,
                    "Programmatic pages az" if prog_indexable < 5 else None,
                ] if w
            ],
        }

    # ─── Indexing Status ─────────────────────────

    async def get_indexing_status(self) -> Dict[str, Any]:
        """Monitor indexing eligibility across all page types."""
        prog_total = await self.db.programmatic_pages.count_documents({"is_active": True})
        prog_indexable = await self.db.programmatic_pages.count_documents({"is_active": True, "is_indexable": True})
        prog_not_indexable = prog_total - prog_indexable

        # Non-indexable reasons
        non_indexable = await self.db.programmatic_pages.find(
            {"is_active": True, "is_indexable": False},
            {"_id": 0, "slug": 1, "eligibility_reason": 1, "combination_type": 1}
        ).limit(20).to_list(20)

        # Published vs unpublished articles
        articles_pub = await self.db.company_articles.count_documents({"is_published": True})
        articles_unpub = await self.db.company_articles.count_documents({"is_published": False})

        return {
            "programmatic_pages": {
                "total": prog_total,
                "indexable": prog_indexable,
                "not_indexable": prog_not_indexable,
                "indexable_pct": round(prog_indexable / max(prog_total, 1) * 100, 1),
            },
            "company_articles": {"published": articles_pub, "unpublished": articles_unpub},
            "non_indexable_reasons": non_indexable,
            "recommendations": [
                r for r in [
                    "Indexable olmayan sayfalarin icerigini zenginlestirin" if prog_not_indexable > 5 else None,
                    "Yayinlanmamis makaleler var — publish queue'ya ekleyin" if articles_unpub > 0 else None,
                ] if r
            ],
        }

    # ─── Full Dashboard ──────────────────────────

    async def get_dashboard(self) -> Dict[str, Any]:
        """Get full admin dashboard data in a single call."""
        return {
            "settings": await self.get_settings(),
            "page_types": await self.get_page_type_status(),
            "agents": await self.get_agent_status(),
            "publishing": await self.get_publish_overview(),
            "serp": await self.get_serp_status(),
            "articles": await self.get_article_status(),
            "sitemap": await self.get_sitemap_health(),
            "indexing": await self.get_indexing_status(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
