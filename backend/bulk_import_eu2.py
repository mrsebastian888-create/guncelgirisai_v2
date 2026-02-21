"""
Bulk European firm import - 100 NEW brands only
"""
import asyncio
import random
import hashlib
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "test_database")

NEW_EUROPE_FIRMS = [
    "Betcris","Marathonbet","Dafabet","10Bet","Vbet","22Bet","Melbet",
    "Betobet","Parimatch","Mostbet","1Win","Rabona","Rolletto","Sportsbet.io",
    "Stake","Cloudbet","Thunderpick","Midnite","Kwiff","LiveScore Bet",
    "Fitzdares","BetGoodwin","Spreadex","Matchbook","Smarkets","Mansion Casino",
    "32Red","Grosvenor Casino","Genting Casino","Sky Bet","Sky Vegas",
    "Virgin Bet","Lottoland","Lotto247","Jackpotjoy","Tombola","Mecca Bingo",
    "Foxy Bingo","Sun Bingo","Gala Casino","Boylesports","Tote","QuinnBet",
    "Midlands Grand National","Betdaq","BetRegal","Campeonbet","Ivibet",
    "Wazamba","Nomini","BetNacional","N1 Bet","Joo Casino","Bitstarz",
    "mBit Casino","BetChain","FortuneJack","WildTornado","KatsuBet",
    "Playamo","Bob Casino","DasIst Casino","Oshi Casino","Betchan",
    "CasinoChan","NightRush","Slottica","GreenSpin","BetFlip",
    "Fairspin","TrustDice","Duelbits","Gamdom","Roobet","CSGOEmpire",
    "Velobet","Donbet","Megapari","BetWinner","Linebet","Rajbet",
    "ComeOn Casino","Vera&John","Casiplay","Yako Casino","PlayOJO",
    "Wishmaker","Volt Casino","DreamVegas","Slotty Vegas","GenesisCasino",
    "SpinAway","Pelaa Casino","Guts Casino","Kaboo Casino","Thrills Casino",
    "Dunder Casino","NYSpins","Hyper Casino","PlayFrank","LuckyNiki",
    "Casino Room","Speedy Casino","CasinoEuro","iGame","Redbet",
]

BONUS_TYPES = [
    ("Deneme Bonusu", "deneme"),
    ("Hosgeldin Bonusu", "hosgeldin"),
    ("Casino Bonusu", "casino"),
    ("Spor Bahis Bonusu", "spor"),
    ("Yatirim Sartsiz Deneme Bonusu", "deneme"),
]

FEATURES_POOL = [
    "Guncel Deneme Bonusu Sitesi",
    "Yatirim Sartsiz Deneme Bonusu Veren Siteler",
    "En Iyi Casino Siteleri",
    "Guvenilir Bahis Siteleri",
    "Lisansli Bahis Siteleri",
    "Canli Casino Secenekleri",
    "Hizli Odeme Yontemleri",
    "Mobil Uyumlu Bahis Sitesi",
]

LOGO_COLORS = ["FF6B6B","4ECDC4","45B7D1","96CEB4","FFEAA7","DDA0DD","98D8C8","F7DC6F","BB8FCE","85C1E9","F0B27A","82E0AA","E74C3C","3498DB","2ECC71","F39C12","9B59B6","1ABC9C"]

LICENSES = [
    "Malta Gaming Authority (MGA)",
    "UK Gambling Commission (UKGC)",
    "Curacao eGaming",
    "Gibraltar Regulatory Authority",
    "Isle of Man Gambling Supervision Commission",
    "Kahnawake Gaming Commission",
    "Swedish Gambling Authority (Spelinspektionen)",
    "Danish Gambling Authority",
    "Estonian Tax and Customs Board",
    "Alderney Gambling Control Commission",
]

PAYMENT_METHODS = [
    ("Visa/Mastercard", "50 TL", "25.000 TL", "Aninda"),
    ("Banka Havale/EFT", "50 TL", "50.000 TL", "15-30 dk"),
    ("Skrill", "30 TL", "20.000 TL", "Aninda"),
    ("Neteller", "30 TL", "20.000 TL", "Aninda"),
    ("Bitcoin", "100 TL", "100.000 TL", "10-30 dk"),
    ("Ethereum", "100 TL", "100.000 TL", "5-15 dk"),
    ("Papara", "50 TL", "30.000 TL", "5-10 dk"),
    ("ecoPayz", "30 TL", "15.000 TL", "Aninda"),
    ("MuchBetter", "20 TL", "10.000 TL", "Aninda"),
    ("Jeton", "50 TL", "20.000 TL", "5-10 dk"),
]


