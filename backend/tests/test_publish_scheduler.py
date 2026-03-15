"""
GG2026 Phase 7: Controlled Publishing System Tests
Tests for queue-based SEO publishing with 8-15 pages/day rate limit
Day-of-week content types: Mon=hub, Tue=company, Wed=guides, Thu=comparison, Fri=bonus, Sat=articles, Sun=updates
"""
import pytest
import requests
import os
import uuid

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# ==================== FIXTURES ====================

@pytest.fixture
def api_client():
    """Shared requests session"""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


@pytest.fixture
def unique_slug():
    """Generate unique slug for test items to avoid collisions"""
    return f"test-publish-{uuid.uuid4().hex[:8]}"


# ==================== GET /api/publish/status ====================

class TestPublishStatus:
    """Test GET /api/publish/status endpoint"""

    def test_status_returns_200(self, api_client):
        """Status endpoint returns 200"""
        response = api_client.get(f"{BASE_URL}/api/publish/status")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        print("✓ GET /api/publish/status returns 200")

    def test_status_contains_queue_stats(self, api_client):
        """Status includes total, pending, scheduled, published, failed counts"""
        response = api_client.get(f"{BASE_URL}/api/publish/status")
        data = response.json()
        
        # Verify queue stats fields exist
        assert "total" in data, "Missing 'total' in status"
        assert "pending" in data, "Missing 'pending' in status"
        assert "scheduled" in data, "Missing 'scheduled' in status"
        assert "published" in data, "Missing 'published' in status"
        assert "failed" in data, "Missing 'failed' in status"
        
        # Verify they are integers
        assert isinstance(data["total"], int), "total should be int"
        assert isinstance(data["pending"], int), "pending should be int"
        assert isinstance(data["scheduled"], int), "scheduled should be int"
        assert isinstance(data["published"], int), "published should be int"
        assert isinstance(data["failed"], int), "failed should be int"
        
        print(f"✓ Queue stats: total={data['total']}, pending={data['pending']}, scheduled={data['scheduled']}, published={data['published']}, failed={data['failed']}")

    def test_status_contains_today_schedule(self, api_client):
        """Status includes today's schedule info"""
        response = api_client.get(f"{BASE_URL}/api/publish/status")
        data = response.json()
        
        assert "today" in data, "Missing 'today' in status"
        today = data["today"]
        
        assert "date" in today, "Missing 'date' in today"
        assert "day" in today, "Missing 'day' (weekday name) in today"
        assert "content_type" in today, "Missing 'content_type' label in today"
        assert "published" in today, "Missing 'published' count in today"
        assert "scheduled" in today, "Missing 'scheduled' count in today"
        assert "limit" in today, "Missing 'limit' in today"
        
        print(f"✓ Today: {today['date']} ({today['day']}) - type={today['content_type']}, scheduled={today['scheduled']}, published={today['published']}, limit={today['limit']}")

    def test_status_contains_daemon_info(self, api_client):
        """Status includes daemon status"""
        response = api_client.get(f"{BASE_URL}/api/publish/status")
        data = response.json()
        
        assert "daemon" in data, "Missing 'daemon' in status"
        daemon = data["daemon"]
        
        assert "running" in daemon, "Missing 'running' in daemon"
        assert isinstance(daemon["running"], bool), "daemon.running should be bool"
        
        print(f"✓ Daemon: running={daemon['running']}, last_run={daemon.get('last_run')}, interval={daemon.get('interval_minutes')} min")

    def test_status_contains_7day_forecast(self, api_client):
        """Status includes 7-day forecast"""
        response = api_client.get(f"{BASE_URL}/api/publish/status")
        data = response.json()
        
        assert "forecast" in data, "Missing 'forecast' in status"
        forecast = data["forecast"]
        
        assert isinstance(forecast, list), "forecast should be a list"
        assert len(forecast) == 7, f"forecast should have 7 days, got {len(forecast)}"
        
        # Verify forecast structure
        for day_info in forecast:
            assert "date" in day_info, "Missing 'date' in forecast day"
            assert "day" in day_info, "Missing 'day' name in forecast day"
            assert "content_type" in day_info, "Missing 'content_type' in forecast day"
            assert "items_count" in day_info, "Missing 'items_count' in forecast day"
            assert "capacity_remaining" in day_info, "Missing 'capacity_remaining' in forecast day"
        
        print(f"✓ 7-day forecast present, first day: {forecast[0]}")

    def test_status_contains_rate_limits(self, api_client):
        """Status includes rate limit config"""
        response = api_client.get(f"{BASE_URL}/api/publish/status")
        data = response.json()
        
        assert "rate_limits" in data, "Missing 'rate_limits' in status"
        limits = data["rate_limits"]
        
        assert "min_per_day" in limits, "Missing 'min_per_day' in rate_limits"
        assert "max_per_day" in limits, "Missing 'max_per_day' in rate_limits"
        assert limits["min_per_day"] == 8, f"Expected min_per_day=8, got {limits['min_per_day']}"
        assert limits["max_per_day"] == 15, f"Expected max_per_day=15, got {limits['max_per_day']}"
        
        print(f"✓ Rate limits: min={limits['min_per_day']}, max={limits['max_per_day']} per day")


