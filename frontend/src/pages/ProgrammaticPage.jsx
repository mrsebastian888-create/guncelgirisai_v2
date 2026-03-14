import { useState, useEffect } from "react";
import { useLocation, Link } from "react-router-dom";
import { motion } from "framer-motion";
import axios from "axios";
import {
  Star, ExternalLink, Shield, Gift, ChevronRight, Globe,
  AlertTriangle, CreditCard, Award, Clock, Lock, Crown, Zap
} from "lucide-react";
import SEOHead from "@/components/SEOHead";
import { API } from "@/App";

const TEMPLATE_ICONS = {
  company_payment: CreditCard,
  company_year: Clock,
  intent_hub: Crown,
  license_hub: Shield,
  country_hub: Globe,
  guide_hub: Award,
};

const TEMPLATE_COLORS = {
  company_payment: "#00F0FF",
  company_year: "#FFD700",
  intent_hub: "#00FF87",
  license_hub: "#00F0FF",
  country_hub: "#FFD700",
  guide_hub: "#00FF87",
};

export default function ProgrammaticPage() {
  const location = useLocation();
  const slug = location.pathname.replace(/^\//, "");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    axios.get(`${API}/programmatic/page/${slug}`)
      .then(res => setData(res.data))
      .catch(e => setError(e.response?.status === 404 ? "Sayfa bulunamadi" : "Hata olustu"))
      .finally(() => setLoading(false));
  }, [slug]);

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center pt-20" data-testid="prog-page-loading">
      <div className="w-10 h-10 border-2 border-neon-green border-t-transparent rounded-full animate-spin" />
    </div>
  );

  if (error || !data) return (
    <div className="min-h-screen flex flex-col items-center justify-center pt-20 gap-4" data-testid="prog-page-error">
      <AlertTriangle className="w-16 h-16 text-yellow-500" />
      <h1 className="font-heading text-2xl">{error || "Sayfa bulunamadi"}</h1>
      <Link to="/" className="text-neon-green hover:underline">Ana Sayfaya Don</Link>
    </div>
  );

  const { page, sites, site_detail, breadcrumb, hub_links } = data;
  const seo = page.seo;
  const template = page.template;
  const accentColor = TEMPLATE_COLORS[template] || "#00FF87";
  const PageIcon = TEMPLATE_ICONS[template] || Globe;
  const isCompanyPage = !!site_detail;

  const breadcrumbJsonLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": breadcrumb.map((b, i) => ({
      "@type": "ListItem", "position": i + 1, "name": b.name,
      "item": `https://guncelgiris.ai${b.url}`
    }))
  };

  const itemListJsonLd = sites.length > 0 ? {
    "@context": "https://schema.org",
    "@type": "ItemList",
    "name": seo.title,
    "numberOfItems": sites.length,
    "itemListElement": sites.slice(0, 20).map((s, i) => ({
      "@type": "ListItem", "position": i + 1, "name": s.name,
    }))
  } : null;

  return (
    <div className="min-h-screen bg-background pb-16" data-testid="programmatic-page">
      <SEOHead
        title={seo.title}
        description={seo.description}
        canonical={page.canonical}
        jsonLd={[breadcrumbJsonLd, itemListJsonLd].filter(Boolean)}
      />

      {/* Hero */}
      <section className="relative py-20 md:py-28 overflow-hidden">
        <div className="absolute inset-0 bg-[#050505]" />
        <div className="absolute inset-0 opacity-[0.05]" style={{
          backgroundImage: `linear-gradient(${accentColor}40 1px, transparent 1px), linear-gradient(90deg, ${accentColor}40 1px, transparent 1px)`,
          backgroundSize: "60px 60px"
        }} />
        <div className="relative z-10 container mx-auto max-w-6xl px-4">
          {/* Breadcrumb */}
          <div className="flex items-center gap-2 text-xs text-muted-foreground mb-6 flex-wrap" data-testid="prog-breadcrumb">
            {breadcrumb.map((b, i) => (
              <span key={i} className="flex items-center gap-2">
                {i > 0 && <ChevronRight className="w-3 h-3" />}
                {i < breadcrumb.length - 1 ? (
                  <Link to={b.url} className="hover:text-neon-green transition-colors">{b.name}</Link>
                ) : (
                  <span style={{ color: accentColor }}>{b.name}</span>
                )}
              </span>
            ))}
          </div>

          <div className="flex items-center gap-3 mb-5">
            {isCompanyPage && site_detail.logo_url && (
              <img src={site_detail.logo_url} alt={site_detail.name} className="w-14 h-14 rounded-xl border-2" style={{ borderColor: `${accentColor}40` }} />
            )}
            <div className="inline-flex items-center gap-2 rounded-full border px-4 py-1.5 text-xs font-semibold uppercase tracking-widest"
              style={{ borderColor: `${accentColor}30`, color: accentColor, background: `${accentColor}08` }}>
              <PageIcon className="w-3.5 h-3.5" />
              {page.combination_type.replace(/_/g, " ")}
            </div>
          </div>

          <h1 className="font-heading font-black text-3xl md:text-5xl lg:text-6xl uppercase tracking-tight leading-none mb-4" data-testid="prog-h1">
            <span className="text-white">{seo.h1.split(" ").slice(0, 2).join(" ")}</span>{" "}
            <span style={{ color: accentColor, textShadow: `0 0 30px ${accentColor}40` }}>
              {seo.h1.split(" ").slice(2).join(" ")}
            </span>
          </h1>
          <p className="text-base md:text-lg text-muted-foreground max-w-2xl">{seo.description}</p>

          <div className="flex flex-wrap gap-4 mt-6">
            <div className="flex items-center gap-2 text-sm"><Shield className="w-4 h-4" style={{ color: accentColor }} /><span className="font-medium">{sites.length}+ Site</span></div>
            <div className="flex items-center gap-2 text-sm"><Lock className="w-4 h-4" style={{ color: accentColor }} /><span className="font-medium">Guvenli</span></div>
            <div className="flex items-center gap-2 text-sm"><Zap className="w-4 h-4" style={{ color: accentColor }} /><span className="font-medium">2026 Guncel</span></div>
          </div>
        </div>
      </section>

      <div className="container mx-auto max-w-6xl px-4 mt-10">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main: Site List */}
          <div className="lg:col-span-2 space-y-3" data-testid="prog-site-list">
            {sites.map((site, i) => {
              const base = (site.slug || "").replace("-guncelgiris", "");
              return (
                <motion.div
                  key={site.id || i}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.03 }}
                  className="group rounded-xl border p-4 transition-all hover:border-opacity-40"
                  style={{ background: i < 3 ? `${accentColor}04` : "rgba(255,255,255,0.02)", borderColor: i < 3 ? `${accentColor}20` : "rgba(255,255,255,0.06)" }}
                  data-testid={`prog-site-${i}`}
                >
                  <div className="flex items-center gap-3">
                    <div className="shrink-0 w-9 h-9 rounded-lg flex items-center justify-center font-heading font-black text-base"
                      style={{ background: i < 3 ? `${accentColor}15` : "rgba(255,255,255,0.05)", color: i < 3 ? accentColor : "var(--muted-foreground)" }}>
                      {i + 1}
                    </div>
                    <img src={site.logo_url} alt={site.name} className="w-10 h-10 rounded-lg border border-white/10"
                      onError={(e) => { e.target.src = `https://placehold.co/80x80/1a1a1a/00FF87?text=${site.name?.charAt(0)}`; }} />
                    <div className="flex-1 min-w-0">
                      <h3 className="font-heading font-bold text-sm uppercase truncate">{site.name}</h3>
                      <div className="flex items-center gap-1.5 mt-0.5">
                        <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                        <span className="text-xs font-medium text-yellow-400">{site.rating || 4.5}</span>
                      </div>
                    </div>
                    <div className="text-right shrink-0">
                      <div className="font-heading font-black text-base" style={{ color: accentColor }}>{site.bonus_amount}</div>
                    </div>
                    <a href={site.affiliate_url} target="_blank" rel="noopener noreferrer"
                      className="shrink-0 hidden sm:flex items-center gap-1.5 px-4 py-2.5 rounded-lg font-heading font-bold uppercase text-xs transition-all hover:scale-105"
                      style={{ background: accentColor, color: "#000" }}
                      data-testid={`prog-cta-${i}`}>
                      <ExternalLink className="w-3.5 h-3.5" /> Siteye Git
                    </a>
                  </div>
                  {base && (
                    <div className="flex flex-wrap gap-2 mt-3 pt-3 border-t border-white/5">
                      <Link to={`/${base}/guncel-giris`} className="text-[11px] px-2 py-1 rounded-md bg-white/5 text-[#00F0FF] hover:bg-[#00F0FF]/10 transition-colors">Guncel Giris</Link>
                      <Link to={`/${base}/deneme-bonusu`} className="text-[11px] px-2 py-1 rounded-md bg-white/5 text-neon-green hover:bg-neon-green/10 transition-colors">Deneme Bonusu</Link>
                      <Link to={`/${base}/makaleler`} className="text-[11px] px-2 py-1 rounded-md bg-white/5 text-muted-foreground hover:bg-white/10 transition-colors">Makaleler</Link>
                      <a href={site.affiliate_url} target="_blank" rel="noopener noreferrer"
                        className="sm:hidden text-[11px] px-2 py-1 rounded-md font-bold" style={{ background: `${accentColor}20`, color: accentColor }}>
                        Siteye Git
                      </a>
                    </div>
                  )}
                </motion.div>
              );
            })}
            {sites.length === 0 && (
              <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-8 text-center text-muted-foreground">
                Bu kategoride henuz firma bulunmamaktadir.
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* CTA for company pages */}
            {isCompanyPage && (
              <div className="rounded-2xl border p-6 text-center" style={{ borderColor: `${accentColor}30`, background: `${accentColor}05` }} data-testid="prog-company-cta">
                <img src={site_detail.logo_url} alt={site_detail.name} className="w-14 h-14 rounded-xl mx-auto mb-3" />
                <h3 className="font-heading text-lg font-bold uppercase">{site_detail.name}</h3>
                <div className="font-heading text-2xl font-black mt-1" style={{ color: accentColor }}>{site_detail.bonus_amount}</div>
                <a href={site_detail.affiliate_url} target="_blank" rel="noopener noreferrer"
                  className="flex items-center justify-center gap-2 mt-3 w-full px-4 py-3 rounded-xl font-heading font-bold uppercase text-sm transition-all hover:scale-105"
                  style={{ background: accentColor, color: "#000" }}>
                  <ExternalLink className="w-4 h-4" /> Siteye Git
                </a>
              </div>
            )}

            {/* Related Hub Links */}
            {hub_links?.length > 0 && (
              <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-5" data-testid="prog-hub-links">
                <h3 className="font-heading text-base font-bold uppercase mb-3 flex items-center gap-2">
                  <Gift className="w-4 h-4" style={{ color: accentColor }} /> Ilgili Sayfalar
                </h3>
                <div className="space-y-1.5">
                  {hub_links.map((hub) => (
                    <Link key={hub.slug} to={hub.url}
                      className="flex items-center gap-2 text-sm p-2 rounded-lg hover:bg-white/5 transition-colors group">
                      <Globe className="w-3.5 h-3.5" style={{ color: accentColor }} />
                      <span className="group-hover:text-neon-green transition-colors text-muted-foreground truncate">{hub.title}</span>
                      <ChevronRight className="w-3 h-3 text-muted-foreground ml-auto" />
                    </Link>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Legal */}
      <div className="container mx-auto max-w-6xl px-4 mt-12">
        <div className="rounded-xl border border-yellow-500/20 bg-yellow-500/5 p-4 text-center text-xs text-muted-foreground">
          <AlertTriangle className="w-4 h-4 inline-block text-yellow-500 mr-1.5" />
          18+ | Kumar bagimliligi yardim hatti: 182. Bu sayfa bilgilendirme amaclidir.
        </div>
      </div>
    </div>
  );
}
