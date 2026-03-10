"""
GG2026 SEO Framework Phase 2 - Template System & Internal Linking Tests
Tests: Company Guide templates, Bonus Guide templates, internal linking, JSON-LD schema support
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

# Company Guide page types (access-related)
COMPANY_GUIDE_PAGE_TYPES = ["guncel-giris", "yeni-giris-adresi", "mobil-giris"]
# Bonus Guide page types (bonus-related)
BONUS_GUIDE_PAGE_TYPES = ["deneme-bonusu", "hosgeldin-bonusu", "bonus-sartlari", "yatirimsiz-deneme-bonusu"]

class TestCompanyGuideTemplate:
    """Tests for Company Guide template sections on access pages"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.base_slug = "maxwin"
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    @pytest.mark.parametrize("page_type", COMPANY_GUIDE_PAGE_TYPES)
    def test_company_guide_returns_all_sections(self, page_type):
        """Test that company guide pages return all 8 required sections"""
        response = self.session.get(f"{BASE_URL}/api/firma-sub/{self.base_slug}/{page_type}")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify template type
        assert data.get("template") == "company-guide", f"Expected template='company-guide', got {data.get('template')}"
        assert data.get("cluster") == "company-guide"
        
        # Verify all required sections exist
        sections = data.get("sections", {})
        required_sections = ["overview", "access_instructions", "address_change", "mobile_login", "safety_notes"]
        for section in required_sections:
            assert section in sections, f"Missing section: {section} in {page_type}"
        
        # Verify overview section structure
        assert "title" in sections["overview"]
        assert "content" in sections["overview"]
        
        # Verify access_instructions has steps array
        assert "steps" in sections["access_instructions"]
        assert isinstance(sections["access_instructions"]["steps"], list)
        assert len(sections["access_instructions"]["steps"]) > 0
        
        # Verify safety_notes has items array
        assert "items" in sections["safety_notes"]
        assert isinstance(sections["safety_notes"]["items"], list)
        assert len(sections["safety_notes"]["items"]) > 0
        
        print(f"PASS: Company guide template for {page_type} has all sections")
    
    def test_company_guide_has_faq(self):
        """Test that company guide page has FAQ array"""
        response = self.session.get(f"{BASE_URL}/api/firma-sub/{self.base_slug}/guncel-giris")
        assert response.status_code == 200
        
        data = response.json()
        faq = data.get("faq", [])
        
        assert isinstance(faq, list)
        assert len(faq) > 0, "FAQ should not be empty for guncel-giris"
        
        # Verify FAQ structure
        for item in faq:
            assert "question" in item
            assert "answer" in item
        
        print(f"PASS: Company guide has {len(faq)} FAQ items")
    
    def test_company_guide_has_hub_links(self):
        """Test that company guide pages have hub links for internal linking"""
        response = self.session.get(f"{BASE_URL}/api/firma-sub/{self.base_slug}/guncel-giris")
        assert response.status_code == 200
        
        data = response.json()
        hub_links = data.get("hub_links", [])
        
        assert isinstance(hub_links, list)
        assert len(hub_links) > 0, "Hub links should not be empty"
        
        # Verify hub link structure
        for link in hub_links:
            assert "title" in link
            assert "url" in link
            assert "type" in link
        
        print(f"PASS: Company guide has {len(hub_links)} hub links")
    
    def test_company_guide_has_cross_cluster_links(self):
        """Test that company guide pages (access) link to bonus pages (cross-cluster)"""
        response = self.session.get(f"{BASE_URL}/api/firma-sub/{self.base_slug}/guncel-giris")
        assert response.status_code == 200
        
        data = response.json()
        cross_links = data.get("cross_cluster_links", [])
        
        assert isinstance(cross_links, list)
        assert len(cross_links) > 0, "Cross cluster links should not be empty for company-guide"
        
        # Company guide pages should link to bonus-guide cluster pages
        for link in cross_links:
            assert "page_type" in link
            assert "url" in link
            assert "cluster" in link
            assert link["cluster"] == "bonus-guide", f"Company guide should link to bonus-guide cluster, got {link['cluster']}"
        
        # Verify links to expected bonus pages
        linked_types = [link["page_type"] for link in cross_links]
        assert any(pt in linked_types for pt in ["deneme-bonusu", "hosgeldin-bonusu", "bonus-sartlari"])
        
        print(f"PASS: Company guide has {len(cross_links)} cross-cluster links to bonus pages")
    
    def test_company_guide_has_last_updated(self):
        """Test that company guide pages have last_updated timestamp"""
        response = self.session.get(f"{BASE_URL}/api/firma-sub/{self.base_slug}/guncel-giris")
        assert response.status_code == 200
        
        data = response.json()
        assert "last_updated" in data
        assert data["last_updated"] is not None
        
        print(f"PASS: Company guide has last_updated: {data['last_updated']}")


