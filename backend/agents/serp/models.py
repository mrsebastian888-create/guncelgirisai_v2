"""
Shared data models for SERP Intelligence layer.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class KeywordData(BaseModel):
    """Validated keyword with metrics."""
    keyword: str
    search_volume: Optional[int] = None
    cpc: Optional[float] = None
    competition: Optional[float] = None  # 0.0 - 1.0
    difficulty: Optional[int] = None  # 0 - 100
    trend: Optional[str] = None  # up / down / stable
    intent: Optional[str] = None  # informational / navigational / transactional / commercial
    serp_features: List[str] = Field(default_factory=list)
    source: str = ""  # provider name


class RankingOpportunity(BaseModel):
    """A detected ranking opportunity."""
    keyword: str
    search_volume: Optional[int] = None
    difficulty: Optional[int] = None
    current_position: Optional[int] = None  # None = not ranking
    estimated_traffic: Optional[int] = None
    opportunity_score: float = 0.0  # 0-100
    suggested_url: Optional[str] = None
    suggested_action: str = ""  # create_page / optimize / build_links
    source: str = ""


class CompetitorGap(BaseModel):
    """Keyword gap between domain and competitor."""
    keyword: str
    search_volume: Optional[int] = None
    our_position: Optional[int] = None
    competitor_position: Optional[int] = None
    competitor_domain: str = ""
    gap_type: str = ""  # missing / weak / strong
    priority: str = "medium"  # high / medium / low
    source: str = ""


class SERPDifficulty(BaseModel):
    """SERP difficulty analysis for a keyword."""
    keyword: str
    difficulty_score: int = 50  # 0-100
    difficulty_label: str = "medium"  # easy / medium / hard / very_hard
    top_results_authority: Optional[float] = None  # avg domain authority of top 10
    content_required: Optional[str] = None  # thin / standard / comprehensive
    estimated_time_months: Optional[int] = None
    source: str = ""


class SERPProviderStatus(BaseModel):
    """Status info for a provider."""
    name: str
    configured: bool = False
    available: bool = False
    capabilities: List[str] = Field(default_factory=list)
    credits_remaining: Optional[int] = None
    error: Optional[str] = None
