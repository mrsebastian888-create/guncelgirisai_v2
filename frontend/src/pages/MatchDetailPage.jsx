import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { motion } from "framer-motion";
import axios from "axios";
import { API } from "@/App";
import {
  ChevronLeft, ExternalLink, Sparkles, Clock, Trophy,
  Activity, Shield, AlertCircle, Loader2, Calendar
} from "lucide-react";
import { Helmet } from "react-helmet-async";

const LEAGUE_LABELS = {
  soccer_turkey_super_league: { name: "Süper Lig", flag: "🇹🇷" },
  soccer_epl: { name: "Premier League", flag: "🏴󠁧󠁢󠁥󠁮󠁧󠁿" },
  soccer_spain_la_liga: { name: "La Liga", flag: "🇪🇸" },
  soccer_germany_bundesliga: { name: "Bundesliga", flag: "🇩🇪" },
  soccer_italy_serie_a: { name: "Serie A", flag: "🇮🇹" },
  soccer_uefa_champs_league: { name: "UEFA Şampiyonlar Ligi", flag: "⭐" },
};

function formatMatchDate(isoString) {
  const d = new Date(isoString);
  return d.toLocaleString("tr-TR", { dateStyle: "long", timeStyle: "short" });
}

function MatchStatusBadge({ match }) {
  const now = new Date();
  const start = new Date(match.commence_time);
  if (match.completed) return <span className="px-2 py-1 rounded text-xs font-bold" style={{ background: "rgba(107,114,128,0.15)", color: "#9CA3AF" }}>Bitti</span>;
  if (start <= now) return (
    <span className="flex items-center gap-1.5 px-2 py-1 rounded text-xs font-bold" style={{ background: "rgba(239,68,68,0.15)", color: "#EF4444" }}>
      <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />Canlı
    </span>
  );
  return <span className="px-2 py-1 rounded text-xs font-bold" style={{ background: "rgba(245,158,11,0.15)", color: "#F59E0B" }}>{formatMatchDate(match.commence_time)}</span>;
}

