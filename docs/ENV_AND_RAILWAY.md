# Ortam Değişkenleri ve Railway Deploy

## Local'de çalıştırmak için yapman gerekenler

### 1. MongoDB

- Backend `MONGO_URL` ile bağlanıyor. Şu an `.env` içinde `mongodb://localhost:27017` var.
- **Seçenek A:** Bilgisayarında MongoDB kurulu ve çalışıyorsa (servis açık) bir şey yapma.
- **Seçenek B:** MongoDB yoksa:
  - [MongoDB Community](https://www.mongodb.com/try/download/community) kur veya
  - Docker: `docker run -d -p 27017:27017 mongo` veya
  - [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) ücretsiz cluster açıp `MONGO_URL` ve `DB_NAME` değerlerini `.env` içinde güncelle.

### 2. Backend (`backend/`)

- **emergentintegrations:** Özel index’ten kurulmalı (requirements.txt’te olsa bile ilk kurulumda):
  ```bash
  pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
  ```
  Tüm bağımlılıklar için: `cd backend` sonra `pip install -r requirements.txt` (aynı `--extra-index-url` gerekebilir; requirements.txt’in ilk satırında tanımlı).

- **Zorunlu:** `backend/.env` içinde mutlaka olmalı:
  - `MONGO_URL` — örn. `mongodb://localhost:27017` veya Atlas connection string
  - `DB_NAME` — örn. `test_database`
- Backend `.env` dosyasını **proje kökünden değil**, `backend` klasöründen yükler (`load_dotenv(ROOT_DIR / '.env')`).
- Başlatma (backend klasöründen):
  ```bash
  cd backend
  uvicorn server:app --reload --port 8001
  ```
- Port **8001** kullanılıyor; frontend buna göre ayarlı.

### 3. Frontend (`frontend/`)

- `frontend/.env` içinde:
  - **REACT_APP_BACKEND_URL=http://localhost:8001** — Backend 8001’de çalıştığı için bu olmalı. (8000 yazıyorsa API istekleri yanlış porta gider.)
  - `ENABLE_HEALTH_CHECK` — istersen `false` bırak.
- Başlatma:
  ```bash
  cd frontend
  yarn install   # veya npm install (ilk seferde)
  yarn start     # veya npm start
  ```
- Uygulama `http://localhost:3000` (veya CRA’nın verdiği port) üzerinde açılır; API istekleri `http://localhost:8001/api` adresine gider.

### 4. Sıra

1. MongoDB’nin çalıştığından emin ol.
2. Backend’i 8001 portunda başlat.
3. Frontend’i başlat; tarayıcıda siteyi aç.

### 5. .env özeti (local)

| Dosya | Değişken | Local için |
|-------|----------|------------|
| `backend/.env` | `MONGO_URL` | Zorunlu. `mongodb://localhost:27017` veya Atlas URL |
| `backend/.env` | `DB_NAME` | Zorunlu. Örn. `test_database` |
| `backend/.env` | `EMERGENT_LLM_KEY` | Videolar (Object Storage) için. Yoksa video listesi/stream kapalı |
| `backend/.env` | Diğerleri | Opsiyonel (admin, Telegram, SERP vb. istersen doldur) |
| `frontend/.env` | `REACT_APP_BACKEND_URL` | `http://localhost:8001` (backend ile aynı port) |
| `frontend/.env` | `ENABLE_HEALTH_CHECK` | İstersen `false` |

### 6. Local’de videoların görünmesi

- `MONGO_URL=mongodb://localhost:27017` kullanıyorsan: **video_library** koleksiyonu local MongoDB’de olmalı (şu an boşsa videolar listelenmez). İstersen production’dan dump alıp local’e import edebilirsin.
- Aynı videoları local’de de görmek istiyorsan: `MONGO_URL`’i geçici olarak **production MongoDB connection string** (Atlas) yap; böylece local uygulama da aynı veriyi kullanır. `EMERGENT_LLM_KEY` local’de tanımlı olsun.

---

## Kısa özet: Local çalıştırma

1. **Backend:** `backend` klasöründe `.env` oluştur (`.env.example` kopyala). En az:
   - `MONGO_URL` — MongoDB bağlantı adresi
   - `DB_NAME` — veritabanı adı

2. **Backend port:** 8001. Başlat: `cd backend && uvicorn server:app --reload --port 8001`

3. **Frontend:** `frontend/.env` içinde `REACT_APP_BACKEND_URL=http://localhost:8001`. Sonra `cd frontend && yarn start`. API istekleri 8001’e gider.

---

## Railway Production

### Backend servisi – Videoların sitede görünmesi için

Railway’de backend servisine **Variables** kısmından şunları ekle:

| Değişken | Zorunlu | Değer (Railway) |
|----------|--------|------------------|
| `MONGO_URL` | Evet | **Production** MongoDB connection string (Atlas; video_library burada) |
| `DB_NAME` | Evet | Aynı veritabanı adı (örn. `test_database` veya prod’daki ad) |
| `EMERGENT_LLM_KEY` | Videolar için | Local’de kullandığın aynı Emergent key |
| `FRONTEND_BASE_URL` | Önerilen | `https://www.guncelgiris.ai` (sitemap, canonical) |
| `CORS_ORIGINS` | Önerilen | `https://www.guncelgiris.ai` (veya frontend domain’in) |
| `JWT_SECRET` | Önerilen | Güçlü rastgele string |
| `ADMIN_PASSWORD_HASH` | Önerilen | bcrypt hash (admin girişi) |

Videoların listelenmesi ve oynatılması için **MONGO_URL** (video metadata’nın olduğu DB) ve **EMERGENT_LLM_KEY** (Object Storage erişimi) mutlaka tanımlı olmalı.

### Tüm backend env’ler (özet)

| Değişken | Açıklama |
|----------|----------|
| `MONGO_URL` | Production MongoDB (Atlas) connection string |
| `DB_NAME` | Veritabanı adı |
| `FRONTEND_BASE_URL` | Sitenin canlı adresi |
| `CORS_ORIGINS` | Frontend domain |
| `JWT_SECRET` | Admin oturumu |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD_HASH` | Admin girişi |
| `EMERGENT_LLM_KEY` | Video/wallpaper + Object Storage |
| `TELEGRAM_*` | İstersen Telegram botları |

### Frontend servisi (ayrı deploy ise)

API backend’i **farklı bir URL’de** çalışıyorsa (örn. `https://api.guncelgiris.ai`):

- Railway’de frontend servisine env ekle: **`REACT_APP_BACKEND_URL=https://api.guncelgiris.ai`**
- Build’de bu değer kullanılır; tüm `/api` istekleri bu adrese gider.

Frontend ve backend **aynı domain** altında (tek servis veya reverse proxy ile `/api` backend’e yönleniyorsa) `REACT_APP_BACKEND_URL` **koyma**; uygulama göreli `/api` kullanır.

---

## Hangi API key’ler ne işe yarıyor?

- **EMERGENT_LLM_KEY:** Video kütüphanesi, wallpaper üretimi, object storage. Yoksa bu özellikler devre dışı kalır; site çalışır.
- **Telegram (API_ID, API_HASH, WEBHOOK_BASE):** Admin panelinden Telegram bot oluşturma. Yoksa sadece bot özelliği kapalı.
- **SERP (AHREFS, SEMRUSH, DATAFORSEO):** SEO agent’ları. Yoksa SERP verisi kullanılmaz; diğer özellikler çalışır.
- **JWT_SECRET + ADMIN_PASSWORD_HASH:** Admin girişi. Production’da mutlaka güçlü değerler ver.

API key vb. eklemek istersen `.env` (local) veya Railway env ekranından ekleyip yeniden deploy etmen yeterli.
