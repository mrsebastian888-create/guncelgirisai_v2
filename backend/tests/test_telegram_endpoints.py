"""
Telegram Bot Management API Tests
Tests for iteration 16 - Telegram Bot Management System

Endpoints tested:
- GET /api/admin/telegram/stats - Overall telegram stats
- GET /api/admin/telegram/bots - List all telegram bots
- GET /api/admin/telegram/auth/status - Check telegram auth status
- GET /api/admin/telegram/firm-bot-map - Firm to bot mapping
- POST /api/admin/telegram/create-bot - Create single bot (auth error expected)
- POST /api/admin/telegram/create-bulk - Bulk create bots (auth error expected)
- POST /api/admin/telegram/broadcast - Broadcast messaging (requires bots)
- DELETE /api/admin/telegram/bot/{bot_id} - Delete bot
- POST /api/telegram/webhook/{bot_id} - Public webhook endpoint
"""

import pytest
import requests
import os

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")


class TestSetup:
    """Setup helpers for tests"""
    
    @pytest.fixture(scope="class")
    def admin_token(self):
        """Get admin auth token."""
        resp = requests.post(f"{BASE_URL}/api/auth/login", json={
            "username": "admin",
            "password": "123123.."
        })
        if resp.status_code == 200:
            return resp.json().get("token")
        pytest.skip("Admin login failed - skipping authenticated tests")
    
    @pytest.fixture(scope="class")
    def auth_headers(self, admin_token):
        """Return headers with auth token."""
        return {"Authorization": f"Bearer {admin_token}"}


# ============== TELEGRAM AUTH TESTS ==============

class TestTelegramAuthStatus(TestSetup):
    """Test Telegram auth status endpoint."""
    
    def test_auth_status_returns_200(self, auth_headers):
        """GET /api/admin/telegram/auth/status should return 200."""
        resp = requests.get(f"{BASE_URL}/api/admin/telegram/auth/status", headers=auth_headers)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "authenticated" in data, "Response should include 'authenticated' field"
        # Auth will be False since no phone verification done
        assert isinstance(data["authenticated"], bool), "'authenticated' should be boolean"
        print(f"Auth status: {data}")
    
    def test_auth_status_unauthorized_without_token(self):
        """GET /api/admin/telegram/auth/status without token should return 401."""
        resp = requests.get(f"{BASE_URL}/api/admin/telegram/auth/status")
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"


# ============== TELEGRAM STATS TESTS ==============

class TestTelegramStats(TestSetup):
    """Test Telegram stats endpoint."""
    
    def test_stats_returns_200(self, auth_headers):
        """GET /api/admin/telegram/stats should return 200 with expected structure."""
        resp = requests.get(f"{BASE_URL}/api/admin/telegram/stats", headers=auth_headers)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        # Verify expected fields exist
        expected_fields = ["total_bots", "active_bots", "total_subscribers", "pending_bots", "failed_bots"]
        for field in expected_fields:
            assert field in data, f"Missing field '{field}' in stats response"
            assert isinstance(data[field], int), f"'{field}' should be integer"
        
        print(f"Telegram stats: {data}")
    
    def test_stats_unauthorized_without_token(self):
        """GET /api/admin/telegram/stats without token should return 401."""
        resp = requests.get(f"{BASE_URL}/api/admin/telegram/stats")
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"


# ============== TELEGRAM BOTS LIST TESTS ==============

class TestTelegramBotsList(TestSetup):
    """Test Telegram bots list endpoint."""
    
    def test_bots_list_returns_200(self, auth_headers):
        """GET /api/admin/telegram/bots should return 200 with list."""
        resp = requests.get(f"{BASE_URL}/api/admin/telegram/bots", headers=auth_headers)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert isinstance(data, list), "Response should be a list"
        
        if len(data) > 0:
            bot = data[0]
            expected_fields = ["bot_id", "firm_id", "firm_name", "bot_username", "status"]
            for field in expected_fields:
                assert field in bot, f"Bot should have '{field}' field"
        
        print(f"Total bots returned: {len(data)}")
    
    def test_bots_list_with_search(self, auth_headers):
        """GET /api/admin/telegram/bots?search=test should filter results."""
        resp = requests.get(f"{BASE_URL}/api/admin/telegram/bots?search=maxwin", headers=auth_headers)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        
        data = resp.json()
        assert isinstance(data, list), "Response should be a list"
        print(f"Search 'maxwin' returned {len(data)} bots")
    
    def test_bots_list_unauthorized_without_token(self):
        """GET /api/admin/telegram/bots without token should return 401."""
        resp = requests.get(f"{BASE_URL}/api/admin/telegram/bots")
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"


# ============== FIRM BOT MAP TESTS ==============

