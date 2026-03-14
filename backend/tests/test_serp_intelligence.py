"""
GG2026 Phase 4: SERP Intelligence Integration Tests
Tests for provider abstraction layer supporting Ahrefs, Semrush, DataForSEO.
Features: keyword validation, ranking opportunities, competitor gap, longtail discovery, SERP difficulty.
AI fallback used when no provider API keys are configured.
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")


class TestSERPStatus:
    """GET /api/agents/serp/status - Provider status (instant, no LLM call)"""

    def test_serp_status_returns_3_providers(self):
        """Status endpoint should return info for all 3 providers."""
        resp = requests.get(f"{BASE_URL}/api/agents/serp/status", timeout=10)
        assert resp.status_code == 200, f"Status code: {resp.status_code}"
        data = resp.json()

        # Verify structure
        assert "providers" in data
        assert "any_configured" in data
        assert "fallback_available" in data

        # Should have exactly 3 providers
        providers = data["providers"]
        assert len(providers) == 3, f"Expected 3 providers, got {len(providers)}"

        # Check provider names
        provider_names = {p["name"] for p in providers}
        assert provider_names == {"ahrefs", "semrush", "dataforseo"}, f"Got: {provider_names}"

        # Each provider should have capabilities and configured/available status
        for p in providers:
            assert "name" in p
            assert "configured" in p
            assert "available" in p
            assert "capabilities" in p
            # All 3 should have 5 capabilities
            assert len(p["capabilities"]) == 5, f"{p['name']} has {len(p['capabilities'])} capabilities"

        # Since no API keys are configured, all should be unconfigured
        assert data["any_configured"] is False, "Expected any_configured=False (no API keys)"
        # LLM fallback should be available
        assert data["fallback_available"] is True, "Expected fallback_available=True (LLM key set)"

    def test_serp_status_provider_capabilities(self):
        """Verify each provider supports the 5 required capabilities."""
        resp = requests.get(f"{BASE_URL}/api/agents/serp/status", timeout=10)
        assert resp.status_code == 200
        data = resp.json()

        expected_caps = {
            "keyword_validation",
            "ranking_opportunities",
            "competitor_gap",
            "longtail_discovery",
            "serp_difficulty",
        }
        for p in data["providers"]:
            caps_set = set(p["capabilities"])
            assert caps_set == expected_caps, f"{p['name']} missing caps: {expected_caps - caps_set}"


class TestSERPValidateKeywords:
    """POST /api/agents/serp/validate - Keyword validation with AI fallback"""

    def test_validate_keywords_ai_fallback(self):
        """Validate keywords returns AI estimates when no provider keys."""
        payload = {"keywords": ["deneme bonusu", "bahis siteleri"], "country": "tr"}
        resp = requests.post(f"{BASE_URL}/api/agents/serp/validate", json=payload, timeout=60)
        assert resp.status_code == 200, f"Status: {resp.status_code}, Body: {resp.text}"
        data = resp.json()

        # Check AI fallback indicators
        assert data.get("source") == "ai_estimate", f"Expected source=ai_estimate, got {data.get('source')}"
        assert data.get("fallback") is True, "Expected fallback=True"

        # Should return keywords list
        assert "keywords" in data
        keywords = data["keywords"]
        assert len(keywords) >= 1, "Should return at least 1 keyword"

        # Verify keyword data structure
        for kw in keywords:
            assert "keyword" in kw
            assert "source" in kw


class TestSERPDifficulty:
    """POST /api/agents/serp/difficulty - SERP difficulty analysis with AI fallback"""

    def test_serp_difficulty_ai_fallback(self):
        """Analyze SERP difficulty returns AI estimates when no provider keys."""
        payload = {"keywords": ["casino bonusu", "slot oyunları"], "country": "tr"}
        resp = requests.post(f"{BASE_URL}/api/agents/serp/difficulty", json=payload, timeout=60)
        assert resp.status_code == 200, f"Status: {resp.status_code}, Body: {resp.text}"
        data = resp.json()

        # Check AI fallback indicators
        assert data.get("source") == "ai_estimate", f"Expected source=ai_estimate, got {data.get('source')}"
        assert data.get("fallback") is True, "Expected fallback=True"

        # Should return difficulties list
        assert "difficulties" in data
        difficulties = data["difficulties"]
        assert len(difficulties) >= 1, "Should return at least 1 difficulty result"

        # Verify difficulty data structure
        for diff in difficulties:
            assert "keyword" in diff
            assert "difficulty_score" in diff or "source" in diff


class TestSERPOpportunities:
    """POST /api/agents/serp/opportunities - Ranking opportunities (SKIP LLM to save credits)"""

    def test_opportunities_endpoint_structure(self):
        """Test opportunities endpoint accepts correct request structure."""
        # Use minimal request to avoid unnecessary LLM credits
        payload = {"domain": "guncelgiris.ai", "country": "tr", "limit": 5}
        resp = requests.post(f"{BASE_URL}/api/agents/serp/opportunities", json=payload, timeout=60)
        assert resp.status_code == 200, f"Status: {resp.status_code}, Body: {resp.text}"
        data = resp.json()

        # Verify structure (AI fallback)
        assert "source" in data
        assert "fallback" in data
        assert "opportunities" in data


class TestSERPCompetitorGap:
    """POST /api/agents/serp/competitor-gap - Competitor gap analysis (SKIP LLM to save credits)"""

    def test_competitor_gap_endpoint_structure(self):
        """Test competitor-gap endpoint accepts correct request structure."""
        payload = {
            "domain": "guncelgiris.ai",
            "competitors": ["bahissiteleri.com"],
            "country": "tr",
            "limit": 5,
        }
        resp = requests.post(f"{BASE_URL}/api/agents/serp/competitor-gap", json=payload, timeout=60)
        assert resp.status_code == 200, f"Status: {resp.status_code}, Body: {resp.text}"
        data = resp.json()

        # Verify structure (AI fallback)
        assert "source" in data
        assert "fallback" in data
        assert "gaps" in data


class TestSERPLongtail:
    """POST /api/agents/serp/longtail - Long-tail discovery (SKIP LLM to save credits)"""

    def test_longtail_endpoint_structure(self):
        """Test longtail endpoint accepts correct request structure."""
        payload = {"seed_keyword": "casino bonusu", "country": "tr", "limit": 10}
        resp = requests.post(f"{BASE_URL}/api/agents/serp/longtail", json=payload, timeout=60)
        assert resp.status_code == 200, f"Status: {resp.status_code}, Body: {resp.text}"
        data = resp.json()

        # Verify structure (AI fallback)
        assert "source" in data
        assert "fallback" in data
        assert "keywords" in data


class TestExistingAgentEndpoints:
    """Verify existing agent endpoints still work after SERP integration."""

    def test_agents_status_still_works(self):
        """GET /api/agents/status should still return 5 agents."""
        resp = requests.get(f"{BASE_URL}/api/agents/status", timeout=10)
        assert resp.status_code == 200, f"Status: {resp.status_code}"
        data = resp.json()
        assert data.get("status") == "operational"
        assert "agents" in data
        assert len(data["agents"]) == 5  # Original 5 agents

    def test_linking_audit_still_works(self):
        """POST /api/agents/linking/audit should still work."""
        resp = requests.post(f"{BASE_URL}/api/agents/linking/audit", timeout=30)
        assert resp.status_code == 200, f"Status: {resp.status_code}"
        data = resp.json()
        assert "job_id" in data or "clusters" in data or "total_firms" in data


class TestExistingRoutes:
    """Verify existing routes are not broken by SERP integration."""

    def test_bonus_sites_still_works(self):
        """GET /api/bonus-sites should still work."""
        resp = requests.get(f"{BASE_URL}/api/bonus-sites", timeout=10)
        assert resp.status_code == 200, f"Status: {resp.status_code}"
        data = resp.json()
        assert isinstance(data, list) or "sites" in data or "firms" in data

    def test_firma_sub_slug_type_still_works(self):
        """GET /api/firma-sub/{slug}/{type} should still work."""
        resp = requests.get(f"{BASE_URL}/api/firma-sub/tulipbet/giris", timeout=10)
        # Should return 200 or 404 (if slug doesn't exist), not 500
        assert resp.status_code in [200, 404], f"Status: {resp.status_code}"


class TestProviderAbstraction:
    """Verify provider abstraction layer design."""

    def test_all_providers_same_capabilities(self):
        """All 3 providers should implement the same 5 capabilities."""
        resp = requests.get(f"{BASE_URL}/api/agents/serp/status", timeout=10)
        assert resp.status_code == 200
        data = resp.json()

        providers = data["providers"]
        capabilities_list = [set(p["capabilities"]) for p in providers]

        # All should have exactly same capabilities
        assert len(set(frozenset(c) for c in capabilities_list)) == 1, "Providers have different capabilities"

        # Should be 5 capabilities
        assert len(capabilities_list[0]) == 5

    def test_providers_show_not_configured(self):
        """Without API keys, providers should show configured=False."""
        resp = requests.get(f"{BASE_URL}/api/agents/serp/status", timeout=10)
        assert resp.status_code == 200
        data = resp.json()

        for p in data["providers"]:
            assert p["configured"] is False, f"{p['name']} should be configured=False"
            assert p["available"] is False, f"{p['name']} should be available=False"
            assert "error" in p or p.get("error") is not None or p.get("configured") is False


class TestEnvVarsPresent:
    """Verify environment variables are present in backend .env"""

    def test_env_vars_in_dotenv(self):
        """SERP provider env vars should exist in backend/.env (even if empty)."""
        # This test reads the .env file directly to verify structure
        env_path = "/app/backend/.env"
        with open(env_path, "r") as f:
            content = f.read()

        # Check all 4 SERP env vars are present
        assert "AHREFS_API_KEY" in content, "AHREFS_API_KEY missing from .env"
        assert "SEMRUSH_API_KEY" in content, "SEMRUSH_API_KEY missing from .env"
        assert "DATAFORSEO_LOGIN" in content, "DATAFORSEO_LOGIN missing from .env"
        assert "DATAFORSEO_PASSWORD" in content, "DATAFORSEO_PASSWORD missing from .env"
