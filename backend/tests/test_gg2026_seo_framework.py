"""
GG2026 SEO Framework Backend Tests
Testing company sub-pages, bonus hubs, payment hubs, and sitemaps
"""
import pytest
import requests
import os
import xml.etree.ElementTree as ET

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Valid page types for company sub-pages
VALID_PAGE_TYPES = [
    "guncel-giris", "guncel-adresi", "yeni-giris-adresi", "mobil-giris",
    "deneme-bonusu", "deneme-bonusu-2026", "hosgeldin-bonusu",
    "yatirimsiz-deneme-bonusu", "bonus-sartlari", "odeme-yontemleri"
]

# Bonus hub pages
BONUS_HUB_SLUGS = [
    "deneme-bonusu-veren-siteler",
    "guncel-deneme-bonusu",
    "yatirimsiz-deneme-bonusu",
    "bonus-veren-siteler"
    # Note: hosgeldin-bonusu uses BonusGuidePage, not BonusHubPage
]

# Payment hub pages
PAYMENT_HUB_SLUGS = [
    "odeme-yontemleri",
    "mobil-odeme-ile-bahis",
    "kredi-karti-ile-bahis",
    "papel-ile-bahis",
    "havale-ile-bahis",
    "kripto-ile-bahis",
    "bddk-onayli-odeme-yontemleri",
    "guvenli-odeme-yontemleri"
]


