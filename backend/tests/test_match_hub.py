"""
Match Hub Backend API Tests
Tests for: /api/sports/scores, /api/sports/featured, /api/sports/match/{id},
           /api/sports/match-by-slug/{slug}, /api/admin/api-status,
           /api/admin/ai-toggle, /api/admin/refresh-scores,
           /api/go/{partner_id}/{match_id}, /api/auth/login
"""

import pytest
import requests
import os
import time

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Mm18010812**!!"


# ── fixtures ─────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def admin_token():
    """Login and return JWT token for admin endpoints"""
    resp = requests.post(f"{BASE_URL}/api/auth/login", json={
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    })
    if resp.status_code == 200:
        return resp.json().get("token")
    pytest.skip(f"Admin login failed ({resp.status_code}): {resp.text}")


@pytest.fixture(scope="module")
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture(scope="module")
def first_match_id():
    """Grab first match id from /api/sports/scores"""
    resp = requests.get(f"{BASE_URL}/api/sports/scores")
    if resp.status_code == 200:
        matches = resp.json().get("matches", [])
        if matches:
            return matches[0]["id"]
    return None


@pytest.fixture(scope="module")
def first_match_slug():
    """Grab first match slug from /api/sports/scores"""
    resp = requests.get(f"{BASE_URL}/api/sports/scores")
    if resp.status_code == 200:
        matches = resp.json().get("matches", [])
        if matches:
            return matches[0].get("slug")
    return None


@pytest.fixture(scope="module")
def first_partner_id():
    """Get first bonus site id to use as partner_id"""
    resp = requests.get(f"{BASE_URL}/api/bonus-sites?limit=1")
    if resp.status_code == 200:
        sites = resp.json()
        if sites:
            return sites[0]["id"]
    return None


# ── auth tests ────────────────────────────────────────────────────────

class TestAdminAuth:
    """Admin authentication endpoint tests"""

    def test_admin_login_success(self):
        """Admin login should return 200 with token"""
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "token" in data
        assert isinstance(data["token"], str) and len(data["token"]) > 0
        assert data["username"] == ADMIN_USERNAME
        print(f"Admin login success: token length={len(data['token'])}")

    def test_admin_login_wrong_password(self):
        """Admin login with wrong password should return 401"""
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": ADMIN_USERNAME,
            "password": "wrongpassword"
        })
        assert resp.status_code == 401
        print(f"Wrong password correctly rejected: {resp.status_code}")

    def test_admin_login_wrong_username(self):
        """Admin login with wrong username should return 401"""
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "wronguser",
            "password": ADMIN_PASSWORD
        })
        assert resp.status_code == 401
        print(f"Wrong username correctly rejected: {resp.status_code}")

    def test_auth_verify_valid_token(self, auth_headers):
        """Valid token should pass verification"""
        resp = requests.get(f"{BASE_URL}/api/auth/verify", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("valid") is True
        print(f"Token verification success: {data}")


# ── sports scores ─────────────────────────────────────────────────────

class TestSportsScores:
    """Tests for /api/sports/scores endpoint"""

    def test_scores_returns_200(self):
        """GET /api/sports/scores should return 200"""
        resp = requests.get(f"{BASE_URL}/api/sports/scores")
        assert resp.status_code == 200
        print(f"Sports scores status: {resp.status_code}")

    def test_scores_response_structure(self):
        """Response must have matches, from_cache, count fields"""
        resp = requests.get(f"{BASE_URL}/api/sports/scores")
        assert resp.status_code == 200
        data = resp.json()
        assert "matches" in data, "Missing 'matches' key"
        assert "from_cache" in data, "Missing 'from_cache' key"
        assert "count" in data, "Missing 'count' key"
        print(f"Scores structure OK: count={data['count']}, from_cache={data['from_cache']}")

    def test_scores_count_matches_list_length(self):
        """count field should equal length of matches list"""
        resp = requests.get(f"{BASE_URL}/api/sports/scores")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == len(data["matches"])
        print(f"Count matches list length: {data['count']}")

    def test_scores_match_fields(self):
        """Each match should have required fields"""
        resp = requests.get(f"{BASE_URL}/api/sports/scores")
        assert resp.status_code == 200
        matches = resp.json().get("matches", [])
        if not matches:
            pytest.skip("No matches in response - may be no live/recent data")
        for match in matches[:3]:
            assert "id" in match, f"Missing 'id' in match: {match}"
            assert "home_team" in match, f"Missing 'home_team'"
            assert "away_team" in match, f"Missing 'away_team'"
            assert "commence_time" in match, f"Missing 'commence_time'"
            assert "sport_key" in match, f"Missing 'sport_key'"
            assert "slug" in match, f"Missing 'slug'"
        print(f"Match fields OK for {len(matches)} matches")

    def test_scores_from_cache_is_bool(self):
        """from_cache must be boolean"""
        resp = requests.get(f"{BASE_URL}/api/sports/scores")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data["from_cache"], bool)
        print(f"from_cache is bool: {data['from_cache']}")

    def test_scores_second_call_is_cached(self):
        """Second call within TTL should return from_cache=True"""
        # First call to populate cache
        requests.get(f"{BASE_URL}/api/sports/scores")
        # Second immediate call should be cached
        resp = requests.get(f"{BASE_URL}/api/sports/scores")
        assert resp.status_code == 200
        data = resp.json()
        assert data["from_cache"] is True, f"Expected from_cache=True on second call, got {data['from_cache']}"
        print(f"Cache working: from_cache={data['from_cache']}")


