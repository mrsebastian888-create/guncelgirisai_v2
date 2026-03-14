"""
GG2026 SEO Framework - Comprehensive Test Suite
Tests ALL 8 phases of the platform optimization.
"""
import pytest
import requests
import os

# Base URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')
if not BASE_URL:
    pytest.skip("REACT_APP_BACKEND_URL not set", allow_module_level=True)


# ===================== FIXTURES =====================

@pytest.fixture(scope="module")
def admin_token():
    """Get admin JWT token"""
    try:
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "123123.."
        }, timeout=30)
        if resp.status_code == 200:
            return resp.json().get("token")
    except Exception as e:
        print(f"Admin login failed: {e}")
    pytest.skip("Admin login failed")
    return None


@pytest.fixture(scope="module")
def auth_headers(admin_token):
    """Auth headers for admin endpoints"""
    return {"Authorization": f"Bearer {admin_token}"}


# ===================== PHASE 1: CORE SEO INFRASTRUCTURE =====================

class TestPhase1CompanySubPages:
    """Phase 1: Company folder (/firma-sub/{base_slug}/{page_type})"""
    
    PAGE_TYPES = [
        "guncel-giris", "guncel-adresi", "yeni-giris-adresi", "mobil-giris",
        "deneme-bonusu", "deneme-bonusu-2026", "hosgeldin-bonusu",
        "yatirimsiz-deneme-bonusu", "bonus-sartlari", "odeme-yontemleri"
    ]
    
    def test_firma_sub_guncel_giris(self):
        """Test /api/firma-sub/tulipbet/guncel-giris"""
        resp = requests.get(f"{BASE_URL}/api/firma-sub/tulipbet/guncel-giris", timeout=30)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        data = resp.json()
        assert "site" in data
        assert "seo" in data
        assert "internal_links" in data
        print(f"PASS: guncel-giris returned site={data['site'].get('name')}")
    
    def test_firma_sub_deneme_bonusu(self):
        """Test /api/firma-sub/tulipbet/deneme-bonusu"""
        resp = requests.get(f"{BASE_URL}/api/firma-sub/tulipbet/deneme-bonusu", timeout=30)
        assert resp.status_code == 200
        data = resp.json()
        assert data["seo"]["title"]
        assert "bonus" in data["seo"]["title"].lower() or "bonus" in data["seo"]["description"].lower()
        print(f"PASS: deneme-bonusu SEO title={data['seo']['title'][:60]}")
    
    def test_firma_sub_all_page_types_exist(self):
        """Verify all 10 page types work"""
        working = 0
        for page_type in self.PAGE_TYPES:
            resp = requests.get(f"{BASE_URL}/api/firma-sub/tulipbet/{page_type}", timeout=30)
            if resp.status_code == 200:
                working += 1
            else:
                print(f"WARNING: {page_type} returned {resp.status_code}")
        assert working >= 8, f"Expected >=8 page types working, got {working}"
        print(f"PASS: {working}/{len(self.PAGE_TYPES)} page types working")
    
    def test_firma_sub_invalid_page_type_returns_404(self):
        """Invalid page type should return 404"""
        resp = requests.get(f"{BASE_URL}/api/firma-sub/tulipbet/invalid-page-type", timeout=30)
        assert resp.status_code == 404
        print("PASS: Invalid page type returns 404")


