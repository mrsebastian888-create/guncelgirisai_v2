"""
Test suite for SEO Assistant endpoints
Tests /api/seo/* endpoints for the Advanced SEO Assistant feature
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestSEODashboard:
    """SEO Dashboard endpoint tests"""
    
    def test_seo_dashboard_returns_200(self):
        """GET /api/seo/dashboard should return 200 and health score"""
        response = requests.get(f"{BASE_URL}/api/seo/dashboard")
        assert response.status_code == 200
        data = response.json()
        
        # Verify required fields
        assert "health_score" in data
        assert "total_articles" in data
        assert "issues" in data
        assert "recommendations" in data
        
        # Verify health_score is a valid number
        assert isinstance(data["health_score"], (int, float))
        assert 0 <= data["health_score"] <= 100
        print(f"✓ Dashboard health_score: {data['health_score']}")
    
    def test_seo_dashboard_with_domain_id(self):
        """GET /api/seo/dashboard with domain_id param"""
        response = requests.get(f"{BASE_URL}/api/seo/dashboard?domain_id=test-domain")
        assert response.status_code == 200
        data = response.json()
        assert "health_score" in data
        print("✓ Dashboard with domain_id works")


class TestKeywordResearch:
    """Keyword Research endpoint tests"""
    
    def test_keyword_research_basic(self):
        """POST /api/seo/keyword-research with keywords list"""
        payload = {
            "keywords": ["deneme bonusu", "bahis siteleri"],
            "niche": "bonus",
            "language": "tr"
        }
        response = requests.post(
            f"{BASE_URL}/api/seo/keyword-research",
            json=payload,
            timeout=60  # AI endpoints may take time
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should return either structured JSON or raw_analysis
        assert "keywords" in data or "raw_analysis" in data
        print(f"✓ Keyword research returned valid response")
        
        # If structured, verify format
        if "keywords" in data and isinstance(data["keywords"], list) and len(data["keywords"]) > 0:
            kw = data["keywords"][0]
            assert "keyword" in kw
            print(f"✓ First keyword analyzed: {kw.get('keyword')}")
    
    def test_keyword_research_single_keyword(self):
        """POST /api/seo/keyword-research with single keyword"""
        payload = {
            "keywords": ["canlı bahis"],
            "niche": "spor",
            "language": "tr"
        }
        response = requests.post(
            f"{BASE_URL}/api/seo/keyword-research",
            json=payload,
            timeout=60
        )
        assert response.status_code == 200
        print("✓ Single keyword research works")


class TestSiteAudit:
    """Site Audit endpoint tests"""
    
    def test_site_audit_returns_structured_data(self):
        """POST /api/seo/site-audit returns overall_score and categories"""
        payload = {"domain_id": None, "url": None}
        response = requests.post(
            f"{BASE_URL}/api/seo/site-audit",
            json=payload,
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should have overall_score and categories
        assert "overall_score" in data or "raw_analysis" in data
        if "categories" in data and isinstance(data["categories"], list):
            cat = data["categories"][0]
            assert "name" in cat
            assert "score" in cat
            print(f"✓ First audit category: {cat.get('name')} - Score: {cat.get('score')}")
        print("✓ Site audit completed successfully")


class TestCompetitorAnalysis:
    """Competitor Deep Analysis endpoint tests"""
    
    def test_competitor_analysis(self):
        """POST /api/seo/competitor-deep returns competitor_profile and action_plan"""
        payload = {
            "competitor_url": "https://example-competitor.com",
            "our_domain": "guncelgiris.ai"
        }
        response = requests.post(
            f"{BASE_URL}/api/seo/competitor-deep",
            json=payload,
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should return competitor_profile or raw_analysis
        assert "competitor_profile" in data or "raw_analysis" in data
        if "competitor_profile" in data:
            assert "domain" in data["competitor_profile"]
            print(f"✓ Competitor profile for: {data['competitor_profile'].get('domain')}")
        
        if "action_plan" in data and isinstance(data["action_plan"], list):
            print(f"✓ Action plan items: {len(data['action_plan'])}")
        print("✓ Competitor analysis completed")


class TestMetaGenerator:
    """Meta Generator endpoint tests"""
    
    def test_meta_generator_returns_options(self):
        """POST /api/seo/meta-generator returns meta title/description options"""
        payload = {
            "topic": "Deneme Bonusu Veren Siteler 2026",
            "page_type": "article",
            "keywords": ["deneme bonusu", "bonus"]
        }
        response = requests.post(
            f"{BASE_URL}/api/seo/meta-generator",
            json=payload,
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should return options array or raw_result
        assert "options" in data or "raw_result" in data
        if "options" in data and isinstance(data["options"], list) and len(data["options"]) > 0:
            opt = data["options"][0]
            assert "meta_title" in opt
            assert "meta_description" in opt
            print(f"✓ Meta title generated: {opt.get('meta_title')[:50]}...")
        print("✓ Meta generator completed")


class TestContentOptimizer:
    """Content Optimizer endpoint tests"""
    
    def test_content_optimizer_with_content(self):
        """POST /api/seo/content-optimizer returns optimization suggestions"""
        payload = {
            "title": "Deneme Bonusu Rehberi",
            "content": "Bu makalede deneme bonusu hakkında bilgi verilecektir. Deneme bonusu, bahis sitelerinin yeni üyelerine sunduğu bir promosyon türüdür. Bu bonuslar sayesinde kullanıcılar risk almadan bahis yapabilirler.",
            "target_keyword": "deneme bonusu"
        }
        response = requests.post(
            f"{BASE_URL}/api/seo/content-optimizer",
            json=payload,
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should return optimization suggestions or raw_result
        has_valid_response = (
            "optimized_title" in data or 
            "content_improvements" in data or 
            "raw_result" in data
        )
        assert has_valid_response
        
        if "optimized_title" in data:
            print(f"✓ Optimized title: {data.get('optimized_title')}")
        print("✓ Content optimizer completed")
    
    def test_content_optimizer_requires_content(self):
        """POST /api/seo/content-optimizer without content returns 400"""
        payload = {
            "title": "",
            "content": "",
            "target_keyword": ""
        }
        response = requests.post(
            f"{BASE_URL}/api/seo/content-optimizer",
            json=payload,
            timeout=30
        )
        # Should return 400 because content is required
        assert response.status_code == 400
        print("✓ Content optimizer validates required fields")


class TestContentScore:
    """Content Score endpoint tests"""
    
    def test_content_score(self):
        """POST /api/seo/content-score returns scoring data"""
        payload = {
            "title": "En İyi Deneme Bonusu Siteleri",
            "content": "Türkiye'deki en güvenilir bahis sitelerinin sunduğu deneme bonuslarını inceliyoruz. Bu rehberde çevrim şartları, bonus miktarları ve kullanım koşulları hakkında detaylı bilgi bulacaksınız. Deneme bonusu almak için yapmanız gereken adımları açıklıyoruz.",
            "target_keyword": "deneme bonusu siteleri"
        }
        response = requests.post(
            f"{BASE_URL}/api/seo/content-score",
            json=payload,
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should have scoring data
        assert "overall_score" in data or "raw_analysis" in data or "word_count" in data
        if "word_count" in data:
            print(f"✓ Word count: {data.get('word_count')}")
        if "overall_score" in data:
            print(f"✓ Content score: {data.get('overall_score')}")
        print("✓ Content scoring completed")


class TestInternalLinks:
    """Internal Links endpoint tests"""
    
    def test_internal_links_suggestions(self):
        """POST /api/seo/internal-links returns link suggestions"""
        payload = {
            "content": "Deneme bonusu hakkında her şeyi bu makalede bulabilirsiniz. Hoşgeldin bonusu ve yatırım bonusu arasındaki farkları öğrenin. Canlı bahis stratejileri için diğer makalelerimize göz atın."
        }
        response = requests.post(
            f"{BASE_URL}/api/seo/internal-links",
            json=payload,
            timeout=60
        )
        assert response.status_code == 200
        data = response.json()
        
        # Should return suggestions or raw_result
        assert "suggestions" in data or "raw_result" in data
        if "suggestions" in data and isinstance(data["suggestions"], list):
            print(f"✓ Internal link suggestions count: {len(data['suggestions'])}")
        print("✓ Internal links analysis completed")


class TestSEOReports:
    """SEO Reports endpoint tests"""
    
    def test_get_reports_list(self):
        """GET /api/seo/reports returns saved reports list"""
        response = requests.get(f"{BASE_URL}/api/seo/reports")
        assert response.status_code == 200
        data = response.json()
        
        assert "reports" in data
        assert "count" in data
        assert isinstance(data["reports"], list)
        print(f"✓ Reports count: {data.get('count')}")
    
    def test_get_reports_with_filter(self):
        """GET /api/seo/reports with report_type filter"""
        response = requests.get(f"{BASE_URL}/api/seo/reports?report_type=keyword_research")
        assert response.status_code == 200
        data = response.json()
        assert "reports" in data
        print(f"✓ Filtered reports count: {data.get('count')}")
    
    def test_delete_report_nonexistent(self):
        """DELETE /api/seo/reports/{id} with non-existent id"""
        response = requests.delete(f"{BASE_URL}/api/seo/reports/non-existent-id-12345")
        # Should return 200 even if not found (MongoDB delete returns success)
        assert response.status_code == 200
        print("✓ Delete non-existent report handled gracefully")


class TestAdminLogin:
    """Admin authentication tests"""
    
    def test_admin_login_success(self):
        """POST /api/auth/login with valid credentials"""
        payload = {
            "username": "admin",
            "password": "Mm18010812**!!"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
        assert response.status_code == 200
        data = response.json()
        
        assert "token" in data
        assert "username" in data
        assert data["username"] == "admin"
        print(f"✓ Admin login successful, token received")
        return data["token"]
    
    def test_admin_login_invalid_password(self):
        """POST /api/auth/login with invalid password returns 401"""
        payload = {
            "username": "admin",
            "password": "wrongpassword"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
        assert response.status_code == 401
        print("✓ Invalid password correctly rejected")
    
    def test_admin_login_invalid_username(self):
        """POST /api/auth/login with invalid username returns 401"""
        payload = {
            "username": "notadmin",
            "password": "somepassword"
        }
        response = requests.post(f"{BASE_URL}/api/auth/login", json=payload)
        assert response.status_code == 401
        print("✓ Invalid username correctly rejected")


class TestHomepageEndpoints:
    """Homepage data endpoints tests"""
    
    def test_homepage_bonus_sites(self):
        """GET /api/bonus-sites returns bonus sites for homepage"""
        response = requests.get(f"{BASE_URL}/api/bonus-sites")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Bonus sites count: {len(data)}")
    
    def test_homepage_articles(self):
        """GET /api/articles returns articles for homepage"""
        response = requests.get(f"{BASE_URL}/api/articles")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Articles count: {len(data)}")
    
    def test_health_endpoint(self):
        """GET /health returns ok"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "ok"
        print("✓ Health check passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
