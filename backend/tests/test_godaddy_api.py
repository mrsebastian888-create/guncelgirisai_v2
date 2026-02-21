"""
GoDaddy API Integration Tests
Tests for GET /api/godaddy/domains and POST /api/godaddy/import endpoints
"""

import pytest
import requests
import os
import time
import uuid

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestGoDaddyAPI:
    """Test GoDaddy API integration endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
    
    def test_health_check(self):
        """Verify API is running"""
        response = self.session.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        print("✓ Health check passed")
    
    def test_godaddy_domains_list(self):
        """GET /api/godaddy/domains - should return list of domains from GoDaddy account"""
        response = self.session.get(f"{BASE_URL}/api/godaddy/domains")
        
        # Check response status
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        
        data = response.json()
        
        # Verify response structure
        assert "total" in data, "Response should have 'total' field"
        assert "domains" in data, "Response should have 'domains' field"
        assert isinstance(data["total"], int), "total should be an integer"
        assert isinstance(data["domains"], list), "domains should be a list"
        
        print(f"✓ GoDaddy domains list returned {data['total']} domains")
        
        # If there are domains, verify domain structure
        if data["total"] > 0:
            domain = data["domains"][0]
            assert "domain" in domain, "Each domain should have 'domain' field"
            assert "status" in domain, "Each domain should have 'status' field"
            assert "expires" in domain, "Each domain should have 'expires' field"
            assert "already_added" in domain, "Each domain should have 'already_added' field"
            print(f"✓ Domain structure verified: {domain['domain']}, status={domain['status']}, already_added={domain['already_added']}")
        
        return data
    
    def test_godaddy_domains_has_expected_fields(self):
        """GET /api/godaddy/domains - verify all expected fields are present"""
        response = self.session.get(f"{BASE_URL}/api/godaddy/domains")
        assert response.status_code == 200
        
        data = response.json()
        
        if data["total"] > 0:
            domain = data["domains"][0]
            expected_fields = ["domain", "status", "expires", "renewable", "renew_auto", "locked", "privacy", "nameServers", "created_at", "already_added"]
            for field in expected_fields:
                assert field in domain, f"Missing field: {field}"
            print(f"✓ All expected fields present in domain response")
        else:
            pytest.skip("No domains in GoDaddy account to verify fields")
    
    def test_godaddy_import_new_domain(self):
        """POST /api/godaddy/import - should import a GoDaddy domain into the platform"""
        # First get a domain that isn't already added
        list_response = self.session.get(f"{BASE_URL}/api/godaddy/domains")
        assert list_response.status_code == 200
        data = list_response.json()
        
        # Find a domain not already in platform
        available_domains = [d for d in data["domains"] if not d["already_added"]]
        
        if not available_domains:
            pytest.skip("All GoDaddy domains are already added to platform")
        
        # Pick a test domain to import
        test_domain = available_domains[0]
        domain_name = test_domain["domain"]
        
        print(f"Testing import of domain: {domain_name}")
        
        # Import the domain
        import_response = self.session.post(
            f"{BASE_URL}/api/godaddy/import",
            json={
                "domain_name": domain_name,
                "focus": "bonus"
            }
        )
        
        assert import_response.status_code == 200, f"Import failed: {import_response.text}"
        result = import_response.json()
        
        # Verify response
        assert "message" in result, "Response should have 'message' field"
        assert "domain" in result, "Response should have 'domain' field"
        assert domain_name in result["message"], "Success message should mention domain name"
        
        # Verify domain object
        domain_obj = result["domain"]
        assert domain_obj["domain_name"] == domain_name
        assert "id" in domain_obj
        assert domain_obj["focus"] == "bonus"
        
        print(f"✓ Domain {domain_name} imported successfully with ID: {domain_obj['id']}")
        
        # Cleanup - delete the test domain to not pollute the platform
        # We'll need to track this for cleanup
        self._cleanup_domain_id = domain_obj["id"]
        return domain_obj
    
    def test_godaddy_import_duplicate_rejection(self):
        """POST /api/godaddy/import - should reject duplicate domain imports"""
        # Get a domain that IS already in the platform
        list_response = self.session.get(f"{BASE_URL}/api/godaddy/domains")
        assert list_response.status_code == 200
        data = list_response.json()
        
        # Find a domain already in platform
        added_domains = [d for d in data["domains"] if d["already_added"]]
        
        if not added_domains:
            # Need to add one first, then try to add again
            available_domains = [d for d in data["domains"] if not d["already_added"]]
            if not available_domains:
                pytest.skip("No domains available for duplicate test")
            
            # Import first
            test_domain = available_domains[0]
            domain_name = test_domain["domain"]
            self.session.post(
                f"{BASE_URL}/api/godaddy/import",
                json={"domain_name": domain_name, "focus": "bonus"}
            )
        else:
            domain_name = added_domains[0]["domain"]
        
        # Try to import again - should fail
        duplicate_response = self.session.post(
            f"{BASE_URL}/api/godaddy/import",
            json={"domain_name": domain_name, "focus": "bonus"}
        )
        
        assert duplicate_response.status_code == 400, f"Expected 400 for duplicate, got {duplicate_response.status_code}"
        error_data = duplicate_response.json()
        assert "detail" in error_data or "error" in error_data
        print(f"✓ Duplicate domain import correctly rejected: {domain_name}")
    
    def test_godaddy_import_empty_domain_name(self):
        """POST /api/godaddy/import - should reject empty domain name"""
        response = self.session.post(
            f"{BASE_URL}/api/godaddy/import",
            json={"domain_name": "", "focus": "bonus"}
        )
        
        assert response.status_code == 400, f"Expected 400 for empty domain, got {response.status_code}"
        print("✓ Empty domain name correctly rejected")
    
    def test_godaddy_domains_already_added_flag(self):
        """GET /api/godaddy/domains - verify already_added flag is accurate"""
        # Get existing platform domains
        domains_response = self.session.get(f"{BASE_URL}/api/domains")
        assert domains_response.status_code == 200
        platform_domains = {d["domain_name"] for d in domains_response.json()}
        
        # Get GoDaddy domains
        godaddy_response = self.session.get(f"{BASE_URL}/api/godaddy/domains")
        assert godaddy_response.status_code == 200
        godaddy_data = godaddy_response.json()
        
        # Verify already_added flags match
        for gd_domain in godaddy_data["domains"][:50]:  # Check first 50
            domain_name = gd_domain["domain"]
            expected_added = domain_name in platform_domains
            assert gd_domain["already_added"] == expected_added, \
                f"Domain {domain_name}: expected already_added={expected_added}, got {gd_domain['already_added']}"
        
        print(f"✓ already_added flags verified for {min(50, len(godaddy_data['domains']))} domains")


class TestGoDaddyImportIntegration:
    """Test GoDaddy import creates all required platform resources"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        self.created_domain_id = None
    
    def teardown_method(self, method):
        """Cleanup after each test"""
        if self.created_domain_id:
            try:
                self.session.delete(f"{BASE_URL}/api/domains/{self.created_domain_id}")
                print(f"Cleaned up test domain: {self.created_domain_id}")
            except:
                pass
    
    def test_imported_domain_appears_in_platform(self):
        """Verify imported domain appears in GET /api/domains"""
        # Get a domain to import
        list_response = self.session.get(f"{BASE_URL}/api/godaddy/domains")
        data = list_response.json()
        
        available_domains = [d for d in data["domains"] if not d["already_added"]]
        if not available_domains:
            pytest.skip("No available domains to test")
        
        domain_name = available_domains[0]["domain"]
        
        # Import
        import_response = self.session.post(
            f"{BASE_URL}/api/godaddy/import",
            json={"domain_name": domain_name, "focus": "bonus"}
        )
        assert import_response.status_code == 200
        self.created_domain_id = import_response.json()["domain"]["id"]
        
        # Verify appears in platform domains
        platform_response = self.session.get(f"{BASE_URL}/api/domains")
        assert platform_response.status_code == 200
        platform_domains = platform_response.json()
        
        found = any(d["domain_name"] == domain_name for d in platform_domains)
        assert found, f"Imported domain {domain_name} not found in platform domains"
        print(f"✓ Imported domain {domain_name} found in platform domains list")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
