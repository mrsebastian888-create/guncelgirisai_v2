import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { motion } from "framer-motion";
import axios from "axios";
import {
  FileText, ChevronRight, Star, ExternalLink, Gift, Globe,
  AlertTriangle, Clock, Tag
} from "lucide-react";
import SEOHead from "@/components/SEOHead";
import { API } from "@/App";

export default function CompanyArticlesListPage() {
  const { companySlug } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    axios.get(`${API}/company-articles/${companySlug}`)
      .then(res => setData(res.data))
      .catch(e => setError(e.response?.status === 404 ? "Firma bulunamadi" : "Hata olustu"))
      .finally(() => setLoading(false));
  }, [companySlug]);

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center pt-20" data-testid="company-articles-loading">
      <div className="w-10 h-10 border-2 border-neon-green border-t-transparent rounded-full animate-spin" />
    </div>
  );

  if (error || !data) return (
    <div className="min-h-screen flex flex-col items-center justify-center pt-20 gap-4" data-testid="company-articles-error">
      <AlertTriangle className="w-16 h-16 text-yellow-500" />
      <h1 className="font-heading text-2xl">{error || "Bulunamadi"}</h1>
      <Link to="/" className="text-neon-green hover:underline">Ana Sayfaya Don</Link>
    </div>
  );

  const { site, articles, general_articles, sub_pages, hub_links, breadcrumb, seo } = data;

  const breadcrumbJsonLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": breadcrumb.map((b, i) => ({
      "@type": "ListItem", "position": i + 1, "name": b.name,
      "item": `https://guncelgiris.ai${b.url}`
    }))
  };

  const allArticles = [...articles, ...general_articles.map(a => ({ ...a, _isGeneral: true }))];

  return (
    <div className="min-h-screen bg-background pt-20 pb-16" data-testid="company-articles-list-page">
      <SEOHead title={seo.title} description={seo.description} canonical={seo.canonical} jsonLd={[breadcrumbJsonLd]} />

      {/* Breadcrumb */}
      <div className="container mx-auto max-w-6xl px-4 mb-6">
        <div className="flex items-center gap-2 text-xs text-muted-foreground flex-wrap" data-testid="articles-breadcrumb">
          {breadcrumb.map((b, i) => (
            <span key={i} className="flex items-center gap-2">
              {i > 0 && <ChevronRight className="w-3 h-3" />}
              {i < breadcrumb.length - 1 ? (
                <Link to={b.url} className="hover:text-neon-green transition-colors">{b.name}</Link>
              ) : (
                <span className="text-neon-green">{b.name}</span>
              )}
            </span>
          ))}
        </div>
      </div>

      {/* Hero */}
      <section className="relative overflow-hidden py-12 md:py-16">
        <div className="absolute inset-0 bg-[#050505]" />
        <div className="absolute inset-0 opacity-[0.04]" style={{
          backgroundImage: "linear-gradient(rgba(0,255,135,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(0,255,135,0.3) 1px, transparent 1px)",
          backgroundSize: "60px 60px"
        }} />
        <div className="relative z-10 container mx-auto max-w-6xl px-4">
          <div className="flex items-center gap-4 mb-4">
            <img src={site.logo_url} alt={site.name} className="w-14 h-14 rounded-xl border-2 border-neon-green/30" />
            <div>
              <span className="text-xs uppercase tracking-widest font-semibold px-2 py-0.5 rounded-full border border-neon-green/40 text-neon-green bg-neon-green/10">
                Makaleler
              </span>
              <h1 className="font-heading font-black text-2xl md:text-4xl uppercase tracking-tight mt-1" data-testid="articles-h1">
                <span className="text-white">{site.name}</span> <span className="text-neon-green">Makaleler</span>
              </h1>
            </div>
          </div>
          <p className="text-muted-foreground max-w-2xl">{seo.description}</p>
        </div>
      </section>

      <div className="container mx-auto max-w-6xl px-4 mt-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Articles */}
          <div className="lg:col-span-2 space-y-4" data-testid="articles-list">
            {allArticles.length === 0 && (
              <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-8 text-center">
                <FileText className="w-12 h-12 text-muted-foreground mx-auto mb-3" />
                <p className="text-muted-foreground">Henuz makale bulunmamaktadir.</p>
                <p className="text-xs text-muted-foreground mt-1">Firmaya ait makaleler yakinda eklenecektir.</p>
              </div>
            )}
            {allArticles.map((article, i) => {
              const url = article._isGeneral
                ? `/makale/${article.slug}`
                : `/${companySlug}/makaleler/${article.slug}`;
              return (
                <motion.div
                  key={article.id || i}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.04 }}
                >
                  <Link
                    to={url}
                    className="group flex gap-4 p-5 rounded-xl border transition-all hover:border-neon-green/25"
                    style={{ background: "rgba(255,255,255,0.02)", borderColor: "rgba(255,255,255,0.06)" }}
                    data-testid={`article-card-${i}`}
                  >
                    <div className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
                      style={{ background: "rgba(0,255,135,0.1)" }}>
                      <FileText className="w-5 h-5 text-neon-green" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-heading font-bold text-sm uppercase group-hover:text-neon-green transition-colors line-clamp-2">
                        {article.title}
                      </h3>
                      {article.excerpt && (
                        <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{article.excerpt}</p>
                      )}
                      <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                        {article.article_type && (
                          <span className="flex items-center gap-1"><Tag className="w-3 h-3" /> {article.article_type}</span>
                        )}
                        {article.created_at && (
                          <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {new Date(article.created_at).toLocaleDateString("tr-TR")}</span>
                        )}
                        {article._isGeneral && (
                          <span className="px-1.5 py-0.5 rounded bg-white/5 text-[#00F0FF]">Genel</span>
                        )}
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-muted-foreground self-center flex-shrink-0" />
                  </Link>
                </motion.div>
              );
            })}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* CTA */}
            <div className="rounded-2xl border border-neon-green/30 bg-neon-green/5 p-6 text-center" data-testid="articles-sidebar-cta">
              <img src={site.logo_url} alt={site.name} className="w-14 h-14 rounded-xl mx-auto mb-3" />
              <h3 className="font-heading text-lg font-bold uppercase">{site.name}</h3>
              <div className="font-heading text-2xl font-black text-neon-green mt-1">{site.bonus_amount}</div>
              <a href={site.affiliate_url} target="_blank" rel="noopener noreferrer"
                className="flex items-center justify-center gap-2 mt-3 w-full px-4 py-3 rounded-xl font-heading font-bold uppercase text-sm bg-neon-green text-black hover:scale-105 transition-all"
                style={{ boxShadow: "0 0 20px rgba(0,255,135,0.3)" }}>
                <ExternalLink className="w-4 h-4" /> Siteye Git
              </a>
            </div>

            {/* Company Pages */}
            <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-5" data-testid="articles-sub-pages">
              <h3 className="font-heading text-base font-bold uppercase mb-3 flex items-center gap-2">
                <Globe className="w-4 h-4 text-[#00F0FF]" /> {site.name} Sayfalari
              </h3>
              <div className="space-y-1.5">
                {sub_pages.slice(0, 6).map((sp) => (
                  <Link key={sp.page_type} to={sp.url}
                    className="flex items-center gap-2 text-sm p-2 rounded-lg hover:bg-white/5 transition-colors group">
                    <Globe className="w-3.5 h-3.5" style={{ color: sp.cluster === "bonus-guide" ? "#00FF87" : "#00F0FF" }} />
                    <span className="group-hover:text-neon-green transition-colors text-muted-foreground truncate">{sp.label}</span>
                  </Link>
                ))}
              </div>
            </div>

            {/* Hub Links */}
            <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-5" data-testid="articles-hub-links">
              <h3 className="font-heading text-base font-bold uppercase mb-3 flex items-center gap-2">
                <Gift className="w-4 h-4 text-neon-green" /> Rehberler
              </h3>
              <div className="space-y-1.5">
                {(hub_links || []).slice(0, 5).map((hub) => (
                  <Link key={hub.slug} to={hub.url}
                    className="flex items-center gap-2 text-sm p-2 rounded-lg hover:bg-white/5 transition-colors group">
                    <Gift className="w-3.5 h-3.5 text-neon-green" />
                    <span className="group-hover:text-neon-green transition-colors text-muted-foreground">{hub.title}</span>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
