import requests
import sys
from datetime import datetime
import json

class TurkishSportsBonusAPITester:
    def __init__(self, base_url="https://sports-bonus-hub.preview.emergentagent.com"):
        self.base_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=30):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=timeout)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=timeout)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    json_data = response.json()
                    if isinstance(json_data, dict):
                        print(f"   Response keys: {list(json_data.keys())[:5]}")
                    elif isinstance(json_data, list):
                        print(f"   Response: List with {len(json_data)} items")
                except:
                    print(f"   Response: {response.text[:100]}...")
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                self.failed_tests.append({
                    "test": name,
                    "expected": expected_status,
                    "actual": response.status_code,
                    "endpoint": endpoint
                })

            return success, response.json() if success and response.content else {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append({
                "test": name,
                "error": str(e),
                "endpoint": endpoint
            })
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root API", "GET", "", 200)

    def test_seed_database(self):
        """Test database seeding"""
        return self.run_test("Seed Database", "POST", "seed", 200)

    def test_bonus_sites_endpoints(self):
        """Test all bonus sites endpoints"""
        print("\n📊 TESTING BONUS SITES ENDPOINTS")
        
        # Get all bonus sites
        success, data = self.run_test("Get All Bonus Sites", "GET", "bonus-sites", 200)
        if not success:
            return False
        
        sites_count = len(data) if isinstance(data, list) else 0
        print(f"   Found {sites_count} bonus sites")
        
        # Get featured bonus sites
        self.run_test("Get Featured Bonus Sites", "GET", "bonus-sites?is_featured=true", 200)
        
        # Get deneme bonus sites
        self.run_test("Get Deneme Bonus Sites", "GET", "bonus-sites?bonus_type=deneme", 200)
        
        # Get limited results
        self.run_test("Get Limited Bonus Sites", "GET", "bonus-sites?limit=3", 200)
        
        # Test single site endpoint if sites exist
        if isinstance(data, list) and len(data) > 0:
            site_id = data[0].get('id')
            if site_id:
                self.run_test("Get Single Bonus Site", "GET", f"bonus-sites/{site_id}", 200)
        
        return True

    def test_articles_endpoints(self):
        """Test all articles endpoints"""
        print("\n📝 TESTING ARTICLES ENDPOINTS")
        
        # Get all articles
        success, data = self.run_test("Get All Articles", "GET", "articles", 200)
        if not success:
            return False
        
        articles_count = len(data) if isinstance(data, list) else 0
        print(f"   Found {articles_count} articles")
        
        # Get spor category articles
        self.run_test("Get Sports Articles", "GET", "articles?category=spor", 200)
        
        # Get bonus category articles
        self.run_test("Get Bonus Articles", "GET", "articles?category=bonus", 200)
        
        # Get limited articles
        self.run_test("Get Limited Articles", "GET", "articles?limit=3", 200)
        
        # Test single article endpoints if articles exist
        if isinstance(data, list) and len(data) > 0:
            article = data[0]
            article_id = article.get('id')
            article_slug = article.get('slug')
            
            if article_id:
                self.run_test("Get Single Article by ID", "GET", f"articles/{article_id}", 200)
            
            if article_slug:
                self.run_test("Get Single Article by Slug", "GET", f"articles/slug/{article_slug}", 200)
        
        return True

    def test_categories_endpoints(self):
        """Test categories endpoints"""
        print("\n🏷️ TESTING CATEGORIES ENDPOINTS")
        
        # Get all categories
        success, data = self.run_test("Get All Categories", "GET", "categories", 200)
        if not success:
            return False
        
        categories_count = len(data) if isinstance(data, list) else 0
        print(f"   Found {categories_count} categories")
        
        # Get bonus categories
        self.run_test("Get Bonus Categories", "GET", "categories?type=bonus", 200)
        
        # Get spor categories
        self.run_test("Get Sports Categories", "GET", "categories?type=spor", 200)
        
        return True

    def test_sports_endpoints(self):
        """Test sports data endpoints"""
        print("\n⚽ TESTING SPORTS ENDPOINTS")
        
        # Get matches (default Premier League)
        success, data = self.run_test("Get Premier League Matches", "GET", "sports/matches", 200)
        if success and isinstance(data, dict):
            matches = data.get('matches', [])
            print(f"   Found {len(matches)} matches")
        
        # Get matches for different leagues
        self.run_test("Get Bundesliga Matches", "GET", "sports/matches?league=BL1", 200)
        self.run_test("Get Serie A Matches", "GET", "sports/matches?league=SA", 200)
        
        # Get standings
        self.run_test("Get Premier League Standings", "GET", "sports/standings", 200)
        
        return True

    def test_ai_endpoints(self):
        """Test AI content generation endpoints"""
        print("\n🤖 TESTING AI ENDPOINTS")
        
        # Test AI content generation
        ai_request = {
            "topic": "Galatasaray vs Fenerbahçe derbi analizi",
            "content_type": "article",
            "language": "tr",
            "keywords": ["galatasaray", "fenerbahçe", "derbi"],
            "tone": "professional",
            "word_count": 300
        }
        
        success, data = self.run_test(
            "Generate AI Article Content", 
            "POST", 
            "ai/generate-content", 
            200, 
            ai_request,
            timeout=60  # AI generation might take longer
        )
        
        if success and isinstance(data, dict):
            content = data.get('content', '')
            print(f"   Generated content length: {len(content)} characters")
        
        # Test different content types
        match_summary_request = {
            "topic": "Manchester United 2-1 Liverpool maç özeti",
            "content_type": "match_summary",
            "language": "tr",
            "tone": "exciting"
        }
        
        self.run_test(
            "Generate Match Summary", 
            "POST", 
            "ai/generate-content", 
            200, 
            match_summary_request,
            timeout=45
        )
        
        return True

    def test_ai_ranking_endpoints(self):
        """Test AI performance ranking system endpoints"""
        print("\n🎯 TESTING AI RANKING SYSTEM")
        
        # Test AI ranking report
        success, data = self.run_test("Get AI Ranking Report", "GET", "ai/ranking-report", 200)
        if success and isinstance(data, dict):
            report = data.get('report', [])
            print(f"   Found {len(report)} sites in ranking report")
            if report:
                # Check if real sites are present
                site_names = [site.get('name', '') for site in report[:8]]
                expected_sites = ['MAXWIN', 'HILTONBET', 'ELEXBET', 'FESTWIN', 'CASINO DIOR', 'BETCI', 'ALFABAHIS', 'TULIPBET']
                found_sites = [name for name in expected_sites if name in site_names]
                print(f"   Real sites found: {found_sites}")
                print(f"   Top 3 sites: {[site.get('name') for site in report[:3]]}")
                
                # Check ranking data structure
                for i, site in enumerate(report[:3]):
                    rank = site.get('rank', 0)
                    score = site.get('performance_score', 0)
                    is_featured = site.get('is_featured', False)
                    data_source = site.get('data_source', '')
                    print(f"   #{rank}: {site.get('name')} - Score: {score}, Featured: {is_featured}, Source: {data_source}")
        
        # Test manual ranking update
        success, data = self.run_test("Update AI Rankings", "POST", "ai/update-rankings", 200)
        if success and isinstance(data, dict):
            updated_count = data.get('sites_updated', 0)
            print(f"   Updated {updated_count} site rankings")
        
        return True

    def test_performance_tracking_endpoints(self):
        """Test performance tracking endpoints"""
        print("\n📊 TESTING PERFORMANCE TRACKING")
        
        # First get a site ID to test with
        success, sites_data = self.run_test("Get Sites for Tracking", "GET", "bonus-sites?limit=1", 200)
        if not success or not isinstance(sites_data, list) or len(sites_data) == 0:
            print("   ⚠️ No sites available for tracking test")
            return False
        
        site_id = sites_data[0].get('id')
        print(f"   Testing tracking with site ID: {site_id}")
        
        # Test tracking events
        tracking_events = [
            {"event_type": "impression", "value": 1.0},
            {"event_type": "cta_click", "value": 1.0},
            {"event_type": "affiliate_click", "value": 1.0},
            {"event_type": "scroll", "value": 75.0},  # 75% scroll depth
            {"event_type": "time_on_page", "value": 45.0}  # 45 seconds
        ]
        
        for event in tracking_events:
            event_data = {
                "site_id": site_id,
                "event_type": event["event_type"],
                "value": event["value"],
                "user_session": "test_session_123",
                "page_url": "https://test.com/"
            }
            
            self.run_test(
                f"Track {event['event_type']} Event",
                "POST",
                "track/event",
                200,
                event_data
            )
        
        # Test batch tracking
        batch_events = [
            {
                "site_id": site_id,
                "event_type": "impression",
                "value": 1.0,
                "user_session": "test_batch_session",
                "page_url": "https://test.com/"
            },
            {
                "site_id": site_id,
                "event_type": "cta_click", 
                "value": 1.0,
                "user_session": "test_batch_session",
                "page_url": "https://test.com/"
            }
        ]
        
        self.run_test(
            "Track Batch Events",
            "POST",
            "track/batch",
            200,
            batch_events
        )
        
        return True

    def test_seo_ai_endpoints(self):
        """Test SEO and AI analysis endpoints"""
        print("\n🔍 TESTING SEO AI ENDPOINTS")
        
        # Test competitor analysis
        competitor_request = {
            "competitor_url": "https://example-competitor.com",
            "analysis_depth": "basic"
        }
        
        success, data = self.run_test(
            "AI Competitor Analysis",
            "POST",
            "ai/competitor-analysis",
            200,
            competitor_request,
            timeout=60
        )
        
        if success and isinstance(data, dict):
            analysis = data.get('analysis', '')
            print(f"   Competitor analysis length: {len(analysis)} characters")
        
        # Test keyword gap analysis
        keywords = ["deneme bonusu", "bahis siteleri", "casino bonus"]
        
        success, data = self.run_test(
            "AI Keyword Gap Analysis",
            "POST",
            "ai/keyword-gap-analysis",
            200,
            keywords,
            timeout=45
        )
        
        if success and isinstance(data, dict):
            analysis = data.get('analysis', '')
            print(f"   Keyword gap analysis length: {len(analysis)} characters")
        
        # Test weekly SEO report
        success, data = self.run_test(
            "Generate Weekly SEO Report",
            "GET",
            "ai/weekly-seo-report",
            200,
            timeout=60
        )
        
        if success and isinstance(data, dict):
            report = data.get('report', '')
            stats = data.get('stats', {})
            print(f"   Weekly report length: {len(report)} characters")
            print(f"   Report stats: {stats}")
        
        return True

    def test_stats_endpoints(self):
        """Test statistics endpoints"""
        print("\n📈 TESTING STATS ENDPOINTS")
        
        success, data = self.run_test("Get Dashboard Stats", "GET", "stats/dashboard", 200)
        if success and isinstance(data, dict):
            print(f"   Stats: Articles: {data.get('total_articles')}, Sites: {data.get('total_bonus_sites')}")
        
        return True

    def test_crud_operations(self):
        """Test CRUD operations with temporary data"""
        print("\n🔧 TESTING CRUD OPERATIONS")
        
        # Test creating a new bonus site
        new_site_data = {
            "name": "Test Bonus Site",
            "logo_url": "https://via.placeholder.com/100",
            "bonus_type": "deneme",
            "bonus_amount": "1000 TL",
            "affiliate_url": "https://example.com",
            "rating": 4.5,
            "features": ["Test Feature"],
            "is_featured": False,
            "order": 999
        }
        
        success, created_site = self.run_test(
            "Create Bonus Site", 
            "POST", 
            "bonus-sites", 
            200,  # API returns 200, not 201
            new_site_data
        )
        
        if success and isinstance(created_site, dict):
            site_id = created_site.get('id')
            print(f"   Created site ID: {site_id}")
            
            # Test updating the created site
            updated_data = {
                **new_site_data,
                "name": "Updated Test Site",
                "rating": 4.8
            }
            
            self.run_test(
                "Update Bonus Site",
                "PUT",
                f"bonus-sites/{site_id}",
                200,
                updated_data
            )
            
            # Test deleting the created site
            self.run_test(
                "Delete Bonus Site",
                "DELETE",
                f"bonus-sites/{site_id}",
                200
            )
        
        # Test creating a new article
        new_article_data = {
            "title": "Test Makale",
            "excerpt": "Bu bir test makalesidir",
            "content": "<p>Test içeriği</p>",
            "category": "bonus",
            "tags": ["test", "bonus"],
            "image_url": "https://via.placeholder.com/800"
        }
        
        success, created_article = self.run_test(
            "Create Article",
            "POST",
            "articles",
            200,
            new_article_data
        )
        
        if success and isinstance(created_article, dict):
            article_id = created_article.get('id')
            print(f"   Created article ID: {article_id}")
            
            # Clean up - delete the test article
            self.run_test(
                "Delete Test Article",
                "DELETE", 
                f"articles/{article_id}",
                200
            )

    def generate_report(self):
        """Generate test report"""
        print("\n" + "="*60)
        print("📋 TEST REPORT SUMMARY")
        print("="*60)
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {len(self.failed_tests)}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.failed_tests:
            print("\n❌ FAILED TESTS:")
            for failure in self.failed_tests:
                print(f"  - {failure['test']}")
                if 'error' in failure:
                    print(f"    Error: {failure['error']}")
                else:
                    print(f"    Expected: {failure['expected']}, Got: {failure['actual']}")
                print(f"    Endpoint: {failure['endpoint']}")
        
        return self.tests_passed == self.tests_run

def main():
    print("🚀 Starting Turkish Sports & Bonus Network API Testing")
    print("="*60)
    
    tester = TurkishSportsBonusAPITester()
    
    try:
        # Test basic connectivity
        tester.test_root_endpoint()
        
        # Seed database first
        tester.test_seed_database()
        
        # Test all endpoints
        tester.test_bonus_sites_endpoints()
        tester.test_articles_endpoints() 
        tester.test_categories_endpoints()
        tester.test_sports_endpoints()
        tester.test_stats_endpoints()
        
        # Test AI endpoints (might be slower)
        tester.test_ai_endpoints()
        
        # Test CRUD operations
        tester.test_crud_operations()
        
        # Generate final report
        success = tester.generate_report()
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n💥 Critical error during testing: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())