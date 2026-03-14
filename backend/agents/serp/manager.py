"""
SERP Intelligence Manager
Provider factory + aggregation layer.
Agents request data through this single interface.
Automatically selects available providers or falls back to AI estimation.
"""
import os
import logging
from typing import List, Optional, Dict, Any
from .base_provider import BaseSERPProvider, SERPCapability
from .ahrefs_provider import AhrefsProvider
from .semrush_provider import SemrushProvider
from .dataforseo_provider import DataForSEOProvider
from .models import SERPProviderStatus

logger = logging.getLogger("agents.serp.manager")


class SERPManager:
    """
    Orchestrates SERP data across multiple providers.
    Instantiates providers from environment variables.
    Falls back to AI estimation when no provider is available.
    """

    def __init__(self, llm_key: str = ""):
        self.llm_key = llm_key
        self._providers: List[BaseSERPProvider] = []
        self._init_providers()

    def _init_providers(self):
        """Initialize providers from environment variables."""
        ahrefs_key = os.environ.get("AHREFS_API_KEY", "")
        if ahrefs_key:
            self._providers.append(AhrefsProvider(api_key=ahrefs_key))
            logger.info("SERP provider registered: Ahrefs")

        semrush_key = os.environ.get("SEMRUSH_API_KEY", "")
        if semrush_key:
            self._providers.append(SemrushProvider(api_key=semrush_key))
            logger.info("SERP provider registered: Semrush")

        dfs_login = os.environ.get("DATAFORSEO_LOGIN", "")
        dfs_password = os.environ.get("DATAFORSEO_PASSWORD", "")
        if dfs_login and dfs_password:
            self._providers.append(DataForSEOProvider(login=dfs_login, password=dfs_password))
            logger.info("SERP provider registered: DataForSEO")

        if not self._providers:
            logger.info("No SERP providers configured — AI fallback will be used")

    @property
    def has_providers(self) -> bool:
        return len(self._providers) > 0

    def _get_provider_for(self, capability: SERPCapability) -> Optional[BaseSERPProvider]:
        """Return first provider that supports a capability."""
        for p in self._providers:
            if p.has_capability(capability):
                return p
        return None

    async def get_all_statuses(self) -> List[SERPProviderStatus]:
        """Get health status for all providers (configured + unconfigured)."""
        statuses = []
        # Always show all 3 providers
        all_providers = {
            "ahrefs": AhrefsProvider(api_key=os.environ.get("AHREFS_API_KEY", "")),
            "semrush": SemrushProvider(api_key=os.environ.get("SEMRUSH_API_KEY", "")),
            "dataforseo": DataForSEOProvider(
                login=os.environ.get("DATAFORSEO_LOGIN", ""),
                password=os.environ.get("DATAFORSEO_PASSWORD", ""),
            ),
        }
        for name, provider in all_providers.items():
            statuses.append(await provider.health_check())
        return statuses

    # ─── Public API: used by agents ────────────────────────

    async def validate_keywords(self, keywords: List[str], country: str = "tr") -> Dict[str, Any]:
        """Validate keywords — uses first available provider or AI fallback."""
        provider = self._get_provider_for(SERPCapability.KEYWORD_VALIDATION)
        if provider:
            results = await provider.validate_keywords(keywords, country)
            return {
                "source": provider.PROVIDER_NAME,
                "fallback": False,
                "keywords": [r.model_dump() for r in results],
            }
        return await self._ai_fallback_validate(keywords)

    async def get_ranking_opportunities(
        self, domain: str, keywords: List[str] = None, country: str = "tr", limit: int = 20
    ) -> Dict[str, Any]:
        provider = self._get_provider_for(SERPCapability.RANKING_OPPORTUNITIES)
        if provider:
            results = await provider.get_ranking_opportunities(domain, keywords, country, limit)
            return {
                "source": provider.PROVIDER_NAME,
                "fallback": False,
                "opportunities": [r.model_dump() for r in results],
            }
        return await self._ai_fallback_opportunities(domain, keywords)

    async def competitor_gap_analysis(
        self, domain: str, competitors: List[str], country: str = "tr", limit: int = 20
    ) -> Dict[str, Any]:
        provider = self._get_provider_for(SERPCapability.COMPETITOR_GAP)
        if provider:
            results = await provider.competitor_gap_analysis(domain, competitors, country, limit)
            return {
                "source": provider.PROVIDER_NAME,
                "fallback": False,
                "gaps": [r.model_dump() for r in results],
            }
        return await self._ai_fallback_gap(domain, competitors)

    async def discover_longtail(
        self, seed_keyword: str, country: str = "tr", limit: int = 30
    ) -> Dict[str, Any]:
        provider = self._get_provider_for(SERPCapability.LONGTAIL_DISCOVERY)
        if provider:
            results = await provider.discover_longtail(seed_keyword, country, limit)
            return {
                "source": provider.PROVIDER_NAME,
                "fallback": False,
                "keywords": [r.model_dump() for r in results],
            }
        return await self._ai_fallback_longtail(seed_keyword)

    async def analyze_serp_difficulty(
        self, keywords: List[str], country: str = "tr"
    ) -> Dict[str, Any]:
        provider = self._get_provider_for(SERPCapability.SERP_DIFFICULTY)
        if provider:
            results = await provider.analyze_serp_difficulty(keywords, country)
            return {
                "source": provider.PROVIDER_NAME,
                "fallback": False,
                "difficulties": [r.model_dump() for r in results],
            }
        return await self._ai_fallback_difficulty(keywords)

    # ─── AI Fallbacks ───────────────────────────────────────

    async def _ai_call(self, prompt: str) -> Dict[str, Any]:
        """LLM call for fallback estimations."""
        import uuid
        import json
        import re
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        if not self.llm_key:
            return {}
        chat = LlmChat(
            api_key=self.llm_key, session_id=str(uuid.uuid4()),
            system_message="Sen bir SEO veri analisti AI'sin. Sadece gecerli JSON dondur.",
        ).with_model("openai", "gpt-4o-mini")
        raw = await chat.send_message(UserMessage(text=prompt))
        match = re.search(r"\{[\s\S]*\}", raw)
        if match:
            return json.loads(match.group(0))
        return json.loads(raw)

    async def _ai_fallback_validate(self, keywords: List[str]) -> Dict[str, Any]:
        prompt = f"""Asagidaki anahtar kelimeler icin tahmini SEO metrikleri uret.
Kelimeler: {', '.join(keywords[:15])}
Ulke: Turkiye

JSON:
{{"keywords": [
  {{"keyword": "kelime", "search_volume": 1000, "cpc": 0.5, "competition": 0.3, "difficulty": 45, "intent": "informational", "source": "ai_estimate"}}
]}}"""
        try:
            result = await self._ai_call(prompt)
            return {"source": "ai_estimate", "fallback": True, "keywords": result.get("keywords", [])}
        except Exception:
            return {"source": "ai_estimate", "fallback": True, "keywords": [{"keyword": kw, "source": "ai_estimate"} for kw in keywords]}

    async def _ai_fallback_opportunities(self, domain: str, keywords: List[str] = None) -> Dict[str, Any]:
        kw_str = ", ".join(keywords[:10]) if keywords else "bahis, deneme bonusu, guncel giris"
        prompt = f"""Domain: {domain}
Anahtar kelimeler: {kw_str}

Siralama firsatlarini tahmin et.
JSON:
{{"opportunities": [
  {{"keyword": "kelime", "search_volume": 500, "difficulty": 40, "current_position": null, "opportunity_score": 70, "suggested_action": "create_page", "source": "ai_estimate"}}
]}}"""
        try:
            result = await self._ai_call(prompt)
            return {"source": "ai_estimate", "fallback": True, "opportunities": result.get("opportunities", [])}
        except Exception:
            return {"source": "ai_estimate", "fallback": True, "opportunities": []}

    async def _ai_fallback_gap(self, domain: str, competitors: List[str]) -> Dict[str, Any]:
        prompt = f"""Domain: {domain}
Rakipler: {', '.join(competitors[:3])}

Anahtar kelime bosluk analizi yap.
JSON:
{{"gaps": [
  {{"keyword": "kelime", "search_volume": 500, "our_position": null, "competitor_position": 5, "competitor_domain": "{competitors[0] if competitors else ''}", "gap_type": "missing", "priority": "high", "source": "ai_estimate"}}
]}}"""
        try:
            result = await self._ai_call(prompt)
            return {"source": "ai_estimate", "fallback": True, "gaps": result.get("gaps", [])}
        except Exception:
            return {"source": "ai_estimate", "fallback": True, "gaps": []}

    async def _ai_fallback_longtail(self, seed_keyword: str) -> Dict[str, Any]:
        prompt = f"""Seed: {seed_keyword}

Uzun kuyruk anahtar kelime varyasyonlari olustur (Turkce, bahis nisi).
JSON:
{{"keywords": [
  {{"keyword": "uzun kuyruk kelime", "search_volume": 200, "difficulty": 25, "source": "ai_estimate"}}
]}}"""
        try:
            result = await self._ai_call(prompt)
            return {"source": "ai_estimate", "fallback": True, "keywords": result.get("keywords", [])}
        except Exception:
            return {"source": "ai_estimate", "fallback": True, "keywords": []}

    async def _ai_fallback_difficulty(self, keywords: List[str]) -> Dict[str, Any]:
        prompt = f"""Kelimeler: {', '.join(keywords[:15])}

SERP zorluk analizi yap.
JSON:
{{"difficulties": [
  {{"keyword": "kelime", "difficulty_score": 45, "difficulty_label": "medium", "estimated_time_months": 3, "source": "ai_estimate"}}
]}}"""
        try:
            result = await self._ai_call(prompt)
            return {"source": "ai_estimate", "fallback": True, "difficulties": result.get("difficulties", [])}
        except Exception:
            return {"source": "ai_estimate", "fallback": True, "difficulties": [{"keyword": kw, "difficulty_score": 50, "difficulty_label": "medium", "source": "ai_estimate"} for kw in keywords]}