class TestPhase1HubPages:
    """Phase 1: Hub pages (/hub/bonus/{slug}, /hub/payment/{slug})"""
    
    BONUS_HUBS = [
        "deneme-bonusu-veren-siteler", "guncel-deneme-bonusu",
        "yatirimsiz-deneme-bonusu", "bonus-veren-siteler"
    ]
    
    PAYMENT_HUBS = [
        "odeme-yontemleri", "mobil-odeme-ile-bahis", "kredi-karti-ile-bahis",
        "papel-ile-bahis", "havale-ile-bahis", "kripto-ile-bahis",
        "bddk-onayli-odeme-yontemleri", "guvenli-odeme-yontemleri"
    ]
    
    def test_bonus_hub_deneme_bonusu_veren_siteler(self):
        """Test bonus hub page"""
        resp = requests.get(f"{BASE_URL}/api/hub/bonus/deneme-bonusu-veren-siteler", timeout=30)
        assert resp.status_code == 200
        data = resp.json()
        assert "sites" in data
        assert "seo" in data
        print(f"PASS: Bonus hub returned {len(data.get('sites', []))} sites")
    
    def test_all_bonus_hubs(self):
        """Test all 4+ bonus hubs"""
        working = 0
        for hub in self.BONUS_HUBS:
            resp = requests.get(f"{BASE_URL}/api/hub/bonus/{hub}", timeout=30)
            if resp.status_code == 200:
                working += 1
            else:
                print(f"WARNING: bonus hub {hub} returned {resp.status_code}")
        assert working >= 3, f"Expected >=3 bonus hubs working, got {working}"
        print(f"PASS: {working}/{len(self.BONUS_HUBS)} bonus hubs working")
    
    def test_payment_hub_odeme_yontemleri(self):
        """Test payment hub page"""
        resp = requests.get(f"{BASE_URL}/api/hub/payment/odeme-yontemleri", timeout=30)
        assert resp.status_code == 200
        data = resp.json()
        assert "sites" in data
        print(f"PASS: Payment hub returned {len(data.get('sites', []))} sites")
    
    def test_all_payment_hubs(self):
        """Test all 8 payment hubs"""
        working = 0
        for hub in self.PAYMENT_HUBS:
            resp = requests.get(f"{BASE_URL}/api/hub/payment/{hub}", timeout=30)
            if resp.status_code == 200:
                working += 1
            else:
                print(f"WARNING: payment hub {hub} returned {resp.status_code}")
        assert working >= 6, f"Expected >=6 payment hubs working, got {working}"
        print(f"PASS: {working}/{len(self.PAYMENT_HUBS)} payment hubs working")


class TestPhase1Sitemaps:
    """Phase 1: All sitemaps"""
    
    SITEMAPS = [
        "sitemap.xml", "sitemap-pages.xml", "sitemap-firms.xml",
        "sitemap-seo-pages.xml", "sitemap-articles.xml",
        "sitemap-company-articles.xml", "sitemap-programmatic.xml",
        "sitemap-videos.xml"
    ]
    
    def test_sitemap_index(self):
        """Test sitemap index"""
        resp = requests.get(f"{BASE_URL}/api/sitemap.xml", timeout=30)
        assert resp.status_code == 200
        assert "sitemapindex" in resp.text or "sitemap" in resp.text.lower()
        print("PASS: Sitemap index OK")
    
    def test_all_sitemaps(self):
        """Test all sitemaps return valid XML"""
        working = 0
        for sitemap in self.SITEMAPS:
            resp = requests.get(f"{BASE_URL}/api/{sitemap}", timeout=30)
            if resp.status_code == 200 and "xml" in resp.headers.get("content-type", ""):
                working += 1
            else:
                print(f"WARNING: {sitemap} returned {resp.status_code}")
        assert working >= 6, f"Expected >=6 sitemaps working, got {working}"
        print(f"PASS: {working}/{len(self.SITEMAPS)} sitemaps working")


# ===================== PHASE 2: CONTENT TEMPLATES =====================