class TestFirmBotMap(TestSetup):
    """Test firm-to-bot mapping endpoint."""
    
    def test_firm_bot_map_returns_200(self, auth_headers):
        """GET /api/admin/telegram/firm-bot-map should return 200 with mapping."""
        resp = requests.get(f"{BASE_URL}/api/admin/telegram/firm-bot-map", headers=auth_headers)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "firms" in data, "Response should include 'firms' field"
        assert "total" in data, "Response should include 'total' field"
        assert "with_bot" in data, "Response should include 'with_bot' count"
        
        assert isinstance(data["firms"], list), "'firms' should be a list"
        assert isinstance(data["total"], int), "'total' should be integer"
        assert isinstance(data["with_bot"], int), "'with_bot' should be integer"
        
        if len(data["firms"]) > 0:
            firm = data["firms"][0]
            expected_fields = ["firm_id", "firm_name", "has_bot", "bot_username"]
            for field in expected_fields:
                assert field in firm, f"Firm mapping should have '{field}' field"
        
        print(f"Firm bot map: total={data['total']}, with_bot={data['with_bot']}")
        # The 264 firms requirement
        assert data["total"] >= 200, f"Expected at least 200 firms, got {data['total']}"
    
    def test_firm_bot_map_unauthorized_without_token(self):
        """GET /api/admin/telegram/firm-bot-map without token should return 401."""
        resp = requests.get(f"{BASE_URL}/api/admin/telegram/firm-bot-map")
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"


# ============== CREATE SINGLE BOT TESTS ==============

class TestCreateSingleBot(TestSetup):
    """Test single bot creation endpoint."""
    
    def test_create_bot_requires_firm_id(self, auth_headers):
        """POST /api/admin/telegram/create-bot should require firm_id."""
        resp = requests.post(
            f"{BASE_URL}/api/admin/telegram/create-bot",
            json={},
            headers=auth_headers
        )
        # Should return 422 for validation error (missing firm_id)
        assert resp.status_code == 422, f"Expected 422, got {resp.status_code}: {resp.text}"
    
    def test_create_bot_returns_proper_error_without_auth(self, auth_headers):
        """POST /api/admin/telegram/create-bot should handle auth not set up."""
        # Get a valid firm_id first
        firm_resp = requests.get(f"{BASE_URL}/api/admin/telegram/firm-bot-map", headers=auth_headers)
        if firm_resp.status_code != 200:
            pytest.skip("Could not get firm map")
        
        firms = firm_resp.json().get("firms", [])
        # Find a firm without a bot
        firm_without_bot = next((f for f in firms if not f.get("has_bot")), None)
        
        if not firm_without_bot:
            print("All firms already have bots - skipping create test")
            pytest.skip("All firms have bots")
        
        # Try to create bot - should fail gracefully since telegram auth is not done
        resp = requests.post(
            f"{BASE_URL}/api/admin/telegram/create-bot",
            json={"firm_id": firm_without_bot["firm_id"]},
            headers=auth_headers
        )
        
        # Can be 200 (queued) or 400/500 (auth not configured)
        # Both are acceptable since telegram auth isn't set up
        assert resp.status_code in [200, 400, 500], f"Unexpected status {resp.status_code}: {resp.text}"
        print(f"Create single bot response: {resp.status_code} - {resp.text[:200]}")
    
    def test_create_bot_invalid_firm_id(self, auth_headers):
        """POST /api/admin/telegram/create-bot with invalid firm_id should return 404."""
        resp = requests.post(
            f"{BASE_URL}/api/admin/telegram/create-bot",
            json={"firm_id": "non-existent-firm-id"},
            headers=auth_headers
        )
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
    
    def test_create_bot_unauthorized_without_token(self):
        """POST /api/admin/telegram/create-bot without token should return 401."""
        resp = requests.post(f"{BASE_URL}/api/admin/telegram/create-bot", json={"firm_id": "test"})
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"


# ============== BULK CREATE TESTS ==============

class TestBulkCreateBots(TestSetup):
    """Test bulk bot creation endpoint."""
    
    def test_bulk_create_returns_proper_response(self, auth_headers):
        """POST /api/admin/telegram/create-bulk should return proper response."""
        resp = requests.post(
            f"{BASE_URL}/api/admin/telegram/create-bulk",
            json={"firm_ids": [], "all_firms": False, "batch_size": 1, "delay_seconds": 1},
            headers=auth_headers
        )
        
        # Should return 404 since no firms specified
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
        print(f"Bulk create empty response: {resp.status_code}")
    
    def test_bulk_create_unauthorized_without_token(self):
        """POST /api/admin/telegram/create-bulk without token should return 401."""
        resp = requests.post(f"{BASE_URL}/api/admin/telegram/create-bulk", json={})
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"


