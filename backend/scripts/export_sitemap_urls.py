#!/usr/bin/env python3
"""
Site haritasındaki tüm URL'leri dışa aktarır.
Kullanım: backend klasöründen: python scripts/export_sitemap_urls.py
Çıktı: docs/SITEMAP_TAM_LISTE.md
"""
import asyncio
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / ".env")
sys.path.insert(0, str(BACKEND_DIR))
os.chdir(BACKEND_DIR)

MONGO_URL = os.environ.get("MONGO_URL", "")
DB_NAME = os.environ.get("DB_NAME", "test_database")
FRONTEND_BASE = os.environ.get("FRONTEND_BASE_URL", "https://www.guncelgiris.ai").rstrip("/")
API_BASE = os.environ.get("API_BASE_URL", "https://api.guncelgiris.ai")

async def main():
    from motor.motor_asyncio import AsyncIOMotorClient

    all_urls = []
    base = FRONTEND_BASE

    # Statik sayfalar
    static = [
        ("/", "Ana sayfa"),
        ("/deneme-bonusu", "Deneme bonusu"),
        ("/hosgeldin-bonusu", "Hoşgeldin bonusu"),
        ("/spor-haberleri", "Spor haberleri"),
        ("/companies", "AI Company Intelligence"),
    ]
    for path, label in static:
        all_urls.append(("pages", base + path, label))

    if not MONGO_URL:
        # DB yoksa sadece statik + açıklama
        lines = [
            "# Site Haritası — Tam URL Listesi",
            "",
            f"**Base URL:** {base}",
            f"**Oluşturulma:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC",
            "",
            "## Statik sayfalar",
            "",
        ]
        for _, url, label in all_urls:
            lines.append(f"- {url} — {label}")
        lines.extend([
            "",
            "---",
            "",
            "Veritabanı bağlantısı olmadan sadece statik sayfalar listelendi. Tam liste için:",
            "`cd backend && python scripts/export_sitemap_urls.py` (MONGO_URL ve DB_NAME .env'de olmalı).",
            "",
        ])
        out_path = BACKEND_DIR.parent / "docs" / "SITEMAP_TAM_LISTE.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"Statik URL'ler yazıldı: {out_path}")
        return

    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]

    # Kategoriler → /bonus/{slug}
    try:
        cats = await db.categories.find({}, {"_id": 0, "slug": 1}).to_list(100)
        for c in cats:
            slug = c.get("slug", "")
            if slug:
                all_urls.append(("pages", f"{base}/bonus/{slug}", f"Bonus kategori: {slug}"))
    except Exception as e:
        print(f"Kategoriler alınamadı: {e}", file=sys.stderr)

    firms = []
    try:
        firms = await db.bonus_sites.find({"is_active": True}, {"_id": 0, "slug": 1, "name": 1}).to_list(500)
        for f in firms:
            slug = f.get("slug", "")
            if slug:
                name = f.get("name", slug)
                all_urls.append(("firms", f"{base}/{slug}", name))
    except Exception as e:
        print(f"Firmalar alınamadı: {e}", file=sys.stderr)

    # Şirketler → /companies/{slug}
    try:
        companies = await db.companies.find(
            {"is_active": True, "is_approved": True},
            {"_id": 0, "slug": 1},
        ).to_list(3000)
        for co in companies:
            slug = co.get("slug", "")
            if slug:
                all_urls.append(("companies", f"{base}/companies/{slug}", slug))
    except Exception as e:
        print(f"Şirketler alınamadı: {e}", file=sys.stderr)

    # Videolar → /{slug}/video
    try:
        for f in firms:
            slug = f.get("slug", "")
            if slug:
                all_urls.append(("videos", f"{base}/{slug}/video", slug))
    except Exception as e:
        print(f"Videolar alınamadı: {e}", file=sys.stderr)

    # Makaleler → /makale/{slug}
    try:
        articles = await db.articles.find(
            {"is_published": True},
            {"_id": 0, "slug": 1, "title": 1},
        ).to_list(5000)
        for a in articles:
            slug = a.get("slug", "")
            if slug:
                title = (a.get("title") or slug)[:50]
                all_urls.append(("articles", f"{base}/makale/{slug}", title))
    except Exception as e:
        print(f"Makaleler alınamadı: {e}", file=sys.stderr)

    client.close()

    # Gruplara göre say
    by_group = {}
    for g, url, _ in all_urls:
        by_group[g] = by_group.get(g, 0) + 1

    # Markdown yaz
    lines = [
        "# Site Haritası — Tam URL Listesi",
        "",
        f"**Base URL:** {base}",
        f"**Oluşturulma:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')} UTC",
        f"**Toplam URL:** {len(all_urls)}",
        "",
        "## Özet",
        "",
        "| Kaynak | Adet |",
        "|--------|------|",
    ]
    for g in ["pages", "firms", "companies", "videos", "articles"]:
        n = by_group.get(g, 0)
        lines.append(f"| {g} | {n} |")
    lines.append("")
    lines.append("---")
    lines.append("")

    current_group = None
    for g, url, label in all_urls:
        if g != current_group:
            current_group = g
            lines.append(f"## {g.upper()}")
            lines.append("")
        lines.append(f"- {url}")
    lines.append("")

    out_path = BACKEND_DIR.parent / "docs" / "SITEMAP_TAM_LISTE.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Toplam {len(all_urls)} URL yazıldı: {out_path}")


if __name__ == "__main__":
    asyncio.run(main())
