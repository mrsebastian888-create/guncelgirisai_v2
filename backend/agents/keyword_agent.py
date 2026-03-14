"""
Agent 1 — Keyword Intelligence Agent
Responsibilities: keyword clustering, search intent grouping,
SERP opportunity detection, topic discovery.
"""
import re
from typing import Dict, Any, List, Optional
from .base import BaseAgent


class KeywordIntelligenceAgent(BaseAgent):
    AGENT_NAME = "keyword_intelligence"

    async def cluster_keywords(self, keywords: List[str], niche: str = "bahis") -> Dict[str, Any]:
        """Group keywords into topical clusters."""
        job = await self._create_job("cluster", {"keywords": keywords, "niche": niche})
        try:
            prompt = f"""Asagidaki anahtar kelimeleri tematik kumelere ayir.
Nis: {niche}
Anahtar kelimeler: {', '.join(keywords)}

JSON formati:
{{
  "clusters": [
    {{
      "cluster_name": "Kume adi",
      "cluster_slug": "kume-slug",
      "primary_keyword": "Ana anahtar kelime",
      "keywords": ["kelime1", "kelime2"],
      "search_volume_estimate": "high/medium/low",
      "content_type": "hub_page/company_page/guide/article"
    }}
  ],
  "unclustered": ["eslesmeyen kelimeler"]
}}"""
            result = await self._ai_json(prompt)
            await self._complete_job(job, result)
            return self._ok("cluster", job.job_id, result)
        except Exception as e:
            await self._fail_job(job, str(e))
            return self._err("cluster", job.job_id, str(e))

    async def detect_search_intent(self, keywords: List[str]) -> Dict[str, Any]:
        """Classify search intent for each keyword."""
        job = await self._create_job("intent", {"keywords": keywords})
        try:
            prompt = f"""Her anahtar kelime icin arama niyetini belirle.
Kelimeler: {', '.join(keywords)}

JSON formati:
{{
  "intents": [
    {{
      "keyword": "kelime",
      "intent": "informational/navigational/transactional/commercial",
      "suggested_page_type": "hub_page/company_sub_page/article/guide",
      "suggested_url": "/ornek-url",
      "priority": "high/medium/low"
    }}
  ]
}}"""
            result = await self._ai_json(prompt)
            await self._complete_job(job, result)
            return self._ok("intent", job.job_id, result)
        except Exception as e:
            await self._fail_job(job, str(e))
            return self._err("intent", job.job_id, str(e))

    async def detect_serp_opportunities(self, domain: str = "guncelgiris.ai", niche: str = "bahis") -> Dict[str, Any]:
        """Identify SERP gaps and ranking opportunities."""
        job = await self._create_job("opportunities", {"domain": domain, "niche": niche})
        try:
            # Gather existing pages from DB
            firms = await self.db.bonus_sites.find(
                {"is_active": True}, {"_id": 0, "name": 1, "slug": 1}
            ).to_list(50)
            firm_names = [f["name"] for f in firms]

            prompt = f"""Domain: {domain}
Nis: {niche} / online bahis / bonus siteleri
Mevcut firmalar: {', '.join(firm_names[:30])}

Bu nis icin Google'da siralama firsati olan anahtar kelimeleri ve sayfa onerilerini belirle.

JSON formati:
{{
  "opportunities": [
    {{
      "keyword": "hedef anahtar kelime",
      "estimated_volume": "high/medium/low",
      "difficulty": "easy/medium/hard",
      "current_coverage": "none/partial/full",
      "suggested_action": "create_hub/create_guide/optimize_existing/create_company_page",
      "suggested_url": "/onerilen-url",
      "suggested_title": "Onerilen baslik",
      "priority_score": 8
    }}
  ],
  "quick_wins": ["hizli kazanim onerileri"]
}}"""
            result = await self._ai_json(prompt)
            await self._complete_job(job, result)
            return self._ok("opportunities", job.job_id, result)
        except Exception as e:
            await self._fail_job(job, str(e))
            return self._err("opportunities", job.job_id, str(e))

    async def discover_topics(self, seed_topic: str, depth: int = 2) -> Dict[str, Any]:
        """Discover related topics and subtopics from a seed."""
        job = await self._create_job("discover", {"seed_topic": seed_topic, "depth": depth})
        try:
            prompt = f"""Konu: {seed_topic}
Derinlik: {depth} seviye

Bu konu etrafinda icerik uretmek icin alt konulari ve iliskili konulari kesfet.

JSON formati:
{{
  "seed_topic": "{seed_topic}",
  "subtopics": [
    {{
      "topic": "Alt konu",
      "slug": "alt-konu-slug",
      "relevance": "high/medium/low",
      "content_type": "hub/guide/article/faq",
      "suggested_url": "/url",
      "related_to": ["iliskili diger konular"]
    }}
  ],
  "content_calendar": [
    {{
      "week": 1,
      "topic": "Konu adi",
      "type": "article/guide",
      "target_keyword": "hedef kelime"
    }}
  ]
}}"""
            result = await self._ai_json(prompt)
            await self._complete_job(job, result)
            return self._ok("discover", job.job_id, result)
        except Exception as e:
            await self._fail_job(job, str(e))
            return self._err("discover", job.job_id, str(e))
