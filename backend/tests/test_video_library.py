"""
Video Library API Tests - Video Gallery & Player System
Tests: /api/videos/* endpoints for gallery, player, upload, register, delete
Includes: Category filtering, company filtering, auth protection, view count increment
"""

import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')


class TestVideoList:
    """Tests for GET /api/videos - Video list endpoint for gallery page"""
    
    def test_videos_list_returns_200(self):
        """GET /api/videos should return 200 with required structure"""
        response = requests.get(f"{BASE_URL}/api/videos")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "videos" in data, "Response should have 'videos' array"
        assert "total" in data, "Response should have 'total' count"
        assert "limit" in data, "Response should have 'limit'"
        assert "offset" in data, "Response should have 'offset'"
        assert isinstance(data["videos"], list), "videos should be a list"
        print(f"✓ Video list returns {data['total']} videos")
    
    def test_videos_list_has_video_fields(self):
        """Videos in list should have required fields"""
        response = requests.get(f"{BASE_URL}/api/videos")
        data = response.json()
        
        if len(data["videos"]) > 0:
            video = data["videos"][0]
            required_fields = ["video_id", "title", "source", "view_count", "created_at", "is_published"]
            for field in required_fields:
                assert field in video, f"Video should have '{field}' field"
            print(f"✓ Video has all required fields: {video['title']}")
        else:
            pytest.skip("No videos in list to verify fields")
    
    def test_videos_filter_by_category(self):
        """GET /api/videos?category=bonus should filter by category"""
        response = requests.get(f"{BASE_URL}/api/videos?category=bonus")
        assert response.status_code == 200
        
        data = response.json()
        # All videos should be in bonus category
        for video in data["videos"]:
            assert video["category"] == "bonus", f"Video {video['video_id']} should have category 'bonus'"
        print(f"✓ Category filter works: {data['total']} bonus videos")
    
    def test_videos_filter_by_company_slug(self):
        """GET /api/videos?company_slug=tulipbet should filter by company"""
        response = requests.get(f"{BASE_URL}/api/videos?company_slug=tulipbet")
        assert response.status_code == 200
        
        data = response.json()
        # All videos should belong to tulipbet
        for video in data["videos"]:
            assert video["company_slug"] == "tulipbet", f"Video {video['video_id']} should have company_slug 'tulipbet'"
        print(f"✓ Company filter works: {data['total']} tulipbet videos")
    
    def test_videos_limit_parameter(self):
        """GET /api/videos?limit=1 should limit results"""
        response = requests.get(f"{BASE_URL}/api/videos?limit=1")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data["videos"]) <= 1, "Should return at most 1 video"
        assert data["limit"] == 1, "Limit should be 1"
        print(f"✓ Limit parameter works: returned {len(data['videos'])} video(s)")


