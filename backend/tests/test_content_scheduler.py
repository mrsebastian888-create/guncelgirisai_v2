"""
Content Scheduler & Queue Backend Tests
Tests for: bulk-add, queue management, scheduler controls, latest articles
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

# Test data prefix for cleanup
TEST_PREFIX = "TEST_SCHEDULER_"


class TestContentQueueBulkAdd:
    """Test POST /api/content-queue/bulk-add endpoint"""

    def test_bulk_add_with_firma_konu_format(self):
        """Test bulk add with FIRMA|Konu format"""
        items_text = f"{TEST_PREFIX}MAXWIN|Maxwin Deneme Bonusu\n{TEST_PREFIX}HILTONBET|Hiltonbet Güvenilir Mi"
        
        response = requests.post(
            f"{BASE_URL}/api/content-queue/bulk-add",
            json={"items": items_text, "company": ""}
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        
        assert "added" in data, "Response should contain 'added' count"
        assert "items" in data, "Response should contain 'items' list"
        assert data["added"] >= 1, f"Should add at least 1 item, got {data['added']}"
        
        # Verify format parsing
        for item in data["items"]:
            if TEST_PREFIX in item.get("company", ""):
                assert item["topic"], "Each item should have a topic"
                print(f"Added: Company={item['company']}, Topic={item['topic']}")

    def test_bulk_add_plain_topics_with_default_company(self):
        """Test bulk add with plain topics and default company"""
        items_text = f"{TEST_PREFIX}Test Topic One\n{TEST_PREFIX}Test Topic Two"
        default_company = f"{TEST_PREFIX}DEFAULTCO"
        
        response = requests.post(
            f"{BASE_URL}/api/content-queue/bulk-add",
            json={"items": items_text, "company": default_company}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["added"] >= 1

    def test_bulk_add_empty_items(self):
        """Test bulk add with empty items should fail"""
        response = requests.post(
            f"{BASE_URL}/api/content-queue/bulk-add",
            json={"items": "", "company": ""}
        )
        
        assert response.status_code == 400, "Empty items should return 400"

    def test_bulk_add_mixed_format(self):
        """Test bulk add with mixed FIRMA|Konu and plain topics"""
        items_text = f"{TEST_PREFIX}FIRMAA|Topic A\n{TEST_PREFIX}Plain Topic B"
        
        response = requests.post(
            f"{BASE_URL}/api/content-queue/bulk-add",
            json={"items": items_text}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["added"] >= 1


class TestContentQueue:
    """Test GET/DELETE /api/content-queue endpoints"""

    def test_get_queue_returns_items_and_stats(self):
        """Test GET /api/content-queue returns items with stats"""
        response = requests.get(f"{BASE_URL}/api/content-queue")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "items" in data, "Response should contain 'items'"
        assert "stats" in data, "Response should contain 'stats'"
        
        # Verify stats structure
        stats = data["stats"]
        assert "pending" in stats, "Stats should have 'pending' count"
        assert "processing" in stats, "Stats should have 'processing' count"
        assert "completed" in stats, "Stats should have 'completed' count"
        assert "failed" in stats, "Stats should have 'failed' count"
        
        print(f"Queue stats: {stats}")

    def test_get_queue_with_status_filter(self):
        """Test GET /api/content-queue with status filter"""
        response = requests.get(f"{BASE_URL}/api/content-queue?status=pending")
        
        assert response.status_code == 200
        data = response.json()
        
        # All items should have pending status if any items exist
        for item in data.get("items", []):
            assert item["status"] == "pending", f"Item should be pending, got {item['status']}"

    def test_delete_queue_item(self):
        """Test DELETE /api/content-queue/{id}"""
        # First add an item
        add_response = requests.post(
            f"{BASE_URL}/api/content-queue/bulk-add",
            json={"items": f"{TEST_PREFIX}DELETE_TEST|Delete Test Topic"}
        )
        assert add_response.status_code == 200
        added_items = add_response.json().get("items", [])
        
        if added_items:
            item_id = added_items[0]["id"]
            
            # Delete the item
            delete_response = requests.delete(f"{BASE_URL}/api/content-queue/{item_id}")
            assert delete_response.status_code == 200
            
            # Verify deletion
            check_response = requests.get(f"{BASE_URL}/api/content-queue")
            queue_ids = [item["id"] for item in check_response.json().get("items", [])]
            assert item_id not in queue_ids, "Item should be deleted from queue"
            print(f"Successfully deleted queue item {item_id}")
        else:
            pytest.skip("No item was added to test deletion")


class TestSchedulerControls:
    """Test scheduler control endpoints"""

    def test_get_scheduler_status(self):
        """Test GET /api/scheduler/status"""
        response = requests.get(f"{BASE_URL}/api/scheduler/status")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify structure
        assert "is_running" in data, "Status should have 'is_running'"
        assert "interval_minutes" in data, "Status should have 'interval_minutes'"
        assert "pending_items" in data, "Status should have 'pending_items'"
        
        print(f"Scheduler status: is_running={data['is_running']}, interval={data['interval_minutes']}min, pending={data['pending_items']}")

    def test_start_scheduler(self):
        """Test POST /api/scheduler/start"""
        response = requests.post(f"{BASE_URL}/api/scheduler/start")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "started"
        print("Scheduler started successfully")

    def test_stop_scheduler(self):
        """Test POST /api/scheduler/stop"""
        response = requests.post(f"{BASE_URL}/api/scheduler/stop")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert data["status"] == "stopped"
        print("Scheduler stopped successfully")

    def test_update_scheduler_interval(self):
        """Test PUT /api/scheduler/interval"""
        new_interval = 10
        response = requests.put(
            f"{BASE_URL}/api/scheduler/interval",
            json={"minutes": new_interval}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["interval_minutes"] == new_interval
        print(f"Scheduler interval set to {new_interval} minutes")
        
        # Verify by getting status
        status_response = requests.get(f"{BASE_URL}/api/scheduler/status")
        assert status_response.json()["interval_minutes"] == new_interval

    def test_update_scheduler_interval_minimum(self):
        """Test PUT /api/scheduler/interval with minimum validation"""
        response = requests.put(
            f"{BASE_URL}/api/scheduler/interval",
            json={"minutes": 0}
        )
        
        # Should reject values less than 1
        assert response.status_code == 400, "Interval < 1 should be rejected"

    def test_run_scheduler_now(self):
        """Test POST /api/scheduler/run-now returns immediately"""
        start_time = time.time()
        response = requests.post(f"{BASE_URL}/api/scheduler/run-now")
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return immediately (within 2 seconds), not wait for generation
        assert elapsed < 5, f"run-now should return immediately, took {elapsed:.2f}s"
        
        assert "status" in data
        print(f"run-now response: {data}, elapsed: {elapsed:.2f}s")


class TestLatestArticles:
    """Test GET /api/articles/latest endpoint"""

    def test_get_latest_articles(self):
        """Test GET /api/articles/latest returns sorted articles"""
        response = requests.get(f"{BASE_URL}/api/articles/latest")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list), "Response should be a list"
        
        if len(data) > 0:
            # Verify structure
            article = data[0]
            assert "id" in article
            assert "title" in article
            assert "is_published" in article
            assert article["is_published"] == True, "Latest articles should be published"
            
            # Content should not be included
            assert "content" not in article, "Content should be excluded from latest endpoint"
            
            print(f"Found {len(data)} latest articles")

    def test_get_latest_articles_with_limit(self):
        """Test GET /api/articles/latest with limit param"""
        limit = 3
        response = requests.get(f"{BASE_URL}/api/articles/latest?limit={limit}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) <= limit, f"Should return max {limit} articles"

    def test_get_latest_articles_filtered_by_category(self):
        """Test GET /api/articles/latest?category=en-iyi-firmalar"""
        category = "en-iyi-firmalar"
        response = requests.get(f"{BASE_URL}/api/articles/latest?category={category}")
        
        assert response.status_code == 200
        data = response.json()
        
        # If there are articles, they should all be in the specified category
        for article in data:
            assert article.get("category") == category, f"Article should be in category '{category}', got '{article.get('category')}'"
        
        print(f"Found {len(data)} articles in category '{category}'")


class TestEnIyiFirmalarCategory:
    """Test 'En İyi Firmalar' category exists and is accessible"""

    def test_en_iyi_firmalar_category_exists(self):
        """Verify 'En İyi Firmalar' category exists"""
        response = requests.get(f"{BASE_URL}/api/categories")
        
        assert response.status_code == 200
        categories = response.json()
        
        # Find the category
        en_iyi_firmalar = next((c for c in categories if c.get("slug") == "en-iyi-firmalar"), None)
        assert en_iyi_firmalar is not None, "'en-iyi-firmalar' category should exist"
        
        print(f"Found category: {en_iyi_firmalar['name']}")


class TestCleanup:
    """Cleanup test data"""

    def test_cleanup_test_queue_items(self):
        """Clean up test queue items"""
        # Get all queue items
        response = requests.get(f"{BASE_URL}/api/content-queue?limit=200")
        if response.status_code == 200:
            items = response.json().get("items", [])
            cleaned = 0
            for item in items:
                # Delete items with test prefix
                if TEST_PREFIX in item.get("company", "") or TEST_PREFIX in item.get("topic", ""):
                    requests.delete(f"{BASE_URL}/api/content-queue/{item['id']}")
                    cleaned += 1
            print(f"Cleaned up {cleaned} test queue items")


# Fixtures
@pytest.fixture(scope="module", autouse=True)
def ensure_scheduler_stopped():
    """Ensure scheduler is stopped before and after tests"""
    requests.post(f"{BASE_URL}/api/scheduler/stop")
    yield
    requests.post(f"{BASE_URL}/api/scheduler/stop")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
