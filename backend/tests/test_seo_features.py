"""
SEO Feature Tests - Iteration 7
Testing: sitemap.xml, robots.txt, seo-data endpoint, article slug endpoint
"""
import pytest
import requests
import os
import xml.etree.ElementTree as ET

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSitemapXml:
    """Tests for GET /api/sitemap.xml"""
    
    def test_sitemap_returns_valid_xml(self):
        """Sitemap should return valid XML with 200 status"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "application/xml" in response.headers.get("Content-Type", ""), "Content-Type should be application/xml"
        
        # Parse XML to verify validity
        try:
            root = ET.fromstring(response.text)
            assert root.tag.endswith("urlset"), f"Root element should be urlset, got {root.tag}"
            print(f"Sitemap XML valid with root tag: {root.tag}")
        except ET.ParseError as e:
            pytest.fail(f"Invalid XML: {e}")
    
    def test_sitemap_contains_static_pages(self):
        """Sitemap should contain static pages: /, /deneme-bonusu, /hosgeldin-bonusu, /spor-haberleri"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200
        
        # Check for static pages
        static_pages = ["/deneme-bonusu", "/hosgeldin-bonusu", "/spor-haberleri"]
        for page in static_pages:
            assert page in response.text, f"Sitemap should contain {page}"
        print(f"Sitemap contains all static pages: {static_pages}")
    
    def test_sitemap_contains_articles(self):
        """Sitemap should contain article URLs with /makale/ prefix"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200
        
        assert "/makale/" in response.text, "Sitemap should contain article URLs with /makale/ prefix"
        print("Sitemap contains article URLs")
    
    def test_sitemap_contains_categories(self):
        """Sitemap should contain category URLs with /bonus/ prefix"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200
        
        assert "/bonus/" in response.text, "Sitemap should contain category URLs with /bonus/ prefix"
        print("Sitemap contains category URLs")


class TestRobotsTxt:
    """Tests for GET /api/robots.txt"""
    
    def test_robots_txt_returns_200(self):
        """Robots.txt should return 200 with text/plain content type"""
        response = requests.get(f"{BASE_URL}/api/robots.txt")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "text/plain" in response.headers.get("Content-Type", ""), "Content-Type should be text/plain"
        print("Robots.txt returns 200 with correct content type")
    
    def test_robots_contains_user_agent(self):
        """Robots.txt should contain User-agent directive"""
        response = requests.get(f"{BASE_URL}/api/robots.txt")
        assert response.status_code == 200
        assert "User-agent:" in response.text, "Robots.txt should contain User-agent directive"
        print("Robots.txt contains User-agent directive")
    
    def test_robots_disallows_admin(self):
        """Robots.txt should disallow /admin and /api/ paths"""
        response = requests.get(f"{BASE_URL}/api/robots.txt")
        assert response.status_code == 200
        assert "Disallow: /admin" in response.text, "Robots.txt should disallow /admin"
        assert "Disallow: /api/" in response.text, "Robots.txt should disallow /api/"
        print("Robots.txt disallows /admin and /api/")
    
    def test_robots_contains_sitemap_reference(self):
        """Robots.txt should contain Sitemap reference"""
        response = requests.get(f"{BASE_URL}/api/robots.txt")
        assert response.status_code == 200
        assert "Sitemap:" in response.text, "Robots.txt should contain Sitemap reference"
        assert "/api/sitemap.xml" in response.text, "Robots.txt should reference sitemap.xml"
        print("Robots.txt contains sitemap reference")


