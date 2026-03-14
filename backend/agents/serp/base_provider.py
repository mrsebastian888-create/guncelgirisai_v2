"""
Abstract base class for SERP Intelligence providers.
All providers (Ahrefs, Semrush, DataForSEO) implement this interface.
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional, Dict, Any
from .models import KeywordData, RankingOpportunity, CompetitorGap, SERPDifficulty, SERPProviderStatus


class SERPCapability(str, Enum):
    KEYWORD_VALIDATION = "keyword_validation"
    RANKING_OPPORTUNITIES = "ranking_opportunities"
    COMPETITOR_GAP = "competitor_gap"
    LONGTAIL_DISCOVERY = "longtail_discovery"
    SERP_DIFFICULTY = "serp_difficulty"


class BaseSERPProvider(ABC):
    """Interface that all SERP data providers must implement."""

    PROVIDER_NAME: str = "base"
    CAPABILITIES: List[SERPCapability] = []

    def __init__(self, **credentials):
        self.credentials = credentials

    @abstractmethod
    async def validate_keywords(self, keywords: List[str], country: str = "tr") -> List[KeywordData]:
        """Validate keywords and return search volume, CPC, difficulty."""
        ...

    @abstractmethod
    async def get_ranking_opportunities(
        self, domain: str, keywords: List[str] = None, country: str = "tr", limit: int = 20
    ) -> List[RankingOpportunity]:
        """Find ranking opportunities for a domain."""
        ...

    @abstractmethod
    async def competitor_gap_analysis(
        self, domain: str, competitors: List[str], country: str = "tr", limit: int = 20
    ) -> List[CompetitorGap]:
        """Analyze keyword gaps between domain and competitors."""
        ...

    @abstractmethod
    async def discover_longtail(
        self, seed_keyword: str, country: str = "tr", limit: int = 30
    ) -> List[KeywordData]:
        """Discover long-tail keyword variations from a seed."""
        ...

    @abstractmethod
    async def analyze_serp_difficulty(
        self, keywords: List[str], country: str = "tr"
    ) -> List[SERPDifficulty]:
        """Analyze SERP difficulty for keywords."""
        ...

    @abstractmethod
    async def health_check(self) -> SERPProviderStatus:
        """Check if provider is configured and reachable."""
        ...

    def has_capability(self, cap: SERPCapability) -> bool:
        return cap in self.CAPABILITIES