class TestBonusGuideTemplate:
    """Tests for Bonus Guide template sections on bonus pages"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.base_slug = "maxwin"
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    @pytest.mark.parametrize("page_type", BONUS_GUIDE_PAGE_TYPES)
    def test_bonus_guide_returns_all_sections(self, page_type):
        """Test that bonus guide pages return all 9 required sections"""
        response = self.session.get(f"{BASE_URL}/api/firma-sub/{self.base_slug}/{page_type}")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify template type
        assert data.get("template") == "bonus-guide", f"Expected template='bonus-guide', got {data.get('template')}"
        assert data.get("cluster") == "bonus-guide"
        
        # Verify all required sections exist
        sections = data.get("sections", {})
        required_sections = ["overview", "bonus_availability", "bonus_types", "wagering", "pros_cons", "who_suits"]
        for section in required_sections:
            assert section in sections, f"Missing section: {section} in {page_type}"
        
        # Verify bonus_availability structure
        assert "amount" in sections["bonus_availability"]
        assert "status" in sections["bonus_availability"]
        
        # Verify bonus_types has items array
        assert "items" in sections["bonus_types"]
        assert isinstance(sections["bonus_types"]["items"], list)
        assert len(sections["bonus_types"]["items"]) > 0
        
        # Verify wagering structure
        assert "multiplier" in sections["wagering"]
        assert "details" in sections["wagering"]
        
        # Verify pros_cons structure
        assert "pros" in sections["pros_cons"]
        assert "cons" in sections["pros_cons"]
        assert isinstance(sections["pros_cons"]["pros"], list)
        assert isinstance(sections["pros_cons"]["cons"], list)
        
        print(f"PASS: Bonus guide template for {page_type} has all sections")
    
    def test_bonus_guide_has_faq(self):
        """Test that bonus guide page has FAQ array"""
        response = self.session.get(f"{BASE_URL}/api/firma-sub/{self.base_slug}/deneme-bonusu")
        assert response.status_code == 200
        
        data = response.json()
        faq = data.get("faq", [])
        
        assert isinstance(faq, list)
        assert len(faq) > 0, "FAQ should not be empty for deneme-bonusu"
        
        # Verify FAQ structure
        for item in faq:
            assert "question" in item
            assert "answer" in item
        
        print(f"PASS: Bonus guide has {len(faq)} FAQ items")
    
    def test_bonus_guide_has_cross_cluster_links(self):
        """Test that bonus guide pages (bonus) link to access pages (cross-cluster)"""
        response = self.session.get(f"{BASE_URL}/api/firma-sub/{self.base_slug}/deneme-bonusu")
        assert response.status_code == 200
        
        data = response.json()
        cross_links = data.get("cross_cluster_links", [])
        
        assert isinstance(cross_links, list)
        assert len(cross_links) > 0, "Cross cluster links should not be empty for bonus-guide"
        
        # Bonus guide pages should link to company-guide cluster pages
        for link in cross_links:
            assert link["cluster"] == "company-guide", f"Bonus guide should link to company-guide cluster, got {link['cluster']}"
        
        # Verify links to expected access pages
        linked_types = [link["page_type"] for link in cross_links]
        assert any(pt in linked_types for pt in ["guncel-giris", "yeni-giris-adresi", "mobil-giris"])
        
        print(f"PASS: Bonus guide has {len(cross_links)} cross-cluster links to access pages")


class TestBonusHubInternalLinking:
    """Tests for internal linking on Bonus Hub pages"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_bonus_hub_has_4_company_links_per_site(self):
        """Test that bonus hub pages show 4 company links per site"""
        response = self.session.get(f"{BASE_URL}/api/hub/bonus/deneme-bonusu-veren-siteler")
        assert response.status_code == 200
        
        data = response.json()
        company_links = data.get("company_links", [])
        
        assert len(company_links) > 0, "Should have company links"
        
        # Verify first company link has all 4 required URLs
        first_link = company_links[0]
        required_urls = ["guncel_giris_url", "deneme_bonusu_url", "hosgeldin_bonusu_url", "odeme_url"]
        
        for url_key in required_urls:
            assert url_key in first_link, f"Missing {url_key} in company_links"
            assert first_link[url_key] is not None
            assert first_link[url_key].startswith("/"), f"{url_key} should be a relative URL"
        
        print(f"PASS: Bonus hub has 4 company links per site - all present")
    
    def test_bonus_hub_company_links_format(self):
        """Test that company links follow correct URL format"""
        response = self.session.get(f"{BASE_URL}/api/hub/bonus/deneme-bonusu-veren-siteler")
        assert response.status_code == 200
        
        data = response.json()
        company_links = data.get("company_links", [])
        
        for link in company_links[:5]:  # Test first 5
            base_slug = link.get("base_slug")
            assert base_slug, "base_slug should exist"
            
            # Verify URL format matches /{base_slug}/{page_type}
            assert link["guncel_giris_url"] == f"/{base_slug}/guncel-giris"
            assert link["deneme_bonusu_url"] == f"/{base_slug}/deneme-bonusu"
            assert link["hosgeldin_bonusu_url"] == f"/{base_slug}/hosgeldin-bonusu"
            assert link["odeme_url"] == f"/{base_slug}/odeme-yontemleri"
        
        print(f"PASS: Bonus hub company links follow correct URL format")


