import { useState, useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { motion } from "framer-motion";
import axios from "axios";
import { Image, Eye, Download, Star, ChevronRight, Search } from "lucide-react";
import SEOHead from "@/components/SEOHead";
import { API } from "@/App";

export default function WallpaperGalleryPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const companySlug = searchParams.get("company") || "";

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams();
    if (companySlug) params.set("company_slug", companySlug);
    params.set("limit", "40");
    axios.get(`${API}/wallpapers?${params.toString()}`)
      .then(res => setData(res.data))
      .catch(() => setData({ wallpapers: [], total: 0 }))
      .finally(() => setLoading(false));
  }, [companySlug]);

  const wallpapers = data?.wallpapers || [];

  return (
    <div className="min-h-screen bg-background pt-20 pb-16" data-testid="wallpaper-gallery-page">
      <SEOHead
        title="Wallpapers & Gorseller 2026 | Firma Tanitim Gorselleri"
        description="Bahis siteleri tanitim gorselleri, bonus wallpapers ve promosyon afisleri. Ucretsiz indir."
        canonical="https://guncelgiris.ai/gorseller"
      />

      {/* Hero */}
      <section className="relative overflow-hidden py-12 md:py-16">
        <div className="absolute inset-0 bg-[#050505]" />
        <div className="absolute inset-0 opacity-[0.04]" style={{
          backgroundImage: "linear-gradient(rgba(236,72,153,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(236,72,153,0.3) 1px, transparent 1px)",
          backgroundSize: "60px 60px"
        }} />
        <div className="relative z-10 container mx-auto max-w-7xl px-4">
          <div className="inline-flex items-center gap-2 rounded-full border px-4 py-1.5 mb-4 text-xs font-semibold uppercase tracking-widest"
            style={{ borderColor: "rgba(236,72,153,0.3)", color: "#EC4899", background: "rgba(236,72,153,0.08)" }}>
            <Image className="w-3.5 h-3.5" /> Wallpapers
          </div>
          <h1 className="font-heading font-black text-3xl md:text-5xl uppercase tracking-tight leading-none mb-3" data-testid="wallpaper-gallery-h1">
            <span className="text-white">GORSEL</span> <span className="text-[#EC4899]">GALERI</span>
          </h1>
          <p className="text-muted-foreground max-w-2xl">Firma tanitim gorselleri, bonus wallpapers ve promosyon afisleri.</p>
        </div>
      </section>

      {/* Grid */}
      <div className="container mx-auto max-w-7xl px-4 mt-8">
        {loading ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
            {[1,2,3,4,5,6,7,8].map(i => (
              <div key={i} className="aspect-square rounded-xl bg-white/5 animate-pulse" />
            ))}
          </div>
        ) : wallpapers.length === 0 ? (
          <div className="text-center py-20" data-testid="wallpaper-gallery-empty">
            <Image className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
            <h2 className="font-heading text-xl text-muted-foreground">Henuz gorsel bulunmuyor</h2>
            <p className="text-sm text-muted-foreground mt-2">Gorseller yakinda eklenecektir.</p>
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4" data-testid="wallpaper-grid">
            {wallpapers.map((wp, i) => (
              <motion.div
                key={wp.wallpaper_id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.03 }}
              >
                <Link
                  to={`/gorseller/${wp.seo_slug}`}
                  className="group block rounded-xl border border-white/6 overflow-hidden transition-all hover:border-[#EC4899]/30 hover:shadow-lg hover:shadow-[#EC4899]/5"
                  style={{ background: "rgba(255,255,255,0.02)" }}
                  data-testid={`wallpaper-card-${i}`}
                >
                  <div className="relative aspect-square bg-black/50">
                    <img
                      src={`${API}/wallpapers/${wp.seo_slug}/file`}
                      alt={wp.alt_text}
                      title={wp.title}
                      className="w-full h-full object-cover"
                      loading="lazy"
                    />
                    {/* Hover overlay */}
                    <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black/50">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full flex items-center justify-center bg-[#EC4899]/90">
                          <Eye className="w-5 h-5 text-white" />
                        </div>
                        <a
                          href={`${API}/wallpapers/${wp.seo_slug}/file`}
                          download={wp.seo_filename}
                          onClick={(e) => e.stopPropagation()}
                          className="w-10 h-10 rounded-full flex items-center justify-center bg-neon-green/90"
                        >
                          <Download className="w-5 h-5 text-black" />
                        </a>
                      </div>
                    </div>
                    {/* AI badge */}
                    {wp.source === "ai_generated" && (
                      <div className="absolute top-2 left-2 px-2 py-0.5 rounded text-[10px] font-bold bg-[#EC4899]/90 text-white">AI</div>
                    )}
                  </div>
                  <div className="p-3">
                    <h3 className="font-heading font-bold text-xs uppercase line-clamp-1 group-hover:text-[#EC4899] transition-colors">
                      {wp.company_name}
                    </h3>
                    <p className="text-[11px] text-muted-foreground mt-0.5">{wp.bonus_amount}</p>
                    <div className="flex items-center gap-2 mt-1 text-[10px] text-muted-foreground">
                      <span className="flex items-center gap-0.5"><Eye className="w-3 h-3" />{wp.view_count}</span>
                      <span className="flex items-center gap-0.5"><Download className="w-3 h-3" />{wp.download_count}</span>
                    </div>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
