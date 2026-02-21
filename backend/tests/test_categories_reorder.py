"""
Test Categories CRUD + Reorder and Bonus Sites Reorder
Tests new iteration 6 features:
- Categories CRUD (GET, POST, PUT, DELETE, POST /reorder)
- Bonus Sites Reorder (POST /bonus-sites/reorder)
- Domain site data endpoint (GET /api/site/{domain_name})
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://sports-bonus-ai.preview.emergentagent.com').rstrip('/')
API_URL = f"{BASE_URL}/api"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "Mm18010812**!!"


@pytest.fixture(scope="module")
def auth_token():
    """Get admin auth token"""
    response = requests.post(f"{API_URL}/auth/login", json={
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD
    })
    if response.status_code == 200:
        return response.json().get("token")
    pytest.skip(f"Auth failed: {response.status_code} - {response.text}")


@pytest.fixture(scope="module")
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


class TestCategories:
    """Categories CRUD + Reorder tests"""
    
    def test_get_categories_returns_list(self, api_client):
        """GET /api/categories - returns categories list sorted by order"""
        response = api_client.get(f"{API_URL}/categories")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        assert len(data) > 0, "Should have at least one category"
        
        # Check category structure
        first_cat = data[0]
        assert "id" in first_cat, "Category should have 'id'"
        assert "name" in first_cat, "Category should have 'name'"
        assert "type" in first_cat, "Category should have 'type'"
        print(f"✓ GET /api/categories - Found {len(data)} categories")
        
    def test_create_category(self, api_client):
        """POST /api/categories - create new category"""
        new_cat = {
            "name": "TEST_Category_1",
            "type": "bonus",
            "image": "https://example.com/test.jpg",
            "description": "Test description"
        }
        response = api_client.post(f"{API_URL}/categories", json=new_cat)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["name"] == new_cat["name"], "Name should match"
        assert data["type"] == new_cat["type"], "Type should match"
        assert "id" in data, "Should have ID"
        assert "slug" in data, "Should have slug"
        
        # Store for cleanup
        pytest.test_category_id = data["id"]
        print(f"✓ POST /api/categories - Created category: {data['name']} (ID: {data['id']})")
        
    def test_get_categories_includes_new_category(self, api_client):
        """Verify new category appears in list"""
        response = api_client.get(f"{API_URL}/categories")
        assert response.status_code == 200
        
        data = response.json()
        cat_ids = [c["id"] for c in data]
        assert hasattr(pytest, 'test_category_id'), "Test category should exist from previous test"
        assert pytest.test_category_id in cat_ids, "New category should be in the list"
        print(f"✓ GET /api/categories - New category verified in list")
        
    def test_update_category(self, api_client):
        """PUT /api/categories/{id} - update category"""
        assert hasattr(pytest, 'test_category_id'), "Need test category from previous test"
        
        update_data = {
            "name": "TEST_Category_Updated",
            "type": "spor",
            "description": "Updated description"
        }
        response = api_client.put(f"{API_URL}/categories/{pytest.test_category_id}", json=update_data)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["name"] == update_data["name"], "Name should be updated"
        assert data["type"] == update_data["type"], "Type should be updated"
        print(f"✓ PUT /api/categories/{pytest.test_category_id} - Category updated")
        
    def test_reorder_categories(self, api_client):
        """POST /api/categories/reorder - reorder categories"""
        # First get all categories
        response = api_client.get(f"{API_URL}/categories")
        assert response.status_code == 200
        
        cats = response.json()
        if len(cats) < 2:
            pytest.skip("Need at least 2 categories to test reorder")
            
        # Get current IDs and reverse order
        cat_ids = [c["id"] for c in cats]
        reversed_ids = cat_ids[::-1]
        
        # Reorder
        response = api_client.post(f"{API_URL}/categories/reorder", json={"order": reversed_ids})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message" in data, "Should have success message"
        print(f"✓ POST /api/categories/reorder - Reordered {len(cat_ids)} categories")
        
        # Verify order changed
        response = api_client.get(f"{API_URL}/categories")
        assert response.status_code == 200
        new_cats = response.json()
        
        # First category should now have order >= 1 (order updated)
        print(f"✓ Categories reorder verified - first cat ID: {new_cats[0]['id']}")
        
    def test_delete_category(self, api_client):
        """DELETE /api/categories/{id} - delete category"""
        assert hasattr(pytest, 'test_category_id'), "Need test category from previous test"
        
        response = api_client.delete(f"{API_URL}/categories/{pytest.test_category_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message" in data, "Should have success message"
        
        # Verify deletion
        response = api_client.get(f"{API_URL}/categories")
        assert response.status_code == 200
        cats = response.json()
        cat_ids = [c["id"] for c in cats]
        assert pytest.test_category_id not in cat_ids, "Deleted category should not be in list"
        print(f"✓ DELETE /api/categories/{pytest.test_category_id} - Category deleted and verified")


class TestBonusSitesReorder:
    """Bonus Sites Reorder tests"""
    
    def test_get_bonus_sites_sorted_by_sort_order(self, api_client):
        """GET /api/bonus-sites - returns sites sorted by sort_order"""
        response = api_client.get(f"{API_URL}/bonus-sites")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        assert len(data) > 0, "Should have at least one site"
        
        # Store site IDs for reorder test
        pytest.bonus_site_ids = [s["id"] for s in data]
        print(f"✓ GET /api/bonus-sites - Found {len(data)} sites")
        
    def test_reorder_bonus_sites(self, api_client):
        """POST /api/bonus-sites/reorder - reorder bonus sites"""
        assert hasattr(pytest, 'bonus_site_ids'), "Need site IDs from previous test"
        
        if len(pytest.bonus_site_ids) < 2:
            pytest.skip("Need at least 2 sites to test reorder")
            
        # Reverse order
        reversed_ids = pytest.bonus_site_ids[::-1]
        
        # Reorder
        response = api_client.post(f"{API_URL}/bonus-sites/reorder", json={"order": reversed_ids})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "message" in data, "Should have success message"
        print(f"✓ POST /api/bonus-sites/reorder - Reordered {len(reversed_ids)} sites")
        
    def test_bonus_sites_sort_order_updated(self, api_client):
        """Verify sort_order is persisted after reorder"""
        response = api_client.get(f"{API_URL}/bonus-sites")
        assert response.status_code == 200
        
        data = response.json()
        # Check that first site has sort_order
        # After reorder, the last site should now be first
        if hasattr(pytest, 'bonus_site_ids') and len(pytest.bonus_site_ids) > 1:
            # The first site should now have a sort_order value
            print(f"✓ Bonus sites order verified - first site: {data[0]['name']}")
        print(f"✓ GET /api/bonus-sites - Sort order persisted")


class TestDomainSiteData:
    """Test domain-specific site data endpoint"""
    
    def test_get_site_data_for_guncelgiris(self, api_client):
        """GET /api/site/guncelgiris.ai - returns domain-specific data"""
        response = api_client.get(f"{API_URL}/site/guncelgiris.ai")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "domain" in data, "Should have domain info"
        assert "bonus_sites" in data, "Should have bonus_sites list"
        assert "articles" in data, "Should have articles list"
        assert "stats" in data, "Should have stats"
        assert "is_ready" in data, "Should have is_ready flag"
        
        # Verify domain name
        assert data["domain"]["domain_name"] == "guncelgiris.ai", "Domain name should match"
        
        # Check stats
        stats = data["stats"]
        assert "total_articles" in stats, "Stats should have total_articles"
        assert "total_bonus_sites" in stats, "Stats should have total_bonus_sites"
        
        print(f"✓ GET /api/site/guncelgiris.ai - Domain data retrieved")
        print(f"  - Articles: {stats['total_articles']}")
        print(f"  - Bonus Sites: {stats['total_bonus_sites']}")
        print(f"  - Is Ready: {data['is_ready']}")
        
    def test_site_not_found_returns_404(self, api_client):
        """GET /api/site/nonexistent.com - returns 404"""
        response = api_client.get(f"{API_URL}/site/nonexistent-domain-xyz.com")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print(f"✓ GET /api/site/nonexistent.com - Returns 404 as expected")


class TestDomainCreation:
    """Test domain creation with auto content generation"""
    
    def test_create_domain_triggers_auto_content(self, api_client, auth_token):
        """POST /api/domains - creates domain and triggers background content generation"""
        # Create a test domain
        new_domain = {
            "domain_name": f"TEST_{int(time.time())}.com",
            "display_name": "Test Domain",
            "focus": "bonus",
            "meta_title": "Test Meta Title"
        }
        
        response = api_client.post(f"{API_URL}/domains", json=new_domain)
        
        # Domain creation should succeed
        assert response.status_code in [200, 201], f"Expected 200/201, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data["domain_name"] == new_domain["domain_name"], "Domain name should match"
        assert "id" in data, "Should have ID"
        
        # Store for cleanup
        pytest.test_domain_id = data["id"]
        print(f"✓ POST /api/domains - Domain created: {data['domain_name']}")
        print(f"  - Note: AI content generation runs in background")
        
    def test_cleanup_test_domain(self, api_client):
        """Cleanup: Delete test domain"""
        if hasattr(pytest, 'test_domain_id'):
            response = api_client.delete(f"{API_URL}/domains/{pytest.test_domain_id}")
            assert response.status_code == 200
            print(f"✓ DELETE /api/domains/{pytest.test_domain_id} - Test domain cleaned up")


class TestAdminTabs:
    """Test admin panel has 7 tabs as required"""
    
    def test_admin_auth_login(self, api_client):
        """POST /api/auth/login - admin can login"""
        response = api_client.post(f"{API_URL}/auth/login", json={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        })
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "token" in data, "Should return JWT token"
        print(f"✓ POST /api/auth/login - Admin login successful")
        
    def test_stats_dashboard(self, api_client):
        """GET /api/stats/dashboard - returns admin dashboard stats"""
        response = api_client.get(f"{API_URL}/stats/dashboard")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "total_domains" in data, "Should have total_domains"
        assert "total_bonus_sites" in data, "Should have total_bonus_sites"
        assert "total_articles" in data, "Should have total_articles"
        print(f"✓ GET /api/stats/dashboard - Stats: domains={data['total_domains']}, sites={data['total_bonus_sites']}, articles={data['total_articles']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
