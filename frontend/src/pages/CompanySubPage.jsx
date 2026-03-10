import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import axios from "axios";
import {
  ExternalLink, Shield, Gift, ChevronRight, Star, Globe,
  CreditCard, Smartphone, AlertTriangle, Award, ArrowRight
} from "lucide-react";
import SEOHead from "@/components/SEOHead";
import CompanyGuideTemplate from "@/components/templates/CompanyGuideTemplate";
import BonusGuideTemplate from "@/components/templates/BonusGuideTemplate";
import { API } from "@/App";

const CLUSTER_COLORS = {
  "company-guide": "#00F0FF",
  "bonus-guide": "#00FF87",
};

const PAGE_TYPE_ICONS = {
  "guncel-giris": Globe,
  "guncel-adresi": Globe,
  "yeni-giris-adresi": ArrowRight,
  "mobil-giris": Smartphone,
  "deneme-bonusu": Gift,
  "deneme-bonusu-2026": Gift,
  "hosgeldin-bonusu": Award,
  "yatirimsiz-deneme-bonusu": Gift,
  "bonus-sartlari": Shield,
  "odeme-yontemleri": CreditCard,
};

export default function CompanySubPage() {
  const { companySlug, pageType } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await axios.get(`${API}/firma-sub/${companySlug}/${pageType}`);
        setData(res.data);
      } catch (e) {
        setError(e.response?.status === 404 ? "Sayfa bulunamadi" : "Bir hata olustu");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [companySlug, pageType]);

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center pt-20" data-testid="company-sub-loading">
      <div className="w-10 h-10 border-2 border-neon-green border-t-transparent rounded-full animate-spin" />
    </div>
  );

  if (error || !data) return (
    <div className="min-h-screen flex flex-col items-center justify-center pt-20 gap-4" data-testid="company-sub-error">
      <AlertTriangle className="w-16 h-16 text-yellow-500" />
      <h1 className="font-heading text-2xl">{error || "Sayfa bulunamadi"}</h1>
      <Link to="/" className="text-neon-green hover:underline">Ana Sayfaya Don</Link>
    </div>
  );

  const { site, seo, breadcrumb, internal_links, similar_same_page, cluster, template, faq, last_updated } = data;
  const accentColor = CLUSTER_COLORS[cluster] || "#00FF87";
  const baseSlug = companySlug;

  // JSON-LD: BreadcrumbList
  const breadcrumbJsonLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": breadcrumb.map((b, i) => ({
      "@type": "ListItem",
      "position": i + 1,
      "name": b.name,
      "item": `https://guncelgiris.ai${b.url}`
    }))
  };

  // JSON-LD: FAQPage
  const faqJsonLd = faq?.length > 0 ? {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": faq.map(item => ({
      "@type": "Question",
      "name": item.question,
      "acceptedAnswer": {
        "@type": "Answer",
        "text": item.answer
      }
    }))
  } : null;

  // JSON-LD: Article
  const articleJsonLd = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": seo.h1,
    "description": seo.description,
    "url": seo.canonical,
    "datePublished": "2026-01-01T00:00:00Z",
    "dateModified": last_updated || new Date().toISOString(),
    "author": { "@type": "Organization", "name": "Guncel Giris" },
    "publisher": {
      "@type": "Organization",
      "name": "Guncel Giris",
      "url": "https://guncelgiris.ai"
    },
    "mainEntityOfPage": { "@type": "WebPage", "@id": seo.canonical }
  };

  const jsonLdSchemas = [breadcrumbJsonLd, faqJsonLd, articleJsonLd].filter(Boolean);

  return (
    <div className="min-h-screen bg-background pt-20 pb-16" data-testid="company-sub-page">
      <SEOHead
        title={seo.title}
        description={seo.description}
        canonical={seo.canonical}
        type="article"
        article={{ modifiedTime: last_updated }}
        jsonLd={jsonLdSchemas}
      />

      {/* Breadcrumb */}
      <div className="container mx-auto max-w-6xl px-4 mb-6" data-testid="company-sub-breadcrumb">
        <div className="flex items-center gap-2 text-xs text-muted-foreground flex-wrap">
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
      </div>

      {/* Hero */}
      <section className="relative overflow-hidden py-12 md:py-16" data-testid="company-sub-hero">
        <div className="absolute inset-0 bg-[#050505]" />
        <div className="absolute inset-0 opacity-[0.04]" style={{
          backgroundImage: `linear-gradient(${accentColor}4D 1px, transparent 1px), linear-gradient(90deg, ${accentColor}4D 1px, transparent 1px)`,
          backgroundSize: "60px 60px"
        }} />
        <div className="relative z-10 container mx-auto max-w-6xl px-4">
          <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
            <div className="flex items-center gap-4">
              <img src={site.logo_url} alt={site.name} className="w-16 h-16 rounded-xl border-2" style={{ borderColor: `${accentColor}50` }} />
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs uppercase tracking-widest font-semibold px-2 py-0.5 rounded-full border"
                    style={{ borderColor: `${accentColor}40`, color: accentColor, background: `${accentColor}10` }}>
                    {cluster === "bonus-guide" ? "Bonus Rehberi" : "Firma Rehberi"}
                  </span>
                </div>
                <h1 className="font-heading font-black text-2xl md:text-4xl uppercase tracking-tight" data-testid="company-sub-h1">
                  <span className="text-white">{site.name}</span>{" "}
                  <span style={{ color: accentColor }}>{seo.h1.replace(site.name, "").trim()}</span>
                </h1>
              </div>
            </div>
            <div className="md:ml-auto flex gap-3">
              <a href={site.affiliate_url} target="_blank" rel="noopener noreferrer" data-testid="company-sub-cta"
                className="inline-flex items-center gap-2 rounded-xl px-6 py-3 font-heading font-bold uppercase text-sm transition-all hover:scale-105"
                style={{ background: accentColor, color: "#000", boxShadow: `0 0 24px ${accentColor}40` }}>
                <ExternalLink className="w-4 h-4" /> Siteye Git
              </a>
              <Link to={`/${site.slug || `${baseSlug}-guncelgiris`}`} data-testid="company-sub-profile-link"
                className="inline-flex items-center gap-2 rounded-xl px-6 py-3 font-heading font-bold uppercase text-sm border transition-all hover:bg-white/5"
                style={{ borderColor: "rgba(255,255,255,0.15)" }}>
                Firma Profili
              </Link>
            </div>
          </div>
        </div>
      </section>

      <div className="container mx-auto max-w-6xl px-4 mt-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content - Template-based */}
          <div className="lg:col-span-2">
            {template === "bonus-guide" ? (
              <BonusGuideTemplate data={data} />
            ) : (
              <CompanyGuideTemplate data={data} />
            )}

            {/* Cluster A: Company Guide Internal Links */}
            {internal_links.company_guide?.length > 0 && (
              <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-6 mt-6" data-testid="company-sub-guide-links">
                <h3 className="font-heading text-lg font-bold uppercase mb-4 flex items-center gap-2">
                  <Globe className="w-5 h-5 text-[#00F0FF]" /> {site.name} Firma Rehberi
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {internal_links.company_guide.map((link) => (
                    <Link key={link.page_type} to={link.url} data-testid={`company-guide-link-${link.page_type}`}
                      className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.03] border border-white/5 hover:border-[#00F0FF]/30 transition-all group">
                      <div className="w-8 h-8 rounded-lg bg-[#00F0FF]/10 flex items-center justify-center flex-shrink-0">
                        <Globe className="w-4 h-4 text-[#00F0FF]" />
                      </div>
                      <span className="text-sm font-medium group-hover:text-[#00F0FF] transition-colors">{link.label}</span>
                      <ChevronRight className="w-4 h-4 text-muted-foreground ml-auto" />
                    </Link>
                  ))}
                </div>
              </div>
            )}

            {/* Cluster B: Bonus Guide Internal Links */}
            {internal_links.bonus_guide?.length > 0 && (
              <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-6 mt-6" data-testid="company-sub-bonus-links">
                <h3 className="font-heading text-lg font-bold uppercase mb-4 flex items-center gap-2">
                  <Gift className="w-5 h-5 text-neon-green" /> {site.name} Bonus Rehberi
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {internal_links.bonus_guide.map((link) => (
                    <Link key={link.page_type} to={link.url} data-testid={`bonus-guide-link-${link.page_type}`}
                      className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.03] border border-white/5 hover:border-neon-green/30 transition-all group">
                      <div className="w-8 h-8 rounded-lg bg-neon-green/10 flex items-center justify-center flex-shrink-0">
                        <Gift className="w-4 h-4 text-neon-green" />
                      </div>
                      <span className="text-sm font-medium group-hover:text-neon-green transition-colors">{link.label}</span>
                      <ChevronRight className="w-4 h-4 text-muted-foreground ml-auto" />
                    </Link>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* CTA Card */}
            <div className="rounded-2xl border p-6 text-center sticky top-24" style={{ borderColor: `${accentColor}30`, background: `${accentColor}05` }} data-testid="company-sub-sidebar-cta">
              <img src={site.logo_url} alt={site.name} className="w-16 h-16 rounded-xl mx-auto mb-3" />
              <h3 className="font-heading text-lg font-bold uppercase">{site.name}</h3>
              <div className="font-heading text-3xl font-black mt-2" style={{ color: accentColor }}>{site.bonus_amount}</div>
              <div className="flex items-center justify-center gap-1 mt-1">
                <Star className="w-3.5 h-3.5 fill-yellow-400 text-yellow-400" />
                <span className="text-sm font-medium text-yellow-400">{site.rating || 4.5}</span>
              </div>
              <a href={site.affiliate_url} target="_blank" rel="noopener noreferrer" data-testid="company-sub-sidebar-cta-btn"
                className="flex items-center justify-center gap-2 mt-4 w-full px-6 py-3.5 rounded-xl font-heading font-bold uppercase tracking-wide text-sm transition-all hover:scale-105"
                style={{ background: accentColor, color: "#000", boxShadow: `0 0 24px ${accentColor}40` }}>
                <ExternalLink className="w-4 h-4" /> Siteye Git
              </a>
              <p className="text-[11px] text-muted-foreground mt-3">18+ | Sorumlu oyun oynayiniz</p>
            </div>

            {/* Similar Firms Same Page */}
            {similar_same_page?.length > 0 && (
              <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-5" data-testid="company-sub-similar">
                <h3 className="font-heading text-base font-bold uppercase mb-3">Benzer Siteler</h3>
                <div className="space-y-2">
                  {similar_same_page.map((s) => (
                    <Link key={s.url} to={s.url} data-testid={`similar-link-${s.name}`}
                      className="flex items-center gap-3 p-2.5 rounded-xl hover:bg-white/5 transition-all group">
                      <img src={s.logo_url} alt={s.name} className="w-8 h-8 rounded-lg" />
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium truncate group-hover:text-neon-green">{s.name}</div>
                        <div className="text-xs" style={{ color: accentColor }}>{s.bonus_amount}</div>
                      </div>
                      <ChevronRight className="w-4 h-4 text-muted-foreground" />
                    </Link>
                  ))}
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
          18+ | Kumar bagimliligi yardim hatti: 182. Bu sayfa bilgilendirme amaclidir.
        </div>
      </div>
    </div>
  );
}
