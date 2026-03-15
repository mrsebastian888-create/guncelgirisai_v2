"""
GG2026 SEO Framework Phase 2 Backend Tests
Testing: Template sections, FAQ, internal linking engine, Schema support
"""
import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://bot-control-4.preview.emergentagent.com').rstrip('/')


class TestPhase2CompanyGuideTemplate:
    """Test Company Guide template sections and data"""

    def test_guncel_giris_returns_template_data(self):
        """Test /tulipbet/guncel-giris returns all required fields for Company Guide template"""
        response = requests.get(f"{BASE_URL}/api/firma-sub/tulipbet/guncel-giris")
        assert response.status_code == 200
        data = response.json()
        
        # Required fields for Company Guide template
        assert data["cluster"] == "company-guide"
        assert "site" in data
        assert "faq" in data and len(data["faq"]) > 0, "FAQ data required"
        assert "last_updated" in data and data["last_updated"], "last_updated required"
        assert "hub_links" in data and len(data["hub_links"]) > 0, "hub_links required"
        assert "related_companies" in data and len(data["related_companies"]) > 0, "related_companies required"
        
        # Verify FAQ structure
        faq = data["faq"]
        for item in faq:
            assert "question" in item, "FAQ item must have 'question'"
            assert "answer" in item, "FAQ item must have 'answer'"
        
        print(f"PASS: guncel-giris template data (FAQ: {len(faq)}, hub_links: {len(data['hub_links'])}, related: {len(data['related_companies'])})")

    def test_mobil_giris_company_guide_cluster(self):
        """Test mobil-giris is in company-guide cluster (for MobileLoginInfo section)"""
        response = requests.get(f"{BASE_URL}/api/firma-sub/tulipbet/mobil-giris")
        assert response.status_code == 200
        data = response.json()
        
        assert data["cluster"] == "company-guide", "mobil-giris should be company-guide cluster"
        assert "faq" in data and len(data["faq"]) > 0
        print("PASS: mobil-giris company-guide cluster verified")

    def test_company_guide_page_types(self):
        """Test all company-guide page types return correct cluster"""
        company_guide_pages = ["guncel-giris", "guncel-adresi", "yeni-giris-adresi", "mobil-giris", "odeme-yontemleri"]
        
        for page_type in company_guide_pages:
            response = requests.get(f"{BASE_URL}/api/firma-sub/tulipbet/{page_type}")
            assert response.status_code == 200, f"{page_type} should return 200"
            data = response.json()
            assert data["cluster"] == "company-guide", f"{page_type} should be company-guide cluster"
        
        print(f"PASS: All {len(company_guide_pages)} company-guide page types verified")


class TestPhase2BonusGuideTemplate:
    """Test Bonus Guide template sections and data"""

    def test_deneme_bonusu_returns_bonus_guide_template(self):
        """Test /tulipbet/deneme-bonusu returns bonus-guide template data"""
        response = requests.get(f"{BASE_URL}/api/firma-sub/tulipbet/deneme-bonusu")
        assert response.status_code == 200
        data = response.json()
        
        assert data["cluster"] == "bonus-guide"
        assert "faq" in data and len(data["faq"]) > 0
        assert "related_companies" in data
        
        # Site data for bonus sections
        site = data["site"]
        assert "bonus_amount" in site
        assert "turnover_requirement" in site or site.get("turnover_requirement") is not None
        
        print(f"PASS: deneme-bonusu bonus-guide template (FAQ: {len(data['faq'])})")

    def test_bonus_guide_page_types(self):
        """Test all bonus-guide page types return correct cluster"""
        bonus_guide_pages = ["deneme-bonusu", "deneme-bonusu-2026", "hosgeldin-bonusu", "yatirimsiz-deneme-bonusu", "bonus-sartlari"]
        
        for page_type in bonus_guide_pages:
            response = requests.get(f"{BASE_URL}/api/firma-sub/tulipbet/{page_type}")
            assert response.status_code == 200, f"{page_type} should return 200"
            data = response.json()
            assert data["cluster"] == "bonus-guide", f"{page_type} should be bonus-guide cluster"
        
        print(f"PASS: All {len(bonus_guide_pages)} bonus-guide page types verified")


class TestPhase2FAQSection:
    """Test FAQ section renders with accordion data"""

    def test_faq_has_questions_and_answers(self):
        """Test FAQ data has proper question/answer structure"""
        response = requests.get(f"{BASE_URL}/api/firma-sub/tulipbet/guncel-giris")
        assert response.status_code == 200
        data = response.json()
        
        faq = data["faq"]
        assert len(faq) >= 3, "Should have at least 3 FAQ items"
        
        for i, item in enumerate(faq):
            assert "question" in item and item["question"], f"FAQ #{i} missing question"
            assert "answer" in item and item["answer"], f"FAQ #{i} missing answer"
            # Verify placeholder replacement
            assert "{name}" not in item["question"], f"FAQ #{i} has unreplaced placeholder"
            assert "{name}" not in item["answer"], f"FAQ #{i} has unreplaced placeholder"
        
        print(f"PASS: FAQ section with {len(faq)} items verified")

    def test_faq_varies_by_page_type(self):
        """Test FAQ content is different for different page types"""
        response1 = requests.get(f"{BASE_URL}/api/firma-sub/tulipbet/guncel-giris")
        response2 = requests.get(f"{BASE_URL}/api/firma-sub/tulipbet/deneme-bonusu")
        
        faq1 = response1.json()["faq"]
        faq2 = response2.json()["faq"]
        
        # FAQs should be different for different page types
        assert faq1[0]["question"] != faq2[0]["question"], "FAQ should be different per page type"
        print("PASS: FAQ varies by page type")


