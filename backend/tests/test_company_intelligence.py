"""
Company Intelligence Module - Phase 1 Tests
Tests for: discovery, classification, enrichment, company profile page, sitemap-companies,
           homepage featured companies slider, admin companies management
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://bot-control-4.preview.emergentagent.com')

class TestCompanyIntelligenceModule:
    """Company Intelligence Module Phase 1 Tests"""
    
    @pytest.fixture(scope="class")
    def auth_token(self):
        """Get admin authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "admin", "password": "123123.."},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        token = response.json().get("token")
        assert token, "No token returned"
        return token
    
    @pytest.fixture(scope="class")
    def auth_headers(self, auth_token):
        """Get auth headers"""
        return {"Authorization": f"Bearer {auth_token}", "Content-Type": "application/json"}
    
    # ============== Admin Discovery Endpoint Tests ==============
    
    def test_admin_discovery_endpoint_unauthorized(self):
        """POST /api/admin/companies/discovery without token should return 401"""
        response = requests.post(
            f"{BASE_URL}/api/admin/companies/discovery",
            json={"query": "Top AI tools 2026", "limit": 5, "run_async": True}
        )
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Admin discovery endpoint requires authentication")
    
    def test_admin_discovery_endpoint_async(self, auth_headers):
        """POST /api/admin/companies/discovery with run_async=true should return 202"""
        response = requests.post(
            f"{BASE_URL}/api/admin/companies/discovery",
            json={"query": "Best fintech companies 2026", "limit": 3, "run_async": True, "auto_approve": False},
            headers=auth_headers
        )
        # 202 for queued async or 200 for sync
        assert response.status_code in [200, 202], f"Expected 200 or 202, got {response.status_code}: {response.text}"
        data = response.json()
        if response.status_code == 202:
            assert data.get("status") == "queued", "Should return queued status for async"
            print("PASS: Admin discovery endpoint returns 202 for async operation")
        else:
            print(f"PASS: Admin discovery completed sync - created: {data.get('created', 0)}")
    
    # ============== Public Company API Tests ==============
    
    def test_get_companies_list(self):
        """GET /api/companies should return list of companies"""
        response = requests.get(f"{BASE_URL}/api/companies?limit=20")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"PASS: GET /api/companies returns {len(data)} companies")
        return data
    
    def test_get_featured_companies(self):
        """GET /api/companies/featured/list should return featured companies"""
        response = requests.get(f"{BASE_URL}/api/companies/featured/list?limit=12")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"PASS: GET /api/companies/featured/list returns {len(data)} featured companies")
        return data
    
    def test_get_company_by_slug(self):
        """GET /api/companies/slug/{slug} should return company profile"""
        # First get a company from list
        companies_response = requests.get(f"{BASE_URL}/api/companies?limit=5")
        companies = companies_response.json()
        
        if len(companies) == 0:
            pytest.skip("No companies available to test slug endpoint")
        
        test_slug = companies[0].get("slug")
        response = requests.get(f"{BASE_URL}/api/companies/slug/{test_slug}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "company" in data, "Response should contain 'company' key"
        assert data["company"]["slug"] == test_slug, "Slug should match"
        print(f"PASS: GET /api/companies/slug/{test_slug} returns company profile")
    
    def test_get_company_by_slug_not_found(self):
        """GET /api/companies/slug/nonexistent should return 404"""
        response = requests.get(f"{BASE_URL}/api/companies/slug/nonexistent-company-12345")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: GET /api/companies/slug/nonexistent returns 404")
    
    # ============== Admin Company CRUD Tests ==============
    
    def test_admin_get_companies(self, auth_headers):
        """GET /api/admin/companies should return companies with stats"""
        response = requests.get(
            f"{BASE_URL}/api/admin/companies?limit=100",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert "items" in data, "Response should contain 'items'"
        assert "stats" in data, "Response should contain 'stats'"
        stats = data["stats"]
        assert "total" in stats, "Stats should contain 'total'"
        assert "approved" in stats, "Stats should contain 'approved'"
        assert "featured" in stats, "Stats should contain 'featured'"
        print(f"PASS: Admin companies list - total: {stats['total']}, approved: {stats['approved']}, featured: {stats['featured']}")
        return data
    
    def test_admin_approve_company(self, auth_headers):
        """POST /api/admin/companies/{id}/approve should approve company"""
        # Get companies list
        companies_response = requests.get(f"{BASE_URL}/api/admin/companies?limit=100", headers=auth_headers)
        items = companies_response.json().get("items", [])
        
        # Find unapproved company
        unapproved = [c for c in items if not c.get("is_approved")]
        if len(unapproved) == 0:
            # Find any company to test
            if len(items) == 0:
                pytest.skip("No companies available for approve test")
            test_company = items[0]
        else:
            test_company = unapproved[0]
        
        company_id = test_company["id"]
        response = requests.post(
            f"{BASE_URL}/api/admin/companies/{company_id}/approve",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"PASS: Admin approve endpoint works for company {test_company.get('name')}")
    
    def test_admin_feature_company(self, auth_headers):
        """POST /api/admin/companies/{id}/feature should toggle featured status"""
        # Get companies list
        companies_response = requests.get(f"{BASE_URL}/api/admin/companies?limit=100", headers=auth_headers)
        items = companies_response.json().get("items", [])
        
        if len(items) == 0:
            pytest.skip("No companies available for feature test")
        
        test_company = items[0]
        company_id = test_company["id"]
        current_featured = test_company.get("featured_boolean", False)
        
        response = requests.post(
            f"{BASE_URL}/api/admin/companies/{company_id}/feature",
            json={"featured": not current_featured, "reason": "test-toggle"},
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"PASS: Admin feature toggle works for company {test_company.get('name')}")
        
        # Toggle back
        requests.post(
            f"{BASE_URL}/api/admin/companies/{company_id}/feature",
            json={"featured": current_featured, "reason": "test-revert"},
            headers=auth_headers
        )
    
    def test_admin_refresh_company(self, auth_headers):
        """POST /api/admin/companies/{id}/refresh should refresh metrics"""
        # Get companies list
        companies_response = requests.get(f"{BASE_URL}/api/admin/companies?limit=10", headers=auth_headers)
        items = companies_response.json().get("items", [])
        
        if len(items) == 0:
            pytest.skip("No companies available for refresh test")
        
        test_company = items[0]
        company_id = test_company["id"]
        
        response = requests.post(
            f"{BASE_URL}/api/admin/companies/{company_id}/refresh",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"PASS: Admin refresh endpoint works for company {test_company.get('name')}")
    
    def test_admin_delete_company_unauthorized(self):
        """DELETE /api/admin/companies/{id} without token should return 401"""
        response = requests.delete(f"{BASE_URL}/api/admin/companies/some-fake-id")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("PASS: Admin delete endpoint requires authentication")
    
    # ============== Sitemap Integration Tests ==============
    
    def test_sitemap_index_contains_companies(self):
        """GET /api/sitemap.xml should contain sitemap-companies.xml reference"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "sitemap-companies.xml" in response.text, "Sitemap index should reference sitemap-companies.xml"
        print("PASS: /api/sitemap.xml contains sitemap-companies.xml reference")
    
    def test_sitemap_companies_returns_valid_xml(self):
        """GET /api/sitemap-companies.xml should return valid XML with company URLs"""
        response = requests.get(f"{BASE_URL}/api/sitemap-companies.xml")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "<?xml" in response.text or "<urlset" in response.text, "Should return valid XML"
        assert "/companies/" in response.text or "urlset" in response.text, "Should contain company URLs or empty urlset"
        print("PASS: /api/sitemap-companies.xml returns valid XML")
    
    # ============== Regression Tests ==============
    
    def test_regression_firm_page_endpoint(self):
        """Regression: GET /api/firma/{slug} should still work"""
        response = requests.get(f"{BASE_URL}/api/bonus-sites?limit=1")
        if response.status_code == 200 and len(response.json()) > 0:
            site = response.json()[0]
            slug = site.get("slug")
            if slug:
                firm_response = requests.get(f"{BASE_URL}/api/firma/{slug}")
                assert firm_response.status_code == 200, f"Firm page endpoint broken: {firm_response.status_code}"
                print(f"PASS: Regression - /api/firma/{slug} still works")
            else:
                print("SKIP: No slug available for firm page test")
        else:
            print("SKIP: No bonus sites available for regression test")
    
    def test_regression_video_endpoint(self):
        """Regression: GET /api/firma/{slug}/video should still work"""
        response = requests.get(f"{BASE_URL}/api/bonus-sites?limit=1")
        if response.status_code == 200 and len(response.json()) > 0:
            site = response.json()[0]
            slug = site.get("slug")
            if slug:
                video_response = requests.get(f"{BASE_URL}/api/firma/{slug}/video")
                assert video_response.status_code == 200, f"Video endpoint broken: {video_response.status_code}"
                print(f"PASS: Regression - /api/firma/{slug}/video still works")
            else:
                print("SKIP: No slug available for video endpoint test")
        else:
            print("SKIP: No bonus sites available for regression test")
    
    def test_regression_amp_endpoint(self):
        """Regression: GET /api/amp/{slug} should still work"""
        response = requests.get(f"{BASE_URL}/api/bonus-sites?limit=1")
        if response.status_code == 200 and len(response.json()) > 0:
            site = response.json()[0]
            slug = site.get("slug")
            if slug:
                amp_response = requests.get(f"{BASE_URL}/api/amp/{slug}")
                assert amp_response.status_code == 200, f"AMP endpoint broken: {amp_response.status_code}"
                assert "<!doctype html>" in amp_response.text.lower() or "amp" in amp_response.text.lower(), "Should return AMP HTML"
                print(f"PASS: Regression - /api/amp/{slug} still works")
            else:
                print("SKIP: No slug available for AMP endpoint test")
        else:
            print("SKIP: No bonus sites available for regression test")


class TestCompanyDataStructure:
    """Tests for company data structure and fields"""
    
    def test_company_profile_has_required_fields(self):
        """Company profile response should have all required fields"""
        # Get a company
        companies_response = requests.get(f"{BASE_URL}/api/companies?limit=1")
        companies = companies_response.json()
        
        if len(companies) == 0:
            pytest.skip("No companies available")
        
        slug = companies[0].get("slug")
        response = requests.get(f"{BASE_URL}/api/companies/slug/{slug}")
        assert response.status_code == 200
        
        data = response.json()
        company = data.get("company", {})
        
        # Check required fields
        required_fields = [
            "id", "name", "slug", "domain", "category_id", "subcategory_id",
            "description_short", "founded_year", "employee_range", "revenue_range",
            "estimated_visits", "bounce_rate", "pages_per_visit", "avg_visit_duration",
            "global_rank", "country_rank", "category_rank",
            "technologies_json", "channels_json", "tags_json",
            "intelligence_score", "seo_title", "seo_description"
        ]
        
        missing_fields = [f for f in required_fields if f not in company]
        assert len(missing_fields) == 0, f"Missing fields: {missing_fields}"
        print("PASS: Company profile has all required fields")
    
    def test_company_metrics_are_valid(self):
        """Company metrics should have valid values"""
        companies_response = requests.get(f"{BASE_URL}/api/companies?limit=1")
        companies = companies_response.json()
        
        if len(companies) == 0:
            pytest.skip("No companies available")
        
        slug = companies[0].get("slug")
        response = requests.get(f"{BASE_URL}/api/companies/slug/{slug}")
        company = response.json().get("company", {})
        
        # Check metrics are valid
        assert company.get("estimated_visits", 0) >= 0, "Visits should be non-negative"
        assert 0 <= company.get("bounce_rate", 0) <= 1, "Bounce rate should be between 0 and 1"
        assert company.get("pages_per_visit", 0) >= 0, "Pages per visit should be non-negative"
        assert company.get("global_rank", 0) >= 0, "Global rank should be non-negative"
        assert 0 <= company.get("intelligence_score", 0) <= 100, "Intelligence score should be 0-100"
        
        print(f"PASS: Company metrics are valid for {company.get('name')}")


class TestAdminRefreshMetrics:
    """Tests for admin refresh metrics endpoint"""
    
    @pytest.fixture(scope="class")
    def auth_headers(self):
        """Get admin authentication token"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "admin", "password": "123123.."},
            headers={"Content-Type": "application/json"}
        )
        token = response.json().get("token")
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    def test_admin_refresh_all_metrics(self, auth_headers):
        """POST /api/admin/companies/refresh-metrics should refresh all company metrics"""
        response = requests.post(
            f"{BASE_URL}/api/admin/companies/refresh-metrics",
            headers=auth_headers
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        # Response may have "refreshed" count
        print(f"PASS: Admin refresh-metrics endpoint works: {data}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
