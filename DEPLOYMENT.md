# Production Deployment Rehberi

## Genel Bakis
```
[Kullanicilar] --> [Vercel (Frontend)] --> [Railway (Backend API)] --> [MongoDB Atlas (DB)]
                                     |
[adminguncelgiris.company] ------>  [Vercel]
[guncelgiris.ai] ---------------->  [Vercel]
[diger-domainler.com] ---------->  [Vercel]
```

---

## ADIM 1: MongoDB Atlas (Veritabani)

### 1.1 Hesap Olusturma
1. https://www.mongodb.com/cloud/atlas adresine gidin
2. Ucretsiz hesap olusturun (Google ile giris yapabilirsiniz)

### 1.2 Cluster Olusturma
1. "Build a Database" tiklayin
2. **M0 Free Tier** secin (ucretsiz, 512MB)
3. Cloud Provider: **AWS** secin
4. Region: **Frankfurt (eu-central-1)** secin (Turkiye'ye yakin)
5. Cluster Name: `dsbn-production` yazin
6. "Create Cluster" tiklayin

### 1.3 Erisim Ayarlari
1. **Database Access** sekmesine gidin
2. "Add New Database User" tiklayin
   - Username: `dsbn_admin`
   - Password: Guclu bir sifre belirleyin (not edin!)
   - Role: "Atlas Admin"
3. **Network Access** sekmesine gidin
4. "Add IP Address" tiklayin
5. "Allow Access from Anywhere" secin (0.0.0.0/0) — Railway icin gerekli

### 1.4 Baglanti URL'sini Alin
1. Cluster sayfasinda "Connect" tiklayin
2. "Connect your application" secin
3. Driver: Python, Version: 3.12+
4. Connection string'i kopyalayin:
   ```
   mongodb+srv://dsbn_admin:<password>@dsbn-production.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
5. `<password>` kismini gercek sifrenizle degistirin

### 1.5 Mevcut Verileri Tasi (Opsiyonel)
Preview ortamindaki verileri Atlas'a tasimak icin:
```bash
# Preview'dan export
mongodump --uri="mongodb://localhost:27017" --db=test_database --out=/tmp/dbbackup

# Atlas'a import
mongorestore --uri="mongodb+srv://dsbn_admin:<password>@dsbn-production.xxxxx.mongodb.net" --db=test_database /tmp/dbbackup/test_database
```

---

## ADIM 2: Railway (Backend Deploy)

### 2.1 Hesap Olusturma
1. https://railway.app adresine gidin
2. GitHub hesabinizla giris yapin

### 2.2 Proje Olusturma
1. "New Project" tiklayin
2. "Deploy from GitHub repo" secin
3. Repository'nizi secin
4. Root Directory: `/backend` olarak ayarlayin

### 2.3 Build Ayarlari
Railway otomatik olarak Python uygulamanizi taniyor. Ama asagidakileri kontrol edin:

**Start Command:**
```
uvicorn server:app --host 0.0.0.0 --port $PORT --workers 4
```

### 2.4 Ortam Degiskenleri (Environment Variables)
Railway dashboard'unda "Variables" sekmesine gidin ve su degiskenleri ekleyin:

```
MONGO_URL=mongodb+srv://dsbn_admin:<password>@dsbn-production.xxxxx.mongodb.net/?retryWrites=true&w=majority
DB_NAME=test_database
EMERGENT_LLM_KEY=sk-emergent-3D99eDdBd4046D5050
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=$2b$12$ovlvmOQqBVH4h/ZWwdmEueaz/z6VzN9cxQjk0cZDwpeBmfiQPDmHe
JWT_SECRET=99281b5f280c9023c297e72de3c69b9395cccbec773a5ca8c64ef9e9c8a2dafa
JWT_EXPIRE_HOURS=24
CORS_ORIGINS=https://guncelgiris.ai,https://www.guncelgiris.ai,https://adminguncelgiris.company,https://www.adminguncelgiris.company
ODDS_API_KEY=cf0633b81337cb40e3ddc0cdbae55b1e
PERIGON_API_KEY=affiliate-news-ai
GODADDY_API_KEY=fYWJAxVtCXrw_KH1Q3dLBVwT62Tgt8mgWMG
GODADDY_API_SECRET=4CoSziun1BUX6jPMsNVvXo
```

### 2.5 Deploy ve URL
- Railway otomatik deploy edecek
- Size bir URL verecek, ornegin: `https://dsbn-backend-production.up.railway.app`
- Bu URL'yi not edin — Frontend icin gerekecek

---

## ADIM 3: Vercel (Frontend Deploy)

### 3.1 Hesap Olusturma
1. https://vercel.com adresine gidin
2. GitHub hesabinizla giris yapin

### 3.2 Proje Import
1. "Add New Project" tiklayin
2. GitHub repo'nuzu secin
3. Framework Preset: **Create React App** secin
4. Root Directory: `/` birakin (vercel.json zaten dogru konfigurasyona sahip)

### 3.3 Ortam Degiskenleri
Vercel dashboard'unda "Settings > Environment Variables" sekmesine gidin:

```
REACT_APP_BACKEND_URL=https://dsbn-backend-production.up.railway.app
REACT_APP_ADMIN_HOST=adminguncelgiris.company
```

**ONEMLI:** `REACT_APP_BACKEND_URL` degerini Railway'den aldiginiz URL ile degistirin!

### 3.4 Build Ayarlari
vercel.json dosyasi zaten dogru konfigurasyona sahip:
- Build: `cd frontend && yarn install && CI=false yarn build`
- Output: `frontend/build`
- Rewrites: Tum route'lar `index.html`'e yonleniyor (SPA)

### 3.5 Deploy
"Deploy" tiklayin. Vercel size bir URL verecek (ornegin: `dsbn-frontend.vercel.app`)

---

## ADIM 4: Custom Domain Baglama

### 4.1 Vercel'de Domain Ekleme
1. Vercel proje dashboard > "Settings" > "Domains"
2. Su domainleri ekleyin:
   - `adminguncelgiris.company`
   - `www.adminguncelgiris.company`
   - `guncelgiris.ai`
   - `www.guncelgiris.ai`

### 4.2 GoDaddy DNS Ayarlari
Her domain icin GoDaddy'de DNS kayitlari ekleyin:

**adminguncelgiris.company icin:**
1. GoDaddy > Domain Manager > adminguncelgiris.company > DNS Management
2. Mevcut A kayitlarini silin
3. Yeni kayitlar ekleyin:
   - Type: **CNAME**, Name: **www**, Value: **cname.vercel-dns.com**
   - Type: **A**, Name: **@**, Value: **76.76.21.21**

**guncelgiris.ai icin:**
- Ayni islem (A record @ -> 76.76.21.21, CNAME www -> cname.vercel-dns.com)

**Diger domainler icin:**
- Platforma eklediginiz her domain icin ayni DNS ayarlarini yapin

### 4.3 SSL Sertifikasi
Vercel otomatik olarak Let's Encrypt SSL sertifikasi olusturur. DNS yayiliminden sonra (5-30 dk) HTTPS otomatik aktif olur.

---

## ADIM 5: Railway Backend'e CORS Guncelleme

Yeni domainler eklendikce Railway'deki `CORS_ORIGINS` degiskenini guncelleyin:
```
CORS_ORIGINS=https://guncelgiris.ai,https://adminguncelgiris.company,https://yeni-domain.com
```

---

## ADIM 6: Dogrulama Kontrol Listesi

Deploy sonrasi su kontrolleri yapin:

- [ ] `https://adminguncelgiris.company/admin-login` aciliyor mu?
- [ ] Admin giris yapabiliyor mu? (admin / 123123..)
- [ ] GoDaddy domainleri listeleniyor mu?
- [ ] Domain platforma eklenebiliyor mu?
- [ ] `https://guncelgiris.ai` ana sayfa aciliyor mu?
- [ ] Makaleler gorunuyor mu?
- [ ] Oto Icerik zamanlayici calisiyor mu?
- [ ] SEO: sitemap.xml erisilebilir mi?

---

## Onemli Notlar

1. **MongoDB Atlas Free Tier:** 512MB limit. 200+ site icin yeterli (tahmini ~100-150MB). Buyurse M2/M5 tier'a gecin.
2. **Railway Free Tier:** Aylik 500 saat. Surekli calisma icin Hobby plan ($5/ay) onerilir.
3. **Vercel Free Tier:** Aylik 100GB bandwidth. Yuksek trafik icin Pro plan ($20/ay) onerilir.
4. **Yedekleme:** MongoDB Atlas otomatik yedekleme yapar (M2+ tier'da).
5. **Workers:** Railway'de `--workers 4` kullanin. CPU'ya gore ayarlayin.
