"""
Admin Panel CRUD Operations Test Suite
Tests all CRUD endpoints for:
- Bonus Sites (PUT, DELETE)
- Articles (POST, PUT, DELETE, GET single, GET search)
- Domains (PUT, DELETE)
"""

import pytest
import requests
import os
import uuid
from datetime import datetime

# Use the production URL from environment
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://sports-bonus-hub-1.preview.emergentagent.com').rstrip('/')

class TestBonusSitesCRUD:
    """Test Bonus Sites CRUD operations - focus on PUT and DELETE"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Get existing bonus sites for testing"""
        self.api = requests.Session()
        self.api.headers.update({"Content-Type": "application/json"})
    
    def test_get_bonus_sites(self):
        """GET /api/bonus-sites - Verify endpoint returns data"""
        response = self.api.get(f"{BASE_URL}/api/bonus-sites")
        assert response.status_code == 200, f"Failed: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Expected list of bonus sites"
        print(f"✓ GET /api/bonus-sites - Found {len(data)} sites")
    
    def test_create_bonus_site(self):
        """POST /api/bonus-sites - Create new site for testing"""
        test_site = {
            "name": f"TEST_Site_{uuid.uuid4().hex[:8]}",
            "logo_url": "https://example.com/logo.png",
            "bonus_type": "deneme",
            "bonus_amount": "500 TL",
            "affiliate_url": "https://example.com/affiliate",
            "rating": 4.5,
            "features": ["Hızlı Ödeme", "7/24 Destek"],
            "turnover_requirement": 10
        }
        response = self.api.post(f"{BASE_URL}/api/bonus-sites", json=test_site)
        assert response.status_code == 200, f"Failed to create: {response.text}"
        
        data = response.json()
        assert data["name"] == test_site["name"]
        assert data["bonus_type"] == "deneme"
        assert "id" in data
        
        # Store for cleanup
        self.created_site_id = data["id"]
        print(f"✓ POST /api/bonus-sites - Created site: {data['id']}")
        return data["id"]
    
    def test_update_bonus_site(self):
        """PUT /api/bonus-sites/{id} - Update a bonus site"""
        # First create a site
        test_site = {
            "name": f"TEST_UpdateSite_{uuid.uuid4().hex[:8]}",
            "logo_url": "https://example.com/logo.png",
            "bonus_type": "deneme",
            "bonus_amount": "500 TL",
            "affiliate_url": "https://example.com/affiliate",
            "rating": 4.5,
            "features": ["Feature1"],
            "turnover_requirement": 10
        }
        create_response = self.api.post(f"{BASE_URL}/api/bonus-sites", json=test_site)
        assert create_response.status_code == 200, f"Create failed: {create_response.text}"
        site_id = create_response.json()["id"]
        
        # Update the site
        update_data = {
            "name": "TEST_UpdatedName",
            "bonus_type": "hosgeldin",
            "bonus_amount": "1000 TL",
            "rating": 4.8,
            "features": "Updated Feature1, Updated Feature2"  # String to test conversion
        }
        update_response = self.api.put(f"{BASE_URL}/api/bonus-sites/{site_id}", json=update_data)
        assert update_response.status_code == 200, f"Update failed: {update_response.text}"
        
        updated = update_response.json()
        assert updated["name"] == "TEST_UpdatedName"
        assert updated["bonus_type"] == "hosgeldin"
        assert updated["bonus_amount"] == "1000 TL"
        assert updated["rating"] == 4.8
        print(f"✓ PUT /api/bonus-sites/{site_id} - Site updated successfully")
        
        # Verify via GET
        get_response = self.api.get(f"{BASE_URL}/api/bonus-sites")
        assert get_response.status_code == 200
        sites = get_response.json()
        found = next((s for s in sites if s["id"] == site_id), None)
        assert found is not None
        assert found["name"] == "TEST_UpdatedName"
        print(f"✓ Verified update persisted in database")
        
        # Cleanup
        self.api.delete(f"{BASE_URL}/api/bonus-sites/{site_id}")
    
    def test_delete_bonus_site(self):
        """DELETE /api/bonus-sites/{id} - Delete a bonus site"""
        # First create a site
        test_site = {
            "name": f"TEST_DeleteSite_{uuid.uuid4().hex[:8]}",
            "logo_url": "",
            "bonus_type": "deneme",
            "bonus_amount": "300 TL",
            "affiliate_url": "https://example.com",
            "rating": 4.0,
            "features": [],
            "turnover_requirement": 10
        }
        create_response = self.api.post(f"{BASE_URL}/api/bonus-sites", json=test_site)
        assert create_response.status_code == 200
        site_id = create_response.json()["id"]
        site_name = test_site["name"]
        
        # Delete the site
        delete_response = self.api.delete(f"{BASE_URL}/api/bonus-sites/{site_id}")
        assert delete_response.status_code == 200, f"Delete failed: {delete_response.text}"
        
        data = delete_response.json()
        assert data.get("message") == "Site deleted"
        print(f"✓ DELETE /api/bonus-sites/{site_id} - Site deleted")
        
        # Verify deletion
        get_response = self.api.get(f"{BASE_URL}/api/bonus-sites")
        sites = get_response.json()
        found = next((s for s in sites if s["id"] == site_id), None)
        assert found is None, "Site should have been deleted"
        print(f"✓ Verified site no longer exists in database")