class TestVideoDetail:
    """Tests for GET /api/videos/{videoId} - Video detail endpoint"""
    
    def get_first_video_id(self):
        """Helper to get first video ID"""
        response = requests.get(f"{BASE_URL}/api/videos?limit=1")
        if response.status_code == 200:
            data = response.json()
            if data["videos"]:
                return data["videos"][0]["video_id"]
        return None
    
    def test_video_detail_returns_200(self):
        """GET /api/videos/{videoId} should return video detail"""
        video_id = self.get_first_video_id()
        if not video_id:
            pytest.skip("No videos available for detail test")
        
        response = requests.get(f"{BASE_URL}/api/videos/{video_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert "video" in data, "Response should have 'video' object"
        assert "related" in data, "Response should have 'related' array"
        assert "company" in data, "Response should have 'company' (null or object)"
        print(f"✓ Video detail returns: {data['video']['title']}")
    
    def test_video_detail_has_required_fields(self):
        """Video detail should have all required fields"""
        video_id = self.get_first_video_id()
        if not video_id:
            pytest.skip("No videos available")
        
        response = requests.get(f"{BASE_URL}/api/videos/{video_id}")
        data = response.json()
        video = data["video"]
        
        required_fields = [
            "video_id", "title", "description", "source", "category",
            "view_count", "created_at", "is_published", "duration_seconds"
        ]
        for field in required_fields:
            assert field in video, f"Video detail should have '{field}'"
        print(f"✓ Video detail has all required fields")
    
    def test_video_detail_increments_view_count(self):
        """GET /api/videos/{videoId} should increment view_count"""
        video_id = self.get_first_video_id()
        if not video_id:
            pytest.skip("No videos available")
        
        # First request - get initial view count
        response1 = requests.get(f"{BASE_URL}/api/videos/{video_id}")
        initial_count = response1.json()["video"]["view_count"]
        
        # Second request - view count should increment
        response2 = requests.get(f"{BASE_URL}/api/videos/{video_id}")
        new_count = response2.json()["video"]["view_count"]
        
        assert new_count > initial_count, "View count should increment on each GET"
        print(f"✓ View count incremented: {initial_count} -> {new_count}")
    
    def test_video_detail_returns_related_videos(self):
        """Video detail should return related videos from same company"""
        video_id = self.get_first_video_id()
        if not video_id:
            pytest.skip("No videos available")
        
        response = requests.get(f"{BASE_URL}/api/videos/{video_id}")
        data = response.json()
        
        assert isinstance(data["related"], list), "related should be a list"
        # Related videos should not include current video
        for rv in data["related"]:
            assert rv["video_id"] != video_id, "Related should not include current video"
        print(f"✓ Related videos: {len(data['related'])} found")
    
    def test_video_detail_returns_company_info(self):
        """Video detail should return company info if linked"""
        video_id = self.get_first_video_id()
        if not video_id:
            pytest.skip("No videos available")
        
        response = requests.get(f"{BASE_URL}/api/videos/{video_id}")
        data = response.json()
        video = data["video"]
        company = data["company"]
        
        # If video has company_slug, company should be populated
        if video.get("company_slug"):
            assert company is not None, "Company should be returned if video has company_slug"
            if company:
                assert "name" in company, "Company should have 'name'"
                assert "logo_url" in company, "Company should have 'logo_url'"
                print(f"✓ Company info: {company['name']}")
        else:
            print("✓ No company linked to this video")
    
    def test_video_detail_404_for_nonexistent(self):
        """GET /api/videos/{invalid} should return 404"""
        response = requests.get(f"{BASE_URL}/api/videos/nonexistent-video-id-12345")
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Returns 404 for nonexistent video")


class TestVideoRegister:
    """Tests for POST /api/videos/register - Register external/AI video"""
    
    def get_auth_token(self):
        """Get admin JWT token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "123123.."
        })
        if response.status_code == 200:
            return response.json().get("token")
        return None
    
    def test_register_requires_auth(self):
        """POST /api/videos/register without auth should return 401"""
        response = requests.post(f"{BASE_URL}/api/videos/register", json={
            "title": "Test Video",
            "source": "external"
        })
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Register endpoint requires authentication")
    
    def test_register_with_auth_creates_video(self):
        """POST /api/videos/register with auth should create video"""
        token = self.get_auth_token()
        if not token:
            pytest.skip("Could not authenticate")
        
        test_id = str(uuid.uuid4())[:8]
        response = requests.post(
            f"{BASE_URL}/api/videos/register",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": f"TEST_Video_{test_id}",
                "description": "Test video description",
                "source": "ai_generated",
                "external_url": "https://example.com/video.mp4",
                "category": "general",
                "company_slug": "tulipbet",
                "company_name": "Tulipbet",
                "duration_seconds": 30,
                "tags": ["test"]
            }
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert data.get("registered") is True, "Should return registered: true"
        assert "video" in data, "Should return video object"
        assert data["video"]["title"] == f"TEST_Video_{test_id}"
        print(f"✓ Video registered: {data['video']['video_id']}")
        
        # Store video_id for cleanup
        return data["video"]["video_id"]


class TestVideoDelete:
    """Tests for DELETE /api/videos/{videoId} - Soft delete video"""
    
    def get_auth_token(self):
        """Get admin JWT token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "123123.."
        })
        if response.status_code == 200:
            return response.json().get("token")
        return None
    
    def create_test_video(self, token):
        """Create a test video for deletion test"""
        test_id = str(uuid.uuid4())[:8]
        response = requests.post(
            f"{BASE_URL}/api/videos/register",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": f"TEST_DeleteMe_{test_id}",
                "source": "external",
                "external_url": "https://example.com/delete-test.mp4"
            }
        )
        if response.status_code == 200:
            return response.json()["video"]["video_id"]
        return None
    
    def test_delete_requires_auth(self):
        """DELETE /api/videos/{id} without auth should return 401"""
        response = requests.delete(f"{BASE_URL}/api/videos/some-video-id")
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Delete endpoint requires authentication")
    
    def test_delete_with_auth_soft_deletes(self):
        """DELETE /api/videos/{id} with auth should soft delete"""
        token = self.get_auth_token()
        if not token:
            pytest.skip("Could not authenticate")
        
        # Create a test video first
        video_id = self.create_test_video(token)
        if not video_id:
            pytest.skip("Could not create test video")
        
        # Delete the video
        response = requests.delete(
            f"{BASE_URL}/api/videos/{video_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert data.get("deleted") is True, "Should return deleted: true"
        print(f"✓ Video soft deleted: {video_id}")
        
        # Verify video is no longer accessible
        check = requests.get(f"{BASE_URL}/api/videos/{video_id}")
        assert check.status_code == 404, "Deleted video should return 404"
        print("✓ Deleted video returns 404 on GET")
    
    def test_delete_nonexistent_returns_404(self):
        """DELETE /api/videos/{invalid} should return 404"""
        token = self.get_auth_token()
        if not token:
            pytest.skip("Could not authenticate")
        
        response = requests.delete(
            f"{BASE_URL}/api/videos/nonexistent-video-99999",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404, f"Expected 404, got {response.status_code}"
        print("✓ Delete nonexistent video returns 404")


class TestVideoUpload:
    """Tests for POST /api/videos/upload - Upload video file"""
    
    def get_auth_token(self):
        """Get admin JWT token"""
        response = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "123123.."
        })
        if response.status_code == 200:
            return response.json().get("token")
        return None
    
    def test_upload_requires_auth(self):
        """POST /api/videos/upload without auth should return 401"""
        # Create a tiny fake file
        files = {"file": ("test.mp4", b"fake video content", "video/mp4")}
        response = requests.post(f"{BASE_URL}/api/videos/upload", files=files)
        assert response.status_code == 401, f"Expected 401, got {response.status_code}"
        print("✓ Upload endpoint requires authentication")