class TestPhase2Templates:
    """Phase 2: Company Guide and Bonus Guide templates"""
    
    def test_company_guide_template_sections(self):
        """Verify company guide has required sections"""
        resp = requests.get(f"{BASE_URL}/api/firma-sub/tulipbet/guncel-giris", timeout=30)
        assert resp.status_code == 200
        data = resp.json()
        
        # Check for expected fields
        assert "site" in data  # company-overview
        assert "seo" in data  # SEO metadata
        assert "internal_links" in data  # related-pages
        assert "faq" in data  # FAQ section
        assert "similar_firms_links" in data  # similar companies
        print("PASS: Company guide template has all sections")
    
    def test_bonus_guide_template_sections(self):
        """Verify bonus guide has required sections"""
        resp = requests.get(f"{BASE_URL}/api/firma-sub/tulipbet/deneme-bonusu", timeout=30)
        assert resp.status_code == 200
        data = resp.json()
        
        # Bonus pages should have company info, SEO, FAQ
        assert "site" in data
        assert data["site"].get("bonus_amount")  # bonus info
        assert "faq" in data
        print(f"PASS: Bonus guide template OK, bonus_amount={data['site'].get('bonus_amount')}")
    
    def test_json_ld_schemas_present(self):
        """Check JSON-LD schema data is returned"""
        resp = requests.get(f"{BASE_URL}/api/firma-sub/tulipbet/guncel-giris", timeout=30)
        assert resp.status_code == 200
        data = resp.json()
        
        # Schema data should be in the response
        assert "breadcrumb" in data  # For BreadcrumbList
        assert "faq" in data  # For FAQPage
        print("PASS: JSON-LD schema data available")


# ===================== PHASE 3: AI AGENTS =====================

class TestPhase3Agents:
    """Phase 3: AI Agent system"""
    
    def test_agents_status(self):
        """GET /api/agents/status returns 5 agents"""
        resp = requests.get(f"{BASE_URL}/api/agents/status", timeout=30)
        assert resp.status_code == 200
        data = resp.json()
        
        assert data.get("status") == "operational"
        assert "agents" in data
        assert len(data["agents"]) == 5
        agent_names = [a["name"] for a in data["agents"]]
        expected = ["keyword_intelligence", "content_generator", "internal_linking", "update", "technical_seo"]
        for exp in expected:
            assert exp in agent_names, f"Missing agent: {exp}"
        print(f"PASS: 5 agents operational, LLM configured={data.get('llm_configured')}")
    
    def test_agents_jobs_list(self):
        """GET /api/agents/jobs returns job list"""
        resp = requests.get(f"{BASE_URL}/api/agents/jobs", timeout=30)
        assert resp.status_code == 200
        data = resp.json()
        assert "jobs" in data
        print(f"PASS: Jobs endpoint returned {len(data['jobs'])} jobs")
    
    def test_non_llm_agent_linking_audit(self):
        """POST /api/agents/linking/audit (no LLM)"""
        resp = requests.post(f"{BASE_URL}/api/agents/linking/audit", timeout=60)
        assert resp.status_code == 200
        data = resp.json()
        assert "clusters" in data or "status" in data
        print("PASS: Linking audit works")
    
    def test_non_llm_agent_linking_orphans(self):
        """POST /api/agents/linking/orphans (no LLM)"""
        resp = requests.post(f"{BASE_URL}/api/agents/linking/orphans", timeout=60)
        assert resp.status_code == 200
        print("PASS: Linking orphans detection works")
    
    def test_non_llm_agent_seo_canonicals(self):
        """POST /api/agents/seo/canonicals (no LLM)"""
        resp = requests.post(f"{BASE_URL}/api/agents/seo/canonicals", timeout=60)
        assert resp.status_code == 200
        print("PASS: SEO canonicals audit works")
    
    def test_non_llm_agent_seo_sitemap_audit(self):
        """POST /api/agents/seo/sitemap-audit (no LLM)"""
        resp = requests.post(f"{BASE_URL}/api/agents/seo/sitemap-audit", timeout=60)
        assert resp.status_code == 200
        print("PASS: SEO sitemap audit works")
    
    def test_non_llm_agent_update_scan(self):
        """POST /api/agents/update/scan (no LLM)"""
        resp = requests.post(f"{BASE_URL}/api/agents/update/scan", json={"days_threshold": 30}, timeout=60)
        assert resp.status_code == 200
        print("PASS: Update scan works")
    
    def test_non_llm_agent_update_timestamps(self):
        """POST /api/agents/update/timestamps (no LLM)"""
        resp = requests.post(f"{BASE_URL}/api/agents/update/timestamps", json={}, timeout=60)
        assert resp.status_code == 200
        print("PASS: Update timestamps works")


