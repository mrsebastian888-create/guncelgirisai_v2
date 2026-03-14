"""
Agent 3 — Internal Linking Agent
Responsibilities: suggest relevant internal links, maintain topical clusters,
prevent orphan pages.
"""
from typing import Dict, Any, List
from .base import BaseAgent


class InternalLinkingAgent(BaseAgent):
    AGENT_NAME = "internal_linking"

    async def suggest_links(self, page_url: str, page_content: str = "", limit: int = 10) -> Dict[str, Any]:
        """Suggest relevant internal links for a given page."""
        job = await self._create_job("suggest", {"page_url": page_url, "limit": limit})
        try:
            # Get all available pages from DB
            firms = await self.db.bonus_sites.find(
                {"is_active": True}, {"_id": 0, "name": 1, "slug": 1, "bonus_type": 1}
            ).to_list(100)

            available_pages = []
            for f in firms[:50]:
                slug = f.get("slug", "")
                base = slug.replace("-guncelgiris", "") if slug.endswith("-guncelgiris") else slug
                if base:
                    available_pages.extend([
                        f"/{base}/guncel-giris",
                        f"/{base}/deneme-bonusu",
                        f"/{base}/hosgeldin-bonusu",
                        f"/{base}/odeme-yontemleri",
                    ])

            hub_pages = [
                "/deneme-bonusu-veren-siteler", "/guncel-deneme-bonusu",
                "/yatirimsiz-deneme-bonusu", "/bonus-veren-siteler",
                "/odeme-yontemleri", "/papel-ile-bahis", "/kripto-ile-bahis",
                "/guvenli-odeme-yontemleri",
            ]

            prompt = f"""Kaynak sayfa: {page_url}
Sayfa icerigi ozeti: {page_content[:500] if page_content else 'Icerik mevcut degil'}

Mevcut sayfalar (ornekler): {', '.join(available_pages[:40])}
Hub sayfalar: {', '.join(hub_pages)}

Bu sayfa icin en alakali {limit} dahili link onerisi yap.

JSON formati:
{{
  "suggestions": [
    {{
      "target_url": "/hedef-url",
      "anchor_text": "Link metni",
      "relevance_score": 9,
      "reason": "Neden bu link oneriliyor",
      "link_type": "contextual/navigation/related/hub"
    }}
  ]
}}"""
            result = await self._ai_json(prompt)
            await self._complete_job(job, result)
            return self._ok("suggest", job.job_id, result)
        except Exception as e:
            await self._fail_job(job, str(e))
            return self._err("suggest", job.job_id, str(e))

    async def audit_clusters(self) -> Dict[str, Any]:
        """Audit topical cluster health and coverage."""
        job = await self._create_job("audit_clusters", {})
        try:
            firms = await self.db.bonus_sites.find(
                {"is_active": True}, {"_id": 0, "name": 1, "slug": 1, "bonus_type": 1}
            ).to_list(500)

            page_types = [
                "guncel-giris", "guncel-adresi", "yeni-giris-adresi", "mobil-giris",
                "deneme-bonusu", "hosgeldin-bonusu", "yatirimsiz-deneme-bonusu",
                "bonus-sartlari", "odeme-yontemleri",
            ]

            total_firms = len(firms)
            total_possible_pages = total_firms * len(page_types)

            # Check which pages have generated content
            generated = await self.db.agent_generated_content.find(
                {}, {"_id": 0, "company_slug": 1, "page_type": 1}
            ).to_list(5000)
            generated_set = {f"{g.get('company_slug')}:{g.get('page_type')}" for g in generated}

            coverage = {pt: 0 for pt in page_types}
            missing = []
            for f in firms:
                slug = f.get("slug", "")
                base = slug.replace("-guncelgiris", "") if slug.endswith("-guncelgiris") else slug
                for pt in page_types:
                    key = f"{base}:{pt}"
                    if key in generated_set:
                        coverage[pt] += 1
                    else:
                        missing.append({"company": f["name"], "base_slug": base, "page_type": pt})

            result = {
                "total_firms": total_firms,
                "page_types": len(page_types),
                "total_possible_pages": total_possible_pages,
                "generated_content_count": len(generated),
                "coverage_by_type": {pt: {"count": c, "pct": round(c / max(total_firms, 1) * 100, 1)} for pt, c in coverage.items()},
                "missing_pages_sample": missing[:20],
                "orphan_risk_pages": [],
            }
            await self._complete_job(job, result)
            return self._ok("audit_clusters", job.job_id, result)
        except Exception as e:
            await self._fail_job(job, str(e))
            return self._err("audit_clusters", job.job_id, str(e))

    async def detect_orphans(self) -> Dict[str, Any]:
        """Find pages that have no internal links pointing to them."""
        job = await self._create_job("orphans", {})
        try:
            # Articles without firm association
            articles = await self.db.articles.find(
                {"is_published": True},
                {"_id": 0, "slug": 1, "title": 1, "category": 1}
            ).to_list(500)

            orphan_candidates = []
            for a in articles:
                slug = a.get("slug", "")
                if slug:
                    orphan_candidates.append({
                        "url": f"/makale/{slug}",
                        "title": a.get("title", ""),
                        "type": "article",
                        "reason": "Firm sayfalarindan link yok olabilir",
                    })

            # Firms without articles
            firms = await self.db.bonus_sites.find(
                {"is_active": True}, {"_id": 0, "name": 1, "slug": 1}
            ).to_list(500)

            for f in firms:
                name = f.get("name", "")
                related_articles = await self.db.articles.count_documents({
                    "is_published": True,
                    "$or": [
                        {"title": {"$regex": name, "$options": "i"}},
                        {"content": {"$regex": name, "$options": "i"}},
                    ]
                })
                if related_articles == 0:
                    base = f["slug"].replace("-guncelgiris", "") if f.get("slug", "").endswith("-guncelgiris") else f.get("slug", "")
                    orphan_candidates.append({
                        "url": f"/{base}/guncel-giris",
                        "title": f"{name} Guncel Giris",
                        "type": "company_page",
                        "reason": "Hicbir makaleden referans yok",
                    })

            result = {
                "orphan_candidates": orphan_candidates[:50],
                "total_checked": len(articles) + len(firms),
                "orphan_count": len(orphan_candidates),
            }
            await self._complete_job(job, result)
            return self._ok("orphans", job.job_id, result)
        except Exception as e:
            await self._fail_job(job, str(e))
            return self._err("orphans", job.job_id, str(e))
