# Company Discovery Module

Bu modül, şirket keşfi ve zenginleştirme akışının dokümantasyonunu içerir.

## Pipeline
1. Query al önce
2. Serper/Brave/Bing/SerpAPI kaynaklarından keşfet
3. AI sınıflandır (kategori, alt kategori, tag)
4. Enrichment (Similarweb/BuiltWith varsa gerçek veri; yoksa fallback)
5. SEO içerik üret
6. `companies` koleksiyonuna kaydet

## Admin Endpoints
- `POST /api/admin/companies/discovery`
- `GET /api/admin/companies`
- `POST /api/admin/companies/{company_id}/approve`
- `POST /api/admin/companies/{company_id}/feature`
- `POST /api/admin/companies/{company_id}/refresh`
- `DELETE /api/admin/companies/{company_id}`
