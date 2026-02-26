#!/usr/bin/env python3
"""Migration script to push all data to production guncelgiris.ai"""
import json
import requests
import sys
import time

PROD_URL = "https://guncelgiris.ai"
SECRET = "dsbn-migrate-2026-guncelgiris"
BATCH_SIZE = 50

def migrate_collection(name, filepath, mode="replace"):
    with open(filepath, 'r') as f:
        items = json.load(f)
    
    print(f"\n{'='*50}")
    print(f"Migrating {name}: {len(items)} items (mode={mode})")
    
    total_inserted = 0
    total_updated = 0
    
    for i in range(0, len(items), BATCH_SIZE):
        batch = items[i:i+BATCH_SIZE]
        try:
            r = requests.post(
                f"{PROD_URL}/api/migrate/bulk-import",
                json={"secret": SECRET, "collection": name, "items": batch, "mode": mode if i == 0 else "upsert"},
                timeout=30
            )
            if r.status_code == 200:
                data = r.json()
                total_inserted += data.get("inserted", 0)
                total_updated += data.get("updated", 0)
                print(f"  Batch {i//BATCH_SIZE + 1}/{(len(items)+BATCH_SIZE-1)//BATCH_SIZE}: +{data.get('inserted',0)} inserted, {data.get('updated',0)} updated")
            else:
                print(f"  ERROR batch {i//BATCH_SIZE + 1}: HTTP {r.status_code} - {r.text[:200]}")
        except Exception as e:
            print(f"  ERROR batch {i//BATCH_SIZE + 1}: {e}")
        time.sleep(0.5)
    
    print(f"  DONE: {total_inserted} inserted, {total_updated} updated")
    return total_inserted + total_updated

def setup_admin():
    print(f"\n{'='*50}")
    print("Setting up admin user...")
    try:
        r = requests.post(
            f"{PROD_URL}/api/migrate/setup-admin",
            json={"secret": SECRET, "username": "admin", "password": "123123.."},
            timeout=15
        )
        if r.status_code == 200:
            print(f"  OK: {r.json()}")
        else:
            print(f"  ERROR: {r.status_code} - {r.text[:200]}")
    except Exception as e:
        print(f"  ERROR: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("PRODUCTION MIGRATION - guncelgiris.ai")
    print("=" * 50)
    
    # 1. Setup admin
    setup_admin()
    
    # 2. Migrate collections (replace mode = clear + insert)
    migrate_collection("bonus_sites", "/tmp/export_firms.json", "replace")
    migrate_collection("articles", "/tmp/export_articles.json", "replace")
    migrate_collection("categories", "/tmp/export_categories.json", "replace")
    migrate_collection("content_queue", "/tmp/export_queue.json", "replace")
    migrate_collection("domains", "/tmp/export_domains.json", "replace")
    
    # 3. Final verification
    print(f"\n{'='*50}")
    print("VERIFICATION")
    print("=" * 50)
    for endpoint, label in [
        ("/api/bonus-sites", "Firmalar"),
        ("/api/articles?limit=1", "Makaleler"),
        ("/api/categories", "Kategoriler"),
    ]:
        try:
            r = requests.get(f"{PROD_URL}{endpoint}", timeout=10)
            data = r.json()
            count = len(data) if isinstance(data, list) else "?"
            print(f"  {label}: {count}")
        except Exception as e:
            print(f"  {label}: ERROR - {e}")
    
    print("\nMigration complete!")