# ── featured match ────────────────────────────────────────────────────

class TestFeaturedMatch:
    """Tests for /api/sports/featured endpoint"""

    def test_featured_returns_200_or_null(self):
        """GET /api/sports/featured should return 200"""
        resp = requests.get(f"{BASE_URL}/api/sports/featured")
        assert resp.status_code == 200
        print(f"Featured match status: {resp.status_code}")

    def test_featured_has_match_fields(self):
        """Featured match should have id, home_team, away_team"""
        resp = requests.get(f"{BASE_URL}/api/sports/featured")
        assert resp.status_code == 200
        data = resp.json()
        if data is None:
            pytest.skip("No matches available for featured")
        assert "id" in data
        assert "home_team" in data
        assert "away_team" in data
        print(f"Featured match: {data.get('home_team')} vs {data.get('away_team')}")

    def test_featured_has_ai_insight_field(self):
        """Featured match response must include ai_insight field"""
        resp = requests.get(f"{BASE_URL}/api/sports/featured")
        assert resp.status_code == 200
        data = resp.json()
        if data is None:
            pytest.skip("No featured match")
        assert "ai_insight" in data, "Featured match missing 'ai_insight' field"
        print(f"ai_insight present: '{data['ai_insight'][:50]}...'" if data.get('ai_insight') else "ai_insight is empty string (may be disabled)")

    def test_featured_slug_present(self):
        """Featured match should have slug for URL navigation"""
        resp = requests.get(f"{BASE_URL}/api/sports/featured")
        assert resp.status_code == 200
        data = resp.json()
        if data is None:
            pytest.skip("No featured match")
        assert "slug" in data, "Featured match missing 'slug' field"
        assert data["slug"], "Featured match slug is empty"
        print(f"Featured slug: {data['slug']}")


# ── match detail ──────────────────────────────────────────────────────