class TestArticlesCRUD:
    """Test Articles CRUD operations - POST, PUT, DELETE, GET single, search"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup API client"""
        self.api = requests.Session()
        self.api.headers.update({"Content-Type": "application/json"})
    
    def test_create_article(self):
        """POST /api/articles - Create new article"""
        test_article = {
            "title": f"TEST_Article_{uuid.uuid4().hex[:8]}",
            "content": "Bu bir test makalesidir. İçerik burada yer alır.",
            "category": "bonus",
            "seo_title": "Test SEO Title",
            "seo_description": "Test SEO description for the article",
            "tags": ["test", "bonus", "article"],
            "is_published": True
        }
        response = self.api.post(f"{BASE_URL}/api/articles", json=test_article)
        assert response.status_code == 200, f"Failed to create: {response.text}"
        
        data = response.json()
        assert data["title"] == test_article["title"]
        assert data["category"] == "bonus"
        assert "id" in data
        assert "slug" in data  # Auto-generated
        print(f"✓ POST /api/articles - Created article: {data['id']}")
        
        # Store for later tests
        self.created_article_id = data["id"]
        return data["id"]
    
    def test_create_article_without_title_fails(self):
        """POST /api/articles - Should fail without title"""
        test_article = {
            "content": "Content without title",
            "category": "bonus"
        }
        response = self.api.post(f"{BASE_URL}/api/articles", json=test_article)
        assert response.status_code == 400, f"Expected 400 error but got {response.status_code}"
        print(f"✓ POST /api/articles without title - Returns 400 as expected")
    
    def test_get_single_article(self):
        """GET /api/articles/{id} - Get single article by ID"""
        # First create
        test_article = {
            "title": f"TEST_SingleArticle_{uuid.uuid4().hex[:8]}",
            "content": "Single article content",
            "category": "rehber",
            "tags": ["test"]
        }
        create_resp = self.api.post(f"{BASE_URL}/api/articles", json=test_article)
        assert create_resp.status_code == 200
        article_id = create_resp.json()["id"]
        
        # Get single article
        get_resp = self.api.get(f"{BASE_URL}/api/articles/{article_id}")
        assert get_resp.status_code == 200, f"Failed to get: {get_resp.text}"
        
        data = get_resp.json()
        assert data["id"] == article_id
        assert data["title"] == test_article["title"]
        print(f"✓ GET /api/articles/{article_id} - Retrieved article successfully")
        
        # Cleanup
        self.api.delete(f"{BASE_URL}/api/articles/{article_id}")
    
    def test_get_nonexistent_article(self):
        """GET /api/articles/{id} - Should return 404 for invalid ID"""
        fake_id = str(uuid.uuid4())
        get_resp = self.api.get(f"{BASE_URL}/api/articles/{fake_id}")
        assert get_resp.status_code == 404, f"Expected 404 but got {get_resp.status_code}"
        print(f"✓ GET /api/articles/<invalid-id> - Returns 404 as expected")
    
    def test_update_article(self):
        """PUT /api/articles/{id} - Update article"""
        # Create article
        test_article = {
            "title": f"TEST_UpdateArticle_{uuid.uuid4().hex[:8]}",
            "content": "Original content",
            "category": "bonus",
            "tags": ["original"]
        }
        create_resp = self.api.post(f"{BASE_URL}/api/articles", json=test_article)
        assert create_resp.status_code == 200
        article_id = create_resp.json()["id"]
        
        # Update article
        update_data = {
            "title": "TEST_UpdatedArticleTitle",
            "content": "Updated content with more details",
            "category": "spor",
            "seo_title": "Updated SEO Title",
            "tags": "updated, tag1, tag2",  # String to test conversion
            "is_published": False
        }
        update_resp = self.api.put(f"{BASE_URL}/api/articles/{article_id}", json=update_data)
        assert update_resp.status_code == 200, f"Update failed: {update_resp.text}"
        
        updated = update_resp.json()
        assert updated["title"] == "TEST_UpdatedArticleTitle"
        assert updated["category"] == "spor"
        assert updated["content"] == "Updated content with more details"
        print(f"✓ PUT /api/articles/{article_id} - Article updated successfully")
        
        # Verify via GET
        verify_resp = self.api.get(f"{BASE_URL}/api/articles/{article_id}")
        assert verify_resp.status_code == 200
        verified = verify_resp.json()
        assert verified["title"] == "TEST_UpdatedArticleTitle"
        print(f"✓ Verified article update persisted")
        
        # Cleanup
        self.api.delete(f"{BASE_URL}/api/articles/{article_id}")
    
    def test_delete_article(self):
        """DELETE /api/articles/{id} - Delete article"""
        # Create article
        test_article = {
            "title": f"TEST_DeleteArticle_{uuid.uuid4().hex[:8]}",
            "content": "Article to be deleted",
            "category": "haber"
        }
        create_resp = self.api.post(f"{BASE_URL}/api/articles", json=test_article)
        assert create_resp.status_code == 200
        article_id = create_resp.json()["id"]
        
        # Delete article
        delete_resp = self.api.delete(f"{BASE_URL}/api/articles/{article_id}")
        assert delete_resp.status_code == 200, f"Delete failed: {delete_resp.text}"
        
        data = delete_resp.json()
        assert data.get("message") == "Makale silindi"
        print(f"✓ DELETE /api/articles/{article_id} - Article deleted")
        
        # Verify deletion
        verify_resp = self.api.get(f"{BASE_URL}/api/articles/{article_id}")
        assert verify_resp.status_code == 404
        print(f"✓ Verified article no longer exists")
    
    def test_search_articles(self):
        """GET /api/articles?search=test - Search articles"""
        # Create searchable article
        unique_term = f"SEARCHTERM_{uuid.uuid4().hex[:8]}"
        test_article = {
            "title": f"Article with {unique_term}",
            "content": "Searchable content",
            "category": "bonus"
        }
        create_resp = self.api.post(f"{BASE_URL}/api/articles", json=test_article)
        assert create_resp.status_code == 200
        article_id = create_resp.json()["id"]
        
        # Search for the article
        search_resp = self.api.get(f"{BASE_URL}/api/articles", params={"search": unique_term})
        assert search_resp.status_code == 200
        
        results = search_resp.json()
        assert isinstance(results, list)
        assert any(unique_term in a.get("title", "") for a in results)
        print(f"✓ GET /api/articles?search={unique_term} - Search works")
        
        # Cleanup
        self.api.delete(f"{BASE_URL}/api/articles/{article_id}")
    
    def test_filter_articles_by_category(self):
        """GET /api/articles?category=bonus - Filter by category"""
        # Create article with specific category
        test_article = {
            "title": f"TEST_CategoryArticle_{uuid.uuid4().hex[:8]}",
            "content": "Category test content",
            "category": "rehber"
        }
        create_resp = self.api.post(f"{BASE_URL}/api/articles", json=test_article)
        assert create_resp.status_code == 200
        article_id = create_resp.json()["id"]
        
        # Filter by category
        filter_resp = self.api.get(f"{BASE_URL}/api/articles", params={"category": "rehber"})
        assert filter_resp.status_code == 200
        
        results = filter_resp.json()
        assert all(a.get("category") == "rehber" for a in results)
        print(f"✓ GET /api/articles?category=rehber - Category filter works")
        
        # Cleanup
        self.api.delete(f"{BASE_URL}/api/articles/{article_id}")


