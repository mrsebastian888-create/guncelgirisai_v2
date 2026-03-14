"""
Ahrefs SERP Provider — /api/v3 integration.
Docs: https://docs.ahrefs.com/docs/api
"""
import logging
from typing import List
import httpx
from .base_provider import BaseSERPProvider, SERPCapability
from .models import KeywordData, RankingOpportunity, CompetitorGap, SERPDifficulty, SERPProviderStatus

logger = logging.getLogger("agents.serp.ahrefs")
API_BASE = "https://api.ahrefs.com/v3"


class AhrefsProvider(BaseSERPProvider):
    PROVIDER_NAME = "ahrefs"
    CAPABILITIES = [
        SERPCapability.KEYWORD_VALIDATION,
        SERPCapability.RANKING_OPPORTUNITIES,
        SERPCapability.COMPETITOR_GAP,
        SERPCapability.LONGTAIL_DISCOVERY,
        SERPCapability.SERP_DIFFICULTY,
    ]

    def __init__(self, api_key: str = ""):
        super().__init__(api_key=api_key)
        self.api_key = api_key

    def _headers(self):
        return {"Authorization": f"Bearer {self.api_key}", "Accept": "application/json"}

    async def _get(self, path: str, params: dict = None) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{API_BASE}{path}", headers=self._headers(), params=params or {})
            resp.raise_for_status()
            return resp.json()

    async def validate_keywords(self, keywords: List[str], country: str = "tr") -> List[KeywordData]:
        try:
            results = []
            # Ahrefs Keywords Explorer: /keywords-explorer/google/search-suggestions
            for kw in keywords[:10]:
                data = await self._get("/keywords-explorer/google/overview", params={
                    "keyword": kw, "country": country,
                })
                metrics = data.get("keywords", [{}])[0] if data.get("keywords") else {}
                results.append(KeywordData(
                    keyword=kw,
                    search_volume=metrics.get("volume"),
                    cpc=metrics.get("cpc"),
                    difficulty=metrics.get("keyword_difficulty"),
                    competition=None,
                    source=self.PROVIDER_NAME,
                ))
            return results
        except Exception as e:
            logger.warning(f"Ahrefs validate_keywords error: {e}")
            return [KeywordData(keyword=kw, source=self.PROVIDER_NAME) for kw in keywords]

    async def get_ranking_opportunities(self, domain: str, keywords: List[str] = None, country: str = "tr", limit: int = 20) -> List[RankingOpportunity]:
        try:
            data = await self._get("/site-explorer/organic-keywords", params={
                "target": domain, "country": country, "limit": limit,
                "where": "position > 10 AND position < 50",
                "order_by": "volume:desc",
            })
            results = []
            for kw in data.get("keywords", [])[:limit]:
                results.append(RankingOpportunity(
                    keyword=kw.get("keyword", ""),
                    search_volume=kw.get("volume"),
                    difficulty=kw.get("keyword_difficulty"),
                    current_position=kw.get("position"),
                    estimated_traffic=kw.get("traffic"),
                    opportunity_score=max(0, 100 - (kw.get("keyword_difficulty", 50) or 50)),
                    source=self.PROVIDER_NAME,
                ))
            return results
        except Exception as e:
            logger.warning(f"Ahrefs ranking_opportunities error: {e}")
            return []

    async def competitor_gap_analysis(self, domain: str, competitors: List[str], country: str = "tr", limit: int = 20) -> List[CompetitorGap]:
        try:
            data = await self._get("/site-explorer/content-gap", params={
                "target": domain,
                "competitors": ",".join(competitors[:3]),
                "country": country, "limit": limit,
            })
            results = []
            for kw in data.get("keywords", [])[:limit]:
                results.append(CompetitorGap(
                    keyword=kw.get("keyword", ""),
                    search_volume=kw.get("volume"),
                    our_position=None,
                    competitor_position=kw.get("position"),
                    competitor_domain=competitors[0] if competitors else "",
                    gap_type="missing",
                    source=self.PROVIDER_NAME,
                ))
            return results
        except Exception as e:
            logger.warning(f"Ahrefs competitor_gap error: {e}")
            return []

    async def discover_longtail(self, seed_keyword: str, country: str = "tr", limit: int = 30) -> List[KeywordData]:
        try:
            data = await self._get("/keywords-explorer/google/related-keywords", params={
                "keyword": seed_keyword, "country": country, "limit": limit,
            })
            results = []
            for kw in data.get("keywords", [])[:limit]:
                results.append(KeywordData(
                    keyword=kw.get("keyword", ""),
                    search_volume=kw.get("volume"),
                    difficulty=kw.get("keyword_difficulty"),
                    source=self.PROVIDER_NAME,
                ))
            return results
        except Exception as e:
            logger.warning(f"Ahrefs discover_longtail error: {e}")
            return []

    async def analyze_serp_difficulty(self, keywords: List[str], country: str = "tr") -> List[SERPDifficulty]:
        try:
            results = []
            for kw in keywords[:10]:
                data = await self._get("/keywords-explorer/google/overview", params={
                    "keyword": kw, "country": country,
                })
                metrics = data.get("keywords", [{}])[0] if data.get("keywords") else {}
                kd = metrics.get("keyword_difficulty", 50) or 50
                label = "easy" if kd < 20 else "medium" if kd < 50 else "hard" if kd < 80 else "very_hard"
                results.append(SERPDifficulty(
                    keyword=kw, difficulty_score=kd, difficulty_label=label,
                    source=self.PROVIDER_NAME,
                ))
            return results
        except Exception as e:
            logger.warning(f"Ahrefs analyze_serp_difficulty error: {e}")
            return [SERPDifficulty(keyword=kw, source=self.PROVIDER_NAME) for kw in keywords]

    async def health_check(self) -> SERPProviderStatus:
        if not self.api_key:
            return SERPProviderStatus(
                name=self.PROVIDER_NAME, configured=False, available=False,
                capabilities=[c.value for c in self.CAPABILITIES],
                error="AHREFS_API_KEY not configured",
            )
        try:
            await self._get("/subscription-info")
            return SERPProviderStatus(
                name=self.PROVIDER_NAME, configured=True, available=True,
                capabilities=[c.value for c in self.CAPABILITIES],
            )
        except Exception as e:
            return SERPProviderStatus(
                name=self.PROVIDER_NAME, configured=True, available=False,
                capabilities=[c.value for c in self.CAPABILITIES],
                error=str(e),
            )