export default function MatchDetailPage() {
  const { slug } = useParams();
  const [match, setMatch] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [apiUrl] = useState(() => process.env.REACT_APP_BACKEND_URL || "");

  useEffect(() => {
    const fetchMatch = async () => {
      try {
        setLoading(true);
        const res = await axios.get(`${API}/sports/match-by-slug/${slug}`);
        setMatch(res.data);
      } catch (err) {
        if (err.response?.status === 404) {
          setError("Maç bulunamadı. Veriler güncellenmiş olabilir.");
        } else {
          setError("Veriler yüklenemedi.");
        }
      } finally {
        setLoading(false);
      }
    };
    fetchMatch();
  }, [slug]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center" style={{ background: "var(--background)" }}>
        <Loader2 className="w-8 h-8 animate-spin" style={{ color: "var(--neon-green)" }} />
      </div>
    );
  }

  if (error || !match) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4 px-4" style={{ background: "var(--background)" }}>
        <AlertCircle className="w-10 h-10 text-red-500" />
        <p style={{ color: "var(--muted-foreground)" }}>{error || "Maç bulunamadı."}</p>
        <Link to="/" className="text-sm font-semibold" style={{ color: "var(--neon-green)" }}>← Anasayfaya Dön</Link>
      </div>
    );
  }

  const league = LEAGUE_LABELS[match.sport_key] || { name: match.sport_title, flag: "⚽" };
  const hasScore = match.home_score !== null && match.away_score !== null;
  const pageTitle = `${match.home_team} - ${match.away_team} Maç Analizi | Canlı Skor, İstatistik, Tahmin`;
  const pageDesc = `${match.home_team} - ${match.away_team} ${league.name} maçı canlı skor, AI analiz ve istatistikleri. Tarafsız bilgi ve maç tahminleri.`;

  // SportsEvent schema
  const schemaData = {
    "@context": "https://schema.org",
    "@type": "SportsEvent",
    "name": `${match.home_team} - ${match.away_team}`,
    "startDate": match.commence_time,
    "sport": "Soccer",
    "description": pageDesc,
    "competitor": [
      { "@type": "SportsTeam", "name": match.home_team },
      { "@type": "SportsTeam", "name": match.away_team },
    ],
  };

  return (
    <>
      <Helmet>
        <title>{`${match.home_team} - ${match.away_team} Maç Analizi | Canlı Skor, İstatistik, Tahmin`}</title>
        <meta name="description" content={pageDesc} />
        <meta property="og:title" content={pageTitle} />
        <meta property="og:description" content={pageDesc} />
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(schemaData) }} />
      </Helmet>

      <div className="min-h-screen py-8 px-4 md:px-6" style={{ background: "var(--background)" }}>
        <div className="container mx-auto max-w-3xl">

          {/* Back */}
          <Link to="/" className="inline-flex items-center gap-1 text-sm mb-6 hover:opacity-70" style={{ color: "var(--muted-foreground)" }}
            data-testid="match-back-btn">
            <ChevronLeft className="w-4 h-4" /> Maçlara Dön
          </Link>

          {/* Hero */}
          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            className="rounded-2xl border p-6 md:p-8 mb-6"
            style={{ background: "var(--card)", borderColor: "rgba(0,255,135,0.15)" }}
            data-testid="match-hero"
          >
            <div className="flex items-center gap-2 mb-4">
              <span>{league.flag}</span>
              <span className="text-sm font-medium" style={{ color: "var(--muted-foreground)" }}>{league.name}</span>
              <MatchStatusBadge match={match} />
            </div>

            <div className="flex items-center justify-between gap-4">
              <h1 className="font-heading font-black text-2xl md:text-4xl uppercase leading-tight" style={{ color: "var(--foreground)" }}>
                {match.home_team}
              </h1>
              <div className="shrink-0 text-center px-4">
                {hasScore ? (
                  <div className="font-heading font-black text-4xl md:text-6xl" style={{ color: "var(--neon-green)" }}>
                    {match.home_score} - {match.away_score}
                  </div>
                ) : (
                  <div className="font-heading font-black text-3xl" style={{ color: "var(--muted-foreground)" }}>VS</div>
                )}
              </div>
              <h1 className="font-heading font-black text-2xl md:text-4xl uppercase leading-tight text-right" style={{ color: "var(--foreground)" }}>
                {match.away_team}
              </h1>
            </div>

            <div className="flex items-center gap-2 mt-4 text-sm" style={{ color: "var(--muted-foreground)" }}>
              <Calendar className="w-4 h-4" />
              {formatMatchDate(match.commence_time)}
            </div>
          </motion.div>

          {/* AI Analysis */}
          {match.ai_analysis && (
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.15 }}
              className="rounded-2xl border p-6 mb-6"
              style={{ background: "rgba(0,240,255,0.04)", borderColor: "rgba(0,240,255,0.2)" }}
              data-testid="ai-analysis-section"
            >
              <div className="flex items-center gap-2 mb-4">
                <Sparkles className="w-5 h-5" style={{ color: "#00F0FF" }} />
                <h2 className="font-heading font-bold uppercase text-base" style={{ color: "#00F0FF" }}>
                  AI Maç Analizi
                </h2>
              </div>
              <div className="text-sm leading-relaxed whitespace-pre-wrap" style={{ color: "var(--muted-foreground)" }}>
                {match.ai_analysis}
              </div>
              <div className="mt-4 pt-4 border-t text-xs" style={{ borderColor: "rgba(255,255,255,0.07)", color: "rgba(156,163,175,0.6)" }}>
                Bu analiz yalnızca bilgi amaçlıdır. Herhangi bir kazanç garantisi içermez.
              </div>
            </motion.div>
          )}

          {/* Recommended Partner */}
          {match.recommended_partner && (
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.25 }}
              className="rounded-2xl border p-6 mb-6"
              style={{ background: "rgba(0,255,135,0.04)", borderColor: "rgba(0,255,135,0.15)" }}
              data-testid="partner-cta-section"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <Trophy className="w-4 h-4" style={{ color: "var(--neon-green)" }} />
                    <span className="font-heading font-bold text-sm uppercase" style={{ color: "var(--foreground)" }}>
                      Önerilen Platform
                    </span>
                    <span className="text-xs px-1.5 py-0.5 rounded" style={{ background: "rgba(107,114,128,0.2)", color: "#9CA3AF" }}>
                      Sponsorlu
                    </span>
                  </div>
                  <p className="text-base font-bold" style={{ color: "var(--foreground)" }}>{match.recommended_partner.name}</p>
                  <p className="text-sm mt-1" style={{ color: "var(--neon-green)" }}>
                    Bonus: {match.recommended_partner.bonus_amount}
                  </p>
                </div>
                <a
                  href={`${apiUrl}/api/go/${match.recommended_partner.id}/${match.id}`}
                  target="_blank"
                  rel="noopener noreferrer sponsored"
                  className="shrink-0 flex items-center gap-2 px-5 py-2.5 rounded-xl font-heading font-bold uppercase text-sm transition-all active:scale-95"
                  style={{ background: "var(--neon-green)", color: "#000" }}
                  data-testid="partner-cta-btn"
                >
                  <ExternalLink className="w-4 h-4" />
                  Oranları Gör
                </a>
              </div>
            </motion.div>
          )}

          {/* Disclaimer */}
          <div
            className="rounded-xl border p-4 text-xs leading-relaxed"
            style={{ borderColor: "rgba(255,255,255,0.06)", background: "rgba(255,255,255,0.02)", color: "var(--muted-foreground)" }}
          >
            <Shield className="w-4 h-4 inline mr-1.5" />
            <strong>Sorumluluk Reddi:</strong> Bu sayfadaki içerikler yalnızca bilgilendirme amaçlıdır. Herhangi bir kazanç garantisi verilmemektedir. Bahis bağımlılığı konusunda yardım için: <strong>182</strong> numaralı hattı arayabilirsiniz.
          </div>

        </div>
      </div>
    </>
  );
}
