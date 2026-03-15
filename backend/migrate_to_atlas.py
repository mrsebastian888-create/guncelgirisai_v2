"""
Migration script: Import data from JSON files to MongoDB Atlas.
Run this once on your local machine to migrate data from Emergent to Atlas.

Usage:
  python migrate_to_atlas.py --atlas-url "mongodb+srv://user:pass@cluster.mongodb.net/dbname"

Or set MONGO_URL in .env and run:
  python migrate_to_atlas.py
"""
import json
import os
import sys
from pymongo import MongoClient

# Atlas connection
ATLAS_URL = sys.argv[2] if len(sys.argv) > 2 and sys.argv[1] == "--atlas-url" else os.environ.get("MONGO_URL", "")
DB_NAME = os.environ.get("DB_NAME", "guncelgiris_db")

if not ATLAS_URL:
    print("ERROR: Atlas URL not provided.")
    print("Usage: python migrate_to_atlas.py --atlas-url 'mongodb+srv://...'")
    print("Or set MONGO_URL in .env")
    sys.exit(1)

# Migration files
MIGRATIONS = [
    ("migration_videos.json", "video_library"),
    ("migration_wallpapers.json", "wallpaper_library"),
    ("migration_shortlinks.json", "short_links"),
    ("migration_programmatic.json", "programmatic_pages"),
    ("migration_company_articles.json", "company_articles"),
    ("migration_agent_jobs.json", "agent_jobs"),
]


def migrate():
    print(f"Connecting to Atlas: {ATLAS_URL[:40]}...")
    client = MongoClient(ATLAS_URL)
    db = client[DB_NAME]

    # Test connection
    db.command("ping")
    print("Atlas connection OK\n")

    total = 0
    for filename, collection_name in MIGRATIONS:
        filepath = os.path.join(os.path.dirname(__file__), filename)
        if not os.path.exists(filepath):
            print(f"SKIP: {filename} not found")
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not data:
            print(f"SKIP: {filename} is empty")
            continue

        collection = db[collection_name]

        # Determine unique key for upsert
        if collection_name == "video_library":
            key_field = "video_id"
        elif collection_name == "wallpaper_library":
            key_field = "seo_slug"
        elif collection_name == "short_links":
            key_field = "slug"
        elif collection_name == "programmatic_pages":
            key_field = "slug"
        elif collection_name == "company_articles":
            key_field = "id"
        elif collection_name == "agent_jobs":
            key_field = "job_id"
        else:
            key_field = "id"

        inserted = 0
        updated = 0
        for doc in data:
            key_value = doc.get(key_field)
            if not key_value:
                continue
            result = collection.update_one(
                {key_field: key_value},
                {"$set": doc},
                upsert=True,
            )
            if result.upserted_id:
                inserted += 1
            elif result.modified_count:
                updated += 1

        print(f"OK: {collection_name:25} → {inserted} inserted, {updated} updated (from {len(data)} records)")
        total += inserted + updated

    print(f"\nMigration complete: {total} total operations")
    client.close()


if __name__ == "__main__":
    migrate()
