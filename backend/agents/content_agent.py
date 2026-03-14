"""
Agent 2 — Content Generator Agent
Responsibilities: generate company page drafts, hub page drafts,
guide content, article content.
"""
from typing import Dict, Any, List, Optional
from .base import BaseAgent


class ContentGeneratorAgent(BaseAgent):
    AGENT_NAME = "content_generator"

    async def generate_company_page(self, company_slug: str, page_type: str) -> Dict[str, Any]:
        """Generate rich content for a company sub-page."""
        job = await self._create_job("company_page", {"company_slug": company_slug, "page_type": page_type})
        try:
            site = await self.db.bonus_sites.find_one(
                {"slug": {"$regex": f"^{company_slug}"}}, {"_id": 0}
            )
            if not site:
                await self._fail_job(job, "Firma bulunamadi")
                return self._err("company_page", job.job_id, "Firma bulunamadi")

            name = site.get("name", company_slug)
            bonus = site.get("bonus_amount", "")
            rating = site.get("rating", 4.5)
            turnover = site.get("turnover_requirement", 10)

            prompt = f"""Firma: {name}
Bonus: {bonus} | Puan: {rating} | Cevrim: {turnover}x
Sayfa tipi: {page_type}

Bu firma icin "{page_type}" sayfasinin tam icerigini olustur.
Turkce, SEO uyumlu, dogal dilde, 400-600 kelime.

JSON formati:
{{
  "title": "SEO basligi (max 60 karakter)",
  "meta_description": "Meta aciklama (max 160 karakter)",
  "h1": "Ana baslik",
  "intro": "Giris paragrafi (2-3 cumle)",
  "sections": [
    {{
      "heading": "Bolum basligi",
      "content": "Bolum icerigi (2-4 paragraf)",
      "type": "text/list/table/faq"
    }}
  ],
  "faq": [
    {{"question": "Soru?", "answer": "Cevap."}}
  ],
  "internal_links_suggested": ["/onerilen-link-1", "/onerilen-link-2"],
  "cta_text": "Harekete gecirici metin"
}}"""
            result = await self._ai_json(prompt)
            result["company_slug"] = company_slug
            result["page_type"] = page_type

            # Store generated content
            await self.db.agent_generated_content.update_one(
                {"company_slug": company_slug, "page_type": page_type},
                {"$set": {**result, "generated_at": job.created_at}},
                upsert=True,
            )
            await self._complete_job(job, result)
            return self._ok("company_page", job.job_id, result)
        except Exception as e:
            await self._fail_job(job, str(e))
            return self._err("company_page", job.job_id, str(e))

    async def generate_hub_page(self, hub_slug: str, hub_type: str = "bonus") -> Dict[str, Any]:
        """Generate content for a hub page."""
        job = await self._create_job("hub_page", {"hub_slug": hub_slug, "hub_type": hub_type})
        try:
            # Get top firms for context
            firms = await self.db.bonus_sites.find(
                {"is_active": True}, {"_id": 0, "name": 1, "bonus_amount": 1, "rating": 1}
            ).sort("sort_order", 1).limit(10).to_list(10)
            firms_ctx = ", ".join([f"{f['name']} ({f.get('bonus_amount','')})" for f in firms])

            prompt = f"""Hub sayfasi: {hub_slug}
Tur: {hub_type}
One cikan firmalar: {firms_ctx}

Bu hub sayfasi icin tam SEO icerigi olustur.
Turkce, 500-800 kelime, doğal ve bilgilendirici.

JSON formati:
{{
  "title": "SEO basligi",
  "meta_description": "Meta aciklama",
  "h1": "Ana baslik",
  "intro": "Giris paragrafi (3-4 cumle)",
  "sections": [
    {{
      "heading": "Bolum basligi",
      "content": "Bolum icerigi",
      "type": "text/list/comparison"
    }}
  ],
  "faq": [
    {{"question": "Soru?", "answer": "Cevap."}}
  ],
  "comparison_table": {{
    "headers": ["Site", "Bonus", "Puan"],
    "rows": [["Firma1", "500 TL", "4.8"]]
  }},
  "conclusion": "Sonuc paragrafi"
}}"""
            result = await self._ai_json(prompt)
            result["hub_slug"] = hub_slug

            await self.db.agent_generated_content.update_one(
                {"hub_slug": hub_slug, "type": "hub_page"},
                {"$set": {**result, "generated_at": job.created_at}},
                upsert=True,
            )
            await self._complete_job(job, result)
            return self._ok("hub_page", job.job_id, result)
        except Exception as e:
            await self._fail_job(job, str(e))
            return self._err("hub_page", job.job_id, str(e))

    async def generate_guide(self, topic: str, target_keyword: str) -> Dict[str, Any]:
        """Generate a comprehensive guide article."""
        job = await self._create_job("guide", {"topic": topic, "target_keyword": target_keyword})
        try:
            prompt = f"""Konu: {topic}
Hedef anahtar kelime: {target_keyword}

Kapsamli bir rehber icerik olustur. 800-1200 kelime, SEO uyumlu.

JSON formati:
{{
  "title": "Rehber basligi",
  "meta_description": "Meta aciklama",
  "slug": "url-slug",
  "intro": "Giris (3-4 cumle)",
  "sections": [
    {{
      "heading": "H2 basligi",
      "content": "Icerik (3-5 paragraf)",
      "subsections": [
        {{"heading": "H3 basligi", "content": "Alt icerik"}}
      ]
    }}
  ],
  "faq": [{{"question": "?", "answer": "."}}],
  "key_takeaways": ["Onemli nokta 1", "Onemli nokta 2"],
  "internal_links": ["/onerilen-link"]
}}"""
            result = await self._ai_json(prompt)
            await self._complete_job(job, result)
            return self._ok("guide", job.job_id, result)
        except Exception as e:
            await self._fail_job(job, str(e))
            return self._err("guide", job.job_id, str(e))

    async def generate_article(self, topic: str, firms: List[str] = None, word_count: int = 600) -> Dict[str, Any]:
        """Generate an SEO article with firm mentions."""
        job = await self._create_job("article", {"topic": topic, "firms": firms, "word_count": word_count})
        try:
            firms_str = ", ".join(firms) if firms else "genel"
            prompt = f"""Konu: {topic}
Bahsedilecek firmalar: {firms_str}
Hedef kelime sayisi: {word_count}

SEO uyumlu makale olustur. Firmalari dogal sekilde oner.

JSON formati:
{{
  "title": "Makale basligi",
  "meta_description": "Meta aciklama",
  "slug": "makale-slug",
  "category": "en-iyi-firmalar",
  "content_html": "<h2>...</h2><p>...</p>",
  "excerpt": "Kisa ozet (2 cumle)",
  "tags": ["etiket1", "etiket2"],
  "internal_links": ["/link1", "/link2"],
  "word_count": 600
}}"""
            result = await self._ai_json(prompt)
            await self._complete_job(job, result)
            return self._ok("article", job.job_id, result)
        except Exception as e:
            await self._fail_job(job, str(e))
            return self._err("article", job.job_id, str(e))
