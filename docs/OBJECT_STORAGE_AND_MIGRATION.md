# Emergent Object Storage + Video/Wallpaper Migration

## Mimari özet

- **Dosyalar:** Emergent Object Storage (cloud) — URL: `https://integrations.emergentagent.com/objstore/api/v1/storage`
- **Metadata:** MongoDB — `video_library` ve `wallpaper_library` koleksiyonları (path, title, company_slug vb.)
- **Auth:** `EMERGENT_LLM_KEY` → `/init` ile `storage_key` alınır; dosya isteklerinde `X-Storage-Key` header kullanılır.

### Path formatları

| Koleksiyon         | Storage path formatı                          |
|--------------------|------------------------------------------------|
| video_library      | `guncelgiris/videos/{uuid}.mp4` (veya .webm)  |
| wallpaper_library | `guncelgiris/wallpapers/{seo-filename}.png`   |

Kod: `backend/agents/video_library.py`, `backend/agents/wallpaper_library.py`.

---

## 1. MongoDB Atlas’a migration (video_library, wallpaper_library)

Metadata’yı (video/wallpaper kayıtları) production Atlas’a taşımak için:

1. **Kaynak:** Verilerin bulunduğu MongoDB (örn. local: `mongodb://localhost:27017`, DB: `test_database`).
2. **Hedef:** Atlas (prod) — `.env` veya script içindeki `MONGO_URL`, `DB_NAME`.

### İki yöntem

**A) JSON dosyalarından:**  
`backend/` içine `migration_videos.json`, `migration_wallpapers.json` vb. koyup script’i çalıştır. Bu dosyaları Emergent veya başka bir yerden export edebilirsin.

**B) Başka bir MongoDB’den (JSON yoksa):**  
Videoların/wallpaper’ların bulunduğu MongoDB’nin connection string’ini ver. Script o DB’den okuyup Atlas’a yazar.

`.env` içine ekle:
- `SOURCE_MONGO_URL` = Kaynak MongoDB connection string (örn. Emergent’ın kullandığı Atlas veya local `mongodb://localhost:27017`)
- `SOURCE_DB_NAME` = Kaynak veritabanı adı (yoksa `DB_NAME` kullanılır)

Sonra:
```bash
cd backend
# Hedef: MONGO_URL, DB_NAME (Atlas)
python migrate_to_atlas.py
```

Script önce JSON dosyalarına bakar; yoksa ve `SOURCE_MONGO_URL` tanımlıysa kaynak DB’den **video_library**, **wallpaper_library**, short_links, programmatic_pages, company_articles, agent_jobs koleksiyonlarını Atlas’a upsert eder.

### Not

- Sadece **metadata** (koleksiyon dökümanları) kopyalanır; gerçek video/wallpaper dosyaları Emergent Object Storage’da kalır.
- Her dökümandaki `storage_path` alanı yukarıdaki path formatına uygun olmalı; backend bu path ile storage’dan dosyayı çeker.

---

## 2. Prod’da dosyalara erişim (Railway / herhangi bir host)

Dosyalar hâlâ Emergent Object Storage’da; backend sadece metadata için MongoDB, dosya içeriği için Object Storage API kullanır.

### Backend’de gerekli env (zaten kullanılıyor)

| Değişken           | Açıklama |
|--------------------|----------|
| `MONGO_URL`        | Atlas connection string (video_library, wallpaper_library bu DB’de) |
| `DB_NAME`          | Veritabanı adı (örn. `guncelgiris_db`) |
| `EMERGENT_LLM_KEY` | Object Storage init + dosya indirme için gerekli |

### Akış

1. Uygulama açılışında veya ilk dosya isteğinde: `POST {STORAGE_URL}/init` + `emergent_key: EMERGENT_LLM_KEY` → `storage_key` alınır.
2. Video/wallpaper isteği: MongoDB’den `storage_path` okunur → `GET {STORAGE_URL}/objects/{storage_path}` + header `X-Storage-Key: {storage_key}` ile dosya indirilir ve kullanıcıya stream/response edilir.

Railway’de bu üç env doğru tanımlıysa prod’da videolar ve wallpapers çalışır. Ek bir “prod erişim” konfigürasyonu gerekmez.

