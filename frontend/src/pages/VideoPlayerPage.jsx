import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { motion } from "framer-motion";
import axios from "axios";
import {
  Play, Eye, Clock, ChevronRight, Star, ExternalLink, Film,
  AlertTriangle, Share2, Tag, ArrowLeft
} from "lucide-react";
import SEOHead from "@/components/SEOHead";
import { API } from "@/App";

export default function VideoPlayerPage() {
  const { videoId } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    axios.get(`${API}/videos/${videoId}`)
      .then(res => setData(res.data))
      .catch(e => setError(e.response?.status === 404 ? "Video bulunamadi" : "Hata olustu"))
      .finally(() => setLoading(false));
  }, [videoId]);

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center pt-20" data-testid="video-player-loading">
      <div className="w-10 h-10 border-2 border-[#8B5CF6] border-t-transparent rounded-full animate-spin" />
    </div>
  );

  if (error || !data) return (
    <div className="min-h-screen flex flex-col items-center justify-center pt-20 gap-4" data-testid="video-player-error">
      <AlertTriangle className="w-16 h-16 text-yellow-500" />
      <h1 className="font-heading text-2xl">{error || "Video bulunamadi"}</h1>
      <Link to="/videolar" className="text-[#8B5CF6] hover:underline">Video Galeriye Don</Link>
    </div>
  );

  const { video, related, company } = data;
  const isFileVideo = video.storage_path || video.source === "upload" || video.source === "ai_generated";
  const videoSrc = isFileVideo && video.storage_path
    ? `${API}/videos/${video.video_id}/file`
    : video.external_url || "";

  const videoJsonLd = {
    "@context": "https://schema.org",
    "@type": "VideoObject",
    "name": video.title,
    "description": video.description,
    "uploadDate": video.created_at,
    "thumbnailUrl": video.thumbnail_url || "",
    "publisher": { "@type": "Organization", "name": "guncelgiris.ai" },
  };

  return (
    <div className="min-h-screen bg-background pt-20 pb-16" data-testid="video-player-page">
      <SEOHead
        title={`${video.title} | Video`}
        description={video.description || `${video.title} video inceleme.`}
        canonical={`https://guncelgiris.ai/videolar/${video.video_id}`}
        jsonLd={[videoJsonLd]}
      />

      <div className="container mx-auto max-w-7xl px-4">
        {/* Breadcrumb */}
        <div className="flex items-center gap-2 text-xs text-muted-foreground mb-4" data-testid="video-breadcrumb">
          <Link to="/" className="hover:text-neon-green transition-colors">Ana Sayfa</Link>
          <ChevronRight className="w-3 h-3" />
          <Link to="/videolar" className="hover:text-[#8B5CF6] transition-colors">Videolar</Link>
          <ChevronRight className="w-3 h-3" />
          <span className="text-[#8B5CF6] truncate max-w-[200px]">{video.title}</span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main: Player + Info */}
          <div className="lg:col-span-2 space-y-4">
            {/* Player */}
            <div className="aspect-video rounded-xl overflow-hidden border border-white/10 bg-black" data-testid="video-player">
              {videoSrc ? (
                isFileVideo && video.storage_path ? (
                  <video
                    className="w-full h-full"
                    controls
                    autoPlay
                    playsInline
                    data-testid="video-element"
                  >
                    <source src={videoSrc} type={video.content_type || "video/mp4"} />
                  </video>
                ) : videoSrc.includes("youtube.com") || videoSrc.includes("youtu.be") ? (
                  <iframe
                    src={videoSrc.replace("watch?v=", "embed/")}
                    title={video.title}
                    className="w-full h-full"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                    data-testid="video-iframe"
                  />
                ) : (
                  <video className="w-full h-full" controls playsInline data-testid="video-element">
                    <source src={videoSrc} type="video/mp4" />
                  </video>
                )
              ) : (
                <div className="w-full h-full flex items-center justify-center" style={{ background: "linear-gradient(135deg, #1a1a2e, #16213e)" }}>
                  <Film className="w-20 h-20 text-[#8B5CF6]/30" />
                </div>
              )}
            </div>

            {/* Video Info */}
            <div className="rounded-xl border border-white/10 bg-white/[0.02] p-5" data-testid="video-info">
              <h1 className="font-heading font-black text-xl md:text-2xl uppercase tracking-tight" data-testid="video-title">
                {video.title}
              </h1>
              <div className="flex flex-wrap items-center gap-4 mt-3 text-xs text-muted-foreground">
                <span className="flex items-center gap-1"><Eye className="w-3.5 h-3.5" /> {video.view_count} goruntulenme</span>
                <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> {new Date(video.created_at).toLocaleDateString("tr-TR", { day: "numeric", month: "long", year: "numeric" })}</span>
                {video.source === "ai_generated" && (
                  <span className="px-2 py-0.5 rounded bg-[#8B5CF6]/15 text-[#8B5CF6] font-bold">AI Video</span>
                )}
                {video.source === "upload" && (
                  <span className="px-2 py-0.5 rounded bg-neon-green/15 text-neon-green font-bold">Upload</span>
                )}
              </div>
              {video.description && (
                <p className="text-sm text-muted-foreground mt-4 leading-relaxed">{video.description}</p>
              )}
              {video.tags?.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-3">
                  {video.tags.map((tag, i) => (
                    <span key={i} className="text-xs px-2 py-0.5 rounded border border-white/10 text-muted-foreground">
                      <Tag className="w-3 h-3 inline mr-1" />{tag}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Company Info if linked */}
            {company && (
              <div className="rounded-xl border border-white/10 bg-white/[0.02] p-5" data-testid="video-company-info">
                <div className="flex items-center gap-4">
                  <img src={company.logo_url} alt={company.name} className="w-12 h-12 rounded-lg border border-neon-green/30" />
                  <div className="flex-1">
                    <h3 className="font-heading font-bold text-base uppercase">{company.name}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-sm font-bold text-neon-green">{company.bonus_amount}</span>
                      <span className="flex items-center gap-1 text-xs text-yellow-400"><Star className="w-3 h-3 fill-yellow-400" />{company.rating}</span>
                    </div>
                  </div>
                  <a href={company.affiliate_url} target="_blank" rel="noopener noreferrer"
                    className="px-4 py-2.5 rounded-lg bg-neon-green text-black font-heading font-bold uppercase text-xs hover:scale-105 transition-all flex items-center gap-1.5">
                    <ExternalLink className="w-3.5 h-3.5" /> Siteye Git
                  </a>
                </div>
              </div>
            )}
          </div>

          {/* Sidebar: Related Videos */}
          <div className="space-y-3" data-testid="video-related">
            <h3 className="font-heading text-base font-bold uppercase mb-2 flex items-center gap-2">
              <Play className="w-4 h-4 text-[#8B5CF6]" /> Ilgili Videolar
            </h3>
            {related?.length > 0 ? related.map((rv) => (
              <Link
                key={rv.video_id}
                to={`/videolar/${rv.video_id}`}
                className="group flex gap-3 rounded-lg p-2 hover:bg-white/5 transition-colors"
                data-testid={`related-video-${rv.video_id}`}
              >
                <div className="relative w-28 h-16 rounded-lg overflow-hidden flex-shrink-0 bg-black/50">
                  {rv.thumbnail_url ? (
                    <img src={rv.thumbnail_url} alt={rv.title} className="w-full h-full object-cover" />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center" style={{ background: "linear-gradient(135deg, #1a1a2e, #16213e)" }}>
                      <Film className="w-6 h-6 text-[#8B5CF6]/30" />
                    </div>
                  )}
                  <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <Play className="w-6 h-6 text-white fill-white" />
                  </div>
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="text-sm font-medium line-clamp-2 group-hover:text-[#8B5CF6] transition-colors">{rv.title}</h4>
                  <div className="flex items-center gap-2 mt-1 text-xs text-muted-foreground">
                    <span>{rv.view_count} izlenme</span>
                  </div>
                </div>
              </Link>
            )) : (
              <p className="text-sm text-muted-foreground">Henuz ilgili video yok.</p>
            )}

            {/* Back to Gallery */}
            <Link to="/videolar"
              className="flex items-center justify-center gap-2 mt-4 w-full px-4 py-3 rounded-xl border border-[#8B5CF6]/30 text-[#8B5CF6] font-heading font-bold uppercase text-sm hover:bg-[#8B5CF6]/10 transition-colors">
              <ArrowLeft className="w-4 h-4" /> Tum Videolar
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
