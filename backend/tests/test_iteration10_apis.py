"""
Test Iteration 10 - Comprehensive API Tests
Testing all features required for production deployment
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://bonus-hub-staging.preview.emergentagent.com')

class TestHealthEndpoints:
    """Health check and API root endpoints"""
    
    def test_api_root(self):
        """Test /api/ endpoint"""
        response = requests.get(f"{BASE_URL}/api/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert data["version"] == "3.0.0"
        print("✓ API root check passed")
    
    def test_api_status(self):
        """Test /api/admin/api-status endpoint"""
        response = requests.get(f"{BASE_URL}/api/admin/api-status")
        assert response.status_code == 200
        data = response.json()
        # This endpoint returns sports cache status, not api_healthy
        assert "ai_insight_enabled" in data
        print(f"✓ API status: ai_enabled={data['ai_insight_enabled']}")


class TestArticlesAPI:
    """Article listing and details API tests"""
    
    def test_articles_list(self):
        """Test GET /api/articles?limit=6"""
        response = requests.get(f"{BASE_URL}/api/articles?limit=6")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 6
        if data:
            assert "title" in data[0]
            assert "slug" in data[0]
        print(f"✓ Articles list returned {len(data)} items")
    
    def test_latest_articles(self):
        """Test GET /api/articles/latest?limit=8"""
        response = requests.get(f"{BASE_URL}/api/articles/latest?limit=8")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 8
        if data:
            assert "title" in data[0]
            assert "is_published" not in data[0] or data[0].get("is_published") == True
        print(f"✓ Latest articles returned {len(data)} items")
    
    def test_article_by_slug(self):
        """Test GET /api/articles/slug/{slug}"""
        # First get an article to get a valid slug
        list_response = requests.get(f"{BASE_URL}/api/articles?limit=1")
        assert list_response.status_code == 200
        articles = list_response.json()
        if articles:
            slug = articles[0]["slug"]
            response = requests.get(f"{BASE_URL}/api/articles/slug/{slug}")
            assert response.status_code == 200
            data = response.json()
            assert data["slug"] == slug
            assert "content" in data
            print(f"✓ Article detail by slug works: {slug[:50]}...")
        else:
            pytest.skip("No articles available")


class TestBonusSitesAPI:
    """Bonus sites (firms) API tests"""
    
    def test_bonus_sites_list(self):
        """Test GET /api/bonus-sites?limit=20"""
        response = requests.get(f"{BASE_URL}/api/bonus-sites?limit=20")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 20
        if data:
            site = data[0]
            assert "name" in site
            assert "bonus_amount" in site
            assert "affiliate_url" in site
        print(f"✓ Bonus sites returned {len(data)} items")
    
    def test_firma_detail_maxwin(self):
        """Test GET /api/firma/maxwin"""
        response = requests.get(f"{BASE_URL}/api/firma/maxwin")
        assert response.status_code == 200
        data = response.json()
        assert "site" in data
        assert "articles" in data
        assert "similar_sites" in data
        assert data["site"]["name"].lower().replace(" ", "") in ["maxwin"]
        print(f"✓ Firma detail works: {data['site']['name']}, {len(data['articles'])} articles")
    
    def test_firma_detail_not_found(self):
        """Test GET /api/firma/{invalid_slug}"""
        response = requests.get(f"{BASE_URL}/api/firma/invalid-slug-that-does-not-exist-12345")
        assert response.status_code == 404
        print("✓ Firma not found returns 404")


class TestCategoriesAPI:
    """Categories API tests"""
    
    def test_categories_list(self):
        """Test GET /api/categories"""
        response = requests.get(f"{BASE_URL}/api/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if data:
            category = data[0]
            assert "name" in category
            assert "slug" in category
            assert "type" in category
        print(f"✓ Categories returned {len(data)} items")


class TestSchedulerAPI:
    """Scheduler status API tests"""
    
    def test_scheduler_status(self):
        """Test GET /api/scheduler/status"""
        response = requests.get(f"{BASE_URL}/api/scheduler/status")
        assert response.status_code == 200
        data = response.json()
        assert "is_running" in data
        assert "pending_items" in data
        assert "completed_items" in data
        print(f"✓ Scheduler status: pending={data['pending_items']}, completed={data['completed_items']}")


class TestAdminAuth:
    """Admin authentication tests"""
    
    def test_admin_login_success(self):
        """Test POST /api/auth/login with valid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "admin", "password": "123123.."}
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert "username" in data
        assert data["username"] == "admin"
        print(f"✓ Admin login success, token received")
    
    def test_admin_login_invalid(self):
        """Test POST /api/auth/login with invalid credentials"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "admin", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        print("✓ Invalid login returns 401")


class TestDomainAPI:
    """Domain management API tests"""
    
    def test_domains_list(self):
        """Test GET /api/domains"""
        response = requests.get(f"{BASE_URL}/api/domains")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Domains list returned {len(data)} items")


class TestContentQueueAPI:
    """Content queue API tests"""
    
    def test_content_queue_list(self):
        """Test GET /api/content-queue"""
        response = requests.get(f"{BASE_URL}/api/content-queue")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "stats" in data
        print(f"✓ Content queue: pending={data['stats']['pending']}, completed={data['stats']['completed']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
