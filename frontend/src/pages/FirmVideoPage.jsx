import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import axios from "axios";
import { AlertTriangle, ExternalLink, PlayCircle, ChevronRight, Video, RefreshCw } from "lucide-react";
import SEOHead from "@/components/SEOHead";
import { API } from "@/App";

const BONUS_TYPE_LABELS = {
  deneme: "Deneme Bonusu",
  hosgeldin: "Hosgeldin Bonusu",
  casino: "Casino Bonusu",
  spor: "Spor Bahis Bonusu",
};

export default function FirmVideoPage() {
  const { slug } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const run = async () => {
      setLoading(true);
      setError("");
      try {
        const res = await axios.get(`${API}/firma/${slug}/video`);
        setData(res.data);
      } catch (e) {
        setError(e.response?.status === 404 ? "Firma video sayfasi bulunamadi" : "Video verisi alinamadi");
      } finally {
        setLoading(false);
      }
    };
    run();
  }, [slug]);

  const jsonLd = useMemo(() => {
    if (!data?.site || !data?.video) return null;
    return {
      "@context": "https://schema.org",
      "@type": "VideoObject",
      name: data.video.video_title,
      description: data.video.video_description,
      contentUrl: data.video.video_url,
      embedUrl: data.video.video_embed_url,
      uploadDate: new Date().toISOString(),
      publisher: {
        "@type": "Organization",
        name: "guncelgiris.ai",
      },
    };
  }, [data]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center pt-20" data-testid="firm-video-loading">
        <div className="w-10 h-10 border-2 border-neon-green border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4 pt-20" data-testid="firm-video-error-state">
        <AlertTriangle className="w-14 h-14 text-yellow-500" />
        <h1 className="font-heading text-2xl">{error || "Video sayfasi acilamadi"}</h1>
        <Link to="/" className="text-neon-green hover:underline" data-testid="firm-video-error-home-link">Ana Sayfaya Don</Link>
      </div>
    );
  }

  const { site, video, canonical_url, amp_url } = data;
  const bonusLabel = BONUS_TYPE_LABELS[site.bonus_type] || site.bonus_type || "Bonus";
  const isFileVideo = video.video_type === "file";

  return (
    <div className="min-h-screen bg-background pt-20 pb-16" data-testid="firm-video-page">
      <SEOHead
        title={`${site.name} Video Inceleme 2026 | ${site.bonus_amount} ${bonusLabel}`}
        description={`${site.name} icin firma ozel video inceleme sayfasi. Guncel giris, bonus detaylari ve hizli erisim.`}
        canonical={canonical_url}
        amphtml={amp_url}
        jsonLd={jsonLd}
      />

      <section className="container mx-auto max-w-6xl px-4">
        <div className="flex items-center gap-2 text-xs mb-6 text-muted-foreground" data-testid="firm-video-breadcrumb">
          <Link to="/" className="hover:text-neon-green transition-colors" data-testid="firm-video-breadcrumb-home">Ana Sayfa</Link>
          <ChevronRight className="w-3 h-3" />
          <Link to={`/${site.slug}`} className="hover:text-neon-green transition-colors" data-testid="firm-video-breadcrumb-firm">{site.name}</Link>
          <ChevronRight className="w-3 h-3" />
          <span className="text-neon-green" data-testid="firm-video-breadcrumb-current">Video</span>
        </div>

        <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-6 md:p-8">
          <div className="flex flex-col md:flex-row md:items-center gap-4 mb-6">
            <img src={site.logo_url} alt={site.name} className="w-16 h-16 rounded-xl object-cover border border-neon-green/30" data-testid="firm-video-site-logo" />
            <div>
              <h1 className="font-heading font-black uppercase text-3xl md:text-4xl leading-tight" data-testid="firm-video-site-name">{site.name} Video Inceleme</h1>
              <p className="text-sm text-muted-foreground mt-1" data-testid="firm-video-bonus-info">{site.bonus_amount} • {bonusLabel}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 space-y-4">
              <div className="aspect-video rounded-xl overflow-hidden border border-white/10 bg-black" data-testid="firm-video-player-wrap">
                {isFileVideo ? (
                  <video className="w-full h-full" controls playsInline data-testid="firm-video-file-player">
                    <source src={video.video_embed_url} type="video/mp4" />
                  </video>
                ) : (
                  <iframe
                    src={video.video_embed_url}
                    title={video.video_title}
                    className="w-full h-full"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                    allowFullScreen
                    data-testid="firm-video-iframe"
                  />
                )}
              </div>
              <div>
                <h2 className="font-heading text-xl font-bold" data-testid="firm-video-title">{video.video_title}</h2>
                <p className="text-sm text-muted-foreground mt-2" data-testid="firm-video-description">{video.video_description}</p>
                {video.ai_video_status === "generating" && (
                  <div className="mt-3 inline-flex items-center gap-2 rounded-lg px-3 py-1.5 text-xs bg-yellow-500/10 text-yellow-400 border border-yellow-500/20" data-testid="firm-video-status-generating">
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" /> AI video uretiliyor, birazdan yenileyin.
                  </div>
                )}
                {video.ai_video_status === "failed" && (
                  <div className="mt-3 text-xs text-red-400" data-testid="firm-video-status-failed">AI video uretimi hatasi: {video.ai_video_error || "Bilinmeyen hata"}</div>
                )}
              </div>
            </div>

            <aside className="space-y-3">
              <a
                href={video.video_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-center gap-2 w-full rounded-xl px-4 py-3 font-heading font-bold uppercase text-sm bg-[#00F0FF] text-black hover:opacity-90 transition-opacity"
                data-testid="firm-video-watch-external"
              >
                <PlayCircle className="w-4 h-4" /> {isFileVideo ? "Videoyu Indir/Ac" : "Videoyu Disarida Ac"}
              </a>

              <a
                href={site.affiliate_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center justify-center gap-2 w-full rounded-xl px-4 py-3 font-heading font-bold uppercase text-sm bg-neon-green text-black hover:opacity-90 transition-opacity"
                data-testid="firm-video-affiliate-cta"
              >
                <ExternalLink className="w-4 h-4" /> Siteye Git
              </a>

              <Link
                to={`/${site.slug}`}
                className="flex items-center justify-center gap-2 w-full rounded-xl px-4 py-3 border border-white/15 font-heading font-bold uppercase text-sm hover:bg-white/5 transition-colors"
                data-testid="firm-video-back-firm"
              >
                <Video className="w-4 h-4" /> Firma Detayi
              </Link>

              <div className="rounded-xl border border-white/10 p-3 text-xs text-muted-foreground" data-testid="firm-video-amp-link-box">
                AMP Link:
                <div className="mt-1 break-all text-neon-green">{amp_url}</div>
              </div>
            </aside>
          </div>
        </div>
      </section>
    </div>
  );
}