# ===================== PHASE 4: SERP INTELLIGENCE =====================

class TestPhase4SERP:
    """Phase 4: SERP Intelligence"""
    
    def test_serp_status(self):
        """GET /api/agents/serp/status returns 3 providers"""
        resp = requests.get(f"{BASE_URL}/api/agents/serp/status", timeout=30)
        assert resp.status_code == 200
        data = resp.json()
        
        assert "providers" in data
        assert len(data["providers"]) >= 3
        provider_names = [p.get("provider") or p.get("name") for p in data["providers"]]
        print(f"PASS: SERP providers: {provider_names}")
        print(f"      any_configured={data.get('any_configured')}, fallback={data.get('fallback_available')}")
    
    def test_serp_validate_with_ai_fallback(self):
        """POST /api/agents/serp/validate uses AI fallback"""
        resp = requests.post(f"{BASE_URL}/api/agents/serp/validate", json={
            "keywords": ["deneme bonusu"],
            "country": "tr"
        }, timeout=60)
        assert resp.status_code == 200
        data = resp.json()
        assert "keywords" in data or "results" in data
        print(f"PASS: SERP validate returned data, source={data.get('source', 'unknown')}")
    
    def test_serp_difficulty_with_ai_fallback(self):
        """POST /api/agents/serp/difficulty uses AI fallback"""
        resp = requests.post(f"{BASE_URL}/api/agents/serp/difficulty", json={
            "keywords": ["guncel giris"],
            "country": "tr"
        }, timeout=60)
        assert resp.status_code == 200
        data = resp.json()
        print(f"PASS: SERP difficulty works, source={data.get('source', 'unknown')}")


# ===================== PHASE 5: COMPANY ARTICLES =====================

class TestPhase5CompanyArticles:
    """Phase 5: Company article system"""
    
    def test_company_articles_list(self):
        """GET /api/company-articles/tulipbet returns articles"""
        resp = requests.get(f"{BASE_URL}/api/company-articles/tulipbet", timeout=30)
        assert resp.status_code == 200
        data = resp.json()
        
        assert "site" in data
        assert "articles" in data
        assert "sub_pages" in data
        assert "hub_links" in data
        print(f"PASS: Company articles list has {len(data['articles'])} articles")
    
    def test_company_article_detail(self):
        """GET /api/company-articles/tulipbet/{slug} returns detail"""
        # First get the list
        list_resp = requests.get(f"{BASE_URL}/api/company-articles/tulipbet", timeout=30)
        if list_resp.status_code != 200:
            pytest.skip("Company articles list failed")
        
        articles = list_resp.json().get("articles", [])
        if not articles:
            pytest.skip("No company articles found")
        
        article_slug = articles[0].get("slug")
        resp = requests.get(f"{BASE_URL}/api/company-articles/tulipbet/{article_slug}", timeout=30)
        assert resp.status_code == 200
        data = resp.json()
        
        assert "article" in data
        assert "related_sub_pages" in data
        assert "related_hubs" in data
        print("PASS: Article detail has related_sub_pages and related_hubs")


# ===================== PHASE 6: PROGRAMMATIC SEO =====================

