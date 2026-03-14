"""
SERP Intelligence Provider Layer
Abstraction for Ahrefs, Semrush, DataForSEO.
"""
from .base_provider import BaseSERPProvider, SERPCapability
from .ahrefs_provider import AhrefsProvider
from .semrush_provider import SemrushProvider
from .dataforseo_provider import DataForSEOProvider
from .manager import SERPManager
from .models import (
    KeywordData, RankingOpportunity, CompetitorGap,
    SERPDifficulty, SERPProviderStatus,
)

__all__ = [
    "BaseSERPProvider", "SERPCapability",
    "AhrefsProvider", "SemrushProvider", "DataForSEOProvider",
    "SERPManager",
    "KeywordData", "RankingOpportunity", "CompetitorGap",
    "SERPDifficulty", "SERPProviderStatus",
]
