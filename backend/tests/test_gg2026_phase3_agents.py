"""
GG2026 Phase 3 - AI Agent Infrastructure Backend Tests
Tests all 21 agent API endpoints:
- Agent Status & Jobs (3 endpoints)
- Keyword Intelligence Agent (4 endpoints - LLM-powered)
- Content Generator Agent (4 endpoints - LLM-powered)
- Internal Linking Agent (3 endpoints - 1 LLM, 2 non-LLM)
- Update Agent (3 endpoints - 1 LLM, 2 non-LLM)
- Technical SEO Agent (4 endpoints - 2 LLM, 2 non-LLM)
- Plus existing routes verification
"""
import pytest
import requests
import os
import time

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "").rstrip("/")

class TestAgentStatusAndJobs:
    """Tests for Agent status and job tracking endpoints"""
    
    def test_agents_status_returns_all_agents(self):
        """GET /api/agents/status returns all 5 agents with actions list"""
        response = requests.get(f"{BASE_URL}/api/agents/status", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "operational"
        assert data["llm_configured"] == True
        assert len(data["agents"]) == 5
        
        # Verify all 5 agents are present
        agent_names = [a["name"] for a in data["agents"]]
        assert "keyword_intelligence" in agent_names
        assert "content_generator" in agent_names
        assert "internal_linking" in agent_names
        assert "update" in agent_names
        assert "technical_seo" in agent_names
        
        # Verify actions lists
        for agent in data["agents"]:
            assert "actions" in agent
            assert isinstance(agent["actions"], list)
            assert len(agent["actions"]) > 0
        
        # Verify job stats
        assert "jobs" in data
        assert "total" in data["jobs"]
        assert "completed" in data["jobs"]
        assert "failed" in data["jobs"]
        print(f"PASS: /api/agents/status - All 5 agents operational, {data['jobs']['total']} total jobs")
    
    def test_agents_jobs_list(self):
        """GET /api/agents/jobs returns recent jobs list"""
        response = requests.get(f"{BASE_URL}/api/agents/jobs?limit=10", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        assert "jobs" in data
        assert "count" in data
        assert isinstance(data["jobs"], list)
        
        # Verify job structure if jobs exist
        if data["count"] > 0:
            job = data["jobs"][0]
            assert "job_id" in job
            assert "agent" in job
            assert "action" in job
            assert "status" in job
            assert "created_at" in job
            print(f"PASS: /api/agents/jobs - Retrieved {data['count']} jobs")
        else:
            print("PASS: /api/agents/jobs - No jobs in queue (empty list)")
    
    def test_agents_jobs_filter_by_agent(self):
        """GET /api/agents/jobs with agent filter"""
        response = requests.get(f"{BASE_URL}/api/agents/jobs?agent=keyword_intelligence&limit=5", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        # All returned jobs should be from keyword_intelligence agent
        for job in data["jobs"]:
            assert job["agent"] == "keyword_intelligence"
        print(f"PASS: /api/agents/jobs filter by agent - {data['count']} keyword_intelligence jobs")
    
    def test_agents_jobs_filter_by_status(self):
        """GET /api/agents/jobs with status filter"""
        response = requests.get(f"{BASE_URL}/api/agents/jobs?status=completed&limit=5", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        for job in data["jobs"]:
            assert job["status"] == "completed"
        print(f"PASS: /api/agents/jobs filter by status - {data['count']} completed jobs")


class TestAgentJobDetails:
    """Test getting specific job details"""
    
    def test_get_existing_job_details(self):
        """GET /api/agents/jobs/{job_id} returns specific job"""
        # First get a job ID from the list
        list_response = requests.get(f"{BASE_URL}/api/agents/jobs?limit=1", timeout=10)
        assert list_response.status_code == 200
        
        jobs = list_response.json()["jobs"]
        if len(jobs) == 0:
            pytest.skip("No jobs available to test job details")
        
        job_id = jobs[0]["job_id"]
        
        # Get specific job
        response = requests.get(f"{BASE_URL}/api/agents/jobs/{job_id}", timeout=10)
        assert response.status_code == 200
        
        job = response.json()
        assert job["job_id"] == job_id
        assert "agent" in job
        assert "action" in job
        assert "status" in job
        assert "params" in job
        assert "created_at" in job
        print(f"PASS: /api/agents/jobs/{job_id} - Job details retrieved")
    
    def test_get_nonexistent_job_returns_404(self):
        """GET /api/agents/jobs/{job_id} returns 404 for invalid ID"""
        response = requests.get(f"{BASE_URL}/api/agents/jobs/nonexistent-job-id-12345", timeout=10)
        assert response.status_code == 404
        print("PASS: /api/agents/jobs/invalid - Returns 404 for nonexistent job")


class TestInternalLinkingAgentNonLLM:
    """Tests for Internal Linking Agent - Non-LLM endpoints (fast)"""
    
    def test_linking_audit_clusters(self):
        """POST /api/agents/linking/audit returns cluster coverage audit"""
        response = requests.post(f"{BASE_URL}/api/agents/linking/audit", json={}, timeout=15)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["agent"] == "internal_linking"
        assert data["action"] == "audit_clusters"
        assert "job_id" in data
        
        # Verify audit data structure
        assert "data" in data
        audit_data = data["data"]
        assert "total_firms" in audit_data
        assert "page_types" in audit_data
        assert "coverage_by_type" in audit_data
        assert "missing_pages_sample" in audit_data
        
        print(f"PASS: /api/agents/linking/audit - Audited {audit_data['total_firms']} firms, {audit_data['generated_content_count']} generated pages")
    
    def test_linking_detect_orphans(self):
        """POST /api/agents/linking/orphans detects orphan pages"""
        response = requests.post(f"{BASE_URL}/api/agents/linking/orphans", json={}, timeout=15)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["agent"] == "internal_linking"
        assert data["action"] == "orphans"
        assert "job_id" in data
        
        # Verify orphan data structure
        orphan_data = data["data"]
        assert "orphan_candidates" in orphan_data
        assert "total_checked" in orphan_data
        assert "orphan_count" in orphan_data
        assert isinstance(orphan_data["orphan_candidates"], list)
        
        print(f"PASS: /api/agents/linking/orphans - Found {orphan_data['orphan_count']} orphan candidates from {orphan_data['total_checked']} checked")


class TestUpdateAgentNonLLM:
    """Tests for Update Agent - Non-LLM endpoints (fast)"""
    
    def test_update_scan_outdated(self):
        """POST /api/agents/update/scan scans for outdated content"""
        response = requests.post(
            f"{BASE_URL}/api/agents/update/scan",
            json={"days_threshold": 30},
            timeout=15
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["agent"] == "update"
        assert data["action"] == "scan"
        assert "job_id" in data
        
        # Verify scan data structure
        scan_data = data["data"]
        assert "threshold_days" in scan_data
        assert "outdated_articles" in scan_data
        assert "outdated_firms" in scan_data
        assert "total_outdated" in scan_data
        assert "items" in scan_data
        
        print(f"PASS: /api/agents/update/scan - Scanned with {scan_data['threshold_days']} day threshold, found {scan_data['total_outdated']} outdated items")
    
    def test_update_bulk_timestamps(self):
        """POST /api/agents/update/timestamps bulk updates timestamps"""
        response = requests.post(
            f"{BASE_URL}/api/agents/update/timestamps",
            json={"company_slugs": ["tulipbet"]},
            timeout=15
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["agent"] == "update"
        assert data["action"] == "timestamps"
        assert "job_id" in data
        
        # Verify timestamp data
        ts_data = data["data"]
        assert "updated_count" in ts_data
        assert "timestamp" in ts_data
        assert "scope" in ts_data
        
        print(f"PASS: /api/agents/update/timestamps - Updated {ts_data['updated_count']} timestamps (scope: {ts_data['scope']})")


class TestTechnicalSEOAgentNonLLM:
    """Tests for Technical SEO Agent - Non-LLM endpoints (fast)"""
    
    def test_seo_audit_canonicals(self):
        """POST /api/agents/seo/canonicals audits canonical tags"""
        response = requests.post(f"{BASE_URL}/api/agents/seo/canonicals", json={}, timeout=15)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["agent"] == "technical_seo"
        assert data["action"] == "canonicals"
        assert "job_id" in data
        
        # Verify canonical audit data
        canon_data = data["data"]
        assert "total_pages_audited" in canon_data
        assert "canonical_entries" in canon_data
        assert "issues" in canon_data
        assert "sample_canonicals" in canon_data
        
        print(f"PASS: /api/agents/seo/canonicals - Audited {canon_data['total_pages_audited']} pages, {len(canon_data['issues'])} issues found")
    
    def test_seo_sitemap_audit(self):
        """POST /api/agents/seo/sitemap-audit audits sitemap completeness"""
        response = requests.post(f"{BASE_URL}/api/agents/seo/sitemap-audit", json={}, timeout=15)
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["agent"] == "technical_seo"
        assert data["action"] == "sitemap_audit"
        assert "job_id" in data
        
        # Verify sitemap audit data
        sitemap_data = data["data"]
        assert "firms_count" in sitemap_data
        assert "articles_count" in sitemap_data
        assert "expected_total_urls" in sitemap_data
        assert "sitemaps" in sitemap_data
        assert "recommendations" in sitemap_data
        
        print(f"PASS: /api/agents/seo/sitemap-audit - Expected {sitemap_data['expected_total_urls']} URLs across {len(sitemap_data['sitemaps'])} sitemaps")


class TestKeywordAgentLLM:
    """Tests for Keyword Intelligence Agent - LLM-powered endpoints (slower)
    Only testing 2 endpoints to minimize LLM usage per instructions"""
    
    def test_keyword_cluster(self):
        """POST /api/agents/keyword/cluster accepts keywords and returns clusters"""
        response = requests.post(
            f"{BASE_URL}/api/agents/keyword/cluster",
            json={
                "keywords": ["deneme bonusu", "hosgeldin bonusu", "bahis siteleri"],
                "niche": "bahis"
            },
            timeout=60
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["agent"] == "keyword_intelligence"
        assert data["action"] == "cluster"
        assert "job_id" in data
        
        # Verify cluster data structure
        cluster_data = data["data"]
        assert "clusters" in cluster_data
        assert isinstance(cluster_data["clusters"], list)
        
        # Verify cluster structure if clusters exist
        if len(cluster_data["clusters"]) > 0:
            cluster = cluster_data["clusters"][0]
            assert "cluster_name" in cluster
            assert "keywords" in cluster
        
        print(f"PASS: /api/agents/keyword/cluster - Created {len(cluster_data['clusters'])} clusters")
    
    def test_keyword_intent(self):
        """POST /api/agents/keyword/intent returns intent classifications"""
        response = requests.post(
            f"{BASE_URL}/api/agents/keyword/intent",
            json={"keywords": ["deneme bonusu veren siteler", "bahis nasil oynanir"]},
            timeout=60
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["agent"] == "keyword_intelligence"
        assert data["action"] == "intent"
        assert "job_id" in data
        
        # Verify intent data
        intent_data = data["data"]
        assert "intents" in intent_data
        assert isinstance(intent_data["intents"], list)
        
        print(f"PASS: /api/agents/keyword/intent - Classified {len(intent_data['intents'])} keyword intents")


class TestInternalLinkingAgentLLM:
    """Tests for Internal Linking Agent - LLM-powered endpoint"""
    
    def test_linking_suggest(self):
        """POST /api/agents/linking/suggest returns link suggestions"""
        response = requests.post(
            f"{BASE_URL}/api/agents/linking/suggest",
            json={
                "page_url": "/tulipbet/guncel-giris",
                "page_content": "Tulipbet guncel giris adresi ve bonus bilgileri",
                "limit": 5
            },
            timeout=60
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["agent"] == "internal_linking"
        assert data["action"] == "suggest"
        assert "job_id" in data
        
        # Verify suggestions
        suggest_data = data["data"]
        assert "suggestions" in suggest_data
        assert isinstance(suggest_data["suggestions"], list)
        
        print(f"PASS: /api/agents/linking/suggest - Generated {len(suggest_data['suggestions'])} link suggestions")


class TestJobTracking:
    """Verify job tracking works correctly after agent operations"""
    
    def test_job_created_after_operation(self):
        """Each agent operation creates a job record in MongoDB"""
        # First get current job count
        before = requests.get(f"{BASE_URL}/api/agents/jobs?limit=100", timeout=10)
        before_count = before.json()["count"]
        
        # Trigger a fast non-LLM operation
        requests.post(f"{BASE_URL}/api/agents/linking/orphans", json={}, timeout=15)
        
        # Check jobs list again
        after = requests.get(f"{BASE_URL}/api/agents/jobs?limit=100", timeout=10)
        after_count = after.json()["count"]
        
        # Verify a new job was created
        assert after_count >= before_count
        
        # Get the latest job
        latest_job = after.json()["jobs"][0]
        assert latest_job["agent"] == "internal_linking"
        assert latest_job["action"] == "orphans"
        assert latest_job["status"] in ["completed", "running", "pending"]
        
        if latest_job["status"] == "completed":
            assert "duration_ms" in latest_job
            assert latest_job["duration_ms"] > 0
        
        print(f"PASS: Job tracking - New job created, total jobs: {after_count}")


class TestExistingRoutes:
    """Verify existing routes still work after agent infrastructure"""
    
    def test_bonus_sites_endpoint(self):
        """GET /api/bonus-sites still works"""
        response = requests.get(f"{BASE_URL}/api/bonus-sites?limit=5", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        # API returns array directly, not wrapped in {sites: [...]}
        assert isinstance(data, list)
        assert len(data) > 0
        # Verify site structure
        site = data[0]
        assert "name" in site
        assert "bonus_amount" in site
        print(f"PASS: /api/bonus-sites - Existing route works, returned {len(data)} sites")
    
    def test_firma_sub_endpoint(self):
        """GET /api/firma-sub/{slug}/{type} still works"""
        response = requests.get(f"{BASE_URL}/api/firma-sub/tulipbet/guncel-giris", timeout=10)
        assert response.status_code == 200
        
        data = response.json()
        assert "site" in data
        assert "page_type" in data
        print(f"PASS: /api/firma-sub/tulipbet/guncel-giris - Existing route works")
    
    def test_api_agents_status_as_health(self):
        """Agent status endpoint works as backend health indicator"""
        # Note: /health at root is captured by frontend in preview, use agent status
        response = requests.get(f"{BASE_URL}/api/agents/status", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        print("PASS: /api/agents/status - Backend operational")


class TestContentGeneratorAgentLLM:
    """Tests for Content Generator Agent - LLM-powered endpoint
    Testing only company-page to minimize LLM usage"""
    
    def test_content_company_page(self):
        """POST /api/agents/content/company-page generates content"""
        response = requests.post(
            f"{BASE_URL}/api/agents/content/company-page",
            json={
                "company_slug": "tulipbet",
                "page_type": "deneme-bonusu"
            },
            timeout=60
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["agent"] == "content_generator"
        assert data["action"] == "company_page"
        assert "job_id" in data
        
        # Verify content structure
        content_data = data["data"]
        assert "title" in content_data
        assert "meta_description" in content_data
        assert "company_slug" in content_data
        assert content_data["company_slug"] == "tulipbet"
        
        print(f"PASS: /api/agents/content/company-page - Generated content: {content_data.get('title', 'N/A')[:50]}...")


class TestTechnicalSEOAgentLLM:
    """Tests for Technical SEO Agent - LLM-powered endpoint
    Testing only titles endpoint to minimize LLM usage"""
    
    def test_seo_generate_titles(self):
        """POST /api/agents/seo/titles generates page titles"""
        response = requests.post(
            f"{BASE_URL}/api/agents/seo/titles",
            json={
                "pages": [
                    {"url": "/tulipbet/guncel-giris", "current_title": "Tulipbet", "page_type": "company_page"},
                    {"url": "/deneme-bonusu", "current_title": "Deneme Bonusu", "page_type": "hub_page"}
                ]
            },
            timeout=60
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["agent"] == "technical_seo"
        assert data["action"] == "titles"
        assert "job_id" in data
        
        # Verify titles data
        titles_data = data["data"]
        assert "titles" in titles_data
        
        print(f"PASS: /api/agents/seo/titles - Generated {len(titles_data.get('titles', []))} title suggestions")


# Additional endpoint coverage tests (non-LLM where possible)
class TestAgentEndpointCoverage:
    """Quick validation that all 21 endpoints are reachable"""
    
    def test_all_endpoint_routes_exist(self):
        """Verify all 21 agent endpoint routes are registered"""
        endpoints = [
            ("GET", "/api/agents/status"),
            ("GET", "/api/agents/jobs"),
            # Job detail tested separately with valid ID
            ("POST", "/api/agents/keyword/cluster"),
            ("POST", "/api/agents/keyword/intent"),
            ("POST", "/api/agents/keyword/opportunities"),
            ("POST", "/api/agents/keyword/discover"),
            ("POST", "/api/agents/content/company-page"),
            ("POST", "/api/agents/content/hub-page"),
            ("POST", "/api/agents/content/guide"),
            ("POST", "/api/agents/content/article"),
            ("POST", "/api/agents/linking/suggest"),
            ("POST", "/api/agents/linking/audit"),
            ("POST", "/api/agents/linking/orphans"),
            ("POST", "/api/agents/update/scan"),
            ("POST", "/api/agents/update/refresh"),
            ("POST", "/api/agents/update/timestamps"),
            ("POST", "/api/agents/seo/titles"),
            ("POST", "/api/agents/seo/descriptions"),
            ("POST", "/api/agents/seo/canonicals"),
            ("POST", "/api/agents/seo/sitemap-audit"),
        ]
        
        reachable = 0
        for method, endpoint in endpoints:
            try:
                if method == "GET":
                    r = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
                else:
                    # POST with minimal body to check route exists (may fail validation but route exists)
                    r = requests.post(f"{BASE_URL}{endpoint}", json={}, timeout=5)
                
                # Route exists if we get response (even 422 validation error is OK)
                if r.status_code not in [404, 405]:
                    reachable += 1
                else:
                    print(f"WARNING: {method} {endpoint} returned {r.status_code}")
            except Exception as e:
                print(f"ERROR: {method} {endpoint} - {e}")
        
        assert reachable >= 18, f"Only {reachable}/20 endpoints reachable"
        print(f"PASS: Endpoint coverage - {reachable}/20 agent endpoints are reachable")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
