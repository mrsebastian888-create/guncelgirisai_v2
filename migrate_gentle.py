#!/usr/bin/env python3
"""Gentle migration - small batches with delays"""
import json
import requests
import time

PROD_URL = "https://guncelgiris.ai"
SECRET = "dsbn-migrate-2026-guncelgiris"
BATCH = 5
DELAY = 3

def push(collection, filepath):
    with open(filepath) as f:
        items = json.load(f)
    
    print(f"\n--- {collection}: {len(items)} items ---")
    ok = 0
    fail = 0
    
    for i in range(0, len(items), BATCH):
        batch = items[i:i+BATCH]
        try:
            r = requests.post(
                f"{PROD_URL}/api/migrate/bulk-import",
                json={"secret": SECRET, "collection": collection, "items": batch, "mode": "upsert"},
                timeout=20
            )
            if r.status_code == 200:
                d = r.json()
                ok += d.get("inserted", 0) + d.get("updated", 0)
                print(f"  [{i+1}-{i+len(batch)}] OK ({d.get('inserted',0)}+{d.get('updated',0)})")
            else:
                fail += len(batch)
                print(f"  [{i+1}-{i+len(batch)}] FAIL: HTTP {r.status_code}")
                if r.status_code in (502, 520):
                    print("  Server recovering, waiting 10s...")
                    time.sleep(10)
        except Exception as e:
            fail += len(batch)
            print(f"  [{i+1}-{i+len(batch)}] ERROR: {e}")
            time.sleep(10)
        time.sleep(DELAY)
    
    print(f"  RESULT: {ok} ok, {fail} fail")
    return ok

# 1. Admin
print("=== ADMIN SETUP ===")
try:
    r = requests.post(f"{PROD_URL}/api/migrate/setup-admin",
        json={"secret": SECRET, "username": "admin", "password": "123123.."},
        timeout=15)
    print(f"Admin: {r.status_code} - {r.text[:100]}")
except Exception as e:
    print(f"Admin ERROR: {e}")

time.sleep(DELAY)

# 2. Firms (most important)
push("bonus_sites", "/tmp/export_firms.json")

# 3. Articles
push("articles", "/tmp/export_articles.json")

# 4. Categories
push("categories", "/tmp/export_categories.json")

# 5. Content queue
push("content_queue", "/tmp/export_queue.json")

# 6. Domains
push("domains", "/tmp/export_domains.json")

# Verify
print("\n=== VERIFY ===")
time.sleep(3)
for ep, label in [("/api/bonus-sites", "Firma"), ("/api/articles?limit=1", "Makale"), ("/api/categories", "Kategori")]:
    try:
        r = requests.get(f"{PROD_URL}{ep}", timeout=10)
        d = r.json()
        print(f"  {label}: {len(d)}")
    except:
        print(f"  {label}: ERROR")