---

## 3. Railway’de deploy sonrası videoların görünmesi — Senin yapacakların

Deploy aldıktan sonra sitede videoların listelenmesi ve oynatılması için sırayla şunları yap:

### Adım 1: Atlas’ta video metadata’sı olsun

Videoların **listesi** MongoDB’deki `video_library` koleksiyonundan gelir. Railway backend’in bağlandığı **Atlas** veritabanında bu koleksiyon olmalı ve içinde kayıt bulunmalı.

- **Videoları nerede oluşturdun?** (Local’de mi, başka bir DB’de mi?)
  - Local MongoDB’deyse: Önce bu veriyi Atlas’a taşı. `backend` klasöründe `.env` içinde `MONGO_URL` = Atlas connection string ve `DB_NAME` = hedef DB adı olsun, sonra:
    ```bash
    cd backend
    python migrate_to_atlas.py
    ```
  - Zaten Atlas’ta (başka bir proje/DB’de) kayıt varsa: Railway’deki `MONGO_URL` ve `DB_NAME` bu Atlas + DB’yi göstermeli.
- **Hiç video kaydı yoksa:** Önce admin panelinden veya API ile video yüklemen / kaydetmen gerekir; kayıtlar Atlas’taki `video_library`’e yazılacak.

### Adım 2: Railway Backend Variables

Railway → Backend servisi → **Variables** sekmesinde şunlar **mutlaka** tanımlı olsun:

| Değişken           | Ne işe yarıyor |
|--------------------|----------------|
| `MONGO_URL`        | Atlas connection string (içinde `video_library` olan DB) |
| `DB_NAME`          | Bu DB’nin adı (örn. `guncelgiris_db`) |
| `EMERGENT_LLM_KEY` | Emergent Object Storage’a erişim; olmazsa video dosyası çekilemez |

Değişken ekleyip kaydettikten sonra Railway yeni bir deploy alır; deploy’un bitmesini bekle.

### Adım 3: Frontend’in backend’e istek atması

Sitede `/videolar` sayfası backend’in `/api/videos` (ve oynatma için `/api/videos/{id}/file`) endpoint’lerini çağırır.

- **Frontend’i Railway’de ayrı bir servis olarak deploy ediyorsan:**  
  Frontend servisinin **Variables** kısmına ekle:  
  `REACT_APP_BACKEND_URL` = Backend’in gerçek adresi  
  (örn. `https://guncelgirisai-v2-backend.up.railway.app`).  
  Build’i bu değişkenle yeniden al (deploy).
- **Frontend ve backend aynı domain’de / tek serviste** çalışıyorsa (veya reverse proxy ile `/api` backend’e gidiyorsa):  
  `REACT_APP_BACKEND_URL` koyma; uygulama göreli `/api` kullanır, ekstra ayar gerekmez.

### Adım 4: Kontrol

- Tarayıcıda canlı siteni aç → `/videolar` sayfasına git. Liste boşsa: Atlas’ta `video_library` koleksiyonunda döküman var mı, Railway’de `MONGO_URL` / `DB_NAME` doğru mu kontrol et.
- Bir videoya tıkla, oynatılıyorsa: Backend Object Storage’a `EMERGENT_LLM_KEY` ile erişiyor demektir.
- Liste var ama oynatma 404/500 ise: `EMERGENT_LLM_KEY` Railway’de tanımlı mı, deploy sonrası değişken kaydedilmiş mi kontrol et.

---

## 4. Özet

- **Migration:** `migrate_to_atlas.py` ile `video_library` ve `wallpaper_library` Atlas’a kopyalanır (kaynak: local veya SOURCE_* env).
- **Prod erişim:** Atlas’ta metadata + Railway’de `EMERGENT_LLM_KEY` + mevcut agent kodu yeterli; dosyalar Object Storage’dan bu key ile çekilir.
- **Railway’de videolar için:** (1) Atlas’ta `video_library` dolu, (2) Backend’de `MONGO_URL`, `DB_NAME`, `EMERGENT_LLM_KEY` tanımlı, (3) Frontend doğru backend URL’ine istek atıyor.
