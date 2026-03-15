"""
GG2026 Phase 5: Company Article System Backend Tests
Tests company-articles endpoints, sitemap, and article-to-company/hub relationships
"""
import requests
import os
import uuid

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

class TestCompanyArticlesListEndpoint:
    """Tests for GET /api/company-articles/{base_slug}"""
    
    def test_list_articles_returns_200(self):
        """Test listing articles for tulipbet returns 200"""
        response = requests.get(f"{BASE_URL}/api/company-articles/tulipbet")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: GET /api/company-articles/tulipbet returns 200")
    
    def test_list_articles_site_info(self):
        """Test site info is returned correctly"""
        response = requests.get(f"{BASE_URL}/api/company-articles/tulipbet")
        assert response.status_code == 200
        data = response.json()
        
        # Verify site section
        assert "site" in data, "Response must have site field"
        site = data["site"]
        assert site.get("name"), "Site must have name"
        assert site.get("base_slug"), "Site must have base_slug"
        assert site.get("logo_url"), "Site must have logo_url"
        print(f"PASS: Site info returned - name={site['name']}, base_slug={site['base_slug']}")
    
    def test_list_articles_returns_articles(self):
        """Test articles list is returned"""
        response = requests.get(f"{BASE_URL}/api/company-articles/tulipbet")
        assert response.status_code == 200
        data = response.json()
        
        assert "articles" in data, "Response must have articles field"
        articles = data["articles"]
        assert isinstance(articles, list), "Articles must be a list"
        assert len(articles) >= 2, f"Expected at least 2 test articles, got {len(articles)}"
        
        # Verify article structure
        for article in articles:
            assert "id" in article or "slug" in article, "Article must have id or slug"
            assert "title" in article, "Article must have title"
            assert "article_type" in article, "Article must have article_type"
        print(f"PASS: {len(articles)} articles returned with correct structure")
    
    def test_list_articles_sub_pages(self):
        """Test sub_pages internal links are returned"""
        response = requests.get(f"{BASE_URL}/api/company-articles/tulipbet")
        assert response.status_code == 200
        data = response.json()
        
        assert "sub_pages" in data, "Response must have sub_pages field"
        sub_pages = data["sub_pages"]
        assert len(sub_pages) >= 5, f"Expected at least 5 sub_pages, got {len(sub_pages)}"
        
        for sp in sub_pages:
            assert "page_type" in sp, "sub_page must have page_type"
            assert "url" in sp, "sub_page must have url"
            assert "label" in sp, "sub_page must have label"
            assert "cluster" in sp, "sub_page must have cluster"
        print(f"PASS: {len(sub_pages)} sub_pages returned for internal linking")
    
    def test_list_articles_hub_links(self):
        """Test hub_links are returned"""
        response = requests.get(f"{BASE_URL}/api/company-articles/tulipbet")
        assert response.status_code == 200
        data = response.json()
        
        assert "hub_links" in data, "Response must have hub_links field"
        hub_links = data["hub_links"]
        assert len(hub_links) >= 5, f"Expected at least 5 hub_links, got {len(hub_links)}"
        
        for hub in hub_links:
            assert "slug" in hub, "hub_link must have slug"
            assert "title" in hub, "hub_link must have title"
            assert "url" in hub, "hub_link must have url"
        print(f"PASS: {len(hub_links)} hub_links returned")
    
    def test_list_articles_breadcrumb(self):
        """Test breadcrumb navigation is returned"""
        response = requests.get(f"{BASE_URL}/api/company-articles/tulipbet")
        assert response.status_code == 200
        data = response.json()
        
        assert "breadcrumb" in data, "Response must have breadcrumb"
        breadcrumb = data["breadcrumb"]
        assert len(breadcrumb) >= 3, "Breadcrumb should have at least 3 items"
        assert breadcrumb[0]["name"] == "Ana Sayfa", "First breadcrumb should be Ana Sayfa"
        assert "Makaleler" in breadcrumb[-1]["name"], "Last breadcrumb should be Makaleler"
        print(f"PASS: Breadcrumb has {len(breadcrumb)} items")
    
    def test_list_articles_seo(self):
        """Test SEO metadata is returned"""
        response = requests.get(f"{BASE_URL}/api/company-articles/tulipbet")
        assert response.status_code == 200
        data = response.json()
        
        assert "seo" in data, "Response must have seo field"
        seo = data["seo"]
        assert seo.get("title"), "SEO must have title"
        assert seo.get("description"), "SEO must have description"
        assert seo.get("canonical"), "SEO must have canonical"
        assert "/makaleler" in seo["canonical"], "Canonical must include /makaleler"
        print(f"PASS: SEO returned - title={seo['title'][:50]}...")
    
    def test_list_articles_404_for_invalid_company(self):
        """Test 404 for non-existent company"""
        response = requests.get(f"{BASE_URL}/api/company-articles/nonexistent-company-xyz")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: 404 returned for non-existent company")