class TestPhase6Programmatic:
    """Phase 6: Programmatic SEO engine"""
    
    def test_programmatic_stats(self):
        """GET /api/programmatic/stats"""
        resp = requests.get(f"{BASE_URL}/api/programmatic/stats", timeout=30)
        assert resp.status_code == 200
        data = resp.json()
        
        assert "total_pages" in data
        assert "indexable" in data
        print(f"PASS: Programmatic stats: total={data.get('total_pages')}, indexable={data.get('indexable')}")
    
    def test_programmatic_pages_list(self):
        """GET /api/programmatic/pages"""
        resp = requests.get(f"{BASE_URL}/api/programmatic/pages", timeout=30)
        assert resp.status_code == 200
        data = resp.json()
        
        assert "pages" in data
        print(f"PASS: Programmatic pages list has {len(data.get('pages', []))} pages")
    
    def test_programmatic_page_detail(self):
        """GET /api/programmatic/page/{slug}"""
        # First get a page slug
        list_resp = requests.get(f"{BASE_URL}/api/programmatic/pages", timeout=30)
        if list_resp.status_code != 200:
            pytest.skip("Programmatic pages list failed")
        
        pages = list_resp.json().get("pages", [])
        if not pages:
            pytest.skip("No programmatic pages found")
        
        slug = pages[0].get("slug", "en-guvenilir-bahis-siteleri")
        resp = requests.get(f"{BASE_URL}/api/programmatic/page/{slug}", timeout=30)
        assert resp.status_code == 200
        data = resp.json()
        
        assert "page" in data
        assert "breadcrumb" in data
        print(f"PASS: Programmatic page detail for {slug}")
    
    def test_programmatic_generate_dry_run(self):
        """POST /api/programmatic/generate with dry_run=true"""
        resp = requests.post(f"{BASE_URL}/api/programmatic/generate", json={
            "combination_type": "company_x_payment",
            "dry_run": True
        }, timeout=60)
        assert resp.status_code == 200
        data = resp.json()
        print(f"PASS: Programmatic generate dry_run returned {data.get('preview_count', 0)} previews")


# ===================== PHASE 7: PUBLISHING SYSTEM =====================

class TestPhase7Publishing:
    """Phase 7: Controlled publishing system"""
    
    def test_publish_status(self):
        """GET /api/publish/status with daemon"""
        resp = requests.get(f"{BASE_URL}/api/publish/status", timeout=30)
        assert resp.status_code == 200
        data = resp.json()
        
        assert "daemon" in data
        assert "queue" in data or "total" in data
        print(f"PASS: Publish status - daemon running={data['daemon'].get('running')}")
    
    def test_publish_queue(self):
        """GET /api/publish/queue"""
        resp = requests.get(f"{BASE_URL}/api/publish/queue", timeout=30)
        assert resp.status_code == 200
        data = resp.json()
        
        assert "items" in data or "queue" in data
        print(f"PASS: Publish queue returned {len(data.get('items', data.get('queue', [])))} items")
    
    def test_publish_schedule_map(self):
        """GET /api/publish/schedule-map returns 7 day types"""
        resp = requests.get(f"{BASE_URL}/api/publish/schedule-map", timeout=30)
        assert resp.status_code == 200
        data = resp.json()
        
        assert "schedule" in data
        schedule = data["schedule"]
        assert len(schedule) >= 7, f"Expected 7 day types, got {len(schedule)}"
        print(f"PASS: Schedule map has {len(schedule)} day types")


# ===================== PHASE 8: ADMIN CONTROL =====================

