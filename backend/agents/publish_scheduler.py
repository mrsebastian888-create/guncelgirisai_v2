"""
GG2026 Phase 7 — Controlled Publishing System
Queue-based SEO publishing with daily rate limits and content-type scheduling.

Rules:
- 8-15 pages per day (configurable)
- Day-of-week content types:
  Mon=hub, Tue=company, Wed=guides, Thu=comparison, Fri=bonus, Sat=articles, Sun=updates
- Manual override support
- Background scheduler processes queue automatically
"""
import uuid
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger("publish_scheduler")

# Day-of-week → content type mapping (0=Monday, 6=Sunday)
DAY_CONTENT_MAP = {
    0: {"day": "Monday", "content_types": ["hub_page", "intent_hub", "license_hub", "country_hub"], "label": "Hub Sayfalari"},
    1: {"day": "Tuesday", "content_types": ["company_page", "company_sub", "company_x_payment", "company_x_year"], "label": "Firma Sayfalari"},
    2: {"day": "Wednesday", "content_types": ["guide", "guide_hub", "guide_x_topic"], "label": "Rehberler"},
    3: {"day": "Thursday", "content_types": ["comparison", "karsilastirma", "intent_x_category"], "label": "Karsilastirma Sayfalari"},
    4: {"day": "Friday", "content_types": ["bonus", "bonus_page", "company_x_bonus", "deneme-bonusu-rehberi", "hosgeldin-bonusu-rehberi"], "label": "Bonus Sayfalari"},
    5: {"day": "Saturday", "content_types": ["article", "company_article", "inceleme", "giris-rehberi"], "label": "Makaleler"},
    6: {"day": "Sunday", "content_types": ["update", "refresh", "content_update"], "label": "Icerik Guncellemeleri"},
}

# Publishing rate limits
DEFAULT_MIN_PER_DAY = 8
DEFAULT_MAX_PER_DAY = 15


