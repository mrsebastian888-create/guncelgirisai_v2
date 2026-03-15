"""
Wallpaper Library — AI image generation + Object Storage for SEO-optimized company visuals.
Generates branded wallpapers with company name + bonus info.
SEO-friendly filenames and URLs.
"""
import os
import uuid
import logging
import requests
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger("wallpaper_library")

STORAGE_URL = "https://integrations.emergentagent.com/objstore/api/v1/storage"
APP_NAME = "guncelgiris"

_storage_key = None


def _init_storage():
    global _storage_key
    if _storage_key:
        return _storage_key
    emergent_key = os.environ.get("EMERGENT_LLM_KEY", "")
    if not emergent_key:
        return None
    try:
        resp = requests.post(f"{STORAGE_URL}/init", json={"emergent_key": emergent_key}, timeout=30)
        resp.raise_for_status()
        _storage_key = resp.json()["storage_key"]
        return _storage_key
    except Exception as e:
        logger.error(f"Storage init failed: {e}")
        return None


def _put_object(path: str, data: bytes, content_type: str) -> dict:
    key = _init_storage()
    if not key:
        raise ValueError("Storage not initialized")
    resp = requests.put(
        f"{STORAGE_URL}/objects/{path}",
        headers={"X-Storage-Key": key, "Content-Type": content_type},
        data=data, timeout=120,
    )
    resp.raise_for_status()
    return resp.json()


def _get_object(path: str) -> tuple:
    key = _init_storage()
    if not key:
        raise ValueError("Storage not initialized")
    resp = requests.get(
        f"{STORAGE_URL}/objects/{path}",
        headers={"X-Storage-Key": key}, timeout=60,
    )
    resp.raise_for_status()
    return resp.content, resp.headers.get("Content-Type", "image/png")


def build_seo_filename(company_name: str, bonus_type: str) -> str:
    """Build SEO-friendly filename: casibom-deneme-bonusu-2026.png"""
    tr_map = {'ç': 'c', 'ğ': 'g', 'ı': 'i', 'ö': 'o', 'ş': 's', 'ü': 'u',
              'Ç': 'c', 'Ğ': 'g', 'İ': 'i', 'Ö': 'o', 'Ş': 's', 'Ü': 'u'}
    name = company_name.lower()
    for k, v in tr_map.items():
        name = name.replace(k, v)
    import re
    name = re.sub(r'[^a-z0-9]+', '-', name).strip('-')

    type_map = {
        "deneme": "deneme-bonusu",
        "hosgeldin": "hosgeldin-bonusu",
        "casino": "casino-bonusu",
        "spor": "spor-bonusu",
        "kayip": "kayip-bonusu",
    }
    bonus_slug = type_map.get(bonus_type, "bonus")
    return f"{name}-{bonus_slug}-2026.png"


def build_seo_slug(company_name: str, bonus_type: str) -> str:
    """Build SEO-friendly URL slug: casibom-deneme-bonusu-2026"""
    filename = build_seo_filename(company_name, bonus_type)
    return filename.replace(".png", "")


def build_wallpaper_prompt(company_name: str, bonus_amount: str, bonus_type: str) -> str:
    """Build AI image generation prompt for company wallpaper."""
    type_labels = {
        "deneme": "Deneme Bonusu",
        "hosgeldin": "Hosgeldin Bonusu",
        "casino": "Casino Bonusu",
        "spor": "Spor Bonusu",
        "kayip": "Kayip Bonusu",
    }
    bonus_label = type_labels.get(bonus_type, "Bonus")

    return (
        f"Premium dark background with neon green glowing accents and subtle geometric patterns. "
        f'Bold text "{company_name.upper()}" in large modern sans-serif typography at center. '
        f'Below it: "{bonus_amount} {bonus_label}" in smaller elegant white text. '
        f"Abstract light particles and geometric shapes around the text. "
        f"Professional digital advertisement style. Clean, modern, high contrast. "
        f"No logos, no real photos, no copyrighted elements."
    )


