import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { motion } from "framer-motion";
import axios from "axios";
import {
  Star, ExternalLink, Shield, Gift, Clock, ChevronRight,
  Award, Zap, Globe, CreditCard, Smartphone, HeadphonesIcon,
  CheckCircle2, AlertTriangle, TrendingUp, FileText, Users
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import SEOHead from "@/components/SEOHead";

const API = process.env.REACT_APP_BACKEND_URL + "/api";

const BONUS_TYPE_LABELS = {
  deneme: "Deneme Bonusu",
  hosgeldin: "Hosgeldin Bonusu",
  casino: "Casino Bonusu",
  spor: "Spor Bahis Bonusu",
};

const FEATURE_ICONS = {
  "Guncel Deneme Bonusu Sitesi": Gift,
  "Yatirim Sartsiz Deneme Bonusu Veren Siteler": Award,
  "En Iyi Casino Siteleri": Star,
  "Guvenilir Bahis Siteleri": Shield,
  "Lisansli Bahis Siteleri": CheckCircle2,
  "Canli Casino Secenekleri": Globe,
  "Hizli Odeme Yontemleri": CreditCard,
  "Mobil Uyumlu Bahis Sitesi": Smartphone,
};

export default function FirmPage() {
  const { slug } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const res = await axios.get(`${API}/firma/${slug}`);
        setData(res.data);
      } catch (e) {
        setError(e.response?.status === 404 ? "Firma bulunamadi" : "Bir hata olustu");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [slug]);

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center pt-20">
      <div className="w-10 h-10 border-2 border-neon-green border-t-transparent rounded-full animate-spin" />
    </div>
  );

  if (error || !data) return (
    <div className="min-h-screen flex flex-col items-center justify-center pt-20 gap-4">
      <AlertTriangle className="w-16 h-16 text-yellow-500" />
      <h1 className="font-heading text-2xl">{error || "Firma bulunamadi"}</h1>
      <Link to="/" className="text-neon-green hover:underline">Ana Sayfaya Don</Link>
    </div>
  );

  const { site, articles, similar_sites } = data;
  const bonusLabel = BONUS_TYPE_LABELS[site.bonus_type] || site.bonus_type;

  const breadcrumbJsonLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      { "@type": "ListItem", "position": 1, "name": "Ana Sayfa", "item": "https://guncelgiris.ai" },
      { "@type": "ListItem", "position": 2, "name": "Firma Rehberi", "item": "https://guncelgiris.ai/#firma-rehberi" },
      { "@type": "ListItem", "position": 3, "name": site.name, "item": `https://guncelgiris.ai/${site.slug || slug}` }
    ]
  };

  const firmJsonLd = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": site.name,
    "url": `https://guncelgiris.ai/${site.slug || slug}`,
    "logo": site.logo_url,
    "description": `${site.name} guncel giris adresi, ${site.bonus_amount} ${bonusLabel} firsati.`,
    "aggregateRating": {
      "@type": "AggregateRating",
      "ratingValue": String(site.rating || 4.5),
      "bestRating": "5",
      "worstRating": "1",
      "ratingCount": "150"
    }
  };

  const reviewJsonLd = {
    "@context": "https://schema.org",
    "@type": "Review",
    "itemReviewed": { "@type": "Organization", "name": site.name },
    "reviewRating": { "@type": "Rating", "ratingValue": String(site.rating || 4.5), "bestRating": "5" },
    "author": { "@type": "Organization", "name": "guncelgiris.ai" },
    "reviewBody": `${site.name} detayli inceleme. ${site.bonus_amount} ${bonusLabel} firsati ile kullanicilarina guvenilir hizmet sunmaktadir.`
  };

  return (
    <div className="min-h-screen bg-background pt-20 pb-16" data-testid="firm-page">
      <SEOHead
        title={`${site.name} Guncel Giris Adresi 2026 | ${site.bonus_amount} ${bonusLabel}`}
        description={`${site.name} guncel giris adresi 2026. ${site.bonus_amount} ${bonusLabel} firsati. Detayli inceleme, bonus rehberi ve guvenilirlik analizi.`}
        canonical={`https://guncelgiris.ai/${site.slug || slug}`}
        amphtml={`https://guncelgiris.ai/api/amp/${site.slug || slug}`}
        jsonLd={[breadcrumbJsonLd, firmJsonLd, reviewJsonLd]}
      />

      {/* ── HERO — 3-Column Firma Banner ─────────────────────────── */}
      <section className="relative overflow-hidden" style={{ minHeight: "500px" }} data-testid="firm-hero">
        <div className="absolute inset-0 bg-[#050505]" />
        <div className="absolute inset-0 opacity-[0.06]" style={{
          backgroundImage: "linear-gradient(rgba(0,255,135,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(0,255,135,0.3) 1px, transparent 1px)",
          backgroundSize: "60px 60px"
        }} />
        <div className="absolute inset-0" style={{ background: "radial-gradient(ellipse at 50% 0%, rgba(0,255,135,0.06) 0%, transparent 60%)" }} />

        <div className="relative z-10 container mx-auto max-w-7xl px-4 md:px-6 flex flex-col justify-center" style={{ minHeight: "500px" }}>

          {/* Breadcrumb */}
          <div className="flex items-center gap-2 text-xs mb-6" style={{ color: "var(--muted-foreground)" }}>
            <Link to="/" className="hover:text-[#00FF87] transition-colors">Ana Sayfa</Link>
            <ChevronRight className="w-3 h-3" />
            <span style={{ color: "#00FF87" }}>{site.name}</span>
          </div>

          {/* 3-Column Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-[260px_1fr_280px] gap-6 items-center">

            {/* LEFT — Firma Kimlik */}
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
              className="hidden lg:flex flex-col items-center text-center gap-4 p-6 rounded-2xl"
              style={{ background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)" }}
            >
              <div className="relative">
                <div className="absolute inset-0 rounded-2xl" style={{ background: "rgba(0,255,135,0.15)", filter: "blur(12px)", animation: "pulseGlow 2s ease-in-out infinite" }} />
                <img src={site.logo_url} alt={site.name} className="relative w-20 h-20 rounded-2xl object-cover border-2" style={{ borderColor: "rgba(0,255,135,0.3)" }} />
              </div>
              <div>
                <h2 className="font-heading font-black text-xl uppercase tracking-tight text-white">{site.name}</h2>
                <div className="flex items-center justify-center gap-2 mt-2">
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold" style={{ background: "rgba(0,255,135,0.12)", color: "#00FF87" }}>
                    <Globe className="w-3 h-3" /> {site.category || "Turkiye"}
                  </span>
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold" style={{ background: "rgba(251,191,36,0.12)", color: "#FBBF24" }}>
                    <Star className="w-3 h-3 fill-yellow-400" /> {site.rating || "4.5"}
                  </span>
                </div>
              </div>
              <p className="text-xs leading-relaxed" style={{ color: "var(--muted-foreground)" }}>
                {site.name} guncel giris adresi ve bonus firsatlari
              </p>

              {/* Ozellikler mini */}
              <div className="w-full space-y-1.5 mt-1">
                {(site.features || []).slice(0, 3).map((f, i) => (
                  <div key={i} className="flex items-center gap-2 text-[11px] px-2 py-1.5 rounded-lg" style={{ background: "rgba(255,255,255,0.03)", color: "var(--muted-foreground)" }}>
                    <CheckCircle2 className="w-3 h-3 flex-shrink-0" style={{ color: "#00FF87" }} />
                    <span className="truncate">{f}</span>
                  </div>
                ))}
              </div>
            </motion.div>

            {/* CENTER — Ana Hero */}
            <motion.div
              initial={{ opacity: 0, scale: 0.97 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6 }}
              className="relative flex flex-col items-center justify-center text-center py-8 lg:py-0"
            >
              {/* Mobil Logo (sadece mobilde) */}
              <div className="flex lg:hidden items-center gap-4 mb-6">
                <img src={site.logo_url} alt={site.name} className="w-16 h-16 rounded-xl object-cover border-2" style={{ borderColor: "rgba(0,255,135,0.3)" }} />
                <div className="text-left">
                  <h1 className="font-heading text-2xl font-black uppercase tracking-tight" data-testid="firm-name">{site.name}</h1>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs font-bold px-2 py-0.5 rounded-full" style={{ background: "rgba(0,255,135,0.12)", color: "#00FF87" }}>{site.category || "Turkiye"}</span>
                    <span className="text-xs font-bold" style={{ color: "#FBBF24" }}>★ {site.rating}</span>
                  </div>
                </div>
              </div>

              <h1 className="hidden lg:block font-heading font-black uppercase leading-none mb-3" data-testid="firm-name" style={{ fontSize: "clamp(2rem, 5vw, 3.5rem)", letterSpacing: "-0.02em" }}>
                <span className="text-white">{site.name}</span>
                <br />
                <span style={{ color: "#00FF87", textShadow: "0 0 40px rgba(0,255,135,0.5)" }}>GUNCEL GIRIS</span>
              </h1>

              <p className="text-sm md:text-base mb-6 max-w-lg mx-auto" style={{ color: "var(--muted-foreground)" }}>
                {site.name} resmi guncel giris adresi. {site.bonus_amount} {bonusLabel} firsatiyla hemen kayit olun.
              </p>

              <div className="flex flex-wrap gap-3 justify-center mb-6">
                <a
                  href={site.affiliate_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  data-testid="firm-cta-main"
                  className="inline-flex items-center gap-2 rounded-xl px-8 py-3.5 font-heading font-bold uppercase tracking-wide text-sm transition-all active:scale-95 hover:scale-105"
                  style={{ background: "#00FF87", color: "#000", boxShadow: "0 0 30px rgba(0,255,135,0.4)" }}
                >
                  <ExternalLink className="w-4 h-4" />
                  Siteye Git
                </a>
                <Link
                  to="/"
                  className="inline-flex items-center gap-2 rounded-xl border px-6 py-3.5 font-heading font-bold uppercase tracking-wide text-sm transition-all hover:bg-white/5"
                  style={{ borderColor: "rgba(255,255,255,0.15)", color: "var(--foreground)" }}
                >
                  Tum Siteler
                </Link>
              </div>

              {/* Mini Stats */}
              <div className="flex items-center gap-4 text-xs" style={{ color: "var(--muted-foreground)" }}>
                <div className="flex items-center gap-1.5"><Shield className="w-3.5 h-3.5" style={{ color: "#00FF87" }} /> Lisansli</div>
                <div className="flex items-center gap-1.5"><Clock className="w-3.5 h-3.5" style={{ color: "#00FF87" }} /> Hizli Odeme</div>
                <div className="flex items-center gap-1.5"><HeadphonesIcon className="w-3.5 h-3.5" style={{ color: "#00FF87" }} /> 7/24 Destek</div>
              </div>

              {/* Alt Orta Logo */}
              <div className="mt-6 flex items-center justify-center gap-3 opacity-50">
                <div className="h-px w-16" style={{ background: "linear-gradient(90deg, transparent, rgba(255,255,255,0.15))" }} />
                <span className="text-[10px] uppercase tracking-[0.2em] font-semibold" style={{ color: "var(--muted-foreground)" }}>guncelgiris.ai</span>
                <div className="h-px w-16" style={{ background: "linear-gradient(90deg, rgba(255,255,255,0.15), transparent)" }} />
              </div>
            </motion.div>

            {/* RIGHT — Bonus Karti */}
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.5 }}
              className="flex flex-col items-center text-center gap-3 p-6 rounded-2xl relative overflow-hidden transition-transform hover:scale-[1.03]"
              style={{
                background: "linear-gradient(160deg, rgba(0,50,20,0.6) 0%, rgba(0,20,10,0.8) 100%)",
                border: "1px solid rgba(0,255,135,0.15)",
                backdropFilter: "blur(16px)",
                boxShadow: "0 0 60px rgba(0,255,135,0.08), inset 0 0 60px rgba(0,255,135,0.03)"
              }}
              data-testid="firm-bonus-box"
            >
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 rounded-full" style={{
                background: "radial-gradient(circle, rgba(0,255,135,0.25) 0%, transparent 70%)",
                filter: "blur(30px)",
                animation: "pulseGlow 2s ease-in-out infinite"
              }} />

              <div className="relative z-10">
                <span className="text-xs uppercase tracking-[0.25em] font-semibold" style={{ color: "rgba(255,255,255,0.5)" }}>
                  {bonusLabel}
                </span>

                <div className="my-4">
                  <span
                    className="font-heading font-black text-5xl md:text-6xl"
                    style={{
                      color: "#00FF87",
                      textShadow: "0 0 40px rgba(0,255,135,0.6), 0 0 80px rgba(0,255,135,0.3), 0 0 120px rgba(0,255,135,0.15)",
                      animation: "pulseGlow 2s ease-in-out infinite"
                    }}
                  >
                    {site.bonus_amount}
                  </span>
                </div>

                <p className="text-xs mb-5" style={{ color: "var(--muted-foreground)" }}>
                  Ilk yatiriminiza ozel bonus firsati
                </p>

                <a
                  href={site.affiliate_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="relative inline-flex items-center justify-center gap-2 w-full rounded-xl px-6 py-3.5 font-heading font-bold uppercase tracking-wide text-sm overflow-hidden"
                  style={{
                    background: "linear-gradient(135deg, #00FF87, #00CC6B)",
                    color: "#000",
                    boxShadow: "0 0 30px rgba(0,255,135,0.35), inset 0 1px 0 rgba(255,255,255,0.2)",
                    animation: "breathing 2s ease-in-out infinite"
                  }}
                  data-testid="firm-bonus-cta"
                >
                  <ExternalLink className="w-4 h-4" />
                  SITEYE GIT
                </a>

                <div className="flex items-center justify-center gap-3 mt-4">
                  <div className="flex items-center gap-1"><Shield className="w-3 h-3" style={{ color: "#00FF87" }} /><span className="text-[10px]" style={{ color: "var(--muted-foreground)" }}>Lisansli</span></div>
                  <div className="flex items-center gap-1"><Clock className="w-3 h-3" style={{ color: "#00FF87" }} /><span className="text-[10px]" style={{ color: "var(--muted-foreground)" }}>Hizli Odeme</span></div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CSS Animations */}
      <style>{`
        @keyframes pulseGlow {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.6; }
        }
        @keyframes breathing {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.04); }
        }
      `}</style>

      <div className="container mx-auto max-w-6xl px-4">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">

          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">

            {/* Features */}
            <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="firm-features">
              <h2 className="font-heading text-xl font-bold uppercase mb-4 flex items-center gap-2">
                <Zap className="w-5 h-5 text-neon-green" /> Ozellikler
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {(site.features || []).map((f, i) => {
                  const Icon = FEATURE_ICONS[f] || CheckCircle2;
                  return (
                    <div key={i} className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.03] border border-white/5">
                      <Icon className="w-5 h-5 text-neon-green flex-shrink-0" />
                      <span className="text-sm">{f}</span>
                    </div>
                  );
                })}
                <div className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.03] border border-white/5">
                  <HeadphonesIcon className="w-5 h-5 text-neon-green flex-shrink-0" />
                  <span className="text-sm">7/24 Canli Destek</span>
                </div>
                <div className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.03] border border-white/5">
                  <Shield className="w-5 h-5 text-neon-green flex-shrink-0" />
                  <span className="text-sm">SSL Guvenlik Sertifikasi</span>
                </div>
              </div>
            </div>

            {/* Bonus Details */}
            <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="firm-bonus-details">
              <h2 className="font-heading text-xl font-bold uppercase mb-4 flex items-center gap-2">
                <Gift className="w-5 h-5 text-yellow-400" /> Bonus Detaylari
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="rounded-xl bg-neon-green/5 border border-neon-green/20 p-4 text-center">
                  <div className="text-xs text-muted-foreground mb-1">Bonus Miktari</div>
                  <div className="font-heading text-xl font-bold text-neon-green">{site.bonus_amount}</div>
                </div>
                <div className="rounded-xl bg-yellow-500/5 border border-yellow-500/20 p-4 text-center">
                  <div className="text-xs text-muted-foreground mb-1">Bonus Tipi</div>
                  <div className="font-heading text-sm font-bold text-yellow-400">{bonusLabel}</div>
                </div>
                <div className="rounded-xl bg-blue-500/5 border border-blue-500/20 p-4 text-center">
                  <div className="text-xs text-muted-foreground mb-1">Cevrim Sarti</div>
                  <div className="font-heading text-xl font-bold text-blue-400">{site.turnover_requirement}x</div>
                </div>
                <div className="rounded-xl bg-purple-500/5 border border-purple-500/20 p-4 text-center">
                  <div className="text-xs text-muted-foreground mb-1">Puan</div>
                  <div className="font-heading text-xl font-bold text-purple-400 flex items-center justify-center gap-1">
                    <Star className="w-4 h-4 fill-purple-400" />{site.rating}
                  </div>
                </div>
              </div>

              {/* Payment methods */}
              <h3 className="font-heading text-base font-bold uppercase mt-6 mb-3 flex items-center gap-2">
                <CreditCard className="w-4 h-4 text-[#00F0FF]" /> Odeme Yontemleri
              </h3>
              <div className="flex flex-wrap gap-2">
                {["Papara","Banka Havale","Kripto Para","Kredi Karti","Jeton","CMT"].map(m => (
                  <span key={m} className="px-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-xs font-medium">{m}</span>
                ))}
              </div>
            </div>

            {/* Articles */}
            {articles.length > 0 && (
              <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="firm-articles">
                <h2 className="font-heading text-xl font-bold uppercase mb-4 flex items-center gap-2">
                  <FileText className="w-5 h-5 text-[#00F0FF]" /> {site.name} Hakkinda Makaleler
                </h2>
                <div className="space-y-3">
                  {articles.map((a) => (
                    <Link
                      key={a.id}
                      to={`/makale/${a.slug}`}
                      className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.03] border border-white/5 hover:border-neon-green/30 transition-all group"
                    >
                      <div className="w-8 h-8 rounded-lg bg-neon-green/10 flex items-center justify-center flex-shrink-0">
                        <FileText className="w-4 h-4 text-neon-green" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium truncate group-hover:text-neon-green transition-colors">{a.title}</div>
                        <div className="text-xs text-muted-foreground">{new Date(a.created_at).toLocaleDateString("tr-TR")}</div>
                      </div>
                      <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-neon-green" />
                    </Link>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* CTA Card */}
            <div className="rounded-2xl border border-neon-green/20 bg-neon-green/5 p-6 text-center sticky top-24" data-testid="firm-sidebar-cta">
              <img src={site.logo_url} alt={site.name} className="w-16 h-16 rounded-xl mx-auto mb-3" />
              <h3 className="font-heading text-lg font-bold uppercase">{site.name}</h3>
              <div className="font-heading text-3xl font-black text-neon-green mt-2">{site.bonus_amount}</div>
              <div className="text-sm text-muted-foreground mt-1">{bonusLabel}</div>
              <a
                href={site.affiliate_url}
                target="_blank"
                rel="noopener noreferrer"
                data-testid="firm-cta-sidebar"
                className="flex items-center justify-center gap-2 mt-4 w-full px-6 py-3.5 rounded-xl font-heading font-bold uppercase tracking-wide text-sm bg-neon-green text-black hover:scale-105 transition-all"
                style={{ boxShadow: "0 0 28px rgba(0,255,135,0.4)" }}
              >
                <ExternalLink className="w-4 h-4" />
                Siteye Git
              </a>
              <p className="text-[11px] text-muted-foreground mt-3">18+ | Sorumlu oyun oynayiniz</p>
            </div>

            {/* Quick Info */}
            <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-5">
              <h3 className="font-heading text-base font-bold uppercase mb-3 flex items-center gap-2">
                <Shield className="w-4 h-4 text-neon-green" /> Hizli Bilgi
              </h3>
              <div className="space-y-2.5 text-sm">
                <div className="flex justify-between"><span className="text-muted-foreground">Kategori</span><span className="font-medium">{site.category || "Turkiye"}</span></div>
                <div className="flex justify-between"><span className="text-muted-foreground">Lisans</span><span className="font-medium">Curacao eGaming</span></div>
                <div className="flex justify-between"><span className="text-muted-foreground">Min. Yatirim</span><span className="font-medium">50 TL</span></div>
                <div className="flex justify-between"><span className="text-muted-foreground">Min. Cekim</span><span className="font-medium">100 TL</span></div>
                <div className="flex justify-between"><span className="text-muted-foreground">Mobil Uyum</span><span className="text-neon-green font-medium">Var</span></div>
                <div className="flex justify-between"><span className="text-muted-foreground">Canli Destek</span><span className="text-neon-green font-medium">7/24</span></div>
              </div>
            </div>

            {/* Similar Sites */}
            {similar_sites.length > 0 && (
              <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-5" data-testid="firm-similar">
                <h3 className="font-heading text-base font-bold uppercase mb-3 flex items-center gap-2">
                  <Users className="w-4 h-4 text-[#00F0FF]" /> Benzer Siteler
                </h3>
                <div className="space-y-2">
                  {similar_sites.map((s) => {
                    const trMap = {'ç':'c','ğ':'g','ı':'i','ö':'o','ş':'s','ü':'u','Ç':'c','Ğ':'g','İ':'i','Ö':'o','Ş':'s','Ü':'u'};
                    let sl = s.name.toLowerCase();
                    for (const [k,v] of Object.entries(trMap)) sl = sl.replaceAll(k,v);
                    const firmSlug = sl.replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') + '-guncelgiris';
                    return (
                    <Link
                      key={s.id}
                      to={`/${s.slug || firmSlug}`}
                      className="flex items-center gap-3 p-2.5 rounded-xl hover:bg-white/5 transition-all group"
                    >
                      <img src={s.logo_url} alt={s.name} className="w-8 h-8 rounded-lg" />
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium truncate group-hover:text-neon-green">{s.name}</div>
                        <div className="text-xs text-neon-green">{s.bonus_amount}</div>
                      </div>
                      <ChevronRight className="w-4 h-4 text-muted-foreground" />
                    </Link>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Legal Footer */}
      <div className="container mx-auto max-w-6xl px-4 mt-12">
        <div className="rounded-xl border border-yellow-500/20 bg-yellow-500/5 p-4 text-center text-xs text-muted-foreground">
          <AlertTriangle className="w-4 h-4 inline-block text-yellow-500 mr-1.5" />
          Bahis ve sans oyunlari 18 yas alti icin yasaktir. Kumar bagimliligi yardim hatti: 182. Bu sayfa bilgilendirme amaclidir, yatirim tavsiyesi degildir.
        </div>
      </div>
    </div>
  );
}
