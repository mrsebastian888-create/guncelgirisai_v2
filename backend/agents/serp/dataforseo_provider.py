"""
DataForSEO SERP Provider — REST API integration.
Docs: https://docs.dataforseo.com/
"""
import logging
import base64
from typing import List
import httpx
from .base_provider import BaseSERPProvider, SERPCapability
from .models import KeywordData, RankingOpportunity, CompetitorGap, SERPDifficulty, SERPProviderStatus

logger = logging.getLogger("agents.serp.dataforseo")
API_BASE = "https://api.dataforseo.com/v3"


class DataForSEOProvider(BaseSERPProvider):
    PROVIDER_NAME = "dataforseo"
    CAPABILITIES = [
        SERPCapability.KEYWORD_VALIDATION,
        SERPCapability.RANKING_OPPORTUNITIES,
        SERPCapability.COMPETITOR_GAP,
        SERPCapability.LONGTAIL_DISCOVERY,
        SERPCapability.SERP_DIFFICULTY,
    ]

    def __init__(self, login: str = "", password: str = ""):
        super().__init__(login=login, password=password)
        self.login = login
        self.password = password

    def _headers(self):
        creds = base64.b64encode(f"{self.login}:{self.password}".encode()).decode()
        return {"Authorization": f"Basic {creds}", "Content-Type": "application/json"}

    async def _post(self, path: str, body: list) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(f"{API_BASE}{path}", headers=self._headers(), json=body)
            resp.raise_for_status()
            return resp.json()

    async def validate_keywords(self, keywords: List[str], country: str = "tr") -> List[KeywordData]:
        try:
            body = [{"keywords": keywords[:50], "location_code": 2792 if country == "tr" else 2840, "language_code": "tr" if country == "tr" else "en"}]
            data = await self._post("/keywords_data/google_ads/search_volume/live", body)
            results = []
            for task in data.get("tasks", []):
                for item in (task.get("result") or []):
                    for kw_data in (item.get("items") or []):
                        sv = kw_data.get("search_volume") or 0
                        comp = kw_data.get("competition") or 0
                        results.append(KeywordData(
                            keyword=kw_data.get("keyword", ""),
                            search_volume=sv,
                            cpc=kw_data.get("cpc"),
                            competition=comp,
                            trend="stable",
                            source=self.PROVIDER_NAME,
                        ))
            # Fill in any missing keywords
            found = {r.keyword for r in results}
            for kw in keywords:
                if kw not in found:
                    results.append(KeywordData(keyword=kw, source=self.PROVIDER_NAME))
            return results
        except Exception as e:
            logger.warning(f"DataForSEO validate_keywords error: {e}")
            return [KeywordData(keyword=kw, source=self.PROVIDER_NAME) for kw in keywords]

    async def get_ranking_opportunities(self, domain: str, keywords: List[str] = None, country: str = "tr", limit: int = 20) -> List[RankingOpportunity]:
        try:
            loc = 2792 if country == "tr" else 2840
            body = [{"target": domain, "location_code": loc, "language_code": "tr" if country == "tr" else "en", "limit": limit, "filters": ["ranked_serp_element.serp_item.rank_absolute", ">", 10]}]
            data = await self._post("/dataforseo_labs/google/ranked_keywords/live", body)
            results = []
            for task in data.get("tasks", []):
                for item in (task.get("result") or []):
                    for kw_item in (item.get("items") or [])[:limit]:
                        kw_info = kw_item.get("keyword_data", {})
                        serp_info = kw_item.get("ranked_serp_element", {}).get("serp_item", {})
                        sv = kw_info.get("keyword_info", {}).get("search_volume", 0) or 0
                        kd = kw_info.get("keyword_properties", {}).get("keyword_difficulty", 50) or 50
                        pos = serp_info.get("rank_absolute")
                        results.append(RankingOpportunity(
                            keyword=kw_info.get("keyword", ""),
                            search_volume=sv,
                            difficulty=kd,
                            current_position=pos,
                            opportunity_score=max(0, 100 - kd),
                            source=self.PROVIDER_NAME,
                        ))
            return results
        except Exception as e:
            logger.warning(f"DataForSEO ranking_opportunities error: {e}")
            return []

    async def competitor_gap_analysis(self, domain: str, competitors: List[str], country: str = "tr", limit: int = 20) -> List[CompetitorGap]:
        try:
            loc = 2792 if country == "tr" else 2840
            body = [{"target1": domain, "target2": competitors[0] if competitors else "", "location_code": loc, "language_code": "tr" if country == "tr" else "en", "limit": limit}]
            data = await self._post("/dataforseo_labs/google/domain_intersection/live", body)
            results = []
            for task in data.get("tasks", []):
                for item in (task.get("result") or []):
                    for kw_item in (item.get("items") or [])[:limit]:
                        kw_info = kw_item.get("keyword_data", {})
                        pos1 = kw_item.get("first_domain_serp_element", {}).get("serp_item", {}).get("rank_absolute")
                        pos2 = kw_item.get("second_domain_serp_element", {}).get("serp_item", {}).get("rank_absolute")
                        gap_type = "missing" if not pos1 else ("weak" if (pos1 or 100) > (pos2 or 100) else "strong")
                        results.append(CompetitorGap(
                            keyword=kw_info.get("keyword", ""),
                            search_volume=kw_info.get("keyword_info", {}).get("search_volume"),
                            our_position=pos1,
                            competitor_position=pos2,
                            competitor_domain=competitors[0] if competitors else "",
                            gap_type=gap_type,
                            source=self.PROVIDER_NAME,
                        ))
            return results
        except Exception as e:
            logger.warning(f"DataForSEO competitor_gap error: {e}")
            return []

    async def discover_longtail(self, seed_keyword: str, country: str = "tr", limit: int = 30) -> List[KeywordData]:
        try:
            loc = 2792 if country == "tr" else 2840
            body = [{"keyword": seed_keyword, "location_code": loc, "language_code": "tr" if country == "tr" else "en", "limit": limit}]
            data = await self._post("/keywords_data/google_ads/keywords_for_keywords/live", body)
            results = []
            for task in data.get("tasks", []):
                for item in (task.get("result") or []):
                    for kw_data in (item.get("items") or [])[:limit]:
                        results.append(KeywordData(
                            keyword=kw_data.get("keyword", ""),
                            search_volume=kw_data.get("search_volume"),
                            cpc=kw_data.get("cpc"),
                            competition=kw_data.get("competition"),
                            source=self.PROVIDER_NAME,
                        ))
            return results
        except Exception as e:
            logger.warning(f"DataForSEO discover_longtail error: {e}")
            return []

    async def analyze_serp_difficulty(self, keywords: List[str], country: str = "tr") -> List[SERPDifficulty]:
        try:
            loc = 2792 if country == "tr" else 2840
            body = [{"keywords": keywords[:50], "location_code": loc, "language_code": "tr" if country == "tr" else "en"}]
            data = await self._post("/dataforseo_labs/google/bulk_keyword_difficulty/live", body)
            results = []
            for task in data.get("tasks", []):
                for item in (task.get("result") or []):
                    for kw_data in (item.get("items") or []):
                        kd = kw_data.get("keyword_difficulty", 50) or 50
                        label = "easy" if kd < 25 else "medium" if kd < 55 else "hard" if kd < 80 else "very_hard"
                        results.append(SERPDifficulty(
                            keyword=kw_data.get("keyword", ""),
                            difficulty_score=kd,
                            difficulty_label=label,
                            source=self.PROVIDER_NAME,
                        ))
            found = {r.keyword for r in results}
            for kw in keywords:
                if kw not in found:
                    results.append(SERPDifficulty(keyword=kw, source=self.PROVIDER_NAME))
            return results
        except Exception as e:
            logger.warning(f"DataForSEO analyze_serp_difficulty error: {e}")
            return [SERPDifficulty(keyword=kw, source=self.PROVIDER_NAME) for kw in keywords]

    async def health_check(self) -> SERPProviderStatus:
        if not self.login or not self.password:
            return SERPProviderStatus(
                name=self.PROVIDER_NAME, configured=False, available=False,
                capabilities=[c.value for c in self.CAPABILITIES],
                error="DATAFORSEO_LOGIN/DATAFORSEO_PASSWORD not configured",
            )
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{API_BASE}/appendix/user_data", headers=self._headers())
                resp.raise_for_status()
                data = resp.json()
                balance = None
                for task in data.get("tasks", []):
                    for item in (task.get("result") or []):
                        balance = item.get("money", {}).get("balance")
                return SERPProviderStatus(
                    name=self.PROVIDER_NAME, configured=True, available=True,
                    capabilities=[c.value for c in self.CAPABILITIES],
                    credits_remaining=int(balance) if balance else None,
                )
        except Exception as e:
            return SERPProviderStatus(
                name=self.PROVIDER_NAME, configured=True, available=False,
                capabilities=[c.value for c in self.CAPABILITIES],
                error=str(e),
            )