class WallpaperLibrary:
    """Wallpaper library with AI generation and object storage."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

    async def generate_wallpaper(self, company_slug: str, company_name: str,
                                  bonus_amount: str, bonus_type: str,
                                  custom_prompt: str = None) -> Dict[str, Any]:
        """Generate a wallpaper using GPT Image 1 and store in cloud."""
        seo_filename = build_seo_filename(company_name, bonus_type)
        seo_slug = build_seo_slug(company_name, bonus_type)
        prompt = custom_prompt or build_wallpaper_prompt(company_name, bonus_amount, bonus_type)

        # Check if already exists
        existing = await self.db.wallpaper_library.find_one(
            {"seo_slug": seo_slug, "is_deleted": False}, {"_id": 0, "wallpaper_id": 1}
        )
        if existing:
            return {"generated": False, "reason": "already_exists", "seo_slug": seo_slug}

        try:
            from emergentintegrations.llm.openai.image_generation import OpenAIImageGeneration

            emergent_key = os.environ.get("EMERGENT_LLM_KEY", "")
            if not emergent_key:
                return {"generated": False, "error": "EMERGENT_LLM_KEY not set"}

            ig = OpenAIImageGeneration(api_key=emergent_key)
            images = await ig.generate_images(
                prompt=prompt,
                model="gpt-image-1",
                number_of_images=1,
                quality="medium",
            )
            image_bytes = images[0] if images and len(images) > 0 else None
            if not image_bytes:
                return {"generated": False, "error": "No image bytes returned"}

            # Upload to cloud storage
            storage_path = f"{APP_NAME}/wallpapers/{seo_filename}"
            _put_object(storage_path, image_bytes, "image/png")

            # Build alt text and title for SEO
            type_labels = {"deneme": "Deneme Bonusu", "hosgeldin": "Hosgeldin Bonusu",
                          "casino": "Casino Bonusu", "spor": "Spor Bonusu", "kayip": "Kayip Bonusu"}
            bonus_label = type_labels.get(bonus_type, "Bonus")

            wallpaper_id = str(uuid.uuid4())
            record = {
                "wallpaper_id": wallpaper_id,
                "seo_slug": seo_slug,
                "seo_filename": seo_filename,
                "storage_path": storage_path,
                "company_slug": company_slug,
                "company_name": company_name,
                "bonus_amount": bonus_amount,
                "bonus_type": bonus_type,
                "title": f"{company_name} {bonus_label} 2026",
                "alt_text": f"{company_name} {bonus_label} 2026 - {bonus_amount} Bonus Firsati",
                "description": f"{company_name} {bonus_amount} {bonus_label.lower()} firsati. Guncel bonus ve giris bilgileri.",
                "prompt": prompt,
                "size": "1024x1024",
                "content_type": "image/png",
                "file_size": len(image_bytes),
                "tags": [company_slug, bonus_type, "2026", "wallpaper"],
                "category": "company_promo",
                "source": "ai_generated",
                "view_count": 0,
                "download_count": 0,
                "is_featured": False,
                "is_published": True,
                "is_deleted": False,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
            await self.db.wallpaper_library.insert_one({k: v for k, v in record.items() if k != "_id"})

            return {"generated": True, "wallpaper": {k: v for k, v in record.items() if k != "_id"}}
        except Exception as e:
            logger.error(f"Wallpaper generation failed for {company_name}: {e}")
            return {"generated": False, "error": str(e)}

    async def list_wallpapers(self, company_slug: str = None, category: str = None,
                               limit: int = 30, offset: int = 0) -> Dict[str, Any]:
        query: Dict[str, Any] = {"is_deleted": False, "is_published": True}
        if company_slug:
            query["company_slug"] = company_slug
        if category:
            query["category"] = category
        total = await self.db.wallpaper_library.count_documents(query)
        items = await self.db.wallpaper_library.find(query, {"_id": 0}).sort("created_at", -1).skip(offset).limit(limit).to_list(limit)
        return {"wallpapers": items, "total": total, "limit": limit, "offset": offset}

    async def get_wallpaper(self, seo_slug: str) -> Optional[Dict[str, Any]]:
        wp = await self.db.wallpaper_library.find_one({"seo_slug": seo_slug, "is_deleted": False}, {"_id": 0})
        if wp:
            await self.db.wallpaper_library.update_one({"seo_slug": seo_slug}, {"$inc": {"view_count": 1}})
            wp["view_count"] = wp.get("view_count", 0) + 1
        return wp

    async def get_file(self, seo_slug: str) -> Optional[tuple]:
        wp = await self.db.wallpaper_library.find_one({"seo_slug": seo_slug, "is_deleted": False}, {"_id": 0})
        if not wp or not wp.get("storage_path"):
            return None
        data, ct = _get_object(wp["storage_path"])
        return data, wp.get("content_type", ct), wp.get("seo_filename", "wallpaper.png")

    async def delete_wallpaper(self, seo_slug: str) -> bool:
        result = await self.db.wallpaper_library.update_one(
            {"seo_slug": seo_slug},
            {"$set": {"is_deleted": True, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        return result.modified_count > 0