class TestCompanyArticleDetailEndpoint:
    """Tests for GET /api/company-articles/{base_slug}/{article_slug}"""
    
    def test_get_article_returns_200(self):
        """Test getting specific article returns 200"""
        response = requests.get(f"{BASE_URL}/api/company-articles/tulipbet/tulipbet-deneme-bonusu-rehberi")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: GET /api/company-articles/tulipbet/tulipbet-deneme-bonusu-rehberi returns 200")
    
    def test_get_article_full_data(self):
        """Test article returns full content and metadata"""
        response = requests.get(f"{BASE_URL}/api/company-articles/tulipbet/tulipbet-deneme-bonusu-rehberi")
        assert response.status_code == 200
        data = response.json()
        
        assert "article" in data, "Response must have article field"
        article = data["article"]
        assert article.get("title"), "Article must have title"
        assert article.get("content"), "Article must have content"
        assert article.get("article_type") == "deneme-bonusu-rehberi", f"Expected type deneme-bonusu-rehberi, got {article.get('article_type')}"
        assert "view_count" in article, "Article must have view_count"
        print(f"PASS: Article returned - title={article['title']}, type={article['article_type']}")
    
    def test_get_article_related_articles(self):
        """Test related_articles are returned"""
        response = requests.get(f"{BASE_URL}/api/company-articles/tulipbet/tulipbet-deneme-bonusu-rehberi")
        assert response.status_code == 200
        data = response.json()
        
        assert "related_articles" in data, "Response must have related_articles"
        related = data["related_articles"]
        assert isinstance(related, list), "related_articles must be a list"
        # Should have at least 1 related article (tulipbet-giris-rehberi)
        assert len(related) >= 1, f"Expected at least 1 related article, got {len(related)}"
        print(f"PASS: {len(related)} related_articles returned")
    
    def test_get_article_related_sub_pages_by_cluster(self):
        """Test related_sub_pages are filtered by article cluster"""
        # Test bonus-guide type article
        response = requests.get(f"{BASE_URL}/api/company-articles/tulipbet/tulipbet-deneme-bonusu-rehberi")
        assert response.status_code == 200
        data = response.json()
        
        assert "related_sub_pages" in data, "Response must have related_sub_pages"
        sub_pages = data["related_sub_pages"]
        assert len(sub_pages) >= 3, f"Expected at least 3 related sub_pages, got {len(sub_pages)}"
        
        # Verify structure
        for sp in sub_pages:
            assert "page_type" in sp
            assert "url" in sp
            assert "label" in sp
        print(f"PASS: {len(sub_pages)} related_sub_pages returned based on article cluster")
    
    def test_get_article_related_hubs(self):
        """Test related_hubs are returned based on cluster"""
        response = requests.get(f"{BASE_URL}/api/company-articles/tulipbet/tulipbet-deneme-bonusu-rehberi")
        assert response.status_code == 200
        data = response.json()
        
        assert "related_hubs" in data, "Response must have related_hubs"
        hubs = data["related_hubs"]
        assert len(hubs) >= 3, f"Expected at least 3 related hubs, got {len(hubs)}"
        
        for hub in hubs:
            assert "slug" in hub
            assert "title" in hub
            assert "url" in hub
        print(f"PASS: {len(hubs)} related_hubs returned")
    
    def test_get_article_similar_company_links(self):
        """Test similar_company_links are returned"""
        response = requests.get(f"{BASE_URL}/api/company-articles/tulipbet/tulipbet-deneme-bonusu-rehberi")
        assert response.status_code == 200
        data = response.json()
        
        assert "similar_company_links" in data, "Response must have similar_company_links"
        similar = data["similar_company_links"]
        assert isinstance(similar, list), "similar_company_links must be a list"
        
        if len(similar) > 0:
            for company in similar:
                assert "name" in company
                assert "articles_url" in company
                assert "/makaleler" in company["articles_url"]
        print(f"PASS: {len(similar)} similar_company_links returned")
    
    def test_get_article_breadcrumb(self):
        """Test breadcrumb has 4 levels for article detail"""
        response = requests.get(f"{BASE_URL}/api/company-articles/tulipbet/tulipbet-deneme-bonusu-rehberi")
        assert response.status_code == 200
        data = response.json()
        
        assert "breadcrumb" in data
        breadcrumb = data["breadcrumb"]
        assert len(breadcrumb) == 4, f"Expected 4 breadcrumb items, got {len(breadcrumb)}"
        assert breadcrumb[0]["name"] == "Ana Sayfa"
        assert "Makaleler" in breadcrumb[2]["name"]
        print(f"PASS: Breadcrumb has {len(breadcrumb)} levels")
    
    def test_get_article_404_for_invalid_slug(self):
        """Test 404 for non-existent article"""
        response = requests.get(f"{BASE_URL}/api/company-articles/tulipbet/nonexistent-article-xyz")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: 404 returned for non-existent article")
    
    def test_company_guide_type_article(self):
        """Test company-guide type article returns correct related sub-pages"""
        response = requests.get(f"{BASE_URL}/api/company-articles/tulipbet/tulipbet-giris-rehberi")
        assert response.status_code == 200
        data = response.json()
        
        article = data["article"]
        assert article.get("article_type") == "giris-rehberi", f"Expected giris-rehberi type, got {article.get('article_type')}"
        
        # Related hubs should be payment hubs for company-guide cluster
        hubs = data.get("related_hubs", [])
        assert len(hubs) > 0, "Should have related hubs"
        print(f"PASS: Company-guide type article has correct related hubs ({len(hubs)} hubs)")