class TestPaymentHubInternalLinking:
    """Tests for internal linking on Payment Hub pages"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_payment_hub_has_3_company_links_per_site(self):
        """Test that payment hub pages show 3 company links per site"""
        response = self.session.get(f"{BASE_URL}/api/hub/payment/odeme-yontemleri")
        assert response.status_code == 200
        
        data = response.json()
        company_links = data.get("company_links", [])
        
        assert len(company_links) > 0, "Should have company links"
        
        # Verify first company link has all 3 required URLs
        first_link = company_links[0]
        required_urls = ["odeme_url", "guncel_giris_url", "deneme_bonusu_url"]
        
        for url_key in required_urls:
            assert url_key in first_link, f"Missing {url_key} in company_links"
            assert first_link[url_key] is not None
        
        print(f"PASS: Payment hub has 3 company links per site - all present")
    
    def test_payment_hub_company_links_format(self):
        """Test that payment hub company links follow correct URL format"""
        response = self.session.get(f"{BASE_URL}/api/hub/payment/odeme-yontemleri")
        assert response.status_code == 200
        
        data = response.json()
        company_links = data.get("company_links", [])
        
        for link in company_links[:5]:  # Test first 5
            base_slug = link.get("base_slug")
            assert base_slug, "base_slug should exist"
            
            # Verify URL format
            assert link["odeme_url"] == f"/{base_slug}/odeme-yontemleri"
            assert link["guncel_giris_url"] == f"/{base_slug}/guncel-giris"
            assert link["deneme_bonusu_url"] == f"/{base_slug}/deneme-bonusu"
        
        print(f"PASS: Payment hub company links follow correct URL format")


class TestFAQContent:
    """Tests for FAQ content generation per page type"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.base_slug = "maxwin"
        self.session = requests.Session()
    
    def test_guncel_giris_has_specific_faq(self):
        """Test guncel-giris page has access-related FAQ"""
        response = self.session.get(f"{BASE_URL}/api/firma-sub/{self.base_slug}/guncel-giris")
        assert response.status_code == 200
        
        faq = response.json().get("faq", [])
        assert len(faq) >= 3, "guncel-giris should have at least 3 FAQ items"
        
        # Check FAQ contains access-related questions
        questions = [item["question"].lower() for item in faq]
        assert any("giris" in q for q in questions), "FAQ should have questions about 'giris'"
        
        print(f"PASS: guncel-giris has {len(faq)} access-related FAQ items")
    
    def test_deneme_bonusu_has_specific_faq(self):
        """Test deneme-bonusu page has bonus-related FAQ"""
        response = self.session.get(f"{BASE_URL}/api/firma-sub/{self.base_slug}/deneme-bonusu")
        assert response.status_code == 200
        
        faq = response.json().get("faq", [])
        assert len(faq) >= 3, "deneme-bonusu should have at least 3 FAQ items"
        
        # Check FAQ contains bonus-related questions
        questions = [item["question"].lower() for item in faq]
        assert any("bonus" in q or "deneme" in q for q in questions), "FAQ should have questions about 'bonus'"
        
        print(f"PASS: deneme-bonusu has {len(faq)} bonus-related FAQ items")
    
    def test_odeme_yontemleri_has_specific_faq(self):
        """Test odeme-yontemleri page has payment-related FAQ"""
        response = self.session.get(f"{BASE_URL}/api/firma-sub/{self.base_slug}/odeme-yontemleri")
        assert response.status_code == 200
        
        faq = response.json().get("faq", [])
        assert len(faq) >= 3, "odeme-yontemleri should have at least 3 FAQ items"
        
        # Check FAQ contains payment-related questions
        questions = [item["question"].lower() for item in faq]
        assert any("odeme" in q or "para" in q or "yatirim" in q for q in questions), "FAQ should have questions about payment"
        
        print(f"PASS: odeme-yontemleri has {len(faq)} payment-related FAQ items")


