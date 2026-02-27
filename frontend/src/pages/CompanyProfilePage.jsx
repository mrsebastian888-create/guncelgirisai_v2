import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import axios from "axios";
import { AlertTriangle, BarChart3, Building2, ChevronRight, ExternalLink, Globe, Layers, Sparkles, Users } from "lucide-react";
import SEOHead from "@/components/SEOHead";

const API = process.env.REACT_APP_BACKEND_URL + "/api";

const formatVisits = (n) => {
  const value = Number(n || 0);
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(1)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
  return `${value}`;
};

export default function CompanyProfilePage() {
  const { slug } = useParams();
  const [payload, setPayload] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const run = async () => {
      setLoading(true);
      setError("");
      try {
        const res = await axios.get(`${API}/companies/slug/${slug}`);
        setPayload(res.data);
      } catch {
        setError("Şirket profili bulunamadı");
      } finally {
        setLoading(false);
      }
    };
    run();
  }, [slug]);

  const jsonLd = useMemo(() => {
    if (!payload?.company) return null;
    const c = payload.company;
    return {
      "@context": "https://schema.org",
      "@type": "Organization",
      name: c.name,
      url: `https://${c.domain}`,
      description: c.description_short,
      foundingDate: c.founded_year,
      sameAs: Object.values(c.social_links_json || {}).filter(Boolean),
    };
  }, [payload]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center pt-20" data-testid="company-profile-loading">
        <div className="w-10 h-10 border-2 border-neon-green border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error || !payload?.company) {
    return (
      <div className="min-h-screen pt-24 flex flex-col items-center justify-center gap-4" data-testid="company-profile-error-state">
        <AlertTriangle className="w-14 h-14 text-yellow-500" />
        <h1 className="font-heading text-2xl">{error || "Profil açılamadı"}</h1>
        <Link to="/" className="text-neon-green hover:underline" data-testid="company-profile-error-home-link">Ana Sayfaya Dön</Link>
      </div>
    );
  }

  const company = payload.company;
  const alternatives = payload.alternatives || [];

  return (
    <div className="min-h-screen bg-background pt-20 pb-16" data-testid="company-profile-page">
      <SEOHead
        title={company.seo_title || `${company.name} Analizi | Company Intelligence`}
        description={company.seo_description || company.description_short}
        canonical={payload.canonical_url}
        jsonLd={jsonLd}
      />

      <section className="container mx-auto max-w-6xl px-4 space-y-6">
        <div className="flex items-center gap-2 text-xs text-muted-foreground" data-testid="company-profile-breadcrumb">
          <Link to="/" className="hover:text-neon-green" data-testid="company-profile-home-link">Ana Sayfa</Link>
          <ChevronRight className="w-3 h-3" />
          <span className="text-neon-green" data-testid="company-profile-current-link">{company.name}</span>
        </div>

        <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-6 md:p-8" data-testid="company-profile-hero">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-6">
            <div className="flex items-center gap-4 min-w-0">
              <img src={company.logo_url} alt={company.name} className="w-16 h-16 rounded-xl border border-neon-green/30" data-testid="company-profile-logo" />
              <div className="min-w-0">
                <h1 className="font-heading font-black text-3xl md:text-4xl uppercase truncate" data-testid="company-profile-name">{company.name}</h1>
                <p className="text-sm text-muted-foreground mt-1" data-testid="company-profile-category">{company.category_id} • {company.subcategory_id}</p>
                <div className="flex flex-wrap gap-2 mt-3" data-testid="company-profile-tags">
                  {(company.tags_json || []).slice(0, 6).map((tag, i) => (
                    <span key={`${tag}-${i}`} className="text-xs px-2 py-1 rounded-full border border-white/10 bg-white/[0.03]">#{tag}</span>
                  ))}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3 text-sm min-w-[260px]" data-testid="company-profile-quick-facts">
              <div className="rounded-lg border border-white/10 bg-black/20 p-3"><p className="text-xs text-muted-foreground">Founded</p><p className="font-semibold" data-testid="company-founded-year">{company.founded_year}</p></div>
              <div className="rounded-lg border border-white/10 bg-black/20 p-3"><p className="text-xs text-muted-foreground">Employee</p><p className="font-semibold" data-testid="company-employee-range">{company.employee_range}</p></div>
              <div className="rounded-lg border border-white/10 bg-black/20 p-3"><p className="text-xs text-muted-foreground">Revenue</p><p className="font-semibold" data-testid="company-revenue-range">{company.revenue_range}</p></div>
              <div className="rounded-lg border border-white/10 bg-black/20 p-3"><p className="text-xs text-muted-foreground">Score</p><p className="font-semibold text-neon-green" data-testid="company-intelligence-score">{company.intelligence_score}</p></div>
            </div>
          </div>

          <p className="mt-5 text-sm text-muted-foreground" data-testid="company-profile-short-description">{company.description_short}</p>
          <div className="flex flex-wrap gap-3 mt-5">
            <a href={`https://${company.domain}`} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 px-5 py-3 rounded-xl bg-neon-green text-black font-heading font-bold uppercase text-xs" data-testid="company-profile-visit-site-button">
              <ExternalLink className="w-4 h-4" /> Siteyi Ziyaret Et
            </a>
            <a href={`https://${company.domain}`} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-2 px-5 py-3 rounded-xl border border-white/15 text-sm" data-testid="company-profile-open-domain-link">
              <Globe className="w-4 h-4" /> {company.domain}
            </a>
          </div>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3" data-testid="company-metrics-cards">
          {[
            { label: "Estimated Visits", value: formatVisits(company.estimated_visits), testId: "company-metric-visits" },
            { label: "Bounce Rate", value: `${Math.round((company.bounce_rate || 0) * 100)}%`, testId: "company-metric-bounce" },
            { label: "Pages/Visit", value: company.pages_per_visit, testId: "company-metric-pages-per-visit" },
            { label: "Avg Duration", value: company.avg_visit_duration, testId: "company-metric-avg-duration" },
          ].map((m) => (
            <div key={m.label} className="rounded-xl border border-white/10 bg-white/[0.02] p-4">
              <p className="text-xs text-muted-foreground">{m.label}</p>
              <p className="mt-1 text-xl font-heading font-bold" data-testid={m.testId}>{m.value}</p>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="rounded-xl border border-white/10 bg-white/[0.02] p-4" data-testid="company-rank-section">
            <h2 className="font-heading text-lg mb-3">Ranking</h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-muted-foreground">Global Rank</span><strong data-testid="company-global-rank">#{company.global_rank || "-"}</strong></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Country Rank</span><strong data-testid="company-country-rank">#{company.country_rank || "-"}</strong></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Category Rank</span><strong data-testid="company-category-rank">#{company.category_rank || "-"}</strong></div>
            </div>
          </div>

          <div className="rounded-xl border border-white/10 bg-white/[0.02] p-4" data-testid="company-channels-section">
            <h2 className="font-heading text-lg mb-3">Service Channels</h2>
            <div className="flex flex-wrap gap-2">
              {(company.channels_json || []).map((ch, i) => (
                <span key={`${ch}-${i}`} className="px-2.5 py-1 rounded-full text-xs border border-[#00F0FF]/40 text-[#00F0FF]" data-testid={`company-channel-badge-${i}`}>{ch}</span>
              ))}
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-white/10 bg-white/[0.02] p-4" data-testid="company-tech-stack-section">
          <h2 className="font-heading text-lg mb-3">Technology Stack</h2>
          <div className="flex flex-wrap gap-2">
            {(company.technologies_json || []).slice(0, 20).map((tech, i) => (
              <span key={`${tech}-${i}`} className="px-2.5 py-1 rounded-md text-xs border border-white/15" data-testid={`company-tech-badge-${i}`}>{tech}</span>
            ))}
          </div>
        </div>

        <div className="rounded-xl border border-white/10 bg-white/[0.02] p-5" data-testid="company-about-section">
          <h2 className="font-heading text-xl mb-3 flex items-center gap-2"><BarChart3 className="w-5 h-5" /> Company Analysis</h2>
          <div className="text-sm leading-relaxed text-muted-foreground whitespace-pre-wrap" data-testid="company-long-description">
            {company.description_long}
          </div>
        </div>

        {alternatives.length > 0 && (
          <div className="rounded-xl border border-white/10 bg-white/[0.02] p-5" data-testid="company-alternatives-section">
            <h2 className="font-heading text-xl mb-4 flex items-center gap-2"><Sparkles className="w-5 h-5" /> Alternatives</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {alternatives.map((alt) => (
                <Link key={alt.id} to={`/companies/${alt.slug}`} className="rounded-lg border border-white/10 p-3 hover:border-neon-green/40 transition-colors" data-testid={`company-alternative-card-${alt.id}`}>
                  <div className="flex items-center gap-3">
                    <img src={alt.logo_url} alt={alt.name} className="w-9 h-9 rounded-md" />
                    <div className="min-w-0">
                      <p className="font-semibold truncate">{alt.name}</p>
                      <p className="text-xs text-muted-foreground truncate">{alt.category_id}</p>
                    </div>
                  </div>
                  <div className="flex justify-between text-xs mt-2">
                    <span className="text-muted-foreground">Visits</span>
                    <span className="text-neon-green">{formatVisits(alt.estimated_visits)}</span>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}