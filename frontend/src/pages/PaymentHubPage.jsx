import { useState, useEffect } from "react";
import { useLocation, Link } from "react-router-dom";
import { motion } from "framer-motion";
import axios from "axios";
import {
  CreditCard, Star, Shield, ExternalLink, ChevronRight, Gift,
  Globe, AlertTriangle, Smartphone, Lock, Banknote
} from "lucide-react";
import SEOHead from "@/components/SEOHead";
import { API } from "@/App";

const PAYMENT_ICONS = {
  "odeme-yontemleri": CreditCard,
  "mobil-odeme-ile-bahis": Smartphone,
  "kredi-karti-ile-bahis": CreditCard,
  "papel-ile-bahis": Banknote,
  "havale-ile-bahis": Banknote,
  "kripto-ile-bahis": Globe,
  "bddk-onayli-odeme-yontemleri": Shield,
  "guvenli-odeme-yontemleri": Lock,
};

export default function PaymentHubPage() {
  const location = useLocation();
  const hubSlug = location.pathname.replace(/^\//, "");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await axios.get(`${API}/hub/payment/${hubSlug}`);
        setData(res.data);
      } catch (e) {
        setError(e.response?.status === 404 ? "Sayfa bulunamadi" : "Bir hata olustu");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [hubSlug]);

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center pt-20" data-testid="payment-hub-loading">
      <div className="w-10 h-10 border-2 border-[#00F0FF] border-t-transparent rounded-full animate-spin" />
    </div>
  );

  if (error || !data) return (
    <div className="min-h-screen flex flex-col items-center justify-center pt-20 gap-4" data-testid="payment-hub-error">
      <AlertTriangle className="w-16 h-16 text-yellow-500" />
      <h1 className="font-heading text-2xl">{error || "Sayfa bulunamadi"}</h1>
      <Link to="/" className="text-neon-green hover:underline">Ana Sayfaya Don</Link>
    </div>
  );

  const { seo, breadcrumb, sites, company_links, related_hubs } = data;
  const HubIcon = PAYMENT_ICONS[hubSlug] || CreditCard;

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

  return (
    <div className="min-h-screen bg-background pb-16" data-testid="payment-hub-page">
      <SEOHead
        title={seo.title}
        description={seo.description}
        canonical={seo.canonical}
        jsonLd={[breadcrumbJsonLd]}
      />

      {/* Hero */}
      <section className="relative py-20 md:py-28 overflow-hidden">
        <div className="absolute inset-0 bg-[#050505]" />
        <div className="absolute inset-0 opacity-[0.06]" style={{
          backgroundImage: "linear-gradient(rgba(0,240,255,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(0,240,255,0.3) 1px, transparent 1px)",
          backgroundSize: "60px 60px"
        }} />
        <div className="absolute inset-0" style={{ background: "radial-gradient(ellipse at 50% 0%, rgba(0,240,255,0.06) 0%, transparent 60%)" }} />

        <div className="relative z-10 container mx-auto max-w-6xl px-4">
          {/* Breadcrumb */}
          <div className="flex items-center gap-2 text-xs text-muted-foreground mb-6" data-testid="payment-hub-breadcrumb">
            {breadcrumb.map((b, i) => (
              <span key={i} className="flex items-center gap-2">
                {i > 0 && <ChevronRight className="w-3 h-3" />}
                {i < breadcrumb.length - 1 ? (
                  <Link to={b.url} className="hover:text-[#00F0FF] transition-colors">{b.name}</Link>
                ) : (
                  <span className="text-[#00F0FF]">{b.name}</span>
                )}
              </span>
            ))}
          </div>

          <div className="inline-flex items-center gap-2 rounded-full border px-4 py-1.5 mb-5 text-xs font-semibold uppercase tracking-widest"
            style={{ borderColor: "rgba(0,240,255,0.3)", color: "#00F0FF", background: "rgba(0,240,255,0.08)" }}>
            <HubIcon className="w-3.5 h-3.5" /> Odeme Rehberi
          </div>

          <h1 className="font-heading font-black text-4xl md:text-5xl lg:text-6xl uppercase tracking-tight leading-none mb-4" data-testid="payment-hub-h1">
            <span className="text-white">{seo.h1.split(" ")[0]}</span>{" "}
            <span className="text-[#00F0FF]" style={{ textShadow: "0 0 40px rgba(0,240,255,0.5)" }}>
              {seo.h1.split(" ").slice(1).join(" ")}
            </span>
          </h1>
          <p className="text-base md:text-lg text-muted-foreground max-w-2xl">{seo.description}</p>

          <div className="flex flex-wrap gap-4 mt-8">
            <div className="flex items-center gap-2 text-sm"><Shield className="w-4 h-4 text-[#00F0FF]" /> <span className="font-medium">Guvenli</span></div>
            <div className="flex items-center gap-2 text-sm"><Lock className="w-4 h-4 text-[#00F0FF]" /> <span className="font-medium">SSL Sertifikali</span></div>
            <div className="flex items-center gap-2 text-sm"><CreditCard className="w-4 h-4 text-[#00F0FF]" /> <span className="font-medium">Hizli Islem</span></div>
          </div>
        </div>
      </section>

      <div className="container mx-auto max-w-6xl px-4 mt-10">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main: Site List */}
          <div className="lg:col-span-2 space-y-3" data-testid="payment-hub-site-list">
            {sites.map((site, i) => (
              <motion.div
                key={site.id || i}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.03 }}
                className="group rounded-xl border p-4 transition-all hover:border-[#00F0FF]/25"
                style={{ background: "rgba(255,255,255,0.02)", borderColor: "rgba(255,255,255,0.06)" }}
                data-testid={`payment-hub-site-${i}`}
              >
                <div className="flex items-center gap-3">
                  <div className="shrink-0 w-9 h-9 rounded-lg flex items-center justify-center font-heading font-black text-base"
                    style={{ background: i < 3 ? "rgba(0,240,255,0.15)" : "rgba(255,255,255,0.05)", color: i < 3 ? "#00F0FF" : "var(--muted-foreground)" }}>
                    {i + 1}
                  </div>
                  <img src={site.logo_url} alt={site.name} className="w-10 h-10 rounded-lg border border-white/10"
                    onError={(e) => { e.target.src = `https://placehold.co/80x80/1a1a1a/00F0FF?text=${site.name?.charAt(0)}`; }} />
                  <div className="flex-1 min-w-0">
                    <h3 className="font-heading font-bold text-sm uppercase truncate">{site.name}</h3>
                    <div className="flex items-center gap-1.5 mt-0.5">
                      <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                      <span className="text-xs font-medium text-yellow-400">{site.rating || 4.5}</span>
                    </div>
                  </div>
                  <div className="text-right shrink-0">
                    <div className="font-heading font-black text-base text-neon-green">{site.bonus_amount}</div>
                  </div>
                  <a
                    href={site.affiliate_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="shrink-0 hidden sm:flex items-center gap-1.5 px-4 py-2.5 rounded-lg font-heading font-bold uppercase text-xs bg-[#00F0FF] text-black hover:scale-105 transition-all"
                    data-testid={`payment-hub-cta-${i}`}
                  >
                    <ExternalLink className="w-3.5 h-3.5" /> Siteye Git
                  </a>
                </div>
                {company_links[i] && (
                  <div className="flex flex-wrap gap-2 mt-3 pt-3 border-t border-white/5">
                    <Link to={company_links[i].odeme_url} className="text-[11px] px-2 py-1 rounded-md bg-white/5 text-[#00F0FF] hover:bg-[#00F0FF]/10 transition-colors">
                      Odeme Yontemleri
                    </Link>
                    <Link to={company_links[i].guncel_giris_url} className="text-[11px] px-2 py-1 rounded-md bg-white/5 text-neon-green hover:bg-neon-green/10 transition-colors">
                      Guncel Giris
                    </Link>
                    <Link to={`/${company_links[i].base_slug}/deneme-bonusu`} className="text-[11px] px-2 py-1 rounded-md bg-white/5 text-neon-green hover:bg-neon-green/10 transition-colors">
                      Deneme Bonusu
                    </Link>
                    <Link to={`/${company_links[i].base_slug}/mobil-giris`} className="text-[11px] px-2 py-1 rounded-md bg-white/5 text-muted-foreground hover:bg-white/10 transition-colors">
                      Mobil Giris
                    </Link>
                    <a href={site.affiliate_url} target="_blank" rel="noopener noreferrer"
                      className="sm:hidden text-[11px] px-2 py-1 rounded-md bg-[#00F0FF]/20 text-[#00F0FF] font-bold">
                      Siteye Git
                    </a>
                  </div>
                )}
              </motion.div>
            ))}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Related Payment Hubs */}
            {related_hubs.payment?.length > 0 && (
              <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-5" data-testid="payment-hub-related-payment">
                <h3 className="font-heading text-base font-bold uppercase mb-3 flex items-center gap-2">
                  <CreditCard className="w-4 h-4 text-[#00F0FF]" /> Odeme Rehberleri
                </h3>
                <div className="space-y-1.5">
                  {related_hubs.payment.map((hub) => (
                    <Link key={hub.slug} to={hub.url} data-testid={`related-payment-${hub.slug}`}
                      className="flex items-center gap-2 text-sm p-2 rounded-lg hover:bg-white/5 transition-colors group">
                      <CreditCard className="w-4 h-4 text-[#00F0FF]" />
                      <span className="group-hover:text-[#00F0FF] transition-colors">{hub.title}</span>
                      <ChevronRight className="w-3 h-3 text-muted-foreground ml-auto" />
                    </Link>
                  ))}
                </div>
              </div>
            )}

            {/* Bonus Hub Links */}
            {related_hubs.bonus?.length > 0 && (
              <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-5" data-testid="payment-hub-related-bonus">
                <h3 className="font-heading text-base font-bold uppercase mb-3 flex items-center gap-2">
                  <Gift className="w-4 h-4 text-neon-green" /> Bonus Rehberleri
                </h3>
                <div className="space-y-1.5">
                  {related_hubs.bonus.map((hub) => (
                    <Link key={hub.slug} to={hub.url} data-testid={`related-bonus-${hub.slug}`}
                      className="flex items-center gap-2 text-sm p-2 rounded-lg hover:bg-white/5 transition-colors group">
                      <Gift className="w-4 h-4 text-neon-green" />
                      <span className="group-hover:text-neon-green transition-colors">{hub.title}</span>
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
