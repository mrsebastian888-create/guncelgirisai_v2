"""
Bulk firm import script - 100 firms (50 Turkey + 50 Europe)
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

TURKEY_FIRMS = [
    "1xBet","Bets10","Mobilbahis","Tipobet","Meritking","Meritbet",
    "Grandpashabet","Pashagaming","Maxwin","Casibom","Jojobet","Marsbahis",
    "Vaycasino","Onwin","Holiganbet","Betwoon","Matbet","Kingbahis",
    "Pusulabet","Rexbet","Bahigo","Youwin","Superbahis","Jetbahis",
    "Sahabet","Betpublic","Betoffice","Restbet","Tarafbet","Betturkey",
    "Exonbet","Diorbet","Royalbet","Gelcasino","Vadicasino","Bycasino",
    "Onbet","Enbet","Favoribahis","Hizlibahis","Betpioner","Superbetin",
    "Betebet","Betewin","Mariobet","Galabet","Betyap","Palazzobet",
    "Fixbet","Supertotobet"
]

EUROPE_FIRMS = [
    "bet365","Paddy Power","Betfair","William Hill","Ladbrokes","Coral",
    "Betfred","888sport","888casino","Unibet","LeoVegas","Betsson",
    "Mr Green","Casumo","ComeOn!","Videoslots","Rizk","PokerStars",
    "Betway","NetBet","BetVictor","GGPoker","Winamax","Betclic",
    "PMU","Sisal","Eurobet","Snai","Lottomatica","Betano",
    "Stoiximan","Novibet","Interwetten","Tipico","bwin","bet-at-home",
    "Pinnacle","Superbet","Fortuna","STS","Coolbet","Paf",
    "Svenska Spel","Veikkaus","Holland Casino Online","TOTO.nl",
    "BetCity.nl","Napoleon Sports & Casino","Codere","Sportium"
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

LOGO_COLORS = ["FF6B6B","4ECDC4","45B7D1","96CEB4","FFEAA7","DDA0DD","98D8C8","F7DC6F","BB8FCE","85C1E9","F0B27A","82E0AA"]


def generate_logo_url(name):
    """Generate a placeholder logo URL"""
    color = random.choice(LOGO_COLORS)
    initial = name[0].upper()
    return f"https://ui-avatars.com/api/?name={initial}&background={color}&color=000&size=100&bold=true&font-size=0.5"


def generate_content_hash(name, category):
    return hashlib.md5(f"{name}-{category}-v1.0".encode()).hexdigest()


def generate_slug(name):
    slug = name.lower().replace(" ", "-").replace("!", "").replace("&", "ve").replace(".", "")
    return slug


def generate_article(name, category, bonus_amount, bonus_type):
    """Generate SEO-optimized article for a firm"""
    cat_label = "Turkiye" if category == "turkey" else "Avrupa"
    year = "2025"
    slug = generate_slug(name)
    
    meta_title = f"{name} Guncel Giris Adresi {year} | Deneme Bonusu"[:60]
    meta_description = f"{name} guncel giris adresi, {bonus_amount} TL {bonus_type} firsati. Guvenilir bahis sitesi incelemesi ve bonus detaylari."[:155]
    
    keywords = [
        f"{name} giris", f"{name} guncel giris", f"{name} bonus",
        f"{name} deneme bonusu", f"{name} hosgeldin bonusu",
        f"{name} canli bahis", f"{name} casino", f"{name} mobil",
        f"{name} uyelik", f"{name} kayit", f"{name} para yatirma",
        f"{name} para cekme", f"{name} guvenilir mi",
        f"{name} lisans", f"{name} musteri hizmetleri",
        f"deneme bonusu veren siteler", f"guncel giris adresleri",
        f"guvenilir bahis siteleri {year}"
    ]
    
    content = f"""# {name} Guncel Giris Adresi ve Bonus Detaylari {year}

## {name} Girisi - Genel Bilgiler

{name}, {cat_label} pazarinda faaliyet gosteren kokenli bir bahis ve casino platformudur. Kullanicilarina genis bir spor bahisleri yelpazesi, canli casino oyunlari ve cekim banka bonus firsatlari sunmaktadir. Platform, kullanici dostu arayuzu ve guclu altyapisiyla dikkat cekmektedir.

{name} platformu, mobil uyumlu tasarimi sayesinde akilli telefon ve tabletlerden de sorunsuz erisim imkani sunmaktadir. SSL sertifikasi ile kullanici verileri guvenle korunmakta ve finansal islemler sifrelenmektedir.