class TestHealthCheck:
    """Basic health check tests"""
    
    def test_api_health(self):
        """Verify API is reachable"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200, f"Health check failed: {response.status_code}"
        data = response.json()
        assert data.get("status") == "ok"
        print("PASS: API health check")


class TestCompanySubPageAPI:
    """Tests for GET /api/firma-sub/{base_slug}/{page_type}"""
    
    @pytest.fixture
    def sample_firm_slug(self):
        """Get a sample firm slug from bonus_sites for testing"""
        response = requests.get(f"{BASE_URL}/api/bonus-sites?limit=1")
        if response.status_code == 200 and response.json():
            site = response.json()[0]
            slug = site.get("slug", "")
            # Extract base slug (remove -guncelgiris suffix if present)
            if slug.endswith("-guncelgiris"):
                return slug[:-len("-guncelgiris")]
            return slug
        return "tulipbet"  # Fallback
    
    def test_company_subpage_guncel_giris(self, sample_firm_slug):
        """Test guncel-giris page type returns correct data"""
        response = requests.get(f"{BASE_URL}/api/firma-sub/{sample_firm_slug}/guncel-giris")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Verify required fields
        assert "site" in data, "Missing 'site' field"
        assert "seo" in data, "Missing 'seo' field"
        assert "breadcrumb" in data, "Missing 'breadcrumb' field"
        assert "internal_links" in data, "Missing 'internal_links' field"
        
        # Verify SEO fields
        seo = data["seo"]
        assert "title" in seo, "Missing title in SEO"
        assert "description" in seo, "Missing description in SEO"
        assert "h1" in seo, "Missing h1 in SEO"
        assert "canonical" in seo, "Missing canonical in SEO"
        
        # Verify cluster
        assert data.get("cluster") == "company-guide", "guncel-giris should be company-guide cluster"
        
        # Verify breadcrumb structure
        assert len(data["breadcrumb"]) >= 2, "Breadcrumb should have at least 2 items"
        assert data["breadcrumb"][0]["name"] == "Ana Sayfa"
        
        print(f"PASS: Company sub-page guncel-giris for {sample_firm_slug}")
    
    def test_company_subpage_deneme_bonusu(self, sample_firm_slug):
        """Test deneme-bonusu page type returns bonus-guide cluster"""
        response = requests.get(f"{BASE_URL}/api/firma-sub/{sample_firm_slug}/deneme-bonusu")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("cluster") == "bonus-guide", "deneme-bonusu should be bonus-guide cluster"
        
        # Verify internal links have both clusters
        internal_links = data.get("internal_links", {})
        assert "company_guide" in internal_links, "Should have company_guide links"
        assert "bonus_guide" in internal_links, "Should have bonus_guide links"
        
        print(f"PASS: Company sub-page deneme-bonusu for {sample_firm_slug}")
    
    def test_all_page_types_valid(self, sample_firm_slug):
        """Test all 10 page types return valid data"""
        passed = 0
        failed = []
        
        for page_type in VALID_PAGE_TYPES:
            response = requests.get(f"{BASE_URL}/api/firma-sub/{sample_firm_slug}/{page_type}")
            if response.status_code == 200:
                data = response.json()
                if "seo" in data and "site" in data:
                    passed += 1
                else:
                    failed.append(f"{page_type}: missing required fields")
            else:
                failed.append(f"{page_type}: HTTP {response.status_code}")
        
        print(f"Page types: {passed}/{len(VALID_PAGE_TYPES)} passed")
        for f in failed:
            print(f"  FAILED: {f}")
        
        assert passed == len(VALID_PAGE_TYPES), f"Some page types failed: {failed}"
        print(f"PASS: All {len(VALID_PAGE_TYPES)} page types work correctly")
    
    def test_invalid_page_type_returns_404(self, sample_firm_slug):
        """Test invalid page type returns 404"""
        response = requests.get(f"{BASE_URL}/api/firma-sub/{sample_firm_slug}/invalid-page-type")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Invalid page type returns 404")
    
    def test_invalid_company_returns_404(self):
        """Test non-existent company returns 404"""
        response = requests.get(f"{BASE_URL}/api/firma-sub/nonexistent-company-xyz/guncel-giris")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Non-existent company returns 404")
    
    def test_similar_firms_included(self, sample_firm_slug):
        """Test similar_same_page field is populated"""
        response = requests.get(f"{BASE_URL}/api/firma-sub/{sample_firm_slug}/guncel-giris")
        assert response.status_code == 200
        
        data = response.json()
        similar = data.get("similar_same_page", [])
        # Similar firms should have URL format /{base}/{page_type}
        if similar:
            first = similar[0]
            assert "name" in first, "Similar firm should have name"
            assert "url" in first, "Similar firm should have url"
            assert "/guncel-giris" in first["url"], "URL should point to same page type"
        
        print(f"PASS: Similar firms check (found {len(similar)} similar)")


class TestBonusHubAPI:
    """Tests for GET /api/hub/bonus/{hub_slug}"""
    
    def test_bonus_hub_deneme_bonusu_veren_siteler(self):
        """Test main bonus hub page"""
        response = requests.get(f"{BASE_URL}/api/hub/bonus/deneme-bonusu-veren-siteler")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Verify structure
        assert "seo" in data, "Missing 'seo' field"
        assert "breadcrumb" in data, "Missing 'breadcrumb' field"
        assert "sites" in data, "Missing 'sites' field"
        assert "company_links" in data, "Missing 'company_links' field"
        assert "related_hubs" in data, "Missing 'related_hubs' field"
        
        # Verify SEO
        seo = data["seo"]
        assert "Deneme Bonusu" in seo.get("title", ""), "Title should mention Deneme Bonusu"
        assert "h1" in seo, "Missing h1"
        
        # Verify sites are returned
        sites = data["sites"]
        assert len(sites) > 0, "Should return at least 1 site"
        
        # Verify company links have sub-page URLs
        company_links = data["company_links"]
        if company_links:
            first_link = company_links[0]
            assert "guncel_giris_url" in first_link, "Missing guncel_giris_url"
            assert "deneme_bonusu_url" in first_link, "Missing deneme_bonusu_url"
        
        # Verify related hubs
        related = data["related_hubs"]
        assert "bonus" in related, "Should have related bonus hubs"
        assert "payment" in related, "Should have cross-cluster payment hubs"
        
        print(f"PASS: Bonus hub 'deneme-bonusu-veren-siteler' returns {len(sites)} sites")
    
    def test_all_bonus_hub_pages(self):
        """Test all bonus hub pages return valid data"""
        passed = 0
        failed = []
        
        for slug in BONUS_HUB_SLUGS:
            response = requests.get(f"{BASE_URL}/api/hub/bonus/{slug}")
            if response.status_code == 200:
                data = response.json()
                if "sites" in data and "seo" in data:
                    passed += 1
                else:
                    failed.append(f"{slug}: missing required fields")
            else:
                failed.append(f"{slug}: HTTP {response.status_code}")
        
        print(f"Bonus hubs: {passed}/{len(BONUS_HUB_SLUGS)} passed")
        for f in failed:
            print(f"  FAILED: {f}")
        
        assert passed == len(BONUS_HUB_SLUGS), f"Some bonus hubs failed: {failed}"
        print(f"PASS: All {len(BONUS_HUB_SLUGS)} bonus hub pages work correctly")
    
    def test_invalid_bonus_hub_returns_404(self):
        """Test invalid hub slug returns 404"""
        response = requests.get(f"{BASE_URL}/api/hub/bonus/invalid-hub-slug")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Invalid bonus hub returns 404")


class TestPaymentHubAPI:
    """Tests for GET /api/hub/payment/{hub_slug}"""
    
    def test_payment_hub_odeme_yontemleri(self):
        """Test main payment hub page"""
        response = requests.get(f"{BASE_URL}/api/hub/payment/odeme-yontemleri")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Verify structure
        assert "seo" in data, "Missing 'seo' field"
        assert "breadcrumb" in data, "Missing 'breadcrumb' field"
        assert "sites" in data, "Missing 'sites' field"
        assert "company_links" in data, "Missing 'company_links' field"
        assert "related_hubs" in data, "Missing 'related_hubs' field"
        
        # Verify company links have payment-specific URLs
        company_links = data["company_links"]
        if company_links:
            first_link = company_links[0]
            assert "odeme_url" in first_link, "Missing odeme_url in company_links"
            assert "guncel_giris_url" in first_link, "Missing guncel_giris_url in company_links"
        
        # Verify cross-cluster links
        related = data["related_hubs"]
        assert "bonus" in related, "Should have cross-cluster bonus hubs"
        assert "payment" in related, "Should have related payment hubs"
        
        print(f"PASS: Payment hub 'odeme-yontemleri' returns {len(data['sites'])} sites")
    
    def test_all_payment_hub_pages(self):
        """Test all payment hub pages return valid data"""
        passed = 0
        failed = []
        
        for slug in PAYMENT_HUB_SLUGS:
            response = requests.get(f"{BASE_URL}/api/hub/payment/{slug}")
            if response.status_code == 200:
                data = response.json()
                if "sites" in data and "seo" in data:
                    passed += 1
                else:
                    failed.append(f"{slug}: missing required fields")
            else:
                failed.append(f"{slug}: HTTP {response.status_code}")
        
        print(f"Payment hubs: {passed}/{len(PAYMENT_HUB_SLUGS)} passed")
        for f in failed:
            print(f"  FAILED: {f}")
        
        assert passed == len(PAYMENT_HUB_SLUGS), f"Some payment hubs failed: {failed}"
        print(f"PASS: All {len(PAYMENT_HUB_SLUGS)} payment hub pages work correctly")
    
    def test_invalid_payment_hub_returns_404(self):
        """Test invalid hub slug returns 404"""
        response = requests.get(f"{BASE_URL}/api/hub/payment/invalid-hub-slug")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("PASS: Invalid payment hub returns 404")


class TestSitemapSEOPages:
    """Tests for /api/sitemap-seo-pages.xml"""
    
    def test_sitemap_seo_pages_returns_xml(self):
        """Test sitemap-seo-pages.xml returns valid XML"""
        response = requests.get(f"{BASE_URL}/api/sitemap-seo-pages.xml")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        # Should be XML content type
        content_type = response.headers.get("content-type", "")
        assert "xml" in content_type.lower(), f"Expected XML content type, got {content_type}"
        
        # Parse XML to verify it's valid
        try:
            root = ET.fromstring(response.content)
            assert root.tag.endswith("urlset"), f"Expected urlset root, got {root.tag}"
        except ET.ParseError as e:
            pytest.fail(f"Invalid XML: {e}")
        
        print("PASS: sitemap-seo-pages.xml returns valid XML")
    
    def test_sitemap_seo_pages_contains_hub_pages(self):
        """Test sitemap includes bonus and payment hub pages"""
        response = requests.get(f"{BASE_URL}/api/sitemap-seo-pages.xml")
        assert response.status_code == 200
        
        content = response.text
        
        # Check bonus hub pages
        for slug in BONUS_HUB_SLUGS:
            assert f"/{slug}" in content, f"Missing bonus hub: {slug}"
        
        # Check payment hub pages
        for slug in PAYMENT_HUB_SLUGS:
            assert f"/{slug}" in content, f"Missing payment hub: {slug}"
        
        print("PASS: Sitemap contains all hub pages")
    
    def test_sitemap_seo_pages_contains_company_subpages(self):
        """Test sitemap includes company sub-pages"""
        response = requests.get(f"{BASE_URL}/api/sitemap-seo-pages.xml")
        assert response.status_code == 200
        
        content = response.text
        
        # Should contain at least some page types
        found_page_types = 0
        for pt in VALID_PAGE_TYPES:
            if f"/{pt}" in content:
                found_page_types += 1
        
        assert found_page_types >= 5, f"Expected at least 5 page types in sitemap, found {found_page_types}"
        print(f"PASS: Sitemap contains {found_page_types} page types")


class TestSitemapIndex:
    """Tests for /api/sitemap.xml (sitemap index)"""
    
    def test_sitemap_index_includes_seo_pages(self):
        """Test sitemap index includes sitemap-seo-pages.xml entry"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        content = response.text
        
        # Should be XML
        assert "<?xml" in content, "Response should be XML"
        
        # Should include seo-pages sitemap
        assert "sitemap-seo-pages.xml" in content, "Sitemap index should include sitemap-seo-pages.xml"
        
        # Verify it's a sitemap index format
        assert "<sitemapindex" in content, "Should be a sitemap index"
        
        print("PASS: Sitemap index includes sitemap-seo-pages.xml")


class TestExistingRoutesStillWork:
    """Test that existing routes haven't been broken"""
    
    def test_homepage_loads(self):
        """Test homepage API works"""
        response = requests.get(f"{BASE_URL}/api/bonus-sites?limit=5")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: Homepage API (bonus-sites) works")
    
    def test_deneme_bonusu_api(self):
        """Test deneme-bonusu category works"""
        response = requests.get(f"{BASE_URL}/api/bonus-sites?category=deneme&limit=5")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print("PASS: Deneme bonusu API works")
    
    def test_firm_page_api(self):
        """Test individual firm API works"""
        # Get a sample firm
        response = requests.get(f"{BASE_URL}/api/bonus-sites?limit=1")
        if response.status_code == 200 and response.json():
            slug = response.json()[0].get("slug", "")
            if slug:
                firm_response = requests.get(f"{BASE_URL}/api/site/{slug}")
                assert firm_response.status_code == 200, f"Expected 200, got {firm_response.status_code}"
                print(f"PASS: Firm page API works for {slug}")
            else:
                pytest.skip("No firm slug found")
        else:
            pytest.skip("Could not get sample firm")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
