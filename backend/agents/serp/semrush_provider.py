"""
Semrush SERP Provider — API integration.
Docs: https://developer.semrush.com/api/
"""
import logging
from typing import List
import httpx
from .base_provider import BaseSERPProvider, SERPCapability
from .models import KeywordData, RankingOpportunity, CompetitorGap, SERPDifficulty, SERPProviderStatus

logger = logging.getLogger("agents.serp.semrush")
API_BASE = "https://api.semrush.com"


class SemrushProvider(BaseSERPProvider):
    PROVIDER_NAME = "semrush"
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

    async def _get(self, params: dict) -> str:
        params["key"] = self.api_key
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(API_BASE, params=params)
            resp.raise_for_status()
            return resp.text

    def _parse_csv(self, text: str) -> List[dict]:
        lines = text.strip().split("\n")
        if len(lines) < 2:
            return []
        headers = lines[0].split(";")
        rows = []
        for line in lines[1:]:
            vals = line.split(";")
            rows.append({h: v for h, v in zip(headers, vals)})
        return rows

    async def validate_keywords(self, keywords: List[str], country: str = "tr") -> List[KeywordData]:
        try:
            results = []
            for kw in keywords[:10]:
                raw = await self._get({
                    "type": "phrase_this", "phrase": kw,
                    "database": country, "export_columns": "Ph,Nq,Cp,Co,Kd",
                })
                rows = self._parse_csv(raw)
                if rows:
                    r = rows[0]
                    results.append(KeywordData(
                        keyword=kw,
                        search_volume=int(r.get("Nq", 0) or 0),
                        cpc=float(r.get("Cp", 0) or 0),
                        competition=float(r.get("Co", 0) or 0),
                        difficulty=int(r.get("Kd", 50) or 50),
                        source=self.PROVIDER_NAME,
                    ))
                else:
                    results.append(KeywordData(keyword=kw, source=self.PROVIDER_NAME))
            return results
        except Exception as e:
            logger.warning(f"Semrush validate_keywords error: {e}")
            return [KeywordData(keyword=kw, source=self.PROVIDER_NAME) for kw in keywords]

    async def get_ranking_opportunities(self, domain: str, keywords: List[str] = None, country: str = "tr", limit: int = 20) -> List[RankingOpportunity]:
        try:
            raw = await self._get({
                "type": "domain_organic", "domain": domain,
                "database": country, "display_limit": limit,
                "display_filter": "+|Po|Gt|10|+|Po|Lt|50",
                "display_sort": "nq_desc",
                "export_columns": "Ph,Po,Nq,Kd,Tr",
            })
            results = []
            for r in self._parse_csv(raw)[:limit]:
                kd = int(r.get("Kd", 50) or 50)
                results.append(RankingOpportunity(
                    keyword=r.get("Ph", ""),
                    search_volume=int(r.get("Nq", 0) or 0),
                    difficulty=kd,
                    current_position=int(r.get("Po", 0) or 0),
                    estimated_traffic=int(float(r.get("Tr", 0) or 0)),
                    opportunity_score=max(0, 100 - kd),
                    source=self.PROVIDER_NAME,
                ))
            return results
        except Exception as e:
            logger.warning(f"Semrush ranking_opportunities error: {e}")
            return []

    async def competitor_gap_analysis(self, domain: str, competitors: List[str], country: str = "tr", limit: int = 20) -> List[CompetitorGap]:
        try:
            results = []
            for comp in competitors[:3]:
                raw = await self._get({
                    "type": "domain_domains",
                    "domains": f"{domain}|or|{comp}|or",
                    "database": country, "display_limit": limit,
                    "display_filter": "+|Fi0|Eq|0",  # keywords where domain doesn't rank
                    "export_columns": "Ph,Nq,Po0,Po1",
                })
                for r in self._parse_csv(raw)[:limit]:
                    results.append(CompetitorGap(
                        keyword=r.get("Ph", ""),
                        search_volume=int(r.get("Nq", 0) or 0),
                        our_position=int(r.get("Po0", 0) or 0) or None,
                        competitor_position=int(r.get("Po1", 0) or 0) or None,
                        competitor_domain=comp,
                        gap_type="missing" if not r.get("Po0") else "weak",
                        source=self.PROVIDER_NAME,
                    ))
            return results[:limit]
        except Exception as e:
            logger.warning(f"Semrush competitor_gap error: {e}")
            return []

    async def discover_longtail(self, seed_keyword: str, country: str = "tr", limit: int = 30) -> List[KeywordData]:
        try:
            raw = await self._get({
                "type": "phrase_related", "phrase": seed_keyword,
                "database": country, "display_limit": limit,
                "export_columns": "Ph,Nq,Cp,Co,Kd",
            })
            results = []
            for r in self._parse_csv(raw)[:limit]:
                results.append(KeywordData(
                    keyword=r.get("Ph", ""),
                    search_volume=int(r.get("Nq", 0) or 0),
                    cpc=float(r.get("Cp", 0) or 0),
                    competition=float(r.get("Co", 0) or 0),
                    difficulty=int(r.get("Kd", 50) or 50),
                    source=self.PROVIDER_NAME,
                ))
            return results
        except Exception as e:
            logger.warning(f"Semrush discover_longtail error: {e}")
            return []

    async def analyze_serp_difficulty(self, keywords: List[str], country: str = "tr") -> List[SERPDifficulty]:
        try:
            results = []
            for kw in keywords[:10]:
                raw = await self._get({
                    "type": "phrase_kdi", "phrase": kw,
                    "database": country, "export_columns": "Ph,Kd",
                })
                rows = self._parse_csv(raw)
                kd = int(rows[0].get("Kd", 50) or 50) if rows else 50
                label = "easy" if kd < 30 else "medium" if kd < 60 else "hard" if kd < 85 else "very_hard"
                results.append(SERPDifficulty(
                    keyword=kw, difficulty_score=kd, difficulty_label=label,
                    source=self.PROVIDER_NAME,
                ))
            return results
        except Exception as e:
            logger.warning(f"Semrush analyze_serp_difficulty error: {e}")
            return [SERPDifficulty(keyword=kw, source=self.PROVIDER_NAME) for kw in keywords]

    async def health_check(self) -> SERPProviderStatus:
        if not self.api_key:
            return SERPProviderStatus(
                name=self.PROVIDER_NAME, configured=False, available=False,
                capabilities=[c.value for c in self.CAPABILITIES],
                error="SEMRUSH_API_KEY not configured",
            )
        try:
            await self._get({"type": "domain_rank", "domain": "google.com", "database": "us", "display_limit": 1, "export_columns": "Dn"})
            return SERPProviderStatus(name=self.PROVIDER_NAME, configured=True, available=True, capabilities=[c.value for c in self.CAPABILITIES])
        except Exception as e:
            return SERPProviderStatus(name=self.PROVIDER_NAME, configured=True, available=False, capabilities=[c.value for c in self.CAPABILITIES], error=str(e))