class TestSeoDataEndpoint:
    """Tests for GET /api/seo-data/{slug}"""
    
    def test_seo_data_for_article(self):
        """SEO data should return article metadata for existing article slug"""
        # Use known article slug
        slug = "canli-bahis-bonuslari-ve-promosyonlar"
        response = requests.get(f"{BASE_URL}/api/seo-data/{slug}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("type") == "article", f"Type should be 'article', got {data.get('type')}"
        assert "title" in data, "Response should contain title"
        assert "description" in data, "Response should contain description"
        assert "published_time" in data, "Response should contain published_time"
        assert "schema_type" in data, "Response should contain schema_type"
        print(f"SEO data for article: type={data['type']}, schema_type={data.get('schema_type')}")
    
    def test_seo_data_for_nonexistent_slug(self):
        """SEO data should return page type for non-existent slug"""
        response = requests.get(f"{BASE_URL}/api/seo-data/nonexistent-slug-12345")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("type") == "page", f"Type should be 'page' for non-existent slug, got {data.get('type')}"
        print(f"SEO data for non-existent slug returns type=page")


class TestArticleSlugEndpoint:
    """Tests for GET /api/articles/slug/{slug}"""
    
    def test_article_slug_returns_article(self):
        """Article slug endpoint should return article data"""
        slug = "canli-bahis-bonuslari-ve-promosyonlar"
        response = requests.get(f"{BASE_URL}/api/articles/slug/{slug}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("slug") == slug, f"Slug should be {slug}, got {data.get('slug')}"
        assert "title" in data, "Response should contain title"
        assert "content" in data, "Response should contain content"
        assert "view_count" in data, "Response should contain view_count"
        print(f"Article slug endpoint returned: title='{data.get('title')[:40]}...', view_count={data.get('view_count')}")
    
    def test_article_slug_increments_view_count(self):
        """Article slug endpoint should increment view_count"""
        slug = "canli-bahis-bonuslari-ve-promosyonlar"
        
        # Get initial view count
        response1 = requests.get(f"{BASE_URL}/api/articles/slug/{slug}")
        assert response1.status_code == 200
        initial_count = response1.json().get("view_count", 0)
        
        # Request again
        response2 = requests.get(f"{BASE_URL}/api/articles/slug/{slug}")
        assert response2.status_code == 200
        new_count = response2.json().get("view_count", 0)
        
        assert new_count > initial_count, f"View count should increment. Initial: {initial_count}, New: {new_count}"
        print(f"View count incremented: {initial_count} -> {new_count}")
    
    def test_article_slug_returns_404_for_nonexistent(self):
        """Article slug endpoint should return 404 for non-existent slug"""
        response = requests.get(f"{BASE_URL}/api/articles/slug/nonexistent-article-12345")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("Article slug endpoint returns 404 for non-existent article")


class TestHealthEndpoints:
    """Tests for health check endpoints"""
    
    def test_health_endpoint(self):
        """Health endpoint should return 200"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("status") == "ok", f"Status should be 'ok', got {data.get('status')}"
        print("Health endpoint returns ok")
    
    def test_db_check_endpoint(self):
        """DB check endpoint should return database status"""
        response = requests.get(f"{BASE_URL}/db-check")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        assert data.get("status") == "connected", f"DB status should be 'connected', got {data.get('status')}"
        print(f"DB check: status={data.get('status')}, latency={data.get('latency_ms')}ms")


class TestArticlesEndpoint:
    """Tests for article list endpoint"""
    
    def test_articles_list(self):
        """Articles endpoint should return list of articles"""
        response = requests.get(f"{BASE_URL}/api/articles?limit=5")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        assert len(data) > 0, "Should have at least one article"
        
        # Check article structure
        article = data[0]
        assert "id" in article, "Article should have id"
        assert "title" in article, "Article should have title"
        assert "slug" in article, "Article should have slug"
        print(f"Articles endpoint returned {len(data)} articles")


class TestBonusSitesEndpoint:
    """Tests for bonus sites endpoint"""
    
    def test_bonus_sites_list(self):
        """Bonus sites endpoint should return list of sites"""
        response = requests.get(f"{BASE_URL}/api/bonus-sites?limit=5")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        assert len(data) > 0, "Should have at least one bonus site"
        
        # Check site structure
        site = data[0]
        assert "id" in site, "Site should have id"
        assert "name" in site, "Site should have name"
        assert "bonus_amount" in site, "Site should have bonus_amount"
        print(f"Bonus sites endpoint returned {len(data)} sites")


class TestCategoriesEndpoint:
    """Tests for categories endpoint"""
    
    def test_categories_list(self):
        """Categories endpoint should return list of categories"""
        response = requests.get(f"{BASE_URL}/api/categories")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert isinstance(data, list), "Response should be a list"
        assert len(data) > 0, "Should have at least one category"
        
        # Check category structure
        cat = data[0]
        assert "id" in cat, "Category should have id"
        assert "name" in cat, "Category should have name"
        assert "slug" in cat, "Category should have slug"
        print(f"Categories endpoint returned {len(data)} categories")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