class PublishQueue:
    """Queue-based publishing system with rate control."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def add_to_queue(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add items to the publish queue.
        Each item: {content_type, slug, title, source, data, priority}
        """
        added = 0
        skipped = 0
        for item in items:
            slug = item.get("slug", "")
            if not slug:
                skipped += 1
                continue
            # Check for duplicates in queue
            existing = await self.db.publish_queue.find_one(
                {"slug": slug, "status": {"$in": ["pending", "scheduled"]}},
                {"_id": 0, "queue_id": 1}
            )
            if existing:
                skipped += 1
                continue

            record = {
                "queue_id": str(uuid.uuid4()),
                "slug": slug,
                "title": item.get("title", ""),
                "content_type": item.get("content_type", "article"),
                "source": item.get("source", "manual"),
                "priority": item.get("priority", 5),  # 1=highest, 10=lowest
                "data": item.get("data", {}),
                "status": "pending",  # pending → scheduled → publishing → published → failed
                "scheduled_date": None,
                "published_at": None,
                "error": None,
                "manual_override": False,
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            await self.db.publish_queue.insert_one({k: v for k, v in record.items() if k != "_id"})
            added += 1

        return {"added": added, "skipped": skipped, "total": len(items)}

    async def schedule_items(self, min_per_day: int = DEFAULT_MIN_PER_DAY, max_per_day: int = DEFAULT_MAX_PER_DAY) -> Dict[str, Any]:
        """Assign dates to pending queue items based on day-of-week rules."""
        pending = await self.db.publish_queue.find(
            {"status": "pending"},
            {"_id": 0}
        ).sort("priority", 1).to_list(500)

        if not pending:
            return {"scheduled": 0, "message": "Kuyrukta bekleyen oge yok"}

        # Find the next available publish date
        today = datetime.now(timezone.utc).date()

        # Count already scheduled items per day
        scheduled_counts = {}
        existing_scheduled = await self.db.publish_queue.find(
            {"status": {"$in": ["scheduled", "publishing", "published"]}, "scheduled_date": {"$ne": None}},
            {"_id": 0, "scheduled_date": 1}
        ).to_list(5000)
        for item in existing_scheduled:
            date_str = str(item.get("scheduled_date", ""))[:10]
            scheduled_counts[date_str] = scheduled_counts.get(date_str, 0) + 1

        scheduled = 0
        current_date = today

        for item in pending:
            content_type = item.get("content_type", "article")

            # Find next valid date for this content type
            target_date = current_date
            attempts = 0
            while attempts < 30:  # look up to 30 days ahead
                weekday = target_date.weekday()
                day_config = DAY_CONTENT_MAP.get(weekday, DAY_CONTENT_MAP[5])
                date_str = target_date.isoformat()
                day_count = scheduled_counts.get(date_str, 0)

                # Check if content type fits this day AND day isn't full
                if content_type in day_config["content_types"] and day_count < max_per_day:
                    break
                # If no specific day matches, use any day that isn't full (after checking all 7 days)
                if attempts >= 7 and day_count < max_per_day:
                    break
                target_date += timedelta(days=1)
                attempts += 1

            if attempts >= 30:
                continue  # Skip if no slot found in 30 days

            date_str = target_date.isoformat()
            scheduled_counts[date_str] = scheduled_counts.get(date_str, 0) + 1

            await self.db.publish_queue.update_one(
                {"queue_id": item["queue_id"]},
                {"$set": {
                    "status": "scheduled",
                    "scheduled_date": date_str,
                }}
            )
            scheduled += 1

        return {"scheduled": scheduled, "total_pending": len(pending)}

    async def publish_due(self) -> Dict[str, Any]:
        """Publish items that are scheduled for today or earlier."""
        today = datetime.now(timezone.utc).date().isoformat()

        items = await self.db.publish_queue.find(
            {"status": "scheduled", "scheduled_date": {"$lte": today}},
            {"_id": 0}
        ).sort("priority", 1).limit(DEFAULT_MAX_PER_DAY).to_list(DEFAULT_MAX_PER_DAY)

        published = 0
        failed = 0
        for item in items:
            try:
                # Mark as publishing
                await self.db.publish_queue.update_one(
                    {"queue_id": item["queue_id"]},
                    {"$set": {"status": "publishing"}}
                )

                # Activate the page
                slug = item.get("slug", "")
                source = item.get("source", "")

                if source == "programmatic":
                    # Activate programmatic page
                    await self.db.programmatic_pages.update_one(
                        {"slug": slug},
                        {"$set": {"is_active": True, "published_at": datetime.now(timezone.utc).isoformat()}}
                    )
                elif source == "company_article":
                    await self.db.company_articles.update_one(
                        {"slug": slug},
                        {"$set": {"is_published": True, "updated_at": datetime.now(timezone.utc).isoformat()}}
                    )
                elif source == "article":
                    await self.db.articles.update_one(
                        {"slug": slug},
                        {"$set": {"is_published": True, "updated_at": datetime.now(timezone.utc).isoformat()}}
                    )

                # Mark as published
                await self.db.publish_queue.update_one(
                    {"queue_id": item["queue_id"]},
                    {"$set": {
                        "status": "published",
                        "published_at": datetime.now(timezone.utc).isoformat(),
                    }}
                )
                published += 1
            except Exception as e:
                await self.db.publish_queue.update_one(
                    {"queue_id": item["queue_id"]},
                    {"$set": {"status": "failed", "error": str(e)}}
                )
                failed += 1

        return {"published": published, "failed": failed, "due_items": len(items)}

    async def manual_publish(self, queue_ids: List[str]) -> Dict[str, Any]:
        """Override: immediately publish specific items regardless of schedule."""
        published = 0
        for qid in queue_ids:
            item = await self.db.publish_queue.find_one({"queue_id": qid}, {"_id": 0})
            if not item:
                continue
            await self.db.publish_queue.update_one(
                {"queue_id": qid},
                {"$set": {
                    "status": "published",
                    "published_at": datetime.now(timezone.utc).isoformat(),
                    "manual_override": True,
                }}
            )
            published += 1
        return {"published": published, "total_requested": len(queue_ids)}

    async def get_queue_status(self) -> Dict[str, Any]:
        """Get overall queue status and daily schedule."""
        total = await self.db.publish_queue.count_documents({})
        pending = await self.db.publish_queue.count_documents({"status": "pending"})
        scheduled = await self.db.publish_queue.count_documents({"status": "scheduled"})
        published = await self.db.publish_queue.count_documents({"status": "published"})
        failed = await self.db.publish_queue.count_documents({"status": "failed"})

        # Today's schedule
        today = datetime.now(timezone.utc)
        today_str = today.date().isoformat()
        weekday = today.weekday()
        day_config = DAY_CONTENT_MAP.get(weekday, DAY_CONTENT_MAP[5])
        today_published = await self.db.publish_queue.count_documents({"scheduled_date": today_str, "status": "published"})
        today_scheduled = await self.db.publish_queue.count_documents({"scheduled_date": today_str, "status": "scheduled"})

        # Next 7 days forecast
        forecast = []
        for i in range(7):
            day = today + timedelta(days=i)
            day_str = day.date().isoformat()
            d_config = DAY_CONTENT_MAP.get(day.weekday(), DAY_CONTENT_MAP[5])
            d_count = await self.db.publish_queue.count_documents({"scheduled_date": day_str, "status": {"$in": ["scheduled", "published"]}})
            forecast.append({
                "date": day_str,
                "day": d_config["day"],
                "content_type": d_config["label"],
                "items_count": d_count,
                "capacity_remaining": max(0, DEFAULT_MAX_PER_DAY - d_count),
            })

        return {
            "total": total,
            "pending": pending,
            "scheduled": scheduled,
            "published": published,
            "failed": failed,
            "today": {
                "date": today_str,
                "day": day_config["day"],
                "content_type": day_config["label"],
                "published": today_published,
                "scheduled": today_scheduled,
                "limit": DEFAULT_MAX_PER_DAY,
            },
            "rate_limits": {
                "min_per_day": DEFAULT_MIN_PER_DAY,
                "max_per_day": DEFAULT_MAX_PER_DAY,
            },
            "schedule": DAY_CONTENT_MAP,
            "forecast": forecast,
        }

    async def get_queue_items(self, status: str = None, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """List queue items with optional status filter."""
        query: Dict[str, Any] = {}
        if status:
            query["status"] = status
        total = await self.db.publish_queue.count_documents(query)
        items = await self.db.publish_queue.find(query, {"_id": 0}).sort([("priority", 1), ("created_at", 1)]).skip(offset).limit(limit).to_list(limit)
        return {"items": items, "total": total, "limit": limit, "offset": offset}

    async def remove_from_queue(self, queue_ids: List[str]) -> Dict[str, Any]:
        """Remove items from queue (only pending/scheduled)."""
        result = await self.db.publish_queue.delete_many(
            {"queue_id": {"$in": queue_ids}, "status": {"$in": ["pending", "scheduled"]}}
        )
        return {"removed": result.deleted_count, "requested": len(queue_ids)}

    async def reschedule_failed(self) -> Dict[str, Any]:
        """Move failed items back to pending for rescheduling."""
        result = await self.db.publish_queue.update_many(
            {"status": "failed"},
            {"$set": {"status": "pending", "error": None, "scheduled_date": None}}
        )
        return {"rescheduled": result.modified_count}


class PublishSchedulerDaemon:
    """Background daemon that runs publish_due() periodically."""

    def __init__(self):
        self.is_running = False
        self.task = None
        self.check_interval_minutes = 30
        self.last_run = None
        self.last_result = None

    async def start(self, db: AsyncIOMotorDatabase):
        if self.is_running:
            return
        self.is_running = True
        self.db = db
        self.task = asyncio.create_task(self._run_loop())
        logger.info("Publish scheduler daemon started")

    async def stop(self):
        self.is_running = False
        if self.task:
            self.task.cancel()
            self.task = None
        logger.info("Publish scheduler daemon stopped")

    async def _run_loop(self):
        while self.is_running:
            try:
                queue = PublishQueue(self.db)
                # Auto-schedule pending items
                await queue.schedule_items()
                # Publish due items
                result = await queue.publish_due()
                self.last_run = datetime.now(timezone.utc).isoformat()
                self.last_result = result
                if result.get("published", 0) > 0:
                    logger.info(f"Publish scheduler: published {result['published']} items")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Publish scheduler error: {e}")
            await asyncio.sleep(self.check_interval_minutes * 60)