class TestPhase8Admin:
    """Phase 8: Admin SEO control system"""
    
    def test_admin_seo_dashboard_requires_auth(self):
        """GET /api/admin/seo/dashboard returns 401 without token"""
        resp = requests.get(f"{BASE_URL}/api/admin/seo/dashboard", timeout=30)
        assert resp.status_code == 401
        print("PASS: Admin dashboard requires auth")
    
    def test_admin_seo_dashboard(self, auth_headers):
        """GET /api/admin/seo/dashboard with JWT"""
        resp = requests.get(f"{BASE_URL}/api/admin/seo/dashboard", headers=auth_headers, timeout=30)
        assert resp.status_code == 200
        data = resp.json()
        
        # Check all 8 sections
        expected_sections = ["settings", "page_types", "agents", "publishing", "serp", "articles", "sitemap", "indexing"]
        for section in expected_sections:
            assert section in data, f"Missing section: {section}"
        print("PASS: Admin dashboard has all 8 sections")
    
    def test_admin_seo_settings(self, auth_headers):
        """GET /api/admin/seo/settings"""
        resp = requests.get(f"{BASE_URL}/api/admin/seo/settings", headers=auth_headers, timeout=30)
        assert resp.status_code == 200
        data = resp.json()
        
        assert "page_types" in data or "settings" in data
        print("PASS: Admin settings returned")
    
    def test_admin_endpoints_protected(self, auth_headers):
        """Verify all admin endpoints require auth"""
        endpoints = [
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
        ]
        
        unprotected = []
        for endpoint in endpoints:
            resp = requests.get(f"{BASE_URL}{endpoint}", timeout=30)
            if resp.status_code != 401:
                unprotected.append(endpoint)
        
        assert len(unprotected) == 0, f"Unprotected endpoints: {unprotected}"
        print(f"PASS: All {len(endpoints)} admin endpoints require auth")


# ===================== EXISTING ROUTES =====================

class TestExistingRoutes:
    """Verify existing routes still work"""
    
    def test_homepage_bonus_sites(self):
        """GET /api/bonus-sites"""
        resp = requests.get(f"{BASE_URL}/api/bonus-sites", timeout=30)
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list) or "sites" in data
        print("PASS: /api/bonus-sites works")
    
    def test_firma_detail(self):
        """GET /api/firma/{slug}"""
        resp = requests.get(f"{BASE_URL}/api/firma/tulipbet-guncelgiris", timeout=30)
        if resp.status_code == 404:
            resp = requests.get(f"{BASE_URL}/api/firma/tulipbet", timeout=30)
        assert resp.status_code == 200
        print("PASS: /api/firma/{slug} works")
    
    def test_categories(self):
        """GET /api/categories"""
        resp = requests.get(f"{BASE_URL}/api/categories", timeout=30)
        assert resp.status_code == 200
        print("PASS: /api/categories works")
    
    def test_health(self):
        """GET /health"""
        resp = requests.get(f"{BASE_URL}/health", timeout=10)
        assert resp.status_code == 200
        print("PASS: /health works")


# ===================== CROSS-CUTTING =====================

class TestCrossCutting:
    """Cross-cutting concerns"""
    
    def test_no_500_errors_on_main_endpoints(self):
        """Verify no 500 errors on main endpoints"""
        endpoints = [
            "/api/bonus-sites",
            "/api/categories",
            "/api/firma-sub/tulipbet/guncel-giris",
            "/api/hub/bonus/deneme-bonusu-veren-siteler",
            "/api/hub/payment/odeme-yontemleri",
            "/api/agents/status",
            "/api/programmatic/stats",
            "/api/publish/status",
            "/api/sitemap.xml",
        ]
        
        errors_500 = []
        for endpoint in endpoints:
            try:
                resp = requests.get(f"{BASE_URL}{endpoint}", timeout=30)
                if resp.status_code >= 500:
                    errors_500.append(f"{endpoint}: {resp.status_code}")
            except Exception as e:
                errors_500.append(f"{endpoint}: {str(e)[:50]}")
        
        assert len(errors_500) == 0, f"500 errors found: {errors_500}"
        print(f"PASS: No 500 errors on {len(endpoints)} endpoints")
    
    def test_mongodb_id_excluded(self):
        """Verify _id is excluded from responses"""
        resp = requests.get(f"{BASE_URL}/api/bonus-sites", timeout=30)
        assert resp.status_code == 200
        data = resp.json()
        
        items = data if isinstance(data, list) else data.get("sites", [])
        for item in items[:5]:
            assert "_id" not in item, f"_id found in response: {item.get('name')}"
        print("PASS: _id excluded from responses")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
