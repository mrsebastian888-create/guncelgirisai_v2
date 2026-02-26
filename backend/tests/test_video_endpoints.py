"""
Video and Sitemap Endpoints Tests - Iteration 12
Tests: Video API, AMP Video, Video Sitemaps, and regression checks for existing AMP
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestVideoAPI:
    """Tests for firm video API endpoints"""
    
    def test_firma_video_api_returns_200(self):
        """GET /api/firma/casibom-guncelgiris/video should return 200 with required fields"""
        response = requests.get(f"{BASE_URL}/api/firma/casibom-guncelgiris/video")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        # Check required fields
        assert "site" in data, "Response should contain 'site'"
        assert "video" in data, "Response should contain 'video'"
        assert "canonical_url" in data, "Response should contain 'canonical_url'"
        assert "amp_url" in data, "Response should contain 'amp_url'"
        
        # Check site fields
        assert "name" in data["site"], "site should have 'name'"
        assert "slug" in data["site"], "site should have 'slug'"
        assert "bonus_amount" in data["site"], "site should have 'bonus_amount'"
        
        # Check video fields
        assert "video_url" in data["video"], "video should have 'video_url'"
        assert "video_embed_url" in data["video"], "video should have 'video_embed_url'"
        assert "video_title" in data["video"], "video should have 'video_title'"
        assert "video_description" in data["video"], "video should have 'video_description'"
        
        print(f"✓ Video API returns correct structure: site={data['site']['name']}")
    
    def test_firma_video_canonical_url_format(self):
        """Video API should return proper canonical URL"""
        response = requests.get(f"{BASE_URL}/api/firma/casibom-guncelgiris/video")
        data = response.json()
        
        assert "/video" in data["canonical_url"], "canonical_url should contain /video path"
        print(f"✓ Canonical URL: {data['canonical_url']}")
    
    def test_firma_video_amp_url_format(self):
        """Video API should return proper AMP URL"""
        response = requests.get(f"{BASE_URL}/api/firma/casibom-guncelgiris/video")
        data = response.json()
        
        assert "/api/amp-video/" in data["amp_url"], "amp_url should contain /api/amp-video/ path"
        print(f"✓ AMP URL: {data['amp_url']}")


class TestAMPVideoEndpoint:
    """Tests for AMP video HTML endpoint"""
    
    def test_amp_video_returns_html(self):
        """GET /api/amp-video/casibom-guncelgiris should return AMP HTML"""
        response = requests.get(f"{BASE_URL}/api/amp-video/casibom-guncelgiris")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        content = response.text
        # AMP required elements
        assert "<!doctype html>" in content.lower() or "<!DOCTYPE html>" in content, "Should have HTML doctype"
        assert "<html amp" in content or "<html ⚡" in content, "Should have AMP html tag"
        assert "cdn.ampproject.org/v0.js" in content, "Should include AMP runtime script"
        assert "amp-boilerplate" in content, "Should have AMP boilerplate style"
        
        print("✓ AMP Video page has all required AMP elements")
    
    def test_amp_video_has_canonical_link(self):
        """AMP video should have canonical link to regular video page"""
        response = requests.get(f"{BASE_URL}/api/amp-video/casibom-guncelgiris")
        content = response.text
        
        assert 'rel="canonical"' in content, "Should have canonical link"
        assert '/video' in content, "Canonical should point to /video page"
        print("✓ AMP Video has canonical link")
    
    def test_amp_video_has_video_schema(self):
        """AMP video should have VideoObject schema.org markup"""
        response = requests.get(f"{BASE_URL}/api/amp-video/casibom-guncelgiris")
        content = response.text
        
        assert '"@type": "VideoObject"' in content or '"@type":"VideoObject"' in content, "Should have VideoObject schema"
        print("✓ AMP Video has VideoObject schema")


class TestSitemapIndex:
    """Tests for sitemap index"""
    
    def test_sitemap_index_returns_xml(self):
        """GET /api/sitemap.xml should return valid sitemap index"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        content = response.text
        assert "<sitemapindex" in content, "Should be a sitemap index"
        print("✓ Sitemap index is valid")
    
    def test_sitemap_index_has_videos_sitemap(self):
        """Sitemap index should include videos sitemap"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        content = response.text
        
        assert "sitemap-videos.xml" in content, "Should include sitemap-videos.xml"
        print("✓ Sitemap index includes sitemap-videos.xml")
    
    def test_sitemap_index_has_amp_videos_sitemap(self):
        """Sitemap index should include AMP videos sitemap"""
        response = requests.get(f"{BASE_URL}/api/sitemap.xml")
        content = response.text
        
        assert "sitemap-amp-videos.xml" in content, "Should include sitemap-amp-videos.xml"
        print("✓ Sitemap index includes sitemap-amp-videos.xml")


class TestVideoSitemap:
    """Tests for video sitemap"""
    
    def test_video_sitemap_returns_xml(self):
        """GET /api/sitemap-videos.xml should return valid XML"""
        response = requests.get(f"{BASE_URL}/api/sitemap-videos.xml")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        content = response.text
        assert "<urlset" in content, "Should be a urlset sitemap"
        print("✓ Video sitemap is valid XML")
    
    def test_video_sitemap_has_video_urls(self):
        """Video sitemap should contain /{slug}/video URLs"""
        response = requests.get(f"{BASE_URL}/api/sitemap-videos.xml")
        content = response.text
        
        assert "/video</loc>" in content, "Should contain /video URLs"
        print("✓ Video sitemap contains video page URLs")


class TestAMPVideoSitemap:
    """Tests for AMP video sitemap"""
    
    def test_amp_video_sitemap_returns_xml(self):
        """GET /api/sitemap-amp-videos.xml should return valid XML"""
        response = requests.get(f"{BASE_URL}/api/sitemap-amp-videos.xml")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        content = response.text
        assert "<urlset" in content, "Should be a urlset sitemap"
        print("✓ AMP Video sitemap is valid XML")
    
    def test_amp_video_sitemap_has_amp_urls(self):
        """AMP video sitemap should contain /api/amp-video/ URLs"""
        response = requests.get(f"{BASE_URL}/api/sitemap-amp-videos.xml")
        content = response.text
        
        assert "/api/amp-video/" in content, "Should contain /api/amp-video/ URLs"
        print("✓ AMP Video sitemap contains AMP video URLs")


class TestExistingAMPRegression:
    """Regression tests for existing AMP endpoints"""
    
    def test_existing_amp_endpoint_still_works(self):
        """GET /api/amp/casibom-guncelgiris should still work"""
        response = requests.get(f"{BASE_URL}/api/amp/casibom-guncelgiris")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        content = response.text
        assert "<html amp" in content or "<html ⚡" in content, "Should be AMP HTML"
        print("✓ Existing AMP endpoint works")
    
    def test_existing_amp_sitemap_still_works(self):
        """GET /api/sitemap-amp.xml should still work"""
        response = requests.get(f"{BASE_URL}/api/sitemap-amp.xml")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        content = response.text
        assert "/api/amp/" in content, "Should contain AMP URLs"
        print("✓ Existing AMP sitemap works")
    
    def test_existing_firma_endpoint_still_works(self):
        """GET /api/firma/casibom-guncelgiris should still work"""
        response = requests.get(f"{BASE_URL}/api/firma/casibom-guncelgiris")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "site" in data, "Should contain site data"
        assert "name" in data["site"], "Site should have name"
        print(f"✓ Existing firma endpoint works: {data['site']['name']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
