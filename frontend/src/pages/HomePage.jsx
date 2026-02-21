import { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import { API } from "@/App";
import {
  Trophy, Zap, TrendingUp, ChevronRight, ChevronLeft, Star,
  Shield, Clock, Gift, Activity, Flame, Target, Coins, Globe,
  ExternalLink, Search, Users, Award, Crown, CheckCircle
} from "lucide-react";
import BonusRow from "@/components/BonusRow";
import NewsCard from "@/components/NewsCard";
import MatchHub from "@/components/MatchHub";
import SEOHead from "@/components/SEOHead";
import {
  Accordion, AccordionContent, AccordionItem, AccordionTrigger,
} from "@/components/ui/accordion";

const FAQ_ITEMS = [
  { question: "Deneme bonusu nedir?", answer: "Deneme bonusu, bahis sitelerinin yeni üyelerine sunduğu yatırımsız bonus fırsatıdır. Hiç para yatırmadan bahis yapabilir ve kazanç elde edebilirsiniz." },
  { question: "Deneme bonusu nasıl alınır?", answer: "Sitemizde listelenen güvenilir bahis sitelerine üye olarak deneme bonusu alabilirsiniz. Üyelik sonrası canlı destek üzerinden bonusunuzu talep edebilirsiniz." },
  { question: "Çevrim şartları nelerdir?", answer: "Her sitenin farklı çevrim şartları vardır. Genellikle bonus miktarının 5-15 katı çevrim yapmanız gerekmektedir. Detaylar site sayfalarında belirtilmektedir." },
  { question: "Hangi siteler güvenilir?", answer: "Sitemizde sadece lisanslı ve güvenilir bahis sitelerini listeliyoruz. Tüm siteler ödeme güvenliği ve müşteri memnuniyeti açısından test edilmiştir." },
];

const HERO_SLIDES = [
  {
    badge: "2026 Guncel Bonus Listesi",
    title: ["EN YUKSEK", "DENEME BONUSU", "VEREN SITELER"],
    desc: "Turkiye'nin en guvenilir bahis siteleri — guncel bonuslar, hizli odeme, 7/24 destek.",
    image: "https://images.pexels.com/photos/12201296/pexels-photo-12201296.jpeg?w=1920&q=80",
    cta: { label: "Bonus Al", href: "#bonus-list" },
    accent: "var(--neon-green)",
  },
  {
    badge: "Hosgeldin Bonusu",
    title: ["2000 TL'YE KADAR", "HOSGELDIN", "BONUSU"],
    desc: "Ilk uyeliginize ozel en yuksek hosgeldin bonuslari. Hemen uye olun, firsati kacirmayin!",
    image: "https://images.pexels.com/photos/10741372/pexels-photo-10741372.jpeg?w=1920&q=80",
    cta: { label: "Firsatlari Gor", href: "/hosgeldin-bonusu" },
    accent: "#FFD700",
  },
  {
    badge: "Canli Spor",
    title: ["CANLI MAC", "SONUCLARI VE", "ANALIZLER"],
    desc: "Yapay zeka destekli mac analizleri, canli skorlar ve uzman tahminleri.",
    image: "https://images.pexels.com/photos/18420917/pexels-photo-18420917.jpeg?w=1920&q=80",
    cta: { label: "Analizlere Git", href: "/spor-haberleri" },
    accent: "#00F0FF",
  },
];

const MAIN_CATEGORIES = [
  { name: "Firma Rehberi", slug: "firma-rehberi", icon: Users, color: "#00F0FF", image: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=400&q=80", isAnchor: true },
  { name: "Bonuslar", slug: "bonuslar", icon: Gift, color: "#00FF87", image: "https://images.pexels.com/photos/29825624/pexels-photo-29825624.jpeg?auto=compress&cs=tinysrgb&w=400" },
  { name: "Guncel Giris", slug: "guncel-giris-adresleri", icon: Globe, color: "#00F0FF", image: "https://images.unsplash.com/photo-1530900198670-847f22a849fe?w=400&q=80" },
  { name: "Deneme Bonusu", slug: "deneme-bonusu", icon: Coins, color: "#FBBF24", image: "https://images.pexels.com/photos/10741372/pexels-photo-10741372.jpeg?auto=compress&cs=tinysrgb&w=400" },
  { name: "Hosgeldin Bonusu", slug: "hosgeldin-bonusu", icon: Gift, color: "#FFD700", image: "https://images.pexels.com/photos/6102155/pexels-photo-6102155.jpeg?auto=compress&cs=tinysrgb&w=400" },
  { name: "Spor Haberleri", slug: "spor-haberleri", icon: Activity, color: "#FF6B6B", image: "https://images.pexels.com/photos/12201296/pexels-photo-12201296.jpeg?auto=compress&cs=tinysrgb&w=400" },
];

const HomePage = () => {
  const [bonusSites, setBonusSites] = useState([]);
  const [allFirms, setAllFirms] = useState([]);
  const [articles, setArticles] = useState([]);
  const [categories, setCategories] = useState([]);
  const [latestArticles, setLatestArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [heroSlide, setHeroSlide] = useState(0);
  const [firmSearch, setFirmSearch] = useState("");
  const [showAllFirms, setShowAllFirms] = useState(false);
  const sliderRef = useRef(null);

  useEffect(() => {
    const timer = setInterval(() => {
      setHeroSlide(prev => (prev + 1) % HERO_SLIDES.length);
    }, 5000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const hostname = window.location.hostname;
        const isPreview = hostname.endsWith(".preview.emergentagent.com") || hostname === "localhost" || hostname === "127.0.0.1";
        
        let siteData = null;
        if (!isPreview && hostname !== "adminguncelgiris.company") {
          try {
            const siteRes = await axios.get(`${API}/site/${hostname}`);
            siteData = siteRes.data;
          } catch {}
        }

        if (siteData && siteData.is_ready) {
          setBonusSites(siteData.bonus_sites || []);
          setArticles(siteData.articles || []);
        } else {
          const [sitesRes, articlesRes, categoriesRes, latestRes, allFirmsRes] = await Promise.all([
            axios.get(`${API}/bonus-sites?limit=20`),
            axios.get(`${API}/articles?limit=6`).catch(() => ({ data: [] })),
            axios.get(`${API}/categories`).catch(() => ({ data: [] })),
            axios.get(`${API}/articles/latest?limit=8`).catch(() => ({ data: [] })),
            axios.get(`${API}/bonus-sites?limit=300`).catch(() => ({ data: [] })),
          ]);
          setBonusSites(sitesRes.data);
          setArticles(articlesRes.data);
          setCategories(categoriesRes.data);
          setLatestArticles(latestRes.data);
          setAllFirms(allFirmsRes.data);
        }
      } catch (error) {
        console.error("Error:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const filteredFirms = firmSearch
    ? allFirms.filter(f => f.name.toLowerCase().includes(firmSearch.toLowerCase()))
    : allFirms;
  const displayedFirms = showAllFirms ? filteredFirms : filteredFirms.slice(0, 30);

  // Top 5 for "Yılın En İyi" (highest bonus)
  const topFive = [...bonusSites].sort((a, b) => {
    const parseBonus = (s) => parseInt(String(s.bonus_amount || '0').replace(/\D/g, '')) || 0;
    return parseBonus(b) - parseBonus(a);
  }).slice(0, 5);

  // Top 5 for "En Güvenilir" (highest rating)
  const trustedFive = [...bonusSites].sort((a, b) => (b.rating || 0) - (a.rating || 0)).slice(0, 5);

  const getFirmSlug = (name) => name.toLowerCase().replace(/\s+/g, '-').replace(/[!&.]/g, '');

  const faqJsonLd = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": FAQ_ITEMS.map((item) => ({
      "@type": "Question",
      "name": item.question,
      "acceptedAnswer": { "@type": "Answer", "text": item.answer },
    })),
  };

  const orgJsonLd = {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": "Bonus Rehberi",
    "url": window.location.origin,
    "description": "En güvenilir bonus siteleri, deneme bonusları ve spor bahis rehberleri.",
    "potentialAction": {
      "@type": "SearchAction",
      "target": `${window.location.origin}/makale/{search_term_string}`,
      "query-input": "required name=search_term_string",
    },
  };

  /* ── Reusable: Top-5 Site Card ── */
  const SiteCard = ({ site, rank, accentColor }) => (
    <div
      className="group flex items-center gap-4 p-4 rounded-xl border transition-all duration-200 hover:scale-[1.01]"
      style={{
        background: rank === 1 ? `${accentColor}08` : "rgba(255,255,255,0.02)",
        borderColor: rank === 1 ? `${accentColor}30` : "rgba(255,255,255,0.06)",
      }}
      data-testid={`top-site-${rank}`}
    >
      <div
        className="shrink-0 w-10 h-10 rounded-lg flex items-center justify-center font-heading font-black text-lg"
        style={{
          background: rank <= 3 ? `${accentColor}18` : "rgba(255,255,255,0.05)",
          color: rank <= 3 ? accentColor : "var(--muted-foreground)",
          border: rank === 1 ? `1px solid ${accentColor}40` : "none",
        }}
      >
        {rank}
      </div>
      <Link to={`/${getFirmSlug(site.name)}`} className="shrink-0 w-11 h-11 rounded-lg overflow-hidden border border-white/10">
        <img
          src={site.logo_url}
          alt={site.name}
          className="w-full h-full object-cover"
          onError={(e) => { e.target.src = `https://placehold.co/80x80/1a1a1a/${accentColor.replace('#', '')}?text=${site.name?.charAt(0)}`; }}
        />
      </Link>
      <div className="flex-1 min-w-0">
        <Link to={`/${getFirmSlug(site.name)}`} className="hover:opacity-80 transition-opacity">
          <h3 className="font-heading font-bold text-sm uppercase tracking-tight truncate" style={{ color: "var(--foreground)" }}>
            {site.name}
          </h3>
        </Link>
        <div className="flex items-center gap-2 mt-0.5">
          <Star className="w-3 h-3 fill-current" style={{ color: "#FBBF24" }} />
          <span className="text-xs font-medium" style={{ color: "#FBBF24" }}>{site.rating || "4.5"}</span>
          {site.features && site.features.slice(0, 2).map((f, fi) => (
            <span key={fi} className="text-[10px] px-1.5 py-0.5 rounded" style={{ background: "rgba(255,255,255,0.06)", color: "var(--muted-foreground)" }}>
              {f}
            </span>
          ))}
        </div>
      </div>
      <div className="shrink-0 text-right mr-2">
        <div className="font-heading font-black text-base" style={{ color: accentColor }}>
          {site.bonus_amount}
        </div>
        <div className="text-[10px] uppercase" style={{ color: "var(--muted-foreground)" }}>
          {site.bonus_type === "deneme" ? "Deneme" : site.bonus_type === "hosgeldin" ? "Hosgeldin" : site.bonus_type === "casino" ? "Casino" : site.bonus_type === "spor" ? "Spor" : site.bonus_type}
        </div>
      </div>
      <a
        href={site.affiliate_url}
        target="_blank"
        rel="noopener noreferrer"
        className="shrink-0 flex items-center gap-1.5 px-4 py-2.5 rounded-lg font-heading font-bold uppercase text-xs tracking-wide transition-all duration-200 active:scale-95 hover:scale-105"
        style={{
          background: accentColor,
          color: "#000",
          boxShadow: `0 0 16px ${accentColor}40`,
        }}
      >
        <ExternalLink className="w-3.5 h-3.5" />
        Kayit Ol
      </a>
    </div>
  );

  return (
    <div className="min-h-screen" data-testid="homepage">
      <SEOHead
        title="Deneme Bonusu Veren Siteler 2026 - En Güncel Bonus Rehberi"
        description="En güvenilir deneme bonusu veren siteler 2026 listesi. Yatırımsız bonus fırsatları, hoşgeldin bonusları ve güncel bahis rehberleri."
        canonical={window.location.origin}
        jsonLd={[faqJsonLd, orgJsonLd]}
      />

      {/* ── HERO SLIDER ─────────────────────────── */}
      <section className="relative overflow-hidden" style={{ minHeight: "60vh" }}>
        <AnimatePresence mode="wait">
          <motion.img
            key={`hero-img-${heroSlide}`}
            src={HERO_SLIDES[heroSlide].image}
            alt="Hero"
            className="absolute inset-0 w-full h-full object-cover opacity-25"
            initial={{ opacity: 0, scale: 1.1 }}
            animate={{ opacity: 0.25, scale: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.8 }}
          />
        </AnimatePresence>
        <div className="absolute inset-0" style={{ background: "linear-gradient(to bottom, rgba(5,5,5,0.7) 0%, rgba(5,5,5,0.95) 100%)" }} />
        <div className="absolute inset-0 opacity-10" style={{
          backgroundImage: `linear-gradient(${HERO_SLIDES[heroSlide].accent}4D 1px, transparent 1px), linear-gradient(90deg, ${HERO_SLIDES[heroSlide].accent}4D 1px, transparent 1px)`,
          backgroundSize: "60px 60px"
        }} />

        <div className="relative z-10 container mx-auto max-w-7xl px-4 md:px-6 flex flex-col justify-center" style={{ minHeight: "60vh" }}>
          <AnimatePresence mode="wait">
            <motion.div
              key={`hero-content-${heroSlide}`}
              initial={{ opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -24 }}
              transition={{ duration: 0.5 }}
              className="max-w-3xl"
            >
              <div
                className="inline-flex items-center gap-2 rounded-full border px-4 py-1.5 mb-5 text-xs font-semibold uppercase tracking-widest"
                style={{ borderColor: `${HERO_SLIDES[heroSlide].accent}4D`, color: HERO_SLIDES[heroSlide].accent, background: `${HERO_SLIDES[heroSlide].accent}12` }}
              >
                <Zap className="w-3.5 h-3.5" />
                {HERO_SLIDES[heroSlide].badge}
              </div>

              <h1
                className="font-heading font-black uppercase leading-none mb-4"
                style={{ fontSize: "clamp(2.8rem, 7vw, 5.5rem)", letterSpacing: "-0.02em" }}
              >
                <span style={{ color: "var(--foreground)" }}>{HERO_SLIDES[heroSlide].title[0]}</span>
                <br />
                <span style={{ color: HERO_SLIDES[heroSlide].accent, textShadow: `0 0 40px ${HERO_SLIDES[heroSlide].accent}66` }}>
                  {HERO_SLIDES[heroSlide].title[1]}
                </span>
                <br />
                <span style={{ color: "var(--foreground)" }}>{HERO_SLIDES[heroSlide].title[2]}</span>
              </h1>

              <p className="text-base md:text-lg mb-8 max-w-xl" style={{ color: "var(--muted-foreground)" }}>
                {HERO_SLIDES[heroSlide].desc}
              </p>

              <div className="flex flex-wrap gap-3">
                <a
                  href={HERO_SLIDES[heroSlide].cta.href}
                  data-testid="hero-cta-btn"
                  className="inline-flex items-center gap-2 rounded-lg px-7 py-3.5 font-heading font-bold uppercase tracking-wide text-sm transition-all active:scale-95 hover:scale-105"
                  style={{ background: HERO_SLIDES[heroSlide].accent, color: "#000", boxShadow: `0 0 24px ${HERO_SLIDES[heroSlide].accent}59` }}
                >
                  <Gift className="w-4 h-4" />
                  {HERO_SLIDES[heroSlide].cta.label}
                </a>
                <Link
                  to="/spor-haberleri"
                  data-testid="hero-sports-btn"
                  className="inline-flex items-center gap-2 rounded-lg border px-6 py-3.5 font-heading font-bold uppercase tracking-wide text-sm transition-all hover:bg-white/5 hover:scale-105"
                  style={{ borderColor: "rgba(255,255,255,0.2)", color: "var(--foreground)" }}
                >
                  <Activity className="w-4 h-4" />
                  Spor Haberleri
                </Link>
              </div>
            </motion.div>
          </AnimatePresence>

          <div className="flex gap-2 mt-8">
            {HERO_SLIDES.map((_, i) => (
              <button
                key={i}
                onClick={() => setHeroSlide(i)}
                data-testid={`hero-slide-${i}`}
                className="h-1.5 rounded-full transition-all duration-300"
                style={{
                  width: heroSlide === i ? "32px" : "12px",
                  background: heroSlide === i ? HERO_SLIDES[heroSlide].accent : "rgba(255,255,255,0.2)",
                }}
              />
            ))}
          </div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="flex flex-wrap gap-6 mt-8"
          >
            {[
              { icon: Trophy, value: "264+", label: "Firma" },
              { icon: Gift, value: "2500 TL", label: "En Yüksek Bonus" },
              { icon: Shield, value: "7/24", label: "Destek" },
              { icon: Clock, value: "Anında", label: "Ödeme" },
            ].map((s, i) => (
              <div key={i} className="flex items-center gap-2">
                <s.icon className="w-5 h-5" style={{ color: "var(--neon-green)" }} />
                <span className="font-heading font-bold text-lg" style={{ color: "var(--foreground)" }}>{s.value}</span>
                <span className="text-sm" style={{ color: "var(--muted-foreground)" }}>{s.label}</span>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ── YILIN EN İYİ SİTELERİ (Slider sonrası ilk alan) ── */}
      {topFive.length > 0 && (
        <section id="bonus-list" className="py-14 md:py-20 px-4 md:px-6" data-testid="top-sites-section">
          <div className="container mx-auto max-w-5xl">
            <div className="flex items-end justify-between mb-8 gap-4">
              <div>
                <div
                  className="inline-flex items-center gap-1.5 rounded-full border px-3 py-1 mb-3 text-xs font-semibold uppercase tracking-widest"
                  style={{ borderColor: "rgba(255,215,0,0.3)", color: "#FFD700", background: "rgba(255,215,0,0.07)" }}
                >
                  <Crown className="w-3 h-3" /> 2026
                </div>
                <h2
                  className="font-heading font-black uppercase leading-none"
                  style={{ fontSize: "clamp(1.8rem, 4vw, 3rem)", color: "var(--foreground)" }}
                >
                  YILIN EN IYI SITELERI
                </h2>
              </div>
              <Link
                to="/deneme-bonusu"
                data-testid="view-all-bonuses-btn"
                className="hidden sm:flex items-center gap-1 text-sm font-semibold transition-opacity hover:opacity-70"
                style={{ color: "#FFD700" }}
              >
                Tumunu Gor <ChevronRight className="w-4 h-4" />
              </Link>
            </div>

            <div className="space-y-3">
              {topFive.map((site, i) => (
                <SiteCard key={site.id || i} site={site} rank={i + 1} accentColor="#FFD700" />
              ))}
            </div>
          </div>
        </section>
      )}

      {/* ── FİRMA REHBERİ ──────── */}
      {allFirms.length > 0 && (
        <section id="firma-rehberi" className="py-14 md:py-20 px-4 md:px-6" data-testid="firma-rehberi-section"
          style={{ background: "linear-gradient(to bottom, rgba(0,255,135,0.02), transparent)" }}>
          <div className="container mx-auto max-w-7xl">
            <div className="flex flex-col md:flex-row items-start md:items-end justify-between mb-8 gap-4">
              <div>
                <div
                  className="inline-flex items-center gap-1.5 rounded-full border px-3 py-1 mb-3 text-xs font-semibold uppercase tracking-widest"
                  style={{ borderColor: "rgba(0,240,255,0.3)", color: "#00F0FF", background: "rgba(0,240,255,0.07)" }}
                >
                  <Users className="w-3 h-3" /> {allFirms.length}+ Site
                </div>
                <h2
                  className="font-heading font-black uppercase leading-none"
                  style={{ fontSize: "clamp(1.8rem, 4vw, 3rem)", color: "var(--foreground)" }}
                >
                  FIRMA REHBERI
                </h2>
              </div>
              <div className="relative w-full md:w-72">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <input
                  type="text"
                  placeholder="Firma ara..."
                  value={firmSearch}
                  onChange={(e) => setFirmSearch(e.target.value)}
                  data-testid="firma-search-input"
                  className="w-full pl-10 pr-4 py-2.5 rounded-xl border text-sm font-medium outline-none transition-all focus:ring-1"
                  style={{
                    background: "rgba(255,255,255,0.04)",
                    borderColor: "rgba(255,255,255,0.1)",
                    color: "var(--foreground)",
                  }}
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3" data-testid="firma-grid">
              {displayedFirms.map((firm, i) => {
                const firmSlug = getFirmSlug(firm.name);
                return (
                  <div
                    key={firm.id || i}
                    className="group flex items-center gap-3 rounded-xl border p-3 transition-all duration-200 hover:border-[rgba(0,255,135,0.25)]"
                    style={{
                      background: "rgba(255,255,255,0.02)",
                      borderColor: "rgba(255,255,255,0.06)",
                    }}
                    data-testid={`firma-card-${i}`}
                  >
                    <Link to={`/${firmSlug}`} className="shrink-0 w-11 h-11 rounded-lg overflow-hidden bg-white/5 border border-white/10">
                      <img
                        src={firm.logo_url}
                        alt={firm.name}
                        className="w-full h-full object-cover"
                        onError={(e) => { e.target.src = "https://placehold.co/80x80/1a1a1a/00FF87?text=" + firm.name?.charAt(0); }}
                      />
                    </Link>

                    <div className="flex-1 min-w-0">
                      <Link to={`/${firmSlug}`} className="hover:text-[var(--neon-green)] transition-colors">
                        <h3 className="font-heading font-bold text-sm tracking-tight truncate" style={{ color: "var(--foreground)" }}>
                          {firm.name}
                        </h3>
                      </Link>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="font-heading font-black text-sm" style={{ color: "var(--neon-green)" }}>
                          {firm.bonus_amount}
                        </span>
                        <span className="text-[10px] px-1.5 py-0.5 rounded-md" style={{ background: "rgba(255,255,255,0.06)", color: "var(--muted-foreground)" }}>
                          {firm.bonus_type === "deneme" ? "Deneme" : firm.bonus_type === "hosgeldin" ? "Hosgeldin" : firm.bonus_type === "casino" ? "Casino" : firm.bonus_type === "spor" ? "Spor" : firm.bonus_type}
                        </span>
                      </div>
                    </div>

                    <a
                      href={firm.affiliate_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      data-testid={`firma-cta-${i}`}
                      className="shrink-0 flex items-center gap-1 px-3 py-2 rounded-lg font-heading font-bold uppercase text-[11px] tracking-wide transition-all duration-200 active:scale-95 hover:scale-105 border"
                      style={{
                        background: "transparent",
                        color: "#00FF87",
                        borderColor: "#00FF87",
                      }}
                    >
                      <ExternalLink className="w-3 h-3" />
                      Giris Yap
                    </a>
                  </div>
                );
              })}
            </div>

            {filteredFirms.length > 30 && (
              <div className="text-center mt-6">
                <button
                  onClick={() => setShowAllFirms(!showAllFirms)}
                  data-testid="firma-show-more-btn"
                  className="inline-flex items-center gap-2 px-6 py-3 rounded-xl font-heading font-bold uppercase text-sm tracking-wide border transition-all hover:bg-white/5"
                  style={{ borderColor: "rgba(0,240,255,0.3)", color: "#00F0FF" }}
                >
                  {showAllFirms ? "Daha Az Goster" : `Tumunu Gor (${filteredFirms.length})`}
                </button>
              </div>
            )}
          </div>
        </section>
      )}

      {/* ── YILIN EN İYİ SİTELERİ (Top 5 by Bonus) ── */}
      {topFive.length > 0 && (
        <section id="bonus-list" className="py-14 md:py-20 px-4 md:px-6" data-testid="top-sites-section">
          <div className="container mx-auto max-w-5xl">
            <div className="flex items-end justify-between mb-8 gap-4">
              <div>
                <div
                  className="inline-flex items-center gap-1.5 rounded-full border px-3 py-1 mb-3 text-xs font-semibold uppercase tracking-widest"
                  style={{ borderColor: "rgba(255,215,0,0.3)", color: "#FFD700", background: "rgba(255,215,0,0.07)" }}
                >
                  <Crown className="w-3 h-3" /> 2026
                </div>
                <h2
                  className="font-heading font-black uppercase leading-none"
                  style={{ fontSize: "clamp(1.8rem, 4vw, 3rem)", color: "var(--foreground)" }}
                >
                  YILIN EN IYI SITELERI
                </h2>
              </div>
              <Link
                to="/deneme-bonusu"
                data-testid="view-all-bonuses-btn"
                className="hidden sm:flex items-center gap-1 text-sm font-semibold transition-opacity hover:opacity-70"
                style={{ color: "#FFD700" }}
              >
                Tumunu Gor <ChevronRight className="w-4 h-4" />
              </Link>
            </div>

            <div className="space-y-3">
              {topFive.map((site, i) => (
                <SiteCard key={site.id || i} site={site} rank={i + 1} accentColor="#FFD700" />
              ))}
            </div>
          </div>
        </section>
      )}

      {/* ── EN GÜVENİLİR SİTELER (Top 5 by Rating) ── */}
      {trustedFive.length > 0 && (
        <section className="py-14 md:py-20 px-4 md:px-6" data-testid="trusted-sites-section"
          style={{ background: "linear-gradient(to bottom, transparent, rgba(0,255,135,0.02), transparent)" }}>
          <div className="container mx-auto max-w-5xl">
            <div className="flex items-end justify-between mb-8 gap-4">
              <div>
                <div
                  className="inline-flex items-center gap-1.5 rounded-full border px-3 py-1 mb-3 text-xs font-semibold uppercase tracking-widest"
                  style={{ borderColor: "rgba(0,255,135,0.3)", color: "#00FF87", background: "rgba(0,255,135,0.07)" }}
                >
                  <Shield className="w-3 h-3" /> Lisansli
                </div>
                <h2
                  className="font-heading font-black uppercase leading-none"
                  style={{ fontSize: "clamp(1.8rem, 4vw, 3rem)", color: "var(--foreground)" }}
                >
                  EN GUVENILIR SITELER
                </h2>
              </div>
            </div>

            <div className="space-y-3">
              {trustedFive.map((site, i) => (
                <SiteCard key={site.id || i} site={site} rank={i + 1} accentColor="#00FF87" />
              ))}
            </div>
          </div>
        </section>
      )}

      {/* ── CATEGORIES ──────────────────────────── */}
      <section className="py-14 md:py-20 px-4 md:px-6" data-testid="categories-section">
        <div className="container mx-auto max-w-7xl">
          <div className="flex items-center justify-between mb-8">
            <div>
              <div
                className="inline-flex items-center gap-1.5 rounded-full border px-3 py-1 mb-3 text-xs font-semibold uppercase tracking-widest"
                style={{ borderColor: "rgba(0,255,135,0.3)", color: "var(--neon-green)", background: "rgba(0,255,135,0.07)" }}
              >
                <Target className="w-3 h-3" /> Kategoriler
              </div>
              <h2
                className="font-heading font-black uppercase"
                style={{ fontSize: "clamp(1.6rem, 3.5vw, 2.5rem)", color: "var(--foreground)" }}
              >
                KESFET
              </h2>
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 md:gap-4">
            {MAIN_CATEGORIES.map((cat) => {
              const href = cat.isAnchor ? `/#${cat.slug}` : (cat.slug === "spor-haberleri" ? "/spor-haberleri" : `/bonus/${cat.slug}`);
              const TagName = cat.isAnchor ? 'a' : Link;
              const linkProps = cat.isAnchor ? { href } : { to: href };
              return (
                <TagName
                  key={cat.slug}
                  {...linkProps}
                  data-testid={`category-card-${cat.slug}`}
                  className="group relative rounded-2xl overflow-hidden transition-all duration-300 hover:scale-[1.05] hover:shadow-lg"
                  style={{ aspectRatio: "3/4" }}
                >
                  <img src={cat.image} alt={cat.name} className="absolute inset-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" />
                  <div className="absolute inset-0" style={{ background: "linear-gradient(to top, rgba(0,0,0,0.9) 0%, rgba(0,0,0,0.3) 50%, rgba(0,0,0,0.1) 100%)" }} />
                  <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300" style={{ background: `linear-gradient(to top, ${cat.color}40 0%, transparent 60%)` }} />
                  <div className="absolute bottom-0 left-0 right-0 p-4 flex flex-col items-start">
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-2 transition-transform group-hover:scale-110" style={{ background: `${cat.color}20`, border: `1px solid ${cat.color}40` }}>
                      <cat.icon className="w-5 h-5" style={{ color: cat.color }} />
                    </div>
                    <h3 className="font-heading font-bold text-sm uppercase tracking-tight text-white leading-tight">{cat.name}</h3>
                  </div>
                  <div className="absolute top-3 right-3 opacity-0 group-hover:opacity-100 transition-all duration-300 translate-x-2 group-hover:translate-x-0" style={{ color: cat.color }}>
                    <ChevronRight className="w-5 h-5" />
                  </div>
                </TagName>
              );
            })}
          </div>
        </div>
      </section>

      {/* ── MATCH HUB + AI (Firmalar altına taşındı) ── */}
      <MatchHub />

      {/* ── SON EKLENEN MAKALELER + EN İYİ FİRMALAR ── */}
      {latestArticles.length > 0 && (
        <section className="py-14 md:py-20 px-4 md:px-6" data-testid="latest-articles-section">
          <div className="container mx-auto max-w-7xl">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2">
                <div
                  className="inline-flex items-center gap-1.5 rounded-full border px-3 py-1 mb-4 text-xs font-semibold uppercase tracking-widest"
                  style={{ borderColor: "rgba(255,215,0,0.3)", color: "#FFD700", background: "rgba(255,215,0,0.07)" }}
                >
                  <Star className="w-3 h-3" /> En Iyi Firmalar
                </div>
                <h2
                  className="font-heading font-black uppercase mb-6"
                  style={{ fontSize: "clamp(1.4rem, 3vw, 2.2rem)", color: "var(--foreground)" }}
                >
                  UZMAN DEGERLENDIRMELERI
                </h2>
                <div className="space-y-3">
                  {(latestArticles.filter(a => a.category === "en-iyi-firmalar").length > 0
                    ? latestArticles.filter(a => a.category === "en-iyi-firmalar").slice(0, 5)
                    : latestArticles.slice(0, 5)
                  ).map((article, i) => (
                    <Link
                      key={article.id || i}
                      to={`/makale/${article.slug}`}
                      className="group flex gap-4 p-4 rounded-xl border transition-all hover:border-[rgba(255,215,0,0.3)]"
                      style={{ background: "rgba(255,255,255,0.02)", borderColor: "rgba(255,255,255,0.06)" }}
                      data-testid={`best-firm-article-${i}`}
                    >
                      <div className="flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center font-bold text-lg"
                        style={{ background: i === 0 ? "rgba(255,215,0,0.15)" : "rgba(255,255,255,0.05)", color: i === 0 ? "#FFD700" : "var(--muted-foreground)" }}>
                        {i + 1}
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="text-sm font-semibold group-hover:text-[#FFD700] transition-colors line-clamp-2">{article.title}</h3>
                        <p className="text-xs text-muted-foreground mt-1 line-clamp-1">{article.excerpt}</p>
                        <div className="flex items-center gap-3 mt-2 text-xs text-muted-foreground">
                          {article.author && <span>{article.author}</span>}
                          {article.created_at && <span>{new Date(article.created_at).toLocaleDateString("tr-TR")}</span>}
                        </div>
                      </div>
                      <ChevronRight className="w-4 h-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity self-center flex-shrink-0" />
                    </Link>
                  ))}
                </div>
              </div>

              <div className="lg:col-span-1">
                <div
                  className="inline-flex items-center gap-1.5 rounded-full border px-3 py-1 mb-4 text-xs font-semibold uppercase tracking-widest"
                  style={{ borderColor: "rgba(0,255,135,0.3)", color: "var(--neon-green)", background: "rgba(0,255,135,0.07)" }}
                >
                  <Clock className="w-3 h-3" /> Yeni
                </div>
                <h2
                  className="font-heading font-black uppercase mb-6"
                  style={{ fontSize: "clamp(1.2rem, 2.5vw, 1.6rem)", color: "var(--foreground)" }}
                >
                  SON MAKALELER
                </h2>
                <div className="space-y-2" data-testid="latest-articles-sidebar">
                  {latestArticles.slice(0, 8).map((article, i) => (
                    <Link
                      key={article.id || i}
                      to={`/makale/${article.slug}`}
                      className="group flex items-start gap-3 p-3 rounded-lg transition-all hover:bg-white/5"
                      data-testid={`latest-article-${i}`}
                    >
                      <span className="flex-shrink-0 w-7 h-7 rounded flex items-center justify-center text-xs font-bold" style={{ background: "rgba(0,255,135,0.1)", color: "var(--neon-green)" }}>
                        {i + 1}
                      </span>
                      <div className="min-w-0">
                        <h4 className="text-sm font-medium group-hover:text-[var(--neon-green)] transition-colors line-clamp-2">{article.title}</h4>
                        <span className="text-xs text-muted-foreground">{article.created_at ? new Date(article.created_at).toLocaleDateString("tr-TR") : ""}</span>
                      </div>
                    </Link>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>
      )}

      {/* ── SPORTS NEWS ──────────────────────────── */}
      {articles.length > 0 && (
        <section className="py-14 md:py-20 px-4 md:px-6" data-testid="news-section"
          style={{ background: "rgba(0,240,255,0.02)" }}>
          <div className="container mx-auto max-w-7xl">
            <div className="flex items-end justify-between mb-8">
              <div>
                <div
                  className="inline-flex items-center gap-1.5 rounded-full border px-3 py-1 mb-3 text-xs font-semibold uppercase tracking-widest"
                  style={{ borderColor: "rgba(0,240,255,0.3)", color: "#00F0FF", background: "rgba(0,240,255,0.07)" }}
                >
                  <TrendingUp className="w-3 h-3" /> Guncel
                </div>
                <h2
                  className="font-heading font-black uppercase leading-none"
                  style={{ fontSize: "clamp(1.8rem, 4vw, 3rem)", color: "var(--foreground)" }}
                >
                  SPOR HABERLERI
                </h2>
              </div>
              <Link
                to="/spor-haberleri"
                data-testid="view-all-news-btn"
                className="hidden sm:flex items-center gap-1 text-sm font-semibold"
                style={{ color: "#00F0FF" }}
              >
                Tumunu Gor <ChevronRight className="w-4 h-4" />
              </Link>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
              {articles.slice(0, 6).map((article, i) => (
                <NewsCard key={article.id} article={article} index={i} />
              ))}
            </div>
          </div>
        </section>
      )}

      {/* ── WHY US ───────────────────────────────── */}
      <section className="py-14 md:py-20 px-4 md:px-6">
        <div className="container mx-auto max-w-7xl">
          <h2 className="font-heading font-black uppercase text-center mb-10" style={{ fontSize: "clamp(1.8rem, 4vw, 3rem)", color: "var(--foreground)" }}>
            NEDEN BIZI SECMELISIN?
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {[
              { icon: Shield, title: "Guvenli Siteler", desc: "Sadece lisansli ve denetlenmis platformlar", color: "var(--neon-green)" },
              { icon: Flame, title: "Guncel Bonuslar", desc: "Her gun guncellenen bonus firsatlari", color: "#FBBF24" },
              { icon: Target, title: "AI Siralama", desc: "Performansa gore otomatik siralama sistemi", color: "#00F0FF" },
              { icon: Clock, title: "Hizli Odeme", desc: "Anlik para cekme garantisi", color: "var(--neon-green)" },
              { icon: Activity, title: "Canli Bahis", desc: "Mac ici bahis firsatlari", color: "#00F0FF" },
              { icon: Coins, title: "Yuksek Oran", desc: "Piyasanin en iyi oranlari", color: "#FBBF24" },
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.07 }}
                className="rounded-xl border p-5"
                style={{ background: "var(--card)", borderColor: "rgba(255,255,255,0.06)" }}
              >
                <item.icon className="w-7 h-7 mb-3" style={{ color: item.color }} />
                <h3 className="font-heading font-bold text-base uppercase mb-1" style={{ color: "var(--foreground)" }}>{item.title}</h3>
                <p className="text-sm" style={{ color: "var(--muted-foreground)" }}>{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ── FAQ ──────────────────────────────────── */}
      <section className="py-14 md:py-20 px-4 md:px-6" data-testid="faq-section"
        style={{ background: "var(--card)" }}>
        <div className="container mx-auto max-w-3xl">
          <h2 className="font-heading font-black uppercase text-center mb-10" style={{ fontSize: "clamp(1.8rem, 4vw, 3rem)", color: "var(--foreground)" }}>
            SIKCA SORULAN SORULAR
          </h2>
          <Accordion type="single" collapsible className="space-y-3">
            {FAQ_ITEMS.map((item, i) => (
              <AccordionItem
                key={i}
                value={`faq-${i}`}
                className="rounded-xl border px-5 overflow-hidden"
                style={{ background: "rgba(255,255,255,0.03)", borderColor: "rgba(255,255,255,0.07)" }}
                data-testid={`faq-item-${i}`}
              >
                <AccordionTrigger className="font-heading font-bold uppercase text-base py-5 hover:no-underline" style={{ color: "var(--foreground)" }}>
                  {item.question}
                </AccordionTrigger>
                <AccordionContent className="pb-5 text-sm leading-relaxed" style={{ color: "var(--muted-foreground)" }}>
                  {item.answer}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>
      </section>

      {/* ── CTA BANNER ───────────────────────────── */}
      <section className="py-14 md:py-20 px-4 md:px-6" data-testid="cta-section">
        <div className="container mx-auto max-w-4xl">
          <div
            className="relative rounded-2xl overflow-hidden p-10 md:p-16 text-center"
            style={{ background: "linear-gradient(135deg, rgba(0,255,135,0.12) 0%, rgba(0,240,255,0.08) 100%)", border: "1px solid rgba(0,255,135,0.2)" }}
          >
            <div className="absolute inset-0 opacity-5" style={{
              backgroundImage: "linear-gradient(rgba(0,255,135,1) 1px, transparent 1px), linear-gradient(90deg, rgba(0,255,135,1) 1px, transparent 1px)",
              backgroundSize: "40px 40px"
            }} />
            <div className="relative z-10">
              <h2 className="font-heading font-black uppercase mb-3" style={{ fontSize: "clamp(1.8rem, 5vw, 3.5rem)", color: "var(--foreground)" }}>
                HEMEN BONUS AL
              </h2>
              <p className="text-base mb-8 max-w-md mx-auto" style={{ color: "var(--muted-foreground)" }}>
                En yuksek deneme bonuslarini kacirma. Guvenilir sitelerde hemen oynamaya basla.
              </p>
              <Link
                to="/deneme-bonusu"
                data-testid="cta-bonus-btn"
                className="inline-flex items-center gap-2 rounded-lg px-8 py-3.5 font-heading font-bold uppercase tracking-wide transition-all active:scale-95 hover:scale-105"
                style={{ background: "var(--neon-green)", color: "#000", boxShadow: "0 0 32px rgba(0,255,135,0.4)" }}
              >
                <Gift className="w-5 h-5" />
                Bonus Al
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