### Temel Ozellikler
- Genis spor bahisleri secenekleri
- Canli casino ve slot oyunlari
- 7/24 musteri hizmetleri
- Mobil uyumlu platform
- Hizli para yatirma ve cekme

## {name} Guncel Giris Adresi

{name} platformuna erisim icin guncel giris adresini kullanmaniz gerekmektedir. BTK tarafindan uygulanan erisim engellemeleri nedeniyle site adresleri periyodik olarak degismektedir.

**Guncel Giris:** {name} resmi web sitesine guvenli erisim icin guncel adresi kullaniniz.

Giris adresinin degismesi durumunda:
- Resmi sosyal medya hesaplarini takip edin
- Guncel giris sayfamizi duzenli kontrol edin
- Musteri hizmetleri ile iletisime gecin

## Odeme Yontemleri

{name} platformu cesitli odeme yontemlerini desteklemektedir:

| Yontem | Min. Yatirim | Max. Yatirim | Islem Suresi |
|--------|-------------|-------------|-------------|
| Banka Havale/EFT | 50 TL | 50.000 TL | 15-30 dk |
| Kripto Para | 100 TL | 100.000 TL | 5-15 dk |
| Papara | 50 TL | 30.000 TL | 5-10 dk |
| Kredi Karti | 50 TL | 25.000 TL | Aninda |

Para cekme islemleri genellikle 24 saat icinde tamamlanmaktadir. Ilk cekim isleminde kimlik dogrulama sureci uygulanabilir.

## Bonuslar ve Promosyonlar

{name} platformu yeni ve mevcut kullanicilarina cesitli bonus firsatlari sunmaktadir:

### Hosgeldin Bonusu
Yeni uyelere ozel **{bonus_amount} TL**'ye kadar hosgeldin bonusu. Bu bonus ilk yatiriminiza ek olarak hesabiniza tanimlanan ekstra bakiyeyi kapsamaktadir.

### Deneme Bonusu
Yatirim sartsiz deneme bonusu ile platformu risksiz deneyimleme firsati. {name} deneme bonusu ile casino ve spor bahislerini ucretsiz kesfedebilirsiniz.

### Kayip Bonusu
Haftalik kayiplariniza karsilik ozel kayip bonusu firsati. Belirli dontmlerde kayiplarinizin belirli bir yuzdesi hesabiniza iade edilmektedir.

### Cekim Sartsiz Bonus
Ozel donetclerde sunulan cekim sartsiz bonuslar ile kazancinizi dogrudan cekebilirsiniz.

## {year} Guncel Deneme Bonusu Analizi

{name} platformunun {year} yilindaki deneme bonusu politikasini analiz ettigimizde sektordeki konumlandirmasi dikkat cekmektedir.

### Rekabet Analizi
{cat_label} pazarindaki diger platformlarla karsilastirildiginda {name}:
- Bonus miktari acisindan sektordeki ortalammanin uzerinde yer almaktadir
- Cevrim sartlari makul seviyelerde tutulmaktadir
- Bonus kullanim suresi yeterli esneklikte sunulmaktadir

### Lisans ve Guvenilirlik
{name} platformu uluslararasi lisans altinda faaliyet gostermektedir. Kullanici verileri SSL sifreleme ile korunmakta, finansal islemler guvenli odeme altyapilari uzerinden gerceklestirilmektedir.

### Degerlendirme
{name} platformu, sundugun bonus cesitliligi, odeme yontemleri ve kullanici deneyimi acisindan {cat_label} pazarinda rekabetci bir konumdadir. Ancak kullanicilarin bonus sartlarini dikkatlice incelemesi ve sorumlu oyun ilkelerine uygun hareket etmesi onerilir.

**Onemli Not:** Bahis ve sans oyunlari 18 yas alti icin yasaktir. Kumar bagimliligi yardim hatti: 182.

