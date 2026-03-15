import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import axios from "axios";
import {
  Image, Eye, Download, Star, ExternalLink, ChevronRight,
  AlertTriangle, Clock, Tag
} from "lucide-react";
import SEOHead from "@/components/SEOHead";
import { API } from "@/App";

export default function WallpaperDetailPage() {
  const { seoSlug } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    axios.get(`${API}/wallpapers/${seoSlug}`)
      .then(res => setData(res.data))
      .catch(e => setError(e.response?.status === 404 ? "Gorsel bulunamadi" : "Hata olustu"))
      .finally(() => setLoading(false));
  }, [seoSlug]);

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center pt-20" data-testid="wallpaper-detail-loading">
      <div className="w-10 h-10 border-2 border-[#EC4899] border-t-transparent rounded-full animate-spin" />
    </div>
  );

  if (error || !data) return (
    <div className="min-h-screen flex flex-col items-center justify-center pt-20 gap-4" data-testid="wallpaper-detail-error">
      <AlertTriangle className="w-16 h-16 text-yellow-500" />
      <h1 className="font-heading text-2xl">{error || "Gorsel bulunamadi"}</h1>
      <Link to="/gorseller" className="text-[#EC4899] hover:underline">Galeriye Don</Link>
    </div>
  );

  const { wallpaper: wp, company, related } = data;

  const imageJsonLd = {
    "@context": "https://schema.org",
    "@type": "ImageObject",
    "name": wp.title,
    "description": wp.description,
    "contentUrl": `https://guncelgiris.ai/api/wallpapers/${wp.seo_slug}/file`,
    "thumbnailUrl": `https://guncelgiris.ai/api/wallpapers/${wp.seo_slug}/file`,
    "uploadDate": wp.created_at,
    "author": { "@type": "Organization", "name": "guncelgiris.ai" },
  };

  return (
    <div className="min-h-screen bg-background pt-20 pb-16" data-testid="wallpaper-detail-page">
      <SEOHead
        title={wp.title}
        description={wp.description}
        canonical={`https://guncelgiris.ai/gorseller/${wp.seo_slug}`}
        image={`https://guncelgiris.ai/api/wallpapers/${wp.seo_slug}/file`}
        jsonLd={[imageJsonLd]}
      />

      <div className="container mx-auto max-w-6xl px-4">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-xs text-muted-foreground mb-4" data-testid="wallpaper-breadcrumb">
          <Link to="/" className="hover:text-neon-green transition-colors">Ana Sayfa</Link>
          <ChevronRight className="w-3 h-3" />
          <Link to="/gorseller" className="hover:text-[#EC4899] transition-colors">Gorseller</Link>
          <ChevronRight className="w-3 h-3" />
          <span className="text-[#EC4899] truncate max-w-[200px]">{wp.company_name}</span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Image */}
          <div className="lg:col-span-2 space-y-4">
            <div className="rounded-xl overflow-hidden border border-white/10 bg-black" data-testid="wallpaper-image">
              <img
                src={`${API}/wallpapers/${wp.seo_slug}/file`}
                alt={wp.alt_text}
                title={wp.title}
                className="w-full h-auto"
              />
            </div>

            <div className="rounded-xl border border-white/10 bg-white/[0.02] p-5" data-testid="wallpaper-info">
              <h1 className="font-heading font-black text-xl md:text-2xl uppercase tracking-tight" data-testid="wallpaper-title">
                {wp.title}
              </h1>
              <div className="flex flex-wrap items-center gap-4 mt-3 text-xs text-muted-foreground">
                <span className="flex items-center gap-1"><Eye className="w-3.5 h-3.5" /> {wp.view_count} goruntulenme</span>
                <span className="flex items-center gap-1"><Download className="w-3.5 h-3.5" /> {wp.download_count} indirme</span>
                <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> {new Date(wp.created_at).toLocaleDateString("tr-TR")}</span>
                {wp.source === "ai_generated" && (
                  <span className="px-2 py-0.5 rounded bg-[#EC4899]/15 text-[#EC4899] font-bold">AI Gorsel</span>
                )}
              </div>
              {wp.description && (
                <p className="text-sm text-muted-foreground mt-3 leading-relaxed">{wp.description}</p>
              )}
              {wp.tags?.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-3">
                  {wp.tags.map((tag, i) => (
                    <span key={i} className="text-xs px-2 py-0.5 rounded border border-white/10 text-muted-foreground">#{tag}</span>
                  ))}
                </div>
              )}

              <a
                href={`${API}/wallpapers/${wp.seo_slug}/file`}
                download={wp.seo_filename}
                className="inline-flex items-center gap-2 mt-4 px-6 py-3 rounded-xl bg-[#EC4899] text-white font-heading font-bold uppercase text-sm hover:scale-105 transition-all"
                data-testid="wallpaper-download-btn"
              >
                <Download className="w-4 h-4" /> Gorseli Indir
              </a>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {company && (
              <div className="rounded-2xl border border-neon-green/30 bg-neon-green/5 p-6 text-center" data-testid="wallpaper-company-cta">
                <img src={company.logo_url} alt={company.name} className="w-14 h-14 rounded-xl mx-auto mb-3" />
                <h3 className="font-heading text-lg font-bold uppercase">{company.name}</h3>
                <div className="font-heading text-2xl font-black text-neon-green mt-1">{company.bonus_amount}</div>
                <a href={company.affiliate_url} target="_blank" rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 mt-3 w-full px-4 py-3 rounded-xl font-heading font-bold uppercase text-sm bg-neon-green text-black hover:scale-105 transition-all">
                  <ExternalLink className="w-4 h-4" /> Siteye Git
                </a>
              </div>
            )}

            {related?.length > 0 && (
              <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-5" data-testid="wallpaper-related">
                <h3 className="font-heading text-base font-bold uppercase mb-3">Diger Gorseller</h3>
                <div className="grid grid-cols-2 gap-2">
                  {related.map((rw) => (
                    <Link key={rw.seo_slug} to={`/gorseller/${rw.seo_slug}`} className="group rounded-lg overflow-hidden border border-white/6 hover:border-[#EC4899]/30">
                      <img
                        src={`${API}/wallpapers/${rw.seo_slug}/file`}
                        alt={rw.alt_text}
                        className="w-full aspect-square object-cover"
                        loading="lazy"
                      />
                    </Link>
                  ))}
                </div>
              </div>
            )}

            <Link to="/gorseller"
              className="flex items-center justify-center gap-2 w-full px-4 py-3 rounded-xl border border-[#EC4899]/30 text-[#EC4899] font-heading font-bold uppercase text-sm hover:bg-[#EC4899]/10 transition-colors">
              <Image className="w-4 h-4" /> Tum Gorseller
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
