"""
Video Library — Object Storage integration + CRUD for video management.
Supports upload (50MB), AI generation (Sora 2), and company-specific video galleries.
"""
import os
import uuid
import logging
import requests
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger("video_library")

STORAGE_URL = "https://integrations.emergentagent.com/objstore/api/v1/storage"
APP_NAME = "guncelgiris"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_TYPES = {"video/mp4", "video/webm", "video/quicktime", "video/x-msvideo"}

_storage_key = None


def init_storage():
    """Initialize object storage — call once at startup."""
    global _storage_key
    if _storage_key:
        return _storage_key
    emergent_key = os.environ.get("EMERGENT_LLM_KEY", "")
    if not emergent_key:
        logger.warning("EMERGENT_LLM_KEY not set — storage disabled")
        return None
    try:
        resp = requests.post(f"{STORAGE_URL}/init", json={"emergent_key": emergent_key}, timeout=30)
        resp.raise_for_status()
        _storage_key = resp.json()["storage_key"]
        logger.info("Object storage initialized")
        return _storage_key
    except Exception as e:
        logger.error(f"Storage init failed: {e}")
        return None


def put_object(path: str, data: bytes, content_type: str) -> dict:
    """Upload file to object storage."""
    key = init_storage()
    if not key:
        raise ValueError("Storage not initialized")
    resp = requests.put(
        f"{STORAGE_URL}/objects/{path}",
        headers={"X-Storage-Key": key, "Content-Type": content_type},
        data=data, timeout=120,
    )
    resp.raise_for_status()
    return resp.json()


def get_object(path: str) -> tuple:
    """Download file from object storage."""
    key = init_storage()
    if not key:
        raise ValueError("Storage not initialized")
    resp = requests.get(
        f"{STORAGE_URL}/objects/{path}",
        headers={"X-Storage-Key": key}, timeout=120,
    )
    resp.raise_for_status()
    return resp.content, resp.headers.get("Content-Type", "video/mp4")


class VideoLibrary:
    """Video library with object storage backend."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def upload_video(self, file_data: bytes, filename: str, content_type: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Upload a video file and create library entry."""
        if len(file_data) > MAX_FILE_SIZE:
            return {"error": f"File too large ({len(file_data)} > {MAX_FILE_SIZE})", "uploaded": False}
        if content_type not in ALLOWED_TYPES:
            return {"error": f"Invalid content type: {content_type}", "uploaded": False}

        ext = filename.rsplit(".", 1)[-1] if "." in filename else "mp4"
        video_id = str(uuid.uuid4())
        storage_path = f"{APP_NAME}/videos/{video_id}.{ext}"

        # Upload to storage
        result = put_object(storage_path, file_data, content_type)

        # Create DB record
        record = {
            "video_id": video_id,
            "storage_path": result.get("path", storage_path),
            "original_filename": filename,
            "content_type": content_type,
            "size": result.get("size", len(file_data)),
            "title": metadata.get("title", filename),
            "description": metadata.get("description", ""),
            "company_slug": metadata.get("company_slug", ""),
            "company_name": metadata.get("company_name", ""),
            "tags": metadata.get("tags", []),
            "category": metadata.get("category", "general"),
            "thumbnail_url": metadata.get("thumbnail_url", ""),
            "duration_seconds": metadata.get("duration_seconds", 0),
            "source": metadata.get("source", "upload"),  # upload / ai_generated / external
            "external_url": metadata.get("external_url", ""),
            "view_count": 0,
            "is_featured": False,
            "is_published": True,
            "is_deleted": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        await self.db.video_library.insert_one({k: v for k, v in record.items() if k != "_id"})
        return {"uploaded": True, "video": {k: v for k, v in record.items() if k != "_id"}}

    async def register_external(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Register an external/AI-generated video without uploading."""
        video_id = str(uuid.uuid4())
        record = {
            "video_id": video_id,
            "storage_path": "",
            "original_filename": "",
            "content_type": "video/mp4",
            "size": 0,
            "title": metadata.get("title", ""),
            "description": metadata.get("description", ""),
            "company_slug": metadata.get("company_slug", ""),
            "company_name": metadata.get("company_name", ""),
            "tags": metadata.get("tags", []),
            "category": metadata.get("category", "general"),
            "thumbnail_url": metadata.get("thumbnail_url", ""),
            "duration_seconds": metadata.get("duration_seconds", 0),
            "source": metadata.get("source", "external"),
            "external_url": metadata.get("external_url", ""),
            "view_count": 0,
            "is_featured": metadata.get("is_featured", False),
            "is_published": True,
            "is_deleted": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        await self.db.video_library.insert_one({k: v for k, v in record.items() if k != "_id"})
        return {"registered": True, "video": {k: v for k, v in record.items() if k != "_id"}}

    async def list_videos(self, company_slug: str = None, category: str = None, limit: int = 30, offset: int = 0) -> Dict[str, Any]:
        """List videos with optional filters."""
        query: Dict[str, Any] = {"is_deleted": False, "is_published": True}
        if company_slug:
            query["company_slug"] = company_slug
        if category:
            query["category"] = category
        total = await self.db.video_library.count_documents(query)
        videos = await self.db.video_library.find(query, {"_id": 0}).sort("created_at", -1).skip(offset).limit(limit).to_list(limit)
        return {"videos": videos, "total": total, "limit": limit, "offset": offset}

    async def get_video(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get a single video by ID and increment view count."""
        video = await self.db.video_library.find_one({"video_id": video_id, "is_deleted": False}, {"_id": 0})
        if video:
            await self.db.video_library.update_one({"video_id": video_id}, {"$inc": {"view_count": 1}})
            video["view_count"] = video.get("view_count", 0) + 1
        return video

    async def get_file(self, video_id: str) -> Optional[tuple]:
        """Get video file data from storage."""
        video = await self.db.video_library.find_one({"video_id": video_id, "is_deleted": False}, {"_id": 0})
        if not video or not video.get("storage_path"):
            return None
        data, ct = get_object(video["storage_path"])
        return data, video.get("content_type", ct)

    async def delete_video(self, video_id: str) -> bool:
        """Soft delete a video."""
        result = await self.db.video_library.update_one(
            {"video_id": video_id},
            {"$set": {"is_deleted": True, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        return result.modified_count > 0
