import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { motion } from "framer-motion";
import axios from "axios";
import {
  FileText, ChevronRight, Star, ExternalLink, Gift, Globe,
  AlertTriangle, Clock, User, Tag, Eye, Share2, CreditCard, Award
} from "lucide-react";
import SEOHead from "@/components/SEOHead";
import { API } from "@/App";

export default function CompanyArticlePage() {
  const { companySlug, articleSlug } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    axios.get(`${API}/company-articles/${companySlug}/${articleSlug}`)
      .then(res => setData(res.data))
      .catch(e => setError(e.response?.status === 404 ? "Makale bulunamadi" : "Hata olustu"))
      .finally(() => setLoading(false));
  }, [companySlug, articleSlug]);

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center pt-20" data-testid="company-article-loading">
      <div className="w-10 h-10 border-2 border-neon-green border-t-transparent rounded-full animate-spin" />
    </div>
  );

  if (error || !data) return (
    <div className="min-h-screen flex flex-col items-center justify-center pt-20 gap-4" data-testid="company-article-error">
      <AlertTriangle className="w-16 h-16 text-yellow-500" />
      <h1 className="font-heading text-2xl">{error || "Makale bulunamadi"}</h1>
      <Link to="/" className="text-neon-green hover:underline">Ana Sayfaya Don</Link>
    </div>
  );

  const { site, article, related_articles, related_sub_pages, related_hubs, similar_company_links, breadcrumb, seo } = data;

  const breadcrumbJsonLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": breadcrumb.map((b, i) => ({
      "@type": "ListItem", "position": i + 1, "name": b.name,
      "item": `https://guncelgiris.ai${b.url}`
    }))
  };

  const articleJsonLd = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": seo.title,
    "description": seo.description,
    "datePublished": article.created_at,
    "dateModified": article.updated_at || article.created_at,
    "author": { "@type": "Person", "name": article.author || "Admin" },
    "publisher": {
      "@type": "Organization", "name": "guncelgiris.ai",
      "logo": { "@type": "ImageObject", "url": "https://guncelgiris.ai/logo.png" }
    },
    "mainEntityOfPage": { "@type": "WebPage", "@id": seo.canonical },
  };

  return (
    <div className="min-h-screen bg-background pt-20 pb-16" data-testid="company-article-page">
      <SEOHead title={seo.title} description={seo.description} canonical={seo.canonical} type="article"
        article={{ publishedTime: article.created_at, modifiedTime: article.updated_at, author: article.author }}
        jsonLd={[breadcrumbJsonLd, articleJsonLd]} />

      {/* Breadcrumb */}
      <div className="container mx-auto max-w-6xl px-4 mb-6">
        <div className="flex items-center gap-2 text-xs text-muted-foreground flex-wrap" data-testid="article-breadcrumb">
          {breadcrumb.map((b, i) => (
            <span key={i} className="flex items-center gap-2">
              {i > 0 && <ChevronRight className="w-3 h-3" />}
              {i < breadcrumb.length - 1 ? (
                <Link to={b.url} className="hover:text-neon-green transition-colors">{b.name}</Link>
              ) : (
                <span className="text-neon-green truncate max-w-[200px]">{b.name}</span>
              )}
            </span>
          ))}
        </div>
      </div>

      {/* Hero */}
      <section className="relative overflow-hidden py-10 md:py-14">
        <div className="absolute inset-0 bg-[#050505]" />
        <div className="absolute inset-0 opacity-[0.04]" style={{
          backgroundImage: "linear-gradient(rgba(0,255,135,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(0,255,135,0.3) 1px, transparent 1px)",
          backgroundSize: "60px 60px"
        }} />
        <div className="relative z-10 container mx-auto max-w-4xl px-4">
          <div className="flex items-center gap-3 mb-4">
            <img src={site.logo_url} alt={site.name} className="w-10 h-10 rounded-lg border border-neon-green/30" />
            <Link to={`/${site.base_slug}`} className="text-sm font-medium hover:text-neon-green transition-colors">{site.name}</Link>
            {article.article_type && (
              <span className="text-xs px-2 py-0.5 rounded-full border border-neon-green/30 text-neon-green bg-neon-green/10">
                {article.article_type}
              </span>
            )}
          </div>
          <h1 className="font-heading font-black text-2xl md:text-4xl uppercase tracking-tight leading-tight" data-testid="article-h1">
            {article.title}
          </h1>
          <div className="flex flex-wrap items-center gap-4 mt-4 text-xs text-muted-foreground">
            <span className="flex items-center gap-1"><User className="w-3.5 h-3.5" /> {article.author || "Admin"}</span>
            <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5" /> {new Date(article.created_at).toLocaleDateString("tr-TR", { day: "numeric", month: "long", year: "numeric" })}</span>
            <span className="flex items-center gap-1"><Eye className="w-3.5 h-3.5" /> {article.view_count} goruntulenme</span>
          </div>
          {article.tags?.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-3">
              {article.tags.map((tag, i) => (
                <span key={i} className="text-xs px-2 py-0.5 rounded border border-white/10 text-muted-foreground">
                  <Tag className="w-3 h-3 inline mr-1" />{tag}
                </span>
              ))}
            </div>
          )}
        </div>
      </section>

      <div className="container mx-auto max-w-6xl px-4 mt-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Article Body */}
            <motion.div
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              className="rounded-2xl border border-white/10 bg-white/[0.02] p-6 md:p-8"
              data-testid="article-content"
            >
              {article.excerpt && (
                <p className="text-base text-muted-foreground mb-6 leading-relaxed border-l-4 border-neon-green pl-4 italic">
                  {article.excerpt}
                </p>
              )}
              <div
                className="prose prose-invert prose-sm max-w-none
                  prose-headings:font-heading prose-headings:uppercase prose-headings:tracking-tight
                  prose-h2:text-xl prose-h2:mt-6 prose-h2:mb-3
                  prose-p:text-muted-foreground prose-p:leading-relaxed
                  prose-a:text-neon-green prose-a:no-underline hover:prose-a:underline
                  prose-li:marker:text-neon-green prose-strong:text-foreground"
                dangerouslySetInnerHTML={{ __html: article.content }}
              />
            </motion.div>

            {/* Related Company Pages — internal linking */}
            {related_sub_pages?.length > 0 && (
              <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="article-related-pages">
                <h3 className="font-heading text-lg font-bold uppercase mb-4 flex items-center gap-2">
                  <Globe className="w-5 h-5 text-[#00F0FF]" /> {site.name} Sayfalari
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {related_sub_pages.map((sp) => (
                    <Link key={sp.page_type} to={sp.url}
                      className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.03] border border-white/5 hover:border-[#00F0FF]/30 transition-all group"
                      data-testid={`article-sub-link-${sp.page_type}`}>
                      <Globe className="w-4 h-4 text-[#00F0FF] flex-shrink-0" />
                      <span className="text-sm group-hover:text-[#00F0FF] transition-colors">{sp.label}</span>
                      <ChevronRight className="w-3 h-3 text-muted-foreground ml-auto" />
                    </Link>
                  ))}
                </div>
              </div>
            )}

            {/* Related Hub Pages */}
            {related_hubs?.length > 0 && (
              <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="article-related-hubs">
                <h3 className="font-heading text-lg font-bold uppercase mb-4 flex items-center gap-2">
                  <Gift className="w-5 h-5 text-neon-green" /> Ilgili Rehberler
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                  {related_hubs.map((hub) => (
                    <Link key={hub.slug} to={hub.url}
                      className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.03] border border-white/5 hover:border-neon-green/30 transition-all group">
                      <Gift className="w-4 h-4 text-neon-green flex-shrink-0" />
                      <span className="text-sm group-hover:text-neon-green transition-colors">{hub.title}</span>
                      <ChevronRight className="w-3 h-3 text-muted-foreground ml-auto" />
                    </Link>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* CTA */}
            <div className="rounded-2xl border border-neon-green/30 bg-neon-green/5 p-6 text-center sticky top-24" data-testid="article-sidebar-cta">
              <img src={site.logo_url} alt={site.name} className="w-14 h-14 rounded-xl mx-auto mb-3" />
              <h3 className="font-heading text-lg font-bold uppercase">{site.name}</h3>
              <div className="font-heading text-2xl font-black text-neon-green mt-1">{site.bonus_amount}</div>
              <a href={site.affiliate_url} target="_blank" rel="noopener noreferrer"
                className="flex items-center justify-center gap-2 mt-3 w-full px-4 py-3 rounded-xl font-heading font-bold uppercase text-sm bg-neon-green text-black hover:scale-105 transition-all">
                <ExternalLink className="w-4 h-4" /> Siteye Git
              </a>
            </div>

            {/* Related Articles */}
            {related_articles?.length > 0 && (
              <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-5" data-testid="article-related-articles">
                <h3 className="font-heading text-base font-bold uppercase mb-3">Diger Makaleler</h3>
                <div className="space-y-2">
                  {related_articles.map((ra) => (
                    <Link key={ra.id || ra.slug} to={`/${companySlug}/makaleler/${ra.slug}`}
                      className="flex items-start gap-3 p-2.5 rounded-lg hover:bg-white/5 transition-all group">
                      <FileText className="w-4 h-4 text-neon-green flex-shrink-0 mt-0.5" />
                      <div className="min-w-0">
                        <div className="text-sm font-medium group-hover:text-neon-green transition-colors line-clamp-2">{ra.title}</div>
                        <div className="text-xs text-muted-foreground">{ra.created_at ? new Date(ra.created_at).toLocaleDateString("tr-TR") : ""}</div>
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            )}

            {/* Similar Companies */}
            {similar_company_links?.length > 0 && (
              <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-5" data-testid="article-similar-companies">
                <h3 className="font-heading text-base font-bold uppercase mb-3">Benzer Firmalar</h3>
                <div className="space-y-2">
                  {similar_company_links.map((sc) => (
                    <Link key={sc.name} to={sc.articles_url}
                      className="flex items-center gap-3 p-2.5 rounded-lg hover:bg-white/5 transition-all group">
                      <img src={sc.logo_url} alt={sc.name} className="w-8 h-8 rounded-lg" />
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium truncate group-hover:text-neon-green">{sc.name}</div>
                        <div className="text-xs text-neon-green">{sc.bonus_amount}</div>
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
