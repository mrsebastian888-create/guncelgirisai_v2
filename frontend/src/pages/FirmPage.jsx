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

const API = process.env.REACT_APP_BACKEND_URL;

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

  return (
    <div className="min-h-screen bg-background pt-20 pb-16" data-testid="firm-page">
      <SEOHead
        title={`${site.name} Guncel Giris Adresi | Bonus ve Inceleme`}
        description={`${site.name} guncel giris adresi, ${site.bonus_amount} ${bonusLabel} firsati. Detayli inceleme ve bonus rehberi.`}
      />

      {/* Hero Banner */}
      <section className="relative overflow-hidden py-12 md:py-16 px-4" data-testid="firm-hero">
        <div className="absolute inset-0 opacity-10" style={{
          backgroundImage: "linear-gradient(rgba(0,255,135,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(0,255,135,0.3) 1px, transparent 1px)",
          backgroundSize: "60px 60px"
        }} />
        <div className="absolute inset-0" style={{ background: "linear-gradient(135deg, rgba(0,255,135,0.05) 0%, transparent 50%, rgba(0,240,255,0.05) 100%)" }} />

        <div className="container mx-auto max-w-6xl relative z-10">
          <div className="flex flex-col md:flex-row items-start md:items-center gap-6 md:gap-10">
            {/* Logo & Name */}
            <div className="flex items-center gap-5">
              <div className="w-20 h-20 md:w-24 md:h-24 rounded-2xl overflow-hidden border-2 border-neon-green/30 bg-white/5 flex-shrink-0">
                <img src={site.logo_url} alt={site.name} className="w-full h-full object-cover" />
              </div>
              <div>
                <h1 className="font-heading text-3xl md:text-4xl font-black uppercase tracking-tight" data-testid="firm-name">
                  {site.name}
                </h1>
                <div className="flex items-center gap-3 mt-2">
                  <Badge className="bg-neon-green/15 text-neon-green border-neon-green/30 font-bold">
                    {site.category || "Turkiye"}
                  </Badge>
                  <div className="flex items-center gap-1">
                    <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    <span className="font-bold text-yellow-400">{site.rating}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Bonus Box */}
            <div className="flex-1" />
            <div className="rounded-2xl border border-neon-green/20 bg-neon-green/5 p-6 md:p-8 text-center min-w-[220px]" data-testid="firm-bonus-box">
              <div className="text-xs uppercase tracking-widest text-muted-foreground mb-1">{bonusLabel}</div>
              <div className="font-heading text-4xl md:text-5xl font-black text-neon-green" style={{ textShadow: "0 0 30px rgba(0,255,135,0.3)" }}>
                {site.bonus_amount}
              </div>
              <a
                href={site.affiliate_url}
                target="_blank"
                rel="noopener noreferrer"
                data-testid="firm-cta-main"
                className="inline-flex items-center gap-2 mt-4 px-8 py-3.5 rounded-xl font-heading font-bold uppercase tracking-wide text-sm bg-neon-green text-black hover:scale-105 transition-all"
                style={{ boxShadow: "0 0 28px rgba(0,255,135,0.4)" }}
              >
                <ExternalLink className="w-4 h-4" />
                Siteye Git
              </a>
            </div>
          </div>
        </div>
      </section>

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
                  {similar_sites.map((s) => (
                    <Link
                      key={s.id}
                      to={`/${s.name.toLowerCase().replace(/\s+/g, '-').replace(/[!&.]/g, '')}`}
                      className="flex items-center gap-3 p-2.5 rounded-xl hover:bg-white/5 transition-all group"
                    >
                      <img src={s.logo_url} alt={s.name} className="w-8 h-8 rounded-lg" />
                      <div className="flex-1 min-w-0">
                        <div className="text-sm font-medium truncate group-hover:text-neon-green">{s.name}</div>
                        <div className="text-xs text-neon-green">{s.bonus_amount}</div>
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
          Bahis ve sans oyunlari 18 yas alti icin yasaktir. Kumar bagimliligi yardim hatti: 182. Bu sayfa bilgilendirme amaclidir, yatirim tavsiyesi degildir.
        </div>
      </div>
    </div>
  );
}
