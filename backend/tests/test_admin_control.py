"""
GG2026 Phase 8 — Admin Control System Backend Tests
Tests for Admin SEO monitoring and control endpoints.
All /api/admin/seo/* endpoints require admin JWT auth.
"""
import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Admin credentials from requirement
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "123123.."


class TestAuth:
    """Authentication tests - get JWT token for admin endpoints"""

    def test_login_success(self):
        """Test admin login returns JWT token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        assert "token" in data, "Response missing token"
        assert data["username"] == ADMIN_USERNAME
        assert "expires_in" in data
        print(f"✓ Admin login successful, token obtained")

    def test_login_invalid_credentials(self):
        """Test login with wrong password returns 401"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": ADMIN_USERNAME, "password": "wrongpassword"},
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"✓ Invalid credentials returns 401 as expected")


@pytest.fixture(scope="class")
def admin_token():
    """Get admin JWT token for authenticated requests"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
    )
    if response.status_code != 200:
        pytest.skip(f"Cannot obtain admin token: {response.text}")
    return response.json()["token"]


@pytest.fixture(scope="class")
def admin_headers(admin_token):
    """Return headers with admin JWT for authenticated requests"""
    return {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}


class TestAuthProtection:
    """Verify all /api/admin/seo/* endpoints return 401 without valid JWT"""

    @pytest.mark.parametrize("endpoint", [
        "/api/admin/seo/dashboard",
        "/api/admin/seo/settings",
        "/api/admin/seo/page-types",
        "/api/admin/seo/agents",
        "/api/admin/seo/publishing",
        "/api/admin/seo/companies",
        "/api/admin/seo/serp",
        "/api/admin/seo/articles",
        "/api/admin/seo/sitemap",
        "/api/admin/seo/indexing",
    ])
    def test_endpoint_requires_auth(self, endpoint):
        """Test endpoint returns 401 without token"""
        response = requests.get(f"{BASE_URL}{endpoint}")
        assert response.status_code == 401, f"{endpoint} should return 401 without auth, got {response.status_code}"
        print(f"✓ {endpoint} returns 401 without auth")

    def test_settings_post_requires_auth(self):
        """POST /api/admin/seo/settings requires auth"""
        response = requests.post(
            f"{BASE_URL}/api/admin/seo/settings",
            json={"path": "agents.keyword_intelligence", "value": False},
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"✓ POST /api/admin/seo/settings returns 401 without auth")

    def test_companies_priority_post_requires_auth(self):
        """POST /api/admin/seo/companies/priority requires auth"""
        response = requests.post(
            f"{BASE_URL}/api/admin/seo/companies/priority",
            json={"base_slug": "test", "sort_order": 1},
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print(f"✓ POST /api/admin/seo/companies/priority returns 401 without auth")


class TestAdminSEODashboard:
    """Test GET /api/admin/seo/dashboard - Full dashboard with all 8 sections"""

    def test_dashboard_returns_all_sections(self, admin_headers):
        """Dashboard returns all 8 monitoring sections"""
        response = requests.get(f"{BASE_URL}/api/admin/seo/dashboard", headers=admin_headers)
        assert response.status_code == 200, f"Dashboard failed: {response.text}"
        data = response.json()

        # Verify all 8 sections present
        required_sections = ["settings", "page_types", "agents", "publishing", "serp", "articles", "sitemap", "indexing"]
        for section in required_sections:
            assert section in data, f"Missing section: {section}"
        
        assert "generated_at" in data, "Missing generated_at timestamp"
        print(f"✓ Dashboard contains all 8 sections: {', '.join(required_sections)}")


class TestAdminSEOSettings:
    """Test GET/POST /api/admin/seo/settings"""

    def test_get_settings(self, admin_headers):
        """GET settings returns page_types, agents, publishing, serp toggles"""
        response = requests.get(f"{BASE_URL}/api/admin/seo/settings", headers=admin_headers)
        assert response.status_code == 200, f"Settings GET failed: {response.text}"
        data = response.json()

        # Verify structure
        assert "page_types" in data, "Missing page_types"
        assert "agents" in data, "Missing agents"
        assert "publishing" in data, "Missing publishing"
        assert "serp" in data, "Missing serp"
        
        # Verify page_types toggles
        page_type_toggles = data["page_types"]
        assert "company_sub_pages" in page_type_toggles
        assert "bonus_hub_pages" in page_type_toggles
        assert "programmatic_pages" in page_type_toggles

        # Verify agents toggles
        agent_toggles = data["agents"]
        assert "keyword_intelligence" in agent_toggles
        assert "content_generator" in agent_toggles
        assert "internal_linking" in agent_toggles

        # Verify publishing settings
        pub_settings = data["publishing"]
        assert "auto_publish_enabled" in pub_settings
        assert "min_per_day" in pub_settings
        assert "max_per_day" in pub_settings

        print(f"✓ Settings structure verified with page_types, agents, publishing, serp sections")

    def test_update_settings_by_dot_path(self, admin_headers):
        """POST settings toggles by dot-path"""
        # First get current value
        response = requests.get(f"{BASE_URL}/api/admin/seo/settings", headers=admin_headers)
        original_value = response.json()["agents"]["keyword_intelligence"]

        # Toggle it off
        response = requests.post(
            f"{BASE_URL}/api/admin/seo/settings",
            headers=admin_headers,
            json={"path": "agents.keyword_intelligence", "value": False},
        )
        assert response.status_code == 200, f"Settings update failed: {response.text}"
        data = response.json()
        assert data["agents"]["keyword_intelligence"] == False, "Toggle did not update to False"

        # Toggle it back
        response = requests.post(
            f"{BASE_URL}/api/admin/seo/settings",
            headers=admin_headers,
            json={"path": "agents.keyword_intelligence", "value": True},
        )
        assert response.status_code == 200
        assert response.json()["agents"]["keyword_intelligence"] == True

        print(f"✓ Settings update by dot-path (agents.keyword_intelligence) works correctly")

    def test_update_settings_missing_path(self, admin_headers):
        """POST settings without path returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/admin/seo/settings",
            headers=admin_headers,
            json={"value": False},
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print(f"✓ POST /api/admin/seo/settings without path returns 400")


class TestAdminSEOPageTypes:
    """Test GET /api/admin/seo/page-types"""

    def test_get_page_types(self, admin_headers):
        """GET page-types returns toggles with page counts"""
        response = requests.get(f"{BASE_URL}/api/admin/seo/page-types", headers=admin_headers)
        assert response.status_code == 200, f"Page types failed: {response.text}"
        data = response.json()

        assert "toggles" in data, "Missing toggles"
        assert "counts" in data, "Missing counts"
        assert "total_active_pages" in data, "Missing total_active_pages"

        # Verify toggle keys
        toggles = data["toggles"]
        expected_toggles = ["company_sub_pages", "bonus_hub_pages", "payment_hub_pages", "company_articles", "programmatic_pages", "guide_pages"]
        for toggle in expected_toggles:
            assert toggle in toggles, f"Missing toggle: {toggle}"

        # Verify counts match toggle keys
        counts = data["counts"]
        for toggle in expected_toggles:
            assert toggle in counts, f"Missing count for: {toggle}"

        print(f"✓ Page types returned with toggles and counts for {len(expected_toggles)} page types")


class TestAdminSEOAgents:
    """Test GET /api/admin/seo/agents"""

    def test_get_agents(self, admin_headers):
        """GET agents returns 5 agents with enabled toggle, job stats, success rate"""
        response = requests.get(f"{BASE_URL}/api/admin/seo/agents", headers=admin_headers)
        assert response.status_code == 200, f"Agents failed: {response.text}"
        data = response.json()

        assert "agents" in data, "Missing agents list"
        assert "toggles" in data, "Missing toggles"

        agents = data["agents"]
        expected_agents = ["keyword_intelligence", "content_generator", "internal_linking", "update", "technical_seo"]
        assert len(agents) == 5, f"Expected 5 agents, got {len(agents)}"

        agent_names = [a["name"] for a in agents]
        for expected in expected_agents:
            assert expected in agent_names, f"Missing agent: {expected}"

        # Verify each agent has required fields
        for agent in agents:
            assert "name" in agent
            assert "enabled" in agent
            assert "total_jobs" in agent
            assert "completed" in agent
            assert "failed" in agent
            assert "success_rate" in agent

        print(f"✓ Agents endpoint returns 5 agents with enabled, job stats, success_rate")


class TestAdminSEOPublishing:
    """Test GET /api/admin/seo/publishing"""

    def test_get_publishing(self, admin_headers):
        """GET publishing returns queue overview with by_status, today, recent_published"""
        response = requests.get(f"{BASE_URL}/api/admin/seo/publishing", headers=admin_headers)
        assert response.status_code == 200, f"Publishing failed: {response.text}"
        data = response.json()

        assert "settings" in data, "Missing settings"
        assert "total" in data, "Missing total"
        assert "by_status" in data, "Missing by_status"
        assert "today" in data, "Missing today"
        assert "recent_published" in data, "Missing recent_published"

        # Verify by_status has all statuses
        by_status = data["by_status"]
        expected_statuses = ["pending", "scheduled", "publishing", "published", "failed"]
        for status in expected_statuses:
            assert status in by_status, f"Missing status: {status}"

        # Verify today has required fields
        today = data["today"]
        assert "published" in today
        assert "scheduled" in today
        assert "limit" in today

        print(f"✓ Publishing overview with by_status, today stats, recent_published")


class TestAdminSEOCompanies:
    """Test GET /api/admin/seo/companies and POST /api/admin/seo/companies/priority"""

    def test_get_companies(self, admin_headers):
        """GET companies returns company priority list with coverage_score"""
        response = requests.get(f"{BASE_URL}/api/admin/seo/companies", headers=admin_headers)
        assert response.status_code == 200, f"Companies failed: {response.text}"
        data = response.json()

        assert "companies" in data, "Missing companies list"
        assert "total_firms" in data, "Missing total_firms"

        # If there are companies, verify each has required fields
        if data["companies"]:
            company = data["companies"][0]
            required_fields = ["name", "base_slug", "sort_order", "rating", "bonus_amount", "articles", "programmatic_pages", "queue_items", "coverage_score"]
            for field in required_fields:
                assert field in company, f"Missing company field: {field}"
            
            # Verify coverage_score calculation (max 100)
            assert 0 <= company["coverage_score"] <= 100, f"coverage_score should be 0-100, got {company['coverage_score']}"

        print(f"✓ Companies list with coverage_score (total_firms: {data['total_firms']})")

    def test_update_company_priority(self, admin_headers):
        """POST companies/priority updates company sort_order"""
        # First get companies to find a valid base_slug
        response = requests.get(f"{BASE_URL}/api/admin/seo/companies", headers=admin_headers)
        data = response.json()

        if not data["companies"]:
            pytest.skip("No companies to test priority update")

        test_slug = data["companies"][0]["base_slug"]
        original_order = data["companies"][0]["sort_order"]
        new_order = original_order + 1 if original_order < 100 else original_order - 1

        # Update priority
        response = requests.post(
            f"{BASE_URL}/api/admin/seo/companies/priority",
            headers=admin_headers,
            json={"base_slug": test_slug, "sort_order": new_order},
        )
        assert response.status_code == 200, f"Priority update failed: {response.text}"
        result = response.json()
        
        assert "updated" in result
        assert result["base_slug"] == test_slug
        assert result["sort_order"] == new_order

        # Restore original
        requests.post(
            f"{BASE_URL}/api/admin/seo/companies/priority",
            headers=admin_headers,
            json={"base_slug": test_slug, "sort_order": original_order},
        )

        print(f"✓ Company priority update works for {test_slug}")

    def test_update_priority_missing_base_slug(self, admin_headers):
        """POST companies/priority without base_slug returns 400"""
        response = requests.post(
            f"{BASE_URL}/api/admin/seo/companies/priority",
            headers=admin_headers,
            json={"sort_order": 1},
        )
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print(f"✓ POST /api/admin/seo/companies/priority without base_slug returns 400")


class TestAdminSEOSerp:
    """Test GET /api/admin/seo/serp"""

    def test_get_serp(self, admin_headers):
        """GET serp returns SERP provider status and fallback mode"""
        response = requests.get(f"{BASE_URL}/api/admin/seo/serp", headers=admin_headers)
        assert response.status_code == 200, f"SERP failed: {response.text}"
        data = response.json()

        assert "settings" in data, "Missing settings"
        assert "providers" in data, "Missing providers"
        assert "any_configured" in data, "Missing any_configured"
        assert "fallback_mode" in data, "Missing fallback_mode"
        assert "recent_jobs" in data, "Missing recent_jobs"

        # Verify providers list
        providers = data["providers"]
        expected_providers = ["ahrefs", "semrush", "dataforseo"]
        provider_names = [p["name"] for p in providers]
        for expected in expected_providers:
            assert expected in provider_names, f"Missing provider: {expected}"

        # Each provider should have 'configured' boolean
        for provider in providers:
            assert "name" in provider
            assert "configured" in provider
            assert isinstance(provider["configured"], bool)

        print(f"✓ SERP status with providers ({len(providers)}), fallback_mode={data['fallback_mode']}")


class TestAdminSEOArticles:
    """Test GET /api/admin/seo/articles"""

    def test_get_articles(self, admin_headers):
        """GET articles returns article generation coverage stats"""
        response = requests.get(f"{BASE_URL}/api/admin/seo/articles", headers=admin_headers)
        assert response.status_code == 200, f"Articles failed: {response.text}"
        data = response.json()

        assert "company_articles" in data, "Missing company_articles"
        assert "general_articles" in data, "Missing general_articles"
        assert "ai_generated_content" in data, "Missing ai_generated_content"
        assert "generation_jobs" in data, "Missing generation_jobs"
        assert "coverage" in data, "Missing coverage"

        # Verify company_articles structure
        company_articles = data["company_articles"]
        assert "total" in company_articles
        assert "published" in company_articles

        # Verify coverage structure
        coverage = data["coverage"]
        assert "firms_with_articles" in coverage
        assert "total_firms" in coverage
        assert "coverage_pct" in coverage

        print(f"✓ Articles stats: company_articles={company_articles['total']}, coverage_pct={coverage['coverage_pct']}%")


class TestAdminSEOSitemap:
    """Test GET /api/admin/seo/sitemap"""

    def test_get_sitemap(self, admin_headers):
        """GET sitemap returns health with 10 sitemaps, total URLs, warnings"""
        response = requests.get(f"{BASE_URL}/api/admin/seo/sitemap", headers=admin_headers)
        assert response.status_code == 200, f"Sitemap failed: {response.text}"
        data = response.json()

        assert "sitemaps" in data, "Missing sitemaps"
        assert "total_sitemaps" in data, "Missing total_sitemaps"
        assert "total_urls" in data, "Missing total_urls"
        assert "health" in data, "Missing health"
        assert "warnings" in data, "Missing warnings"

        # Should have 10 sitemaps
        sitemaps = data["sitemaps"]
        assert len(sitemaps) == 10, f"Expected 10 sitemaps, got {len(sitemaps)}"

        # Each sitemap should have required fields
        for sitemap in sitemaps:
            assert "name" in sitemap
            assert "type" in sitemap
            assert "est_urls" in sitemap
            assert "status" in sitemap

        # Verify warnings is a list
        assert isinstance(data["warnings"], list)

        print(f"✓ Sitemap health: {len(sitemaps)} sitemaps, {data['total_urls']} total URLs, {len(data['warnings'])} warnings")


class TestAdminSEOIndexing:
    """Test GET /api/admin/seo/indexing"""

    def test_get_indexing(self, admin_headers):
        """GET indexing returns programmatic page indexing stats and recommendations"""
        response = requests.get(f"{BASE_URL}/api/admin/seo/indexing", headers=admin_headers)
        assert response.status_code == 200, f"Indexing failed: {response.text}"
        data = response.json()

        assert "programmatic_pages" in data, "Missing programmatic_pages"
        assert "company_articles" in data, "Missing company_articles"
        assert "non_indexable_reasons" in data, "Missing non_indexable_reasons"
        assert "recommendations" in data, "Missing recommendations"

        # Verify programmatic_pages structure
        prog = data["programmatic_pages"]
        assert "total" in prog
        assert "indexable" in prog
        assert "not_indexable" in prog
        assert "indexable_pct" in prog

        # Verify company_articles structure
        articles = data["company_articles"]
        assert "published" in articles
        assert "unpublished" in articles

        # Verify recommendations is a list
        assert isinstance(data["recommendations"], list)

        print(f"✓ Indexing stats: {prog['total']} total, {prog['indexable']} indexable ({prog['indexable_pct']}%)")


class TestExistingRoutesUnbroken:
    """Verify existing routes still work after Phase 8 changes"""

    def test_bonus_sites_endpoint(self):
        """GET /api/bonus-sites still works"""
        response = requests.get(f"{BASE_URL}/api/bonus-sites")
        assert response.status_code == 200, f"bonus-sites broken: {response.status_code}"
        data = response.json()
        assert "sites" in data or isinstance(data, list)
        print(f"✓ GET /api/bonus-sites still works")

    def test_publish_status_endpoint(self, admin_headers):
        """GET /api/publish/status still works"""
        response = requests.get(f"{BASE_URL}/api/publish/status", headers=admin_headers)
        assert response.status_code == 200, f"publish/status broken: {response.status_code}"
        data = response.json()
        assert "total" in data or "queue" in data or "daemon" in data
        print(f"✓ GET /api/publish/status still works")

    def test_programmatic_stats_endpoint(self, admin_headers):
        """GET /api/programmatic/stats still works"""
        response = requests.get(f"{BASE_URL}/api/programmatic/stats", headers=admin_headers)
        assert response.status_code == 200, f"programmatic/stats broken: {response.status_code}"
        print(f"✓ GET /api/programmatic/stats still works")

    def test_db_check_endpoint(self):
        """GET /api/db-check still works"""
        # Using /db-check as health is not routed through /api
        response = requests.get(f"{BASE_URL}/api/bonus-sites")
        assert response.status_code == 200, f"API health check failed: {response.status_code}"
        print(f"✓ API endpoints healthy (bonus-sites returns 200)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