class TestDomainsCRUD:
    """Test Domains CRUD operations - PUT, DELETE"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup API client"""
        self.api = requests.Session()
        self.api.headers.update({"Content-Type": "application/json"})
    
    def test_get_domains(self):
        """GET /api/domains - Get all domains"""
        response = self.api.get(f"{BASE_URL}/api/domains")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ GET /api/domains - Found {len(data)} domains")
    
    def test_create_domain(self):
        """POST /api/domains - Create new domain"""
        test_domain = {
            "domain_name": f"test-{uuid.uuid4().hex[:8]}.com",
            "display_name": "Test Domain",
            "focus": "bonus",
            "meta_title": "Test Domain Meta Title"
        }
        response = self.api.post(f"{BASE_URL}/api/domains", json=test_domain)
        assert response.status_code == 200, f"Failed to create: {response.text}"
        
        data = response.json()
        assert data["domain_name"] == test_domain["domain_name"]
        assert data["display_name"] == "Test Domain"
        assert data["focus"] == "bonus"
        assert "id" in data
        print(f"✓ POST /api/domains - Created domain: {data['id']}")
        
        return data["id"]
    
    def test_update_domain(self):
        """PUT /api/domains/{id} - Update domain"""
        # Create domain
        test_domain = {
            "domain_name": f"update-test-{uuid.uuid4().hex[:8]}.com",
            "display_name": "Original Name",
            "focus": "bonus",
            "meta_title": "Original Title"
        }
        create_resp = self.api.post(f"{BASE_URL}/api/domains", json=test_domain)
        assert create_resp.status_code == 200
        domain_id = create_resp.json()["id"]
        
        # Update domain
        update_data = {
            "display_name": "Updated Display Name",
            "focus": "spor",
            "meta_title": "Updated Meta Title"
        }
        update_resp = self.api.put(f"{BASE_URL}/api/domains/{domain_id}", json=update_data)
        assert update_resp.status_code == 200, f"Update failed: {update_resp.text}"
        
        updated = update_resp.json()
        assert updated["display_name"] == "Updated Display Name"
        assert updated["focus"] == "spor"
        assert updated["meta_title"] == "Updated Meta Title"
        print(f"✓ PUT /api/domains/{domain_id} - Domain updated successfully")
        
        # Verify via GET
        get_resp = self.api.get(f"{BASE_URL}/api/domains/{domain_id}")
        assert get_resp.status_code == 200
        verified = get_resp.json()
        assert verified["display_name"] == "Updated Display Name"
        print(f"✓ Verified domain update persisted")
        
        # Cleanup
        self.api.delete(f"{BASE_URL}/api/domains/{domain_id}")
    
    def test_delete_domain(self):
        """DELETE /api/domains/{id} - Delete domain"""
        # Create domain
        test_domain = {
            "domain_name": f"delete-test-{uuid.uuid4().hex[:8]}.com",
            "display_name": "Domain To Delete",
            "focus": "bonus"
        }
        create_resp = self.api.post(f"{BASE_URL}/api/domains", json=test_domain)
        assert create_resp.status_code == 200
        domain_id = create_resp.json()["id"]
        
        # Delete domain
        delete_resp = self.api.delete(f"{BASE_URL}/api/domains/{domain_id}")
        assert delete_resp.status_code == 200, f"Delete failed: {delete_resp.text}"
        
        data = delete_resp.json()
        assert data.get("message") == "Domain deleted"
        print(f"✓ DELETE /api/domains/{domain_id} - Domain deleted")
        
        # Verify deletion
        verify_resp = self.api.get(f"{BASE_URL}/api/domains/{domain_id}")
        assert verify_resp.status_code == 404
        print(f"✓ Verified domain no longer exists")
    
    def test_create_duplicate_domain_fails(self):
        """POST /api/domains - Should fail for duplicate domain"""
        unique_name = f"unique-{uuid.uuid4().hex[:8]}.com"
        test_domain = {
            "domain_name": unique_name,
            "display_name": "First Domain",
            "focus": "bonus"
        }
        
        # Create first
        create_resp1 = self.api.post(f"{BASE_URL}/api/domains", json=test_domain)
        assert create_resp1.status_code == 200
        domain_id = create_resp1.json()["id"]
        
        # Try to create duplicate
        test_domain["display_name"] = "Second Domain"
        create_resp2 = self.api.post(f"{BASE_URL}/api/domains", json=test_domain)
        assert create_resp2.status_code == 400, f"Expected 400 for duplicate, got {create_resp2.status_code}"
        print(f"✓ POST /api/domains with duplicate name - Returns 400 as expected")
        
        # Cleanup
        self.api.delete(f"{BASE_URL}/api/domains/{domain_id}")


