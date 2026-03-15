import { useState, useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { motion } from "framer-motion";
import axios from "axios";
import {
  Play, Eye, Clock, ChevronRight, Search, Film,
  AlertTriangle, Star, ExternalLink
} from "lucide-react";
import SEOHead from "@/components/SEOHead";
import { API } from "@/App";

const CATEGORIES = [
  { slug: "", label: "Tumu" },
  { slug: "general", label: "Genel" },
  { slug: "bonus", label: "Bonus" },
  { slug: "giris", label: "Giris" },
  { slug: "inceleme", label: "Inceleme" },
];

export default function VideoGalleryPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const category = searchParams.get("category") || "";
  const companySlug = searchParams.get("company") || "";

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams();
    if (category) params.set("category", category);
    if (companySlug) params.set("company_slug", companySlug);
    params.set("limit", "30");
    axios.get(`${API}/videos?${params.toString()}`)
      .then(res => setData(res.data))
      .catch(() => setData({ videos: [], total: 0 }))
      .finally(() => setLoading(false));
  }, [category, companySlug]);

  const videos = data?.videos || [];

  return (
    <div className="min-h-screen bg-background pt-20 pb-16" data-testid="video-gallery-page">
      <SEOHead
        title="Video Galeri 2026 | Firma Video Incelemeleri"
        description="Bahis siteleri video incelemeleri, bonus rehberleri ve guncel giris videolari."
        canonical="https://guncelgiris.ai/videolar"
      />

      {/* Hero */}
      <section className="relative overflow-hidden py-12 md:py-16">
        <div className="absolute inset-0 bg-[#050505]" />
        <div className="absolute inset-0 opacity-[0.04]" style={{
          backgroundImage: "linear-gradient(rgba(139,92,246,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(139,92,246,0.3) 1px, transparent 1px)",
          backgroundSize: "60px 60px"
        }} />
        <div className="relative z-10 container mx-auto max-w-7xl px-4">
          <div className="inline-flex items-center gap-2 rounded-full border px-4 py-1.5 mb-4 text-xs font-semibold uppercase tracking-widest"
            style={{ borderColor: "rgba(139,92,246,0.3)", color: "#8B5CF6", background: "rgba(139,92,246,0.08)" }}>
            <Film className="w-3.5 h-3.5" /> Video Galeri
          </div>
          <h1 className="font-heading font-black text-3xl md:text-5xl uppercase tracking-tight leading-none mb-3" data-testid="video-gallery-h1">
            <span className="text-white">VIDEO</span> <span className="text-[#8B5CF6]">GALERI</span>
          </h1>
          <p className="text-muted-foreground max-w-2xl">Firma video incelemeleri, bonus rehberleri ve guncel giris videolari.</p>

          {/* Category Filter */}
          <div className="flex flex-wrap gap-2 mt-6" data-testid="video-category-filter">
            {CATEGORIES.map(cat => (
              <button
                key={cat.slug}
                onClick={() => {
                  const p = new URLSearchParams(searchParams);
                  if (cat.slug) p.set("category", cat.slug); else p.delete("category");
                  setSearchParams(p);
                }}
                className="px-4 py-2 rounded-lg text-sm font-heading font-bold uppercase tracking-wide transition-all"
                style={{
                  background: (category || "") === cat.slug ? "#8B5CF6" : "rgba(255,255,255,0.05)",
                  color: (category || "") === cat.slug ? "#000" : "var(--muted-foreground)",
                  border: `1px solid ${(category || "") === cat.slug ? "#8B5CF6" : "rgba(255,255,255,0.1)"}`,
                }}
                data-testid={`video-filter-${cat.slug || "all"}`}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* Video Grid */}
      <div className="container mx-auto max-w-7xl px-4 mt-8">
        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1,2,3,4,5,6].map(i => (
              <div key={i} className="aspect-video rounded-xl bg-white/5 animate-pulse" />
            ))}
          </div>
        ) : videos.length === 0 ? (
          <div className="text-center py-20" data-testid="video-gallery-empty">
            <Film className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
            <h2 className="font-heading text-xl text-muted-foreground">Henuz video bulunmuyor</h2>
            <p className="text-sm text-muted-foreground mt-2">Videolar yakinda eklenecektir.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4" data-testid="video-grid">
            {videos.map((video, i) => (
              <motion.div
                key={video.video_id}
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.04 }}
              >
                <Link
                  to={`/videolar/${video.video_id}`}
                  className="group block rounded-xl border border-white/6 overflow-hidden transition-all hover:border-[#8B5CF6]/30 hover:shadow-lg hover:shadow-[#8B5CF6]/5"
                  style={{ background: "rgba(255,255,255,0.02)" }}
                  data-testid={`video-card-${i}`}
                >
                  {/* Thumbnail */}
                  <div className="relative aspect-video bg-black/50">
                    {video.thumbnail_url ? (
                      <img src={video.thumbnail_url} alt={video.title} className="w-full h-full object-cover" />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center" style={{ background: "linear-gradient(135deg, #1a1a2e, #16213e)" }}>
                        <Film className="w-12 h-12 text-[#8B5CF6]/40" />
                      </div>
                    )}
                    {/* Play overlay */}
                    <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity bg-black/40">
                      <div className="w-14 h-14 rounded-full flex items-center justify-center" style={{ background: "rgba(139,92,246,0.9)" }}>
                        <Play className="w-6 h-6 text-white fill-white ml-0.5" />
                      </div>
                    </div>
                    {/* Duration */}
                    {video.duration_seconds > 0 && (
                      <div className="absolute bottom-2 right-2 px-1.5 py-0.5 rounded text-[10px] font-bold bg-black/80 text-white">
                        {Math.floor(video.duration_seconds / 60)}:{String(video.duration_seconds % 60).padStart(2, "0")}
                      </div>
                    )}
                    {/* Source badge */}
                    {video.source === "ai_generated" && (
                      <div className="absolute top-2 left-2 px-2 py-0.5 rounded text-[10px] font-bold bg-[#8B5CF6]/90 text-white">
                        AI
                      </div>
                    )}
                  </div>
                  {/* Info */}
                  <div className="p-3">
                    <h3 className="font-heading font-bold text-sm uppercase line-clamp-2 group-hover:text-[#8B5CF6] transition-colors">
                      {video.title}
                    </h3>
                    <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                      {video.company_name && (
                        <span className="flex items-center gap-1"><Star className="w-3 h-3" /> {video.company_name}</span>
                      )}
                      <span className="flex items-center gap-1"><Eye className="w-3 h-3" /> {video.view_count}</span>
                      <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {new Date(video.created_at).toLocaleDateString("tr-TR")}</span>
                    </div>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        )}

        {data && data.total > 30 && (
          <div className="text-center mt-8">
            <button className="px-6 py-3 rounded-xl border border-[#8B5CF6]/30 text-[#8B5CF6] font-heading font-bold uppercase text-sm hover:bg-[#8B5CF6]/10 transition-colors"
              data-testid="video-load-more">
              Daha Fazla
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