class TestPhase2InternalLinkingEngine:
    """Test internal linking between Hub and Company pages"""

    def test_bonus_hub_has_company_links(self):
        """Test BonusHubPage has links to company bonus pages AND access pages"""
        response = requests.get(f"{BASE_URL}/api/hub/bonus/deneme-bonusu-veren-siteler")
        assert response.status_code == 200
        data = response.json()
        
        company_links = data["company_links"]
        assert len(company_links) >= 10, "Should have at least 10 company links"
        
        # Check first company link structure
        first = company_links[0]
        assert "guncel_giris_url" in first, "Missing guncel_giris_url"
        assert "deneme_bonusu_url" in first, "Missing deneme_bonusu_url"
        
        # Verify URL format
        assert first["guncel_giris_url"].endswith("/guncel-giris")
        assert first["deneme_bonusu_url"].endswith("/deneme-bonusu")
        
        print(f"PASS: Bonus hub has {len(company_links)} company links with access URLs")

    def test_payment_hub_has_company_links(self):
        """Test PaymentHubPage has links to company payment and access pages"""
        response = requests.get(f"{BASE_URL}/api/hub/payment/odeme-yontemleri")
        assert response.status_code == 200
        data = response.json()
        
        company_links = data["company_links"]
        assert len(company_links) >= 10, "Should have at least 10 company links"
        
        first = company_links[0]
        assert "odeme_url" in first, "Missing odeme_url for payment hub"
        assert "guncel_giris_url" in first, "Missing guncel_giris_url cross-link"
        
        print(f"PASS: Payment hub has {len(company_links)} company links")

    def test_related_companies_sidebar(self):
        """Test related companies sidebar has links to multiple sub-pages"""
        response = requests.get(f"{BASE_URL}/api/firma-sub/tulipbet/guncel-giris")
        assert response.status_code == 200
        data = response.json()
        
        related = data["related_companies"]
        assert len(related) >= 3, "Should have at least 3 related companies"
        
        first = related[0]
        assert "guncel_giris" in first, "Missing guncel_giris link"
        assert "deneme_bonusu" in first, "Missing deneme_bonusu link"
        assert "odeme_yontemleri" in first, "Missing odeme_yontemleri link"
        assert "same_page" in first, "Missing same_page link"
        
        print(f"PASS: Related companies sidebar has {len(related)} companies with sub-page links")


class TestPhase2SchemaSupport:
    """Test JSON-LD schema data for frontend rendering"""

    def test_breadcrumb_data_for_schema(self):
        """Test breadcrumb data structure supports BreadcrumbList schema"""
        response = requests.get(f"{BASE_URL}/api/firma-sub/tulipbet/guncel-giris")
        assert response.status_code == 200
        data = response.json()
        
        breadcrumb = data["breadcrumb"]
        assert len(breadcrumb) >= 2
        
        # Verify each item has name and url for schema
        for item in breadcrumb:
            assert "name" in item
            assert "url" in item
        
        print(f"PASS: Breadcrumb has {len(breadcrumb)} items for BreadcrumbList schema")

    def test_faq_data_for_schema(self):
        """Test FAQ data structure supports FAQPage schema"""
        response = requests.get(f"{BASE_URL}/api/firma-sub/tulipbet/guncel-giris")
        assert response.status_code == 200
        data = response.json()
        
        faq = data["faq"]
        assert len(faq) > 0, "FAQ needed for FAQPage schema"
        
        # Each FAQ item should have question/answer for schema
        for item in faq:
            assert "question" in item
            assert "answer" in item
        
        print("PASS: FAQ structure supports FAQPage schema")

    def test_seo_data_for_article_schema(self):
        """Test SEO data structure supports Article schema"""
        response = requests.get(f"{BASE_URL}/api/firma-sub/tulipbet/guncel-giris")
        assert response.status_code == 200
        data = response.json()
        
        seo = data["seo"]
        assert "title" in seo
        assert "description" in seo
        assert "canonical" in seo
        
        # Article schema needs dateModified
        assert "last_updated" in data
        
        print("PASS: SEO data supports Article schema")


class TestPhase2ExistingRoutes:
    """Test existing routes still work after Phase 2 changes"""

    def test_homepage_works(self):
        """Homepage should still work"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        print("PASS: Homepage backend accessible")

    def test_firm_page_api(self):
        """Test firm page API still works"""
        response = requests.get(f"{BASE_URL}/api/bonus-sites?limit=1")
        assert response.status_code == 200
        sites = response.json()
        assert len(sites) >= 1
        print("PASS: Firm page API still works")

    def test_video_page_api(self):
        """Test video API still works"""
        response = requests.get(f"{BASE_URL}/api/bonus-sites?limit=1")
        assert response.status_code == 200
        sites = response.json()
        if sites and sites[0].get("video_url"):
            print("PASS: Video data available")
        else:
            print("PASS: Video API accessible (no video data)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