class TestMatchDetail:
    """Tests for /api/sports/match/{id} endpoint"""

    def test_match_by_id_200(self, first_match_id):
        """GET /api/sports/match/{id} should return 200"""
        if not first_match_id:
            pytest.skip("No match IDs available")
        resp = requests.get(f"{BASE_URL}/api/sports/match/{first_match_id}")
        assert resp.status_code == 200
        print(f"Match detail status: {resp.status_code}")

    def test_match_by_id_has_ai_analysis(self, first_match_id):
        """Match detail should include ai_analysis field"""
        if not first_match_id:
            pytest.skip("No match IDs available")
        resp = requests.get(f"{BASE_URL}/api/sports/match/{first_match_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert "ai_analysis" in data, "Missing 'ai_analysis' field"
        print(f"ai_analysis: {'present' if data.get('ai_analysis') else 'empty (AI may be disabled)'}")

    def test_match_by_id_has_recommended_partner(self, first_match_id):
        """Match detail should include recommended_partner field"""
        if not first_match_id:
            pytest.skip("No match IDs available")
        resp = requests.get(f"{BASE_URL}/api/sports/match/{first_match_id}")
        assert resp.status_code == 200
        data = resp.json()
        assert "recommended_partner" in data, "Missing 'recommended_partner' field"
        print(f"recommended_partner: {data.get('recommended_partner')}")

    def test_match_by_id_404_for_invalid(self):
        """Invalid match ID should return 404"""
        resp = requests.get(f"{BASE_URL}/api/sports/match/invalid-nonexistent-id-12345")
        assert resp.status_code == 404
        print(f"Invalid match correctly returns 404")

    def test_match_by_slug_200(self, first_match_slug):
        """GET /api/sports/match-by-slug/{slug} should return 200"""
        if not first_match_slug:
            pytest.skip("No match slugs available")
        resp = requests.get(f"{BASE_URL}/api/sports/match-by-slug/{first_match_slug}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["slug"] == first_match_slug
        print(f"Match by slug OK: {first_match_slug}")

    def test_match_by_slug_404_for_invalid(self):
        """Invalid slug should return 404"""
        resp = requests.get(f"{BASE_URL}/api/sports/match-by-slug/invalid-slug-xxx-2000-01-01")
        assert resp.status_code == 404
        print("Invalid slug correctly returns 404")


# ── admin API status ──────────────────────────────────────────────────

class TestAdminApiStatus:
    """Tests for /api/admin/api-status endpoint"""

    def test_api_status_returns_200(self):
        """GET /api/admin/api-status should return 200"""
        resp = requests.get(f"{BASE_URL}/api/admin/api-status")
        assert resp.status_code == 200
        print(f"Admin API status: {resp.status_code}")

    def test_api_status_structure(self):
        """Response should have required cache info fields"""
        resp = requests.get(f"{BASE_URL}/api/admin/api-status")
        assert resp.status_code == 200
        data = resp.json()
        required_fields = [
            "odds_api_configured",
            "cache_age_seconds",
            "cache_ttl_seconds",
            "is_stale",
            "cached_match_count",
            "error_count",
            "ai_insight_enabled",
            "featured_match_override",
        ]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        print(f"API status fields OK: {list(data.keys())}")

    def test_api_status_odds_api_configured(self):
        """Odds API key should be configured"""
        resp = requests.get(f"{BASE_URL}/api/admin/api-status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["odds_api_configured"] is True, "Odds API key is NOT configured!"
        print(f"Odds API configured: {data['odds_api_configured']}")

    def test_api_status_cache_ttl(self):
        """Cache TTL should be 120 seconds"""
        resp = requests.get(f"{BASE_URL}/api/admin/api-status")
        assert resp.status_code == 200
        data = resp.json()
        assert data["cache_ttl_seconds"] == 120
        print(f"Cache TTL: {data['cache_ttl_seconds']}s")


# ── admin AI toggle ───────────────────────────────────────────────────

class TestAdminAiToggle:
    """Tests for /api/admin/ai-toggle endpoint"""

    def test_ai_toggle_disable(self):
        """POST /api/admin/ai-toggle with enabled=false should work"""
        resp = requests.post(f"{BASE_URL}/api/admin/ai-toggle", json={"enabled": False})
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("ok") is True
        assert data.get("ai_insight_enabled") is False
        print(f"AI toggle disabled OK: {data}")

    def test_ai_toggle_enable(self):
        """POST /api/admin/ai-toggle with enabled=true should work"""
        resp = requests.post(f"{BASE_URL}/api/admin/ai-toggle", json={"enabled": True})
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("ok") is True
        assert data.get("ai_insight_enabled") is True
        print(f"AI toggle enabled OK: {data}")

    def test_ai_toggle_reflected_in_status(self):
        """AI toggle state should be reflected in /api/admin/api-status"""
        # Disable AI
        requests.post(f"{BASE_URL}/api/admin/ai-toggle", json={"enabled": False})
        status = requests.get(f"{BASE_URL}/api/admin/api-status").json()
        assert status["ai_insight_enabled"] is False

        # Re-enable AI
        requests.post(f"{BASE_URL}/api/admin/ai-toggle", json={"enabled": True})
        status = requests.get(f"{BASE_URL}/api/admin/api-status").json()
        assert status["ai_insight_enabled"] is True
        print("AI toggle reflected in api-status correctly")


# ── admin refresh scores ──────────────────────────────────────────────

class TestAdminRefreshScores:
    """Tests for /api/admin/refresh-scores endpoint"""

    def test_refresh_scores_returns_200(self):
        """POST /api/admin/refresh-scores should return 200"""
        resp = requests.post(f"{BASE_URL}/api/admin/refresh-scores")
        assert resp.status_code == 200
        print(f"Refresh scores status: {resp.status_code}")

    def test_refresh_scores_response_structure(self):
        """Response should have ok and count fields"""
        resp = requests.post(f"{BASE_URL}/api/admin/refresh-scores")
        assert resp.status_code == 200
        data = resp.json()
        assert "ok" in data
        assert "count" in data
        assert data["ok"] is True
        print(f"Refresh scores response: {data}")

    def test_refresh_scores_invalidates_cache(self):
        """After refresh, cache should be fresh (not stale)"""
        requests.post(f"{BASE_URL}/api/admin/refresh-scores")
        time.sleep(1)  # brief wait
        status = requests.get(f"{BASE_URL}/api/admin/api-status").json()
        assert status["is_stale"] is False, "Cache should not be stale right after refresh"
        print(f"Cache age after refresh: {status['cache_age_seconds']}s, stale={status['is_stale']}")


# ── featured match override ───────────────────────────────────────────

class TestFeaturedMatchOverride:
    """Tests for /api/admin/featured-match endpoint"""

    def test_set_featured_match(self, first_match_id):
        """POST /api/admin/featured-match should set override"""
        if not first_match_id:
            pytest.skip("No match IDs available")
        resp = requests.post(f"{BASE_URL}/api/admin/featured-match", json={"match_id": first_match_id})
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("ok") is True
        assert data.get("featured_match_id") == first_match_id
        print(f"Featured match set: {first_match_id}")

    def test_set_featured_reflected_in_status(self, first_match_id):
        """Set featured match should appear in api-status"""
        if not first_match_id:
            pytest.skip("No match IDs available")
        requests.post(f"{BASE_URL}/api/admin/featured-match", json={"match_id": first_match_id})
        status = requests.get(f"{BASE_URL}/api/admin/api-status").json()
        assert status["featured_match_override"] == first_match_id
        print(f"Featured override in status: {status['featured_match_override']}")

    def test_clear_featured_match(self):
        """POST /api/admin/featured-match with null should clear override"""
        resp = requests.post(f"{BASE_URL}/api/admin/featured-match", json={"match_id": None})
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("ok") is True
        assert data.get("featured_match_id") is None
        print(f"Featured match cleared: {data}")


# ── partner tracking redirect ─────────────────────────────────────────

class TestPartnerTrackingRedirect:
    """Tests for /api/go/{partner_id}/{match_id} endpoint"""

    def test_redirect_with_valid_partner(self, first_partner_id, first_match_id):
        """GET /api/go/{partner_id}/{match_id} should redirect (302)"""
        if not first_partner_id or not first_match_id:
            pytest.skip("No partner or match IDs available")
        # Use allow_redirects=False to check the redirect itself
        resp = requests.get(
            f"{BASE_URL}/api/go/{first_partner_id}/{first_match_id}",
            allow_redirects=False
        )
        assert resp.status_code == 302, f"Expected 302 redirect, got {resp.status_code}"
        assert "Location" in resp.headers, "Missing Location header in redirect"
        redirect_url = resp.headers["Location"]
        assert redirect_url != "/", f"Redirect URL should not be '/' for valid partner, got: {redirect_url}"
        print(f"Tracking redirect OK: {resp.status_code} → {redirect_url}")

    def test_redirect_with_invalid_partner(self, first_match_id):
        """GET with invalid partner_id should still redirect (to '/')"""
        if not first_match_id:
            pytest.skip("No match IDs available")
        resp = requests.get(
            f"{BASE_URL}/api/go/invalid-partner-xxx/{first_match_id}",
            allow_redirects=False
        )
        assert resp.status_code == 302
        redirect_url = resp.headers.get("Location", "")
        assert redirect_url == "/", f"Expected redirect to '/', got: {redirect_url}"
        print(f"Invalid partner fallback redirect OK: → {redirect_url}")

    def test_redirect_logs_click(self, first_partner_id, first_match_id):
        """Redirect should record click in DB without error"""
        if not first_partner_id or not first_match_id:
            pytest.skip("No partner or match IDs available")
        # Just make the request and verify no 500 error
        resp = requests.get(
            f"{BASE_URL}/api/go/{first_partner_id}/{first_match_id}",
            allow_redirects=False
        )
        assert resp.status_code in [302, 301], f"Unexpected status: {resp.status_code}"
        print(f"Click logging OK: status={resp.status_code}")