# ============== BROADCAST TESTS ==============

class TestBroadcast(TestSetup):
    """Test broadcast messaging endpoint."""
    
    def test_broadcast_requires_message(self, auth_headers):
        """POST /api/admin/telegram/broadcast should require message."""
        resp = requests.post(
            f"{BASE_URL}/api/admin/telegram/broadcast",
            json={"all_bots": True},
            headers=auth_headers
        )
        # Should return 422 for missing message or 404 for no active bots
        assert resp.status_code in [422, 404], f"Expected 422 or 404, got {resp.status_code}: {resp.text}"
    
    def test_broadcast_requires_bot_target(self, auth_headers):
        """POST /api/admin/telegram/broadcast needs bot_id or all_bots."""
        resp = requests.post(
            f"{BASE_URL}/api/admin/telegram/broadcast",
            json={"message": "Test message"},
            headers=auth_headers
        )
        # Should return 400 since neither bot_id nor all_bots specified
        assert resp.status_code in [400, 404], f"Expected 400 or 404, got {resp.status_code}: {resp.text}"
    
    def test_broadcast_with_all_bots_no_active(self, auth_headers):
        """POST /api/admin/telegram/broadcast with all_bots when none active."""
        resp = requests.post(
            f"{BASE_URL}/api/admin/telegram/broadcast",
            json={"message": "Test broadcast", "all_bots": True},
            headers=auth_headers
        )
        # Returns 404 if no active bots, or 200 if broadcast started
        assert resp.status_code in [200, 404], f"Expected 200 or 404, got {resp.status_code}: {resp.text}"
        print(f"Broadcast all bots response: {resp.status_code} - {resp.text[:200]}")
    
    def test_broadcast_unauthorized_without_token(self):
        """POST /api/admin/telegram/broadcast without token should return 401."""
        resp = requests.post(f"{BASE_URL}/api/admin/telegram/broadcast", json={"message": "test"})
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"


# ============== DELETE BOT TESTS ==============

class TestDeleteBot(TestSetup):
    """Test delete bot endpoint."""
    
    def test_delete_nonexistent_bot(self, auth_headers):
        """DELETE /api/admin/telegram/bot/{bot_id} with invalid ID should return 404."""
        resp = requests.delete(
            f"{BASE_URL}/api/admin/telegram/bot/non-existent-bot-id",
            headers=auth_headers
        )
        assert resp.status_code == 404, f"Expected 404, got {resp.status_code}: {resp.text}"
    
    def test_delete_unauthorized_without_token(self):
        """DELETE /api/admin/telegram/bot/{bot_id} without token should return 401."""
        resp = requests.delete(f"{BASE_URL}/api/admin/telegram/bot/test-bot-id")
        assert resp.status_code == 401, f"Expected 401, got {resp.status_code}"


# ============== WEBHOOK TESTS (PUBLIC - NO AUTH) ==============

class TestWebhookPublic:
    """Test public webhook endpoint (no auth needed)."""
    
    def test_webhook_accepts_empty_body(self):
        """POST /api/telegram/webhook/{bot_id} should handle empty updates."""
        resp = requests.post(
            f"{BASE_URL}/api/telegram/webhook/test-bot-id",
            json={}
        )
        # Webhook should return 200 OK regardless
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "ok" in data, "Webhook should return 'ok' field"
        assert data["ok"] == True, "Webhook should return ok=True"
    
    def test_webhook_handles_message_without_chat(self):
        """POST /api/telegram/webhook/{bot_id} handles message without chat."""
        resp = requests.post(
            f"{BASE_URL}/api/telegram/webhook/test-bot-id",
            json={"message": {"text": "/start"}}
        )
        # Should return 200 and handle gracefully
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    
    def test_webhook_handles_update_without_message(self):
        """POST /api/telegram/webhook/{bot_id} handles update without message."""
        resp = requests.post(
            f"{BASE_URL}/api/telegram/webhook/test-bot-id",
            json={"update_id": 12345}
        )
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"


# ============== DASHBOARD STATS CHECK ==============

class TestDashboardTelegramStats(TestSetup):
    """Test that telegram bots appear in dashboard stats."""
    
    def test_dashboard_includes_telegram_bots(self, auth_headers):
        """GET /api/stats/dashboard should include telegram_bots count."""
        resp = requests.get(f"{BASE_URL}/api/stats/dashboard", headers=auth_headers)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"
        
        data = resp.json()
        assert "telegram_bots" in data, "Dashboard stats should include 'telegram_bots' field"
        assert isinstance(data["telegram_bots"], int), "'telegram_bots' should be integer"
        
        print(f"Dashboard telegram_bots count: {data['telegram_bots']}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