class TestCreateCompanyArticle:
    """Tests for POST /api/company-articles"""
    
    def test_create_article_returns_200(self):
        """Test creating article returns 200"""
        unique_id = str(uuid.uuid4())[:8]
        payload = {
            "company_slug": "tulipbet",
            "title": f"TEST Pytest Article {unique_id}",
            "content": "<p>Test content for pytest.</p>",
            "article_type": "inceleme",
            "is_published": False
        }
        response = requests.post(f"{BASE_URL}/api/company-articles", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("id"), "Response must have id"
        assert data.get("slug"), "Response must have slug"
        assert data.get("company_slug") == "tulipbet"
        print(f"PASS: Article created with id={data['id'][:8]}...")
    
    def test_create_article_auto_generates_slug(self):
        """Test slug is auto-generated from title"""
        unique_id = str(uuid.uuid4())[:8]
        payload = {
            "company_slug": "tulipbet",
            "title": f"TEST Auto Slug {unique_id}",
            "content": "<p>Content</p>",
            "is_published": False
        }
        response = requests.post(f"{BASE_URL}/api/company-articles", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "test-auto-slug" in data["slug"].lower(), f"Expected auto-generated slug, got {data['slug']}"
        print(f"PASS: Slug auto-generated: {data['slug']}")
    
    def test_create_article_requires_company_slug(self):
        """Test 400 if company_slug missing"""
        payload = {
            "title": "Test Missing Company",
            "content": "<p>Content</p>"
        }
        response = requests.post(f"{BASE_URL}/api/company-articles", json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("PASS: 400 returned when company_slug missing")
    
    def test_create_article_requires_title(self):
        """Test 400 if title missing"""
        payload = {
            "company_slug": "tulipbet",
            "content": "<p>Content</p>"
        }
        response = requests.post(f"{BASE_URL}/api/company-articles", json=payload)
        assert response.status_code == 400, f"Expected 400, got {response.status_code}"
        print("PASS: 400 returned when title missing")
    
    def test_create_article_with_article_type(self):
        """Test article type taxonomy is stored correctly"""
        unique_id = str(uuid.uuid4())[:8]
        payload = {
            "company_slug": "tulipbet",
            "title": f"TEST Bonus Rehberi {unique_id}",
            "content": "<p>Content</p>",
            "article_type": "hosgeldin-bonusu-rehberi",
            "is_published": False
        }
        response = requests.post(f"{BASE_URL}/api/company-articles", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data.get("article_type") == "hosgeldin-bonusu-rehberi"
        print(f"PASS: Article type stored correctly: {data['article_type']}")


class TestCompanyArticlesSitemap:
    """Tests for GET /api/sitemap-company-articles.xml"""
    
    def test_sitemap_returns_200_xml(self):
        """Test sitemap returns 200 with XML content"""
        response = requests.get(f"{BASE_URL}/api/sitemap-company-articles.xml")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        assert "xml" in response.headers.get("content-type", "").lower()
        print("PASS: Sitemap returns 200 with XML content-type")
    
    def test_sitemap_contains_article_urls(self):
        """Test sitemap contains article URLs"""
        response = requests.get(f"{BASE_URL}/api/sitemap-company-articles.xml")
        assert response.status_code == 200
        
        content = response.text
        assert "tulipbet/makaleler/tulipbet-deneme-bonusu-rehberi" in content
        assert "tulipbet/makaleler/tulipbet-giris-rehberi" in content
        print("PASS: Sitemap contains test article URLs")
    
    def test_sitemap_contains_listing_page_urls(self):
        """Test sitemap contains listing page URLs for all firms"""
        response = requests.get(f"{BASE_URL}/api/sitemap-company-articles.xml")
        assert response.status_code == 200
        
        content = response.text
        # Should have /makaleler listing pages
        assert "/makaleler</loc>" in content, "Sitemap should contain /makaleler listing pages"
        print("PASS: Sitemap contains /makaleler listing page URLs")
    
    def test_sitemap_valid_xml_structure(self):
        """Test sitemap has valid XML structure"""
        response = requests.get(f"{BASE_URL}/api/sitemap-company-articles.xml")
        assert response.status_code == 200
        
        content = response.text
        assert '<?xml version="1.0"' in content
        assert "<urlset" in content
        assert "<loc>" in content
        assert "<lastmod>" in content
        assert "</urlset>" in content
        print("PASS: Sitemap has valid XML structure")


class TestMainSitemapIncludesArticles:
    """Test main sitemap.xml includes company-articles sitemap"""
    
    def test_main_sitemap_references_articles_sitemap(self):
        """Test /api/sitemap.xml includes sitemap-company-articles.xml"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200
        
        content = response.text
        assert "sitemap-company-articles.xml" in content, "Main sitemap must reference company-articles sitemap"
        print("PASS: Main sitemap includes sitemap-company-articles.xml")


class TestExistingRoutes:
    """Verify existing routes are not broken by Phase 5"""
    
    def test_homepage_api(self):
        """Test homepage data still works"""
        response = requests.get(f"{BASE_URL}/api/bonus-sites")
        assert response.status_code == 200
        print("PASS: /api/bonus-sites still works")
    
    def test_company_sub_page_api(self):
        """Test firma-sub endpoint still works"""
        response = requests.get(f"{BASE_URL}/api/firma-sub/tulipbet/deneme-bonusu")
        assert response.status_code == 200
        data = response.json()
        assert data.get("site", {}).get("name")
        print("PASS: /api/firma-sub still works")
    
    def test_main_sitemap(self):
        """Test main sitemap still works"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200
        print("PASS: /api/sitemap.xml still works")