class TestAutoContent:
    """Test Auto Content Generation endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup API client"""
        self.api = requests.Session()
        self.api.headers.update({"Content-Type": "application/json"})
    
    def test_generate_article(self):
        """POST /api/auto-content/generate-article - Generate AI article"""
        response = self.api.post(
            f"{BASE_URL}/api/auto-content/generate-article",
            params={"topic": "Test Article Topic 2026"}
        )
        # Should return 200 with status
        assert response.status_code == 200, f"Failed: {response.text}"
        
        data = response.json()
        assert "status" in data  # Either 'created' or 'skipped'
        print(f"✓ POST /api/auto-content/generate-article - Status: {data.get('status')}")


class TestAdminAPIStatus:
    """Test Admin API Status endpoint"""
    
    def test_api_status(self):
        """GET /api/admin/api-status - Check API health status"""
        api = requests.Session()
        response = api.get(f"{BASE_URL}/api/admin/api-status")
        assert response.status_code == 200
        
        data = response.json()
        assert "odds_api_configured" in data
        assert "cache_age_seconds" in data
        assert "ai_insight_enabled" in data
        print(f"✓ GET /api/admin/api-status - API status retrieved")
        print(f"  - Odds API configured: {data['odds_api_configured']}")
        print(f"  - AI insight enabled: {data['ai_insight_enabled']}")


# Cleanup helper to remove test data
def cleanup_test_data():
    """Remove all TEST_ prefixed data"""
    api = requests.Session()
    api.headers.update({"Content-Type": "application/json"})
    
    # Cleanup bonus sites
    sites = api.get(f"{BASE_URL}/api/bonus-sites").json()
    for site in sites:
        if site.get("name", "").startswith("TEST_"):
            api.delete(f"{BASE_URL}/api/bonus-sites/{site['id']}")
    
    # Cleanup articles
    articles = api.get(f"{BASE_URL}/api/articles").json()
    for article in articles:
        if article.get("title", "").startswith("TEST_"):
            api.delete(f"{BASE_URL}/api/articles/{article['id']}")
    
    # Cleanup domains
    domains = api.get(f"{BASE_URL}/api/domains").json()
    for domain in domains:
        if "test" in domain.get("domain_name", "").lower():
            api.delete(f"{BASE_URL}/api/domains/{domain['id']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