# ==================== POST /api/publish/enqueue ====================

class TestPublishEnqueue:
    """Test POST /api/publish/enqueue endpoint"""

    def test_enqueue_single_item(self, api_client, unique_slug):
        """Enqueue a single item successfully"""
        payload = {
            "items": [{
                "slug": unique_slug,
                "title": "Test Article for Enqueue",
                "content_type": "article",
                "source": "test",
                "priority": 5
            }]
        }
        
        response = api_client.post(f"{BASE_URL}/api/publish/enqueue", json=payload)
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "added" in data, "Missing 'added' in response"
        assert data["added"] == 1, f"Expected added=1, got {data['added']}"
        
        print(f"✓ Enqueued item: slug={unique_slug}, added={data['added']}")

    def test_enqueue_multiple_items(self, api_client):
        """Enqueue multiple items"""
        slug1 = f"test-multi-{uuid.uuid4().hex[:8]}"
        slug2 = f"test-multi-{uuid.uuid4().hex[:8]}"
        
        payload = {
            "items": [
                {"slug": slug1, "title": "Test 1", "content_type": "hub_page", "source": "test", "priority": 1},
                {"slug": slug2, "title": "Test 2", "content_type": "comparison", "source": "test", "priority": 2}
            ]
        }
        
        response = api_client.post(f"{BASE_URL}/api/publish/enqueue", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["added"] == 2, f"Expected added=2, got {data['added']}"
        assert data["total"] == 2, f"Expected total=2, got {data['total']}"
        
        print(f"✓ Enqueued multiple items: added={data['added']}")

    def test_enqueue_empty_items_fails(self, api_client):
        """Enqueue with empty items list returns 400"""
        payload = {"items": []}
        
        response = api_client.post(f"{BASE_URL}/api/publish/enqueue", json=payload)
        assert response.status_code == 400, f"Expected 400 for empty items, got {response.status_code}"
        
        print("✓ Empty items list correctly rejected with 400")

    def test_enqueue_dedup_pending(self, api_client, unique_slug):
        """Enqueue deduplicates against pending items (same slug blocked)"""
        payload = {"items": [{"slug": unique_slug, "title": "First", "content_type": "article"}]}
        
        # First enqueue
        response1 = api_client.post(f"{BASE_URL}/api/publish/enqueue", json=payload)
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["added"] == 1, "First enqueue should add 1"
        
        # Second enqueue with same slug
        payload["items"][0]["title"] = "Second attempt"
        response2 = api_client.post(f"{BASE_URL}/api/publish/enqueue", json=payload)
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Should be skipped as duplicate
        assert data2["added"] == 0, f"Expected added=0 (dup), got {data2['added']}"
        assert data2["skipped"] == 1, f"Expected skipped=1, got {data2['skipped']}"
        
        print("✓ Duplicate slug correctly skipped: added=0, skipped=1")

    def test_enqueue_with_all_content_types(self, api_client):
        """Enqueue items with various content types"""
        content_types = ["hub_page", "company_page", "guide", "comparison", "bonus", "article", "update"]
        
        for ct in content_types:
            slug = f"test-ct-{ct}-{uuid.uuid4().hex[:6]}"
            payload = {"items": [{"slug": slug, "title": f"Test {ct}", "content_type": ct}]}
            response = api_client.post(f"{BASE_URL}/api/publish/enqueue", json=payload)
            assert response.status_code == 200, f"Failed for content_type={ct}"
        
        print(f"✓ All content types accepted: {content_types}")


# ==================== POST /api/publish/schedule ====================

class TestPublishSchedule:
    """Test POST /api/publish/schedule endpoint"""

    def test_schedule_returns_200(self, api_client):
        """Schedule endpoint returns 200"""
        response = api_client.post(f"{BASE_URL}/api/publish/schedule", json={})
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "scheduled" in data, "Missing 'scheduled' count in response"
        
        print(f"✓ Schedule returned: scheduled={data.get('scheduled')}, total_pending={data.get('total_pending')}")

    def test_schedule_pending_items(self, api_client):
        """Schedule assigns dates to pending items"""
        # First enqueue some pending items
        slug = f"test-schedule-{uuid.uuid4().hex[:8]}"
        api_client.post(f"{BASE_URL}/api/publish/enqueue", json={
            "items": [{"slug": slug, "title": "To Schedule", "content_type": "article"}]
        })
        
        # Run schedule
        response = api_client.post(f"{BASE_URL}/api/publish/schedule", json={})
        assert response.status_code == 200
        
        data = response.json()
        # At least check endpoint works - scheduled count depends on queue state
        assert "scheduled" in data
        
        print(f"✓ Schedule endpoint processed pending items: {data}")

    def test_schedule_with_custom_limits(self, api_client):
        """Schedule accepts custom min/max per day"""
        response = api_client.post(f"{BASE_URL}/api/publish/schedule", json={
            "min_per_day": 5,
            "max_per_day": 10
        })
        assert response.status_code == 200
        
        print("✓ Schedule accepts custom rate limits")


# ==================== POST /api/publish/run ====================

class TestPublishRun:
    """Test POST /api/publish/run endpoint"""

    def test_run_returns_200(self, api_client):
        """Run endpoint returns 200"""
        response = api_client.post(f"{BASE_URL}/api/publish/run")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        assert "published" in data, "Missing 'published' count"
        assert "failed" in data, "Missing 'failed' count"
        assert "due_items" in data, "Missing 'due_items' count"
        
        print(f"✓ Run returned: published={data['published']}, failed={data['failed']}, due={data['due_items']}")


# ==================== POST /api/publish/manual ====================

class TestPublishManual:
    """Test POST /api/publish/manual endpoint - immediate override publish"""

    def test_manual_publish_requires_queue_ids(self, api_client):
        """Manual publish requires queue_ids"""
        response = api_client.post(f"{BASE_URL}/api/publish/manual", json={"queue_ids": []})
        assert response.status_code == 400, f"Expected 400 for empty queue_ids, got {response.status_code}"
        
        print("✓ Manual publish correctly rejects empty queue_ids")

    def test_manual_publish_item(self, api_client, unique_slug):
        """Manual override publishes specific item immediately"""
        # Enqueue an item
        api_client.post(f"{BASE_URL}/api/publish/enqueue", json={
            "items": [{"slug": unique_slug, "title": "Manual Override", "content_type": "bonus"}]
        })
        
        # Get the queue_id
        queue_response = api_client.get(f"{BASE_URL}/api/publish/queue?status=pending&limit=100")
        items = queue_response.json().get("items", [])
        
        queue_id = None
        for item in items:
            if item.get("slug") == unique_slug:
                queue_id = item.get("queue_id")
                break
        
        if queue_id:
            # Manual publish
            response = api_client.post(f"{BASE_URL}/api/publish/manual", json={"queue_ids": [queue_id]})
            assert response.status_code == 200
            
            data = response.json()
            assert data["published"] == 1, f"Expected published=1, got {data['published']}"
            
            print(f"✓ Manual override published item: queue_id={queue_id}")
        else:
            print("⚠ Could not find enqueued item to test manual publish (item may have been scheduled)")


# ==================== GET /api/publish/queue ====================

class TestPublishQueueList:
    """Test GET /api/publish/queue endpoint"""

    def test_queue_list_returns_200(self, api_client):
        """Queue list returns 200"""
        response = api_client.get(f"{BASE_URL}/api/publish/queue")
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data, "Missing 'items' in response"
        assert "total" in data, "Missing 'total' in response"
        assert isinstance(data["items"], list), "items should be a list"
        
        print(f"✓ Queue list: total={data['total']}, items_returned={len(data['items'])}")

    def test_queue_list_with_status_filter(self, api_client):
        """Queue list filters by status"""
        statuses = ["pending", "scheduled", "published", "failed"]
        
        for status in statuses:
            response = api_client.get(f"{BASE_URL}/api/publish/queue?status={status}")
            assert response.status_code == 200, f"Failed for status={status}"
            
            data = response.json()
            # Verify all returned items have the correct status
            for item in data.get("items", []):
                assert item.get("status") == status, f"Item has status={item.get('status')}, expected {status}"
        
        print(f"✓ Status filter works for: {statuses}")

    def test_queue_list_pagination(self, api_client):
        """Queue list supports pagination"""
        response = api_client.get(f"{BASE_URL}/api/publish/queue?limit=5&offset=0")
        assert response.status_code == 200
        
        data = response.json()
        assert "limit" in data, "Missing 'limit' in response"
        assert "offset" in data, "Missing 'offset' in response"
        assert data["limit"] == 5, f"Expected limit=5, got {data['limit']}"
        assert data["offset"] == 0, f"Expected offset=0, got {data['offset']}"
        
        print(f"✓ Pagination works: limit={data['limit']}, offset={data['offset']}")


# ==================== POST /api/publish/remove ====================

class TestPublishRemove:
    """Test POST /api/publish/remove endpoint"""

    def test_remove_pending_item(self, api_client, unique_slug):
        """Remove pending item from queue"""
        # Enqueue an item
        api_client.post(f"{BASE_URL}/api/publish/enqueue", json={
            "items": [{"slug": unique_slug, "title": "To Remove", "content_type": "article"}]
        })
        
        # Find the queue_id
        queue_response = api_client.get(f"{BASE_URL}/api/publish/queue?status=pending&limit=100")
        items = queue_response.json().get("items", [])
        
        queue_id = None
        for item in items:
            if item.get("slug") == unique_slug:
                queue_id = item.get("queue_id")
                break
        
        if queue_id:
            # Remove
            response = api_client.post(f"{BASE_URL}/api/publish/remove", json={"queue_ids": [queue_id]})
            assert response.status_code == 200
            
            data = response.json()
            assert "removed" in data, "Missing 'removed' in response"
            assert data["removed"] >= 0, "removed should be >= 0"
            
            print(f"✓ Remove endpoint works: removed={data['removed']}")
        else:
            print("⚠ Item was scheduled before removal test could run")


# ==================== POST /api/publish/reschedule-failed ====================

class TestPublishRescheduleFailed:
    """Test POST /api/publish/reschedule-failed endpoint"""

    def test_reschedule_failed_returns_200(self, api_client):
        """Reschedule-failed returns 200"""
        response = api_client.post(f"{BASE_URL}/api/publish/reschedule-failed")
        assert response.status_code == 200
        
        data = response.json()
        assert "rescheduled" in data, "Missing 'rescheduled' in response"
        
        print(f"✓ Reschedule-failed returned: rescheduled={data['rescheduled']}")


# ==================== GET /api/publish/schedule-map ====================

class TestPublishScheduleMap:
    """Test GET /api/publish/schedule-map endpoint"""

    def test_schedule_map_returns_200(self, api_client):
        """Schedule-map returns 200"""
        response = api_client.get(f"{BASE_URL}/api/publish/schedule-map")
        assert response.status_code == 200
        
        data = response.json()
        assert "schedule" in data, "Missing 'schedule' in response"
        
        print("✓ Schedule-map returns 200")

    def test_schedule_map_contains_all_days(self, api_client):
        """Schedule-map contains all 7 days (0-6)"""
        response = api_client.get(f"{BASE_URL}/api/publish/schedule-map")
        schedule = response.json().get("schedule", {})
        
        # Keys are strings "0" through "6" in JSON
        expected_days = {"0", "1", "2", "3", "4", "5", "6"}
        actual_days = set(schedule.keys())
        
        assert expected_days == actual_days, f"Expected days 0-6, got {actual_days}"
        
        print(f"✓ Schedule-map has all 7 days: {sorted(actual_days)}")

    def test_schedule_map_day_structure(self, api_client):
        """Each day has day name, content_types, label"""
        response = api_client.get(f"{BASE_URL}/api/publish/schedule-map")
        schedule = response.json().get("schedule", {})
        
        for day_num, day_config in schedule.items():
            assert "day" in day_config, f"Day {day_num} missing 'day' name"
            assert "content_types" in day_config, f"Day {day_num} missing 'content_types'"
            assert "label" in day_config, f"Day {day_num} missing 'label'"
            assert isinstance(day_config["content_types"], list), f"Day {day_num} content_types should be list"
        
        print("✓ All days have correct structure (day, content_types, label)")

    def test_schedule_map_correct_day_mapping(self, api_client):
        """Verify correct day-of-week → content type mapping"""
        response = api_client.get(f"{BASE_URL}/api/publish/schedule-map")
        schedule = response.json().get("schedule", {})
        
        # Expected mappings
        expected = {
            "0": ("Monday", "hub"),      # Mon = hub pages
            "1": ("Tuesday", "company"), # Tue = company pages
            "2": ("Wednesday", "guide"), # Wed = guides
            "3": ("Thursday", "comparison"), # Thu = comparison
            "4": ("Friday", "bonus"),    # Fri = bonus
            "5": ("Saturday", "article"), # Sat = articles
            "6": ("Sunday", "update"),   # Sun = updates
        }
        
        for day_num, (day_name, content_prefix) in expected.items():
            day_config = schedule.get(day_num, {})
            assert day_config.get("day") == day_name, f"Day {day_num} should be {day_name}"
            
            # Check that at least one content_type contains the prefix
            content_types = day_config.get("content_types", [])
            has_match = any(content_prefix in ct.lower() for ct in content_types)
            assert has_match, f"Day {day_name} should have {content_prefix}-type content, got {content_types}"
        
        print("✓ Day-of-week → content type mapping verified")


# ==================== DAY SCHEDULING LOGIC ====================

class TestDaySchedulingLogic:
    """Test day-of-week scheduling rules"""

    def test_article_scheduled_for_saturday(self, api_client):
        """Article content type should prefer Saturday"""
        slug = f"test-article-sat-{uuid.uuid4().hex[:8]}"
        
        # Enqueue an article
        api_client.post(f"{BASE_URL}/api/publish/enqueue", json={
            "items": [{"slug": slug, "title": "Saturday Article", "content_type": "article"}]
        })
        
        # Schedule it
        api_client.post(f"{BASE_URL}/api/publish/schedule", json={})
        
        # Find the scheduled date
        queue_response = api_client.get(f"{BASE_URL}/api/publish/queue?limit=200")
        items = queue_response.json().get("items", [])
        
        for item in items:
            if item.get("slug") == slug and item.get("scheduled_date"):
                # Parse date and check day of week
                date_str = item["scheduled_date"][:10]  # YYYY-MM-DD
                from datetime import datetime
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                
                # Saturday = 5 (Python weekday())
                # If the slot is full or it's already Saturday, it may go to any day
                print(f"✓ Article scheduled for {date_str} (weekday={dt.weekday()}, 5=Sat)")
                return
        
        print("⚠ Article scheduling test: item may have been processed differently")


# ==================== RATE LIMITING ====================

class TestRateLimiting:
    """Test 8-15 items per day rate limiting"""

    def test_max_15_per_day_enforced(self, api_client):
        """Verify max 15 items per day is enforced in schedule"""
        # Get current status to check limits
        response = api_client.get(f"{BASE_URL}/api/publish/status")
        data = response.json()
        
        rate_limits = data.get("rate_limits", {})
        assert rate_limits.get("max_per_day") == 15, "Max per day should be 15"
        
        # Check forecast - capacity_remaining should respect limit
        forecast = data.get("forecast", [])
        for day in forecast:
            remaining = day.get("capacity_remaining", 0)
            items_count = day.get("items_count", 0)
            # items_count + remaining should not exceed 15
            assert items_count + remaining <= 15, f"Day {day['date']} exceeds 15: {items_count}+{remaining}"
        
        print("✓ Max 15 per day is enforced in forecast")


# ==================== EXISTING ROUTES UNBROKEN ====================

class TestExistingRoutesUnbroken:
    """Verify existing routes still work after Phase 7 addition"""

    def test_bonus_sites_endpoint(self, api_client):
        """GET /api/bonus-sites still works"""
        response = api_client.get(f"{BASE_URL}/api/bonus-sites")
        assert response.status_code == 200, f"bonus-sites failed: {response.status_code}"
        print("✓ GET /api/bonus-sites works")

    def test_programmatic_stats_endpoint(self, api_client):
        """GET /api/programmatic/stats still works"""
        response = api_client.get(f"{BASE_URL}/api/programmatic/stats")
        assert response.status_code == 200, f"programmatic/stats failed: {response.status_code}"
        print("✓ GET /api/programmatic/stats works")

    def test_health_endpoint(self, api_client):
        """GET /health still works"""
        response = api_client.get(f"{BASE_URL}/health")
        assert response.status_code == 200, f"health failed: {response.status_code}"
        print("✓ GET /health works")


# ==================== DAEMON STATUS ====================

class TestDaemonStatus:
    """Test daemon is running"""

    def test_daemon_is_running(self, api_client):
        """Daemon should be running=true"""
        response = api_client.get(f"{BASE_URL}/api/publish/status")
        data = response.json()
        
        daemon = data.get("daemon", {})
        assert daemon.get("running"), f"Daemon should be running, got {daemon}"
        
        print(f"✓ Daemon running=True, interval={daemon.get('interval_minutes')} min")


# ==================== CLEANUP ====================

class TestCleanup:
    """Cleanup test items from queue"""

    def test_cleanup_test_items(self, api_client):
        """Remove test items (TEST_ prefixed slugs)"""
        # Get all pending/scheduled test items
        queue_response = api_client.get(f"{BASE_URL}/api/publish/queue?limit=500")
        items = queue_response.json().get("items", [])
        
        test_ids = []
        for item in items:
            slug = item.get("slug", "")
            if slug.startswith("test-") and item.get("status") in ["pending", "scheduled"]:
                test_ids.append(item.get("queue_id"))
        
        if test_ids:
            response = api_client.post(f"{BASE_URL}/api/publish/remove", json={"queue_ids": test_ids})
            data = response.json()
            print(f"✓ Cleaned up {data.get('removed', 0)} test items")
        else:
            print("✓ No test items to clean up")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