class TestSchemaSupport:
    """Tests to verify API returns data needed for JSON-LD schema generation"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.base_slug = "maxwin"
        self.session = requests.Session()
    
    def test_company_page_has_breadcrumb_data(self):
        """Test that company page returns breadcrumb data for BreadcrumbList schema"""
        response = self.session.get(f"{BASE_URL}/api/firma-sub/{self.base_slug}/guncel-giris")
        assert response.status_code == 200
        
        data = response.json()
        breadcrumb = data.get("breadcrumb", [])
        
        assert len(breadcrumb) >= 3, "Breadcrumb should have at least 3 items"
        
        for item in breadcrumb:
            assert "name" in item
            assert "url" in item
        
        print(f"PASS: Company page has breadcrumb data for BreadcrumbList schema")
    
    def test_company_page_has_faq_data(self):
        """Test that company page returns FAQ data for FAQPage schema"""
        response = self.session.get(f"{BASE_URL}/api/firma-sub/{self.base_slug}/guncel-giris")
        assert response.status_code == 200
        
        data = response.json()
        faq = data.get("faq", [])
        
        assert len(faq) > 0, "FAQ should exist for FAQPage schema"
        
        for item in faq:
            assert "question" in item
            assert "answer" in item
        
        print(f"PASS: Company page has FAQ data for FAQPage schema")
    
    def test_company_page_has_article_data(self):
        """Test that company page returns data needed for Article schema"""
        response = self.session.get(f"{BASE_URL}/api/firma-sub/{self.base_slug}/guncel-giris")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify SEO data for Article headline/description
        seo = data.get("seo", {})
        assert "h1" in seo, "Need h1 for Article headline"
        assert "description" in seo, "Need description for Article"
        assert "canonical" in seo, "Need canonical for Article url"
        
        # Verify last_updated for dateModified
        assert "last_updated" in data, "Need last_updated for Article dateModified"
        
        print(f"PASS: Company page has data for Article schema")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
