"""
Agent 4 — Update Agent
Responsibilities: detect outdated content, refresh evergreen pages,
update timestamps.
"""
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from .base import BaseAgent


class UpdateAgent(BaseAgent):
    AGENT_NAME = "update"

    async def scan_outdated(self, days_threshold: int = 30) -> Dict[str, Any]:
        """Scan for content that hasn't been updated within threshold."""
        job = await self._create_job("scan", {"days_threshold": days_threshold})
        try:
            cutoff = datetime.now(timezone.utc) - timedelta(days=days_threshold)
            cutoff_str = cutoff.isoformat()

            # Check articles
            old_articles = await self.db.articles.find(
                {"is_published": True, "updated_at": {"$lt": cutoff_str}},
                {"_id": 0, "slug": 1, "title": 1, "updated_at": 1, "category": 1}
            ).sort("updated_at", 1).limit(50).to_list(50)

            # Check firms without recent updates
            old_firms = await self.db.bonus_sites.find(
                {"is_active": True, "updated_at": {"$lt": cutoff_str}},
                {"_id": 0, "name": 1, "slug": 1, "updated_at": 1}
            ).sort("updated_at", 1).limit(50).to_list(50)

            # Check generated content age
            old_generated = await self.db.agent_generated_content.find(
                {"generated_at": {"$lt": cutoff_str}},
                {"_id": 0, "company_slug": 1, "page_type": 1, "hub_slug": 1, "generated_at": 1}
            ).to_list(50)

            outdated_items = []
            for a in old_articles:
                outdated_items.append({
                    "type": "article",
                    "url": f"/makale/{a['slug']}",
                    "title": a.get("title", ""),
                    "last_updated": a.get("updated_at", ""),
                    "days_old": (datetime.now(timezone.utc) - datetime.fromisoformat(a["updated_at"].replace("Z", "+00:00") if isinstance(a.get("updated_at"), str) else cutoff_str)).days if a.get("updated_at") else days_threshold,
                    "priority": "high" if a.get("category") == "en-iyi-firmalar" else "medium",
                })

            for f in old_firms:
                base = f["slug"].replace("-guncelgiris", "") if f.get("slug", "").endswith("-guncelgiris") else f.get("slug", "")
                outdated_items.append({
                    "type": "firm",
                    "url": f"/{base}/guncel-giris",
                    "title": f"{f['name']} Sayfasi",
                    "last_updated": f.get("updated_at", ""),
                    "days_old": days_threshold,
                    "priority": "medium",
                })

            result = {
                "threshold_days": days_threshold,
                "outdated_articles": len(old_articles),
                "outdated_firms": len(old_firms),
                "outdated_generated": len(old_generated),
                "total_outdated": len(outdated_items),
                "items": outdated_items[:50],
            }
            await self._complete_job(job, result)
            return self._ok("scan", job.job_id, result)
        except Exception as e:
            await self._fail_job(job, str(e))
            return self._err("scan", job.job_id, str(e))

    async def refresh_page(self, company_slug: str, page_type: str) -> Dict[str, Any]:
        """Refresh content for a specific company page using AI."""
        job = await self._create_job("refresh", {"company_slug": company_slug, "page_type": page_type})
        try:
            site = await self.db.bonus_sites.find_one(
                {"slug": {"$regex": f"^{company_slug}"}}, {"_id": 0}
            )
            if not site:
                await self._fail_job(job, "Firma bulunamadi")
                return self._err("refresh", job.job_id, "Firma bulunamadi")

            existing = await self.db.agent_generated_content.find_one(
                {"company_slug": company_slug, "page_type": page_type},
                {"_id": 0}
            )

            name = site.get("name", company_slug)
            bonus = site.get("bonus_amount", "")

            prompt = f"""Firma: {name} | Bonus: {bonus} | Sayfa: {page_type}
Mevcut icerik: {existing.get('intro', 'Yok') if existing else 'Yok'}

Bu sayfanin icerigini 2026 yili icin guncelle.
- Tarihleri guncelle (2026)
- Bonus bilgilerini guncelle ({bonus})
- Yeni bilgiler ekle

JSON formati:
{{
  "title": "Guncel baslik",
  "meta_description": "Guncel meta",
  "intro": "Guncel giris paragrafi",
  "updated_sections": [
    {{"heading": "Baslik", "content": "Guncel icerik"}}
  ],
  "changes_made": ["Yapilan degisiklik 1", "Degisiklik 2"]
}}"""
            result = await self._ai_json(prompt)
            result["company_slug"] = company_slug
            result["page_type"] = page_type
            result["refreshed_at"] = datetime.now(timezone.utc).isoformat()

            # Update generated content
            await self.db.agent_generated_content.update_one(
                {"company_slug": company_slug, "page_type": page_type},
                {"$set": {
                    "title": result.get("title", ""),
                    "meta_description": result.get("meta_description", ""),
                    "intro": result.get("intro", ""),
                    "refreshed_at": result["refreshed_at"],
                }},
                upsert=True,
            )

            # Update firm timestamp
            await self.db.bonus_sites.update_one(
                {"slug": {"$regex": f"^{company_slug}"}},
                {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
            )

            await self._complete_job(job, result)
            return self._ok("refresh", job.job_id, result)
        except Exception as e:
            await self._fail_job(job, str(e))
            return self._err("refresh", job.job_id, str(e))

    async def bulk_update_timestamps(self, company_slugs: List[str] = None) -> Dict[str, Any]:
        """Update timestamps for multiple pages."""
        job = await self._create_job("timestamps", {"company_slugs": company_slugs})
        try:
            now = datetime.now(timezone.utc).isoformat()
            if company_slugs:
                query = {"slug": {"$in": [f"{s}-guncelgiris" for s in company_slugs]}}
            else:
                query = {"is_active": True}

            result_update = await self.db.bonus_sites.update_many(query, {"$set": {"updated_at": now}})

            result = {
                "updated_count": result_update.modified_count,
                "timestamp": now,
                "scope": "selected" if company_slugs else "all",
            }
            await self._complete_job(job, result)
            return self._ok("timestamps", job.job_id, result)
        except Exception as e:
            await self._fail_job(job, str(e))
            return self._err("timestamps", job.job_id, str(e))