---
*Bu icerik bilgilendirme amaciyla hazirlanmistir. Yatirim tavsiyesi degildir.*
"""
    
    return {
        "title": f"{name} Guncel Giris Adresi ve Bonus Detaylari {year}",
        "slug": f"{slug}-guncel-giris-bonus-{year}",
        "content": content,
        "excerpt": f"{name} guncel giris adresi, {bonus_amount} TL {bonus_type} firsati ve detayli platform incelemesi.",
        "meta_title": meta_title,
        "meta_description": meta_description,
        "keywords": keywords,
        "category": "en-iyi-firmalar",
        "author": "Uzman Editor",
        "is_published": True,
        "is_auto_generated": True,
        "seo_score": random.randint(82, 96),
    }


async def main():
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Get existing site names
    existing = await db.bonus_sites.find({}, {"_id": 0, "name": 1}).to_list(1000)
    existing_names = {s["name"].lower() for s in existing}
    
    # Get existing article slugs
    existing_articles = await db.articles.find({}, {"_id": 0, "slug": 1}).to_list(5000)
    existing_slugs = {a["slug"] for a in existing_articles}
    
    # Get current sort order
    max_sort = await db.bonus_sites.count_documents({})
    
    stats = {"added": 0, "skipped": 0, "articles": 0, "turkey": 0, "europe": 0}
    reports = []
    
    all_firms = [(name, "turkey") for name in TURKEY_FIRMS] + [(name, "europe") for name in EUROPE_FIRMS]
    
    for i, (name, category) in enumerate(all_firms):
        # Duplicate check
        if name.lower() in existing_names:
            print(f"  SKIP (duplicate): {name}")
            stats["skipped"] += 1
            continue
        
        now = datetime.now(timezone.utc)
        bonus_type_display, bonus_type_code = random.choice(BONUS_TYPES)
        bonus_value = random.randint(5, 25) * 100  # 500-2500
        bonus_amount = f"{bonus_value} TL"
        features = random.sample(FEATURES_POOL, k=random.randint(3, 5))
        rating = round(random.uniform(4.0, 4.9), 1)
        
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
            "category": "Turkiye" if category == "turkey" else "Avrupa",
            "version": "1.0",
            "seo_status": "new",
            "content_hash": generate_content_hash(name, category),
        }
        
        await db.bonus_sites.insert_one(site)
        existing_names.add(name.lower())
        
        # Generate article
        article_data = generate_article(name, category, bonus_amount, bonus_type_display)
        if article_data["slug"] not in existing_slugs:
            article_id = str(uuid.uuid4())
            article = {
                "id": article_id,
                "domain_id": "global",
                **article_data,
                "views": 0,
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
            }
            await db.articles.insert_one(article)
            existing_slugs.add(article_data["slug"])
            stats["articles"] += 1
        
        stats["added"] += 1
        if category == "turkey":
            stats["turkey"] += 1
        else:
            stats["europe"] += 1
        
        cat_label = "Turkiye" if category == "turkey" else "Avrupa"
        total = stats["added"]
        print(f"  [{total:3d}] {name:30s} | {cat_label:8s} | {bonus_amount:8s} | {bonus_type_display}")
        
        reports.append({
            "firma": name,
            "kategori": cat_label,
            "bonus": bonus_amount,
            "durum": "Yeni Eklendi",
            "versiyon": "1.0",
            "affiliate": "https://xlinks.art/girisai",
        })
    
    # Update counters
    total_firms = await db.bonus_sites.count_documents({})
    turkey_count = await db.bonus_sites.count_documents({"category": "Turkiye"})
    europe_count = await db.bonus_sites.count_documents({"category": "Avrupa"})
    
    await db.firm_stats.update_one(
        {"type": "global"},
        {"$set": {
            "total_firm_count": total_firms,
            "turkey_firm_count": turkey_count,
            "europe_firm_count": europe_count,
            "last_added_firm": all_firms[-1][0] if all_firms else "",
            "last_update_timestamp": datetime.now(timezone.utc).isoformat(),
        }},
        upsert=True
    )
    
    # Copy new sites to existing domains
    domains = await db.domains.find({}, {"_id": 0, "id": 1}).to_list(100)
    for domain in domains:
        new_sites = await db.bonus_sites.find({"is_global": True, "is_active": True}, {"_id": 0, "id": 1}).to_list(500)
        existing_domain_sites = await db.domain_sites.find({"domain_id": domain["id"]}, {"_id": 0, "site_id": 1}).to_list(500)
        existing_site_ids = {ds["site_id"] for ds in existing_domain_sites}
        for site in new_sites:
            if site["id"] not in existing_site_ids:
                await db.domain_sites.insert_one({
                    "id": str(uuid.uuid4()),
                    "domain_id": domain["id"],
                    "site_id": site["id"],
                    "is_active": True,
                    "custom_sort_order": None,
                })
    
    print(f"\n{'='*60}")
    print(f"SONUC RAPORU")
    print(f"{'='*60}")
    print(f"Eklenen firma:     {stats['added']}")
    print(f"Atlanan (duplike):  {stats['skipped']}")
    print(f"Uretilen makale:   {stats['articles']}")
    print(f"Turkiye firmalari: {stats['turkey']}")
    print(f"Avrupa firmalari:  {stats['europe']}")
    print(f"Toplam firma:      {total_firms}")
    print(f"{'='*60}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
