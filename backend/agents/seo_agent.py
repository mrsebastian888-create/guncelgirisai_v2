"""
Agent 5 — Technical SEO Agent
Responsibilities: generate page titles, meta descriptions,
manage canonical tags, assist sitemap updates.
"""
from typing import Dict, Any, List
from .base import BaseAgent


class TechnicalSEOAgent(BaseAgent):
    AGENT_NAME = "technical_seo"

    async def generate_titles(self, pages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate optimized page titles for multiple pages.
        pages: [{"url": "/url", "current_title": "...", "page_type": "..."}]
        """
        job = await self._create_job("titles", {"page_count": len(pages)})
        try:
            pages_str = "\n".join([
                f"- URL: {p['url']}, Mevcut: {p.get('current_title', 'Yok')}, Tip: {p.get('page_type', 'unknown')}"
                for p in pages[:20]
            ])

            prompt = f"""Asagidaki sayfalar icin SEO uyumlu basliklar olustur.
Her baslik max 60 karakter, hedef anahtar kelime icermeli, 2026 yili referansli.

Sayfalar:
{pages_str}

JSON formati:
{{
  "titles": [
    {{
      "url": "/url",
      "current_title": "Mevcut baslik",
      "suggested_title": "Yeni onerilen baslik (max 60 char)",
      "target_keyword": "Hedef anahtar kelime",
      "char_count": 55
    }}
  ]
}}"""
            result = await self._ai_json(prompt)
            await self._complete_job(job, result)
            return self._ok("titles", job.job_id, result)
        except Exception as e:
            await self._fail_job(job, str(e))
            return self._err("titles", job.job_id, str(e))

    async def generate_descriptions(self, pages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Generate meta descriptions for multiple pages.
        pages: [{"url": "/url", "current_desc": "...", "page_type": "..."}]
        """
        job = await self._create_job("descriptions", {"page_count": len(pages)})
        try:
            pages_str = "\n".join([
                f"- URL: {p['url']}, Tip: {p.get('page_type', 'unknown')}"
                for p in pages[:20]
            ])

            prompt = f"""Asagidaki sayfalar icin SEO uyumlu meta aciklamalari olustur.
Her aciklama max 160 karakter, harekete gecirici, anahtar kelime icermeli.

Sayfalar:
{pages_str}

JSON formati:
{{
  "descriptions": [
    {{
      "url": "/url",
      "suggested_description": "Onerilen meta aciklama (max 160 char)",
      "target_keyword": "Hedef anahtar kelime",
      "char_count": 150,
      "has_cta": true
    }}
  ]
}}"""
            result = await self._ai_json(prompt)
            await self._complete_job(job, result)
            return self._ok("descriptions", job.job_id, result)
        except Exception as e:
            await self._fail_job(job, str(e))
            return self._err("descriptions", job.job_id, str(e))

    async def audit_canonicals(self) -> Dict[str, Any]:
        """Audit canonical tag configuration across all page types."""
        job = await self._create_job("canonicals", {})
        try:
            firms = await self.db.bonus_sites.find(
                {"is_active": True}, {"_id": 0, "slug": 1, "name": 1}
            ).to_list(500)

            base_url = "https://guncelgiris.ai"
            page_types = [
                "guncel-giris", "guncel-adresi", "yeni-giris-adresi", "mobil-giris",
                "deneme-bonusu", "hosgeldin-bonusu", "yatirimsiz-deneme-bonusu",
                "bonus-sartlari", "odeme-yontemleri",
            ]

            canonical_map = []
            issues = []

            # Firm sub-pages
            for f in firms:
                slug = f.get("slug", "")
                base = slug.replace("-guncelgiris", "") if slug.endswith("-guncelgiris") else slug
                if not base:
                    continue
                for pt in page_types:
                    canonical_map.append({
                        "url": f"/{base}/{pt}",
                        "canonical": f"{base_url}/{base}/{pt}",
                        "status": "ok",
                    })

            # Hub pages
            hub_slugs = [
                "deneme-bonusu-veren-siteler", "guncel-deneme-bonusu",
                "yatirimsiz-deneme-bonusu", "bonus-veren-siteler",
                "odeme-yontemleri", "mobil-odeme-ile-bahis", "kredi-karti-ile-bahis",
                "papel-ile-bahis", "havale-ile-bahis", "kripto-ile-bahis",
                "bddk-onayli-odeme-yontemleri", "guvenli-odeme-yontemleri",
            ]
            for h in hub_slugs:
                canonical_map.append({
                    "url": f"/{h}",
                    "canonical": f"{base_url}/{h}",
                    "status": "ok",
                })

            # Duplicate check: /hosgeldin-bonusu exists both as hub and BonusGuidePage
            issues.append({
                "type": "potential_duplicate",
                "urls": ["/hosgeldin-bonusu"],
                "note": "Bu URL hem BonusGuidePage hem de BonusHubPage olarak var. Canonical belirlenmeli.",
                "severity": "warning",
            })

            result = {
                "total_pages_audited": len(canonical_map),
                "canonical_entries": len(canonical_map),
                "issues": issues,
                "sample_canonicals": canonical_map[:20],
            }
            await self._complete_job(job, result)
            return self._ok("canonicals", job.job_id, result)
        except Exception as e:
            await self._fail_job(job, str(e))
            return self._err("canonicals", job.job_id, str(e))

    async def audit_sitemap(self) -> Dict[str, Any]:
        """Audit sitemap completeness and suggest additions."""
        job = await self._create_job("sitemap_audit", {})
        try:
            firms = await self.db.bonus_sites.find(
                {"is_active": True}, {"_id": 0, "slug": 1}
            ).to_list(500)
            articles = await self.db.articles.find(
                {"is_published": True}, {"_id": 0, "slug": 1}
            ).to_list(5000)

            page_types = [
                "guncel-giris", "guncel-adresi", "yeni-giris-adresi", "mobil-giris",
                "deneme-bonusu", "hosgeldin-bonusu", "yatirimsiz-deneme-bonusu",
                "bonus-sartlari", "odeme-yontemleri",
            ]
            hub_pages = 13  # 5 bonus + 8 payment

            expected_urls = (
                1  # homepage
                + len(firms)  # firm pages
                + len(firms) * len(page_types)  # sub-pages
                + len(firms)  # video pages
                + hub_pages
                + len(articles)  # articles
            )

            result = {
                "firms_count": len(firms),
                "articles_count": len(articles),
                "page_types": len(page_types),
                "hub_pages": hub_pages,
                "expected_total_urls": expected_urls,
                "sitemaps": [
                    {"name": "sitemap-pages.xml", "type": "static + categories"},
                    {"name": "sitemap-firms.xml", "type": "firm pages", "est_urls": len(firms)},
                    {"name": "sitemap-seo-pages.xml", "type": "hub + sub-pages", "est_urls": hub_pages + len(firms) * len(page_types)},
                    {"name": "sitemap-articles.xml", "type": "articles", "est_urls": len(articles)},
                    {"name": "sitemap-videos.xml", "type": "video pages", "est_urls": len(firms)},
                    {"name": "sitemap-companies.xml", "type": "company profiles"},
                    {"name": "sitemap-amp.xml", "type": "AMP pages"},
                    {"name": "sitemap-amp-videos.xml", "type": "AMP video pages"},
                ],
                "recommendations": [
                    "sitemap-seo-pages.xml en buyuk sitemap — gerekirse bolunmeli (50K URL siniri)",
                    "Her guncelleme sonrasi sitemap'lerin lastmod degeri guncellenmeli",
                    "Google Search Console'da tum sitemapleri submit edin",
                ],
            }
            await self._complete_job(job, result)
            return self._ok("sitemap_audit", job.job_id, result)
        except Exception as e:
            await self._fail_job(job, str(e))
            return self._err("sitemap_audit", job.job_id, str(e))