class TestVideoFile:
    """Tests for GET /api/videos/{videoId}/file - Stream video file"""
    
    def get_uploaded_video_id(self):
        """Get a video that has storage_path (uploaded)"""
        response = requests.get(f"{BASE_URL}/api/videos")
        if response.status_code == 200:
            data = response.json()
            for video in data["videos"]:
                if video.get("storage_path"):
                    return video["video_id"]
        return None
    
    def test_video_file_404_for_nonexistent(self):
        """GET /api/videos/{invalid}/file should return 404"""
        response = requests.get(f"{BASE_URL}/api/videos/nonexistent-id/file")
        assert response.status_code == 404
        print("✓ Video file returns 404 for nonexistent video")
    
    def test_video_file_404_for_external_video(self):
        """GET /api/videos/{external}/file should return 404 (no storage_path)"""
        # Get any external video (has no storage_path)
        response = requests.get(f"{BASE_URL}/api/videos")
        if response.status_code == 200:
            data = response.json()
            for video in data["videos"]:
                if not video.get("storage_path"):
                    file_response = requests.get(f"{BASE_URL}/api/videos/{video['video_id']}/file")
                    assert file_response.status_code == 404, "External video file should return 404"
                    print(f"✓ External video file returns 404 (no storage_path)")
                    return
        pytest.skip("No external videos to test")


class TestExistingRoutesRegression:
    """Regression tests to ensure existing routes still work"""
    
    def test_homepage_api_works(self):
        """GET /api/bonus-sites should still work"""
        response = requests.get(f"{BASE_URL}/api/bonus-sites?limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        print(f"✓ Homepage bonus sites API works: {len(data)} sites")
    
    def test_deneme_bonusu_api_works(self):
        """GET /api/categories should still work"""
        response = requests.get(f"{BASE_URL}/api/categories")
        assert response.status_code == 200
        print("✓ Categories API works")
    
    def test_tulipbet_guncel_giris_api_works(self):
        """GET /api/firma-sub/tulipbet/guncel-giris should still work"""
        response = requests.get(f"{BASE_URL}/api/firma-sub/tulipbet/guncel-giris")
        assert response.status_code == 200
        data = response.json()
        assert "site" in data
        print(f"✓ Tulipbet guncel giris API works")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