def generate_logo_url(name):
    color = random.choice(LOGO_COLORS)
    initial = name[0].upper()
    return f"https://ui-avatars.com/api/?name={initial}&background={color}&color=fff&size=100&bold=true&font-size=0.5"


def generate_slug(name):
    return name.lower().replace(" ", "-").replace("!", "").replace("&", "ve").replace(".", "").replace("@","")


def generate_article(name, bonus_amount, bonus_type, license_info):
    year = "2025"
    slug = generate_slug(name)
    
    meta_title = f"{name} Guncel Giris Adresi {year} | Deneme Bonusu"[:60]
    meta_description = f"{name} guncel giris adresi, {bonus_amount} TL {bonus_type} firsati. Avrupa lisansli platform incelemesi."[:155]
    
    keywords = [
        f"{name} giris", f"{name} guncel giris", f"{name} bonus",
        f"{name} deneme bonusu", f"{name} hosgeldin bonusu",
        f"{name} canli bahis", f"{name} casino", f"{name} mobil",
        f"{name} uyelik", f"{name} kayit", f"{name} para yatirma",
        f"{name} para cekme", f"{name} guvenilir mi",
        f"{name} lisans", f"{name} musteri hizmetleri",
        f"deneme bonusu veren siteler {year}", f"guncel giris adresleri {year}",
        f"avrupa bahis siteleri", f"lisansli casino siteleri",
    ]
    
    payments = random.sample(PAYMENT_METHODS, k=random.randint(4, 6))
    payment_table = "| Yontem | Min. Yatirim | Max. Yatirim | Islem Suresi |\n|--------|-------------|-------------|-------------|\n"
    for p in payments:
        payment_table += f"| {p[0]} | {p[1]} | {p[2]} | {p[3]} |\n"
    
    competitors = random.sample(NEW_EUROPE_FIRMS, k=min(3, len(NEW_EUROPE_FIRMS)))
    competitor_section = f"Avrupa pazarindaki diger platformlar ({', '.join(competitors)}) ile karsilastirildiginda {name}:"
    
    content = f"""# {name} Guncel Giris Adresi ve Detayli Platform Incelemesi {year}

## {name} Girisi - Genel Bilgiler

{name}, Avrupa pazarinda faaliyet gosteren ve {license_info} lisansi altinda hizmet veren bir online bahis ve casino platformudur. Platform, genis spor bahisleri yelpazesi, canli casino oyunlari ve cazip bonus firsatlari ile kullanicilarina kapsamli bir deneyim sunmaktadir.

{name} platformu, modern ve kullanici dostu arayuzu ile on plana cikmaktadir. Responsive tasarim sayesinde masaustu, tablet ve mobil cihazlardan sorunsuz erisim saglanmaktadir. SSL 256-bit sifreleme teknolojisi ile tum kullanici verileri ve finansal islemler guvenle korunmaktadir.

### Platform Teknik Altyapisi
- Yuksek performansli sunucu altyapisi
- 99.9% uptime garantisi
- Canli yayin destekli bahis secenekleri
- Coklu dil ve para birimi destegi
- 7/24 canli destek hizmeti

## {name} Guncel Giris Adresi

{name} platformuna erisim icin guncel giris adresinin kullanilmasi gerekmektedir. Cesitli ulkelerdeki regulasyon duzenlemeleri nedeniyle platform adresleri zaman zaman guncellenmektedir.

**{name} Guncel Giris Bilgileri:**
- Resmi web sitesi uzerinden giris yapilmasi onerilmektedir
- Giris adresi degisiklikleri resmi sosyal medya kanallarindan duyurulmaktadir
- Alternatif giris adresleri icin musteri hizmetleri ile iletisime gecilebilir

### Guvenli Giris Icin Onerilr
1. Tarayici adres cubugunda SSL kilit simgesini kontrol edin
2. Resmi kaynaklardan paylasilan linkleri kullanin
3. Sifrenizi duzenlii olarak guncelleyin
4. Iki faktorlu kimlik dogrulama (2FA) aktif edin

## Odeme Yontemleri

{name} platformu cesitli odeme yontemlerini destekleyerek kullanicilarina esneklik sunmaktadir:

{payment_table}

### Odeme Surecleri Hakkinda Bilgilendirme
- Ilk para cekme isleminde kimlik dogrulama (KYC) sureci uygulanmaktadir
- Para cekme islemleri genellikle 24-48 saat icinde tamamlanmaktadir
- Kripto para islemlerinde blockchain onay suresi ek zaman gerektirebilir
- Minimum ve maksimum limitler odeme yontemine gore degisiklik gostermektedir

## Bonuslar ve Promosyonlar

{name} platformu yeni ve mevcut kullanicilarina cesitli bonus programlari sunmaktadir:

### Hosgeldin Bonus Paketi
Yeni uyelere ozel **{bonus_amount} TL**'ye kadar hosgeldin bonusu. Bu bonus, ilk yatiriminiza ek olarak hesabiniza tanimlanan bakiyeyi kapsamaktadir.

### Deneme Bonusu
Platformu tanima amacli sunulan yatirim sartsiz deneme bonusu ile {name}'in sundugu hizmetleri risksiz olarak deneyimleyebilirsiniz.

### Haftalik Promosyonlar
- Kayip bonusu programi
- Reload bonus firsatlari
- Ozel etkinlik promosyonlari
- VIP sadakat programi

### Bonus Kullanim Kosullari
Bonus kullaniminda cevrim sartlari ve zaman limitleri uygulanmaktadir. Detayli bilgi icin platformun bonus kosullari sayfasinin incelenmesi onerilir.

## {year} Guncel Deneme Bonusu Analizi

{name} platformunun {year} donemindeki bonus politikasini analitik bir perspektiften degerlendirdigimizde sektordeki konumlandirmasi incelenebilir.

### Lisans ve Guvenilirlik Degerlendirmesi

{name}, **{license_info}** lisansi altinda faaliyet gostermektedir. Bu lisans:
- Duzenli denetim ve raporlama yukumlulugu gerektirir
- Kullanici fonlarinin ayri hesaplarda tutulmasini zorunlu kilar
- Sorumlu oyun politikalarinin uygulanmasini saglar
- Sikayet cozum mekanizmasi sunar

### Rakip Karsilastirma Analizi

{competitor_section}
- Bonus miktari acisindan sektorde rekabetci bir pozisyonda yer almaktadir
- Odeme yontemi cesitliligi bakimindan ortalamanin uzerindedir
- Musteri hizmetleri erisilebiiligi acisindan olumlu degerlendirmeler almaktadir
- Mobil platform performansi sektordeki standartlari karsilamaktadir

### Sonuc ve Degerlendirme

{name} platformu, Avrupa regulasyonlarina uygun sekilde faaliyet gosteren ve kullanicilarina kapsamli hizmet sunan bir platformdur. Bonus programlari, odeme yontemi cesitliligi ve teknik altyapi acisindan sektorde rekabetci bir konumdadir.

Kullanicilarin platform seciminde lisans durumu, bonus kosullari ve odeme sureclerini dikkatle degerlendirmesi onerilir. Bahis ve sans oyunlarinin eglence amacli oldugu, sorumlu oyun ilkelerine uygun hareket edilmesi gerektigi unutulmamalidir.

**Onemli Uyari:** Bahis ve sans oyunlari 18 yas alti icin yasaktir. Kumar bagimliligi yardim hatti: 182.

---
*Bu icerik bilgilendirme amaciyla hazirlanmis olup yatirim tavsiyesi niteligi tasimamaktadir. {year} verileri referans alinmistir.*
"""
    
    return {
        "title": f"{name} Guncel Giris Adresi ve Detayli Inceleme {year}",
        "slug": f"{slug}-guncel-giris-inceleme-{year}",
        "content": content,
        "excerpt": f"{name} Avrupa lisansli platform incelemesi. {bonus_amount} TL {bonus_type}, guncel giris adresi ve detayli analiz.",
        "meta_title": meta_title,
        "meta_description": meta_description,
        "keywords": keywords,
        "category": "en-iyi-firmalar",
        "author": "Uzman Editor",
        "is_published": True,
        "is_auto_generated": True,
        "seo_score": random.randint(84, 97),
    }


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    existing = await db.bonus_sites.find({}, {"_id": 0, "name": 1}).to_list(1000)
    existing_names = {s["name"].lower() for s in existing}
    
    existing_articles = await db.articles.find({}, {"_id": 0, "slug": 1}).to_list(5000)
    existing_slugs = {a["slug"] for a in existing_articles}
    
    max_sort = await db.bonus_sites.count_documents({})
    
    stats = {"added": 0, "skipped": 0, "articles": 0}
    
    # Content queue topics
    queue_topics = []
    
    for i, name in enumerate(NEW_EUROPE_FIRMS):
        if name.lower() in existing_names:
            print(f"  SKIP (duplicate): {name}")
            stats["skipped"] += 1
            continue
        
        now = datetime.now(timezone.utc)
        bonus_type_display, bonus_type_code = random.choice(BONUS_TYPES)
        bonus_value = random.randint(5, 25) * 100
        bonus_amount = f"{bonus_value} TL"
        features = random.sample(FEATURES_POOL, k=random.randint(3, 5))
        rating = round(random.uniform(4.0, 4.9), 1)
        license_info = random.choice(LICENSES)
        
        site_id = str(uuid.uuid4())
        
        site = {
            "id": site_id,
            "name": name,
            "logo_url": generate_logo_url(name),
            "bonus_type": bonus_type_code,
            "bonus_amount": bonus_amount,
            "bonus_value": bonus_value,
            "affiliate_url": "https://xlinks.art/girisai",
            "rating": rating,
            "features": features,
            "turnover_requirement": round(random.uniform(5.0, 15.0), 1),
            "global_cta_clicks": 0,
            "global_affiliate_clicks": 0,
            "global_impressions": 0,
            "is_active": True,
            "is_global": True,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "sort_order": max_sort + i + 1,
            "category": "Avrupa",
            "version": "1.0",
            "seo_status": "new",
            "content_hash": hashlib.md5(f"{name}-europe-v1.0".encode()).hexdigest(),
        }
        
        await db.bonus_sites.insert_one(site)
        existing_names.add(name.lower())
        
        # Generate article
        article_data = generate_article(name, bonus_amount, bonus_type_display, license_info)
        if article_data["slug"] not in existing_slugs:
            article = {
                "id": str(uuid.uuid4()),
                "domain_id": "global",
                **article_data,
                "views": 0,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
            }
            await db.articles.insert_one(article)
            existing_slugs.add(article_data["slug"])
            stats["articles"] += 1
        
        # Queue topics
        queue_topics.append(f"{name}|{name} Guncel Adresi Degisti mi? {name} Yeni Giris Adresi 2025")
        queue_topics.append(f"{name}|{name} Telegram Kanali ve Sosyal Medya Hesaplari 2025")
        queue_topics.append(f"{name}|{name} Twitter Resmi Hesabi ve Guncel Paylasimlar")
        queue_topics.append(f"{name}|{name} Guncel Sikayet ve Kullanici Yorumlari 2025")
        
        stats["added"] += 1
        print(f"  [{stats['added']:3d}] Firma: {name:25s} | Europe | Yeni | v1.0 | Bonus: {bonus_amount}")
    
    # Add queue topics
    queue_added = 0
    for topic_line in queue_topics:
        parts = topic_line.split("|", 1)
        comp = parts[0].strip()
        topic = parts[1].strip()
        existing_q = await db.content_queue.find_one({"company": comp, "topic": topic, "status": {"$in": ["pending", "processing"]}})
        if not existing_q:
            from pydantic import BaseModel
            item_id = str(uuid.uuid4())
            await db.content_queue.insert_one({
                "id": item_id,
                "company": comp,
                "topic": topic,
                "status": "pending",
                "article_id": None,
                "error": None,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "completed_at": None,
            })
            queue_added += 1
    
    # Copy to existing domains
    domains = await db.domains.find({}, {"_id": 0, "id": 1}).to_list(100)
    for domain in domains:
        new_sites = await db.bonus_sites.find({"is_global": True, "is_active": True}, {"_id": 0, "id": 1}).to_list(500)
        existing_ds = await db.domain_sites.find({"domain_id": domain["id"]}, {"_id": 0, "site_id": 1}).to_list(500)
        existing_sids = {ds["site_id"] for ds in existing_ds}
        for site in new_sites:
            if site["id"] not in existing_sids:
                await db.domain_sites.insert_one({
                    "id": str(uuid.uuid4()),
                    "domain_id": domain["id"],
                    "site_id": site["id"],
                    "is_active": True,
                    "custom_sort_order": None,
                })
    
    # Update stats
    total = await db.bonus_sites.count_documents({})
    eu_count = await db.bonus_sites.count_documents({"category": "Avrupa"})
    tr_count = await db.bonus_sites.count_documents({"category": "Turkiye"})
    
    await db.firm_stats.update_one(
        {"type": "global"},
        {"$set": {
            "total_firm_count": total,
            "turkey_firm_count": tr_count,
            "europe_firm_count": eu_count,
            "last_added_firm": NEW_EUROPE_FIRMS[-1],
            "last_update_timestamp": datetime.now(timezone.utc).isoformat(),
        }},
        upsert=True
    )
    
    print(f"\n{'='*60}")
    print(f"ADMIN RAPOR - AVRUPA FIRMA EKLEME")
    print(f"{'='*60}")
    print(f"Eklenen firma:       {stats['added']}")
    print(f"Atlanan (duplike):   {stats['skipped']}")
    print(f"Uretilen makale:     {stats['articles']}")
    print(f"Kuyruga eklenen:     {queue_added} konu")
    print(f"{'='*60}")
    print(f"Toplam EU firma:     {eu_count}")
    print(f"Toplam TR firma:     {tr_count}")
    print(f"Toplam firma:        {total}")
    print(f"{'='*60}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
