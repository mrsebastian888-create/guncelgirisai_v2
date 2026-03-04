import { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import { API } from "@/App";

const BACKEND_BASE = process.env.REACT_APP_BACKEND_URL || "";
import {
  Activity, Clock, Trophy, ChevronRight, ChevronLeft,
  Sparkles, ExternalLink, RefreshCw, AlertCircle, Zap, Calendar
} from "lucide-react";

const LEAGUE_LABELS = {
  soccer_turkey_super_league: { name: "Süper Lig", flag: "🇹🇷" },
  soccer_epl: { name: "Premier League", flag: "🏴󠁧󠁢󠁥󠁮󠁧󠁿" },
  soccer_spain_la_liga: { name: "La Liga", flag: "🇪🇸" },
  soccer_germany_bundesliga: { name: "Bundesliga", flag: "🇩🇪" },
  soccer_italy_serie_a: { name: "Serie A", flag: "🇮🇹" },
  soccer_uefa_champs_league: { name: "UCL", flag: "⭐" },
};

function getMatchStatus(match) {
  const now = new Date();
  const start = new Date(match.commence_time);
  if (match.completed) return { label: "Bitti", color: "#6B7280", pulse: false };
  if (start <= now) return { label: "Canlı", color: "#EF4444", pulse: true };
  // upcoming — show kickoff time
  const diff = start - now;
  const hours = Math.floor(diff / 3600000);
  const mins = Math.floor((diff % 3600000) / 60000);
  if (hours < 24) return { label: hours > 0 ? `${hours}s ${mins}dk` : `${mins}dk`, color: "#F59E0B", pulse: false, upcoming: true };
  return { label: start.toLocaleDateString("tr-TR", { day: "2-digit", month: "2-digit" }), color: "#6B7280", pulse: false, upcoming: true };
}

// Single match card
function MatchCard({ match, featured, partnerSite }) {
  const league = LEAGUE_LABELS[match.sport_key] || { name: match.sport_title, flag: "⚽" };
  const status = getMatchStatus(match);
  const hasScore = match.home_score !== null && match.away_score !== null;

  return (
    <div
      className="shrink-0 flex flex-col gap-3 rounded-xl border p-4 transition-all duration-200 hover:border-opacity-50"
      style={{
        width: "clamp(240px, 28vw, 300px)",
        background: featured ? "rgba(0,255,135,0.05)" : "var(--card)",
        borderColor: featured ? "rgba(0,255,135,0.25)" : "rgba(255,255,255,0.07)",
        scrollSnapAlign: "start",
      }}
      data-testid={`match-card-${match.id}`}
    >
      {/* League + Status */}
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium" style={{ color: "var(--muted-foreground)" }}>
          {league.flag} {league.name}
        </span>
        <div className="flex items-center gap-1.5">
          {status.pulse && <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />}
          <span className="text-xs font-bold" style={{ color: status.color }}>{status.label}</span>
          {featured && (
            <span className="ml-1 text-xs px-1.5 py-0.5 rounded font-semibold"
              style={{ background: "rgba(0,255,135,0.15)", color: "var(--neon-green)" }}>
              Öne Çıkan
            </span>
          )}
        </div>
      </div>

      {/* Teams + Score */}
      <div className="flex flex-col gap-1.5">
        <div className="grid items-center" style={{ gridTemplateColumns: "1fr auto 1fr" }}>
          <p className="font-heading font-bold text-sm truncate" style={{ color: "var(--foreground)" }}>
            {match.home_team}
          </p>
          <div className="text-center px-3" style={{ minWidth: "40px" }}>
            <span className="font-heading font-black text-xl" style={{ color: hasScore ? (match.completed ? "var(--muted-foreground)" : "var(--neon-green)") : "var(--muted-foreground)" }}>
              {hasScore ? match.home_score : ""}
            </span>
            <span className="font-heading font-bold text-sm mx-1" style={{ color: "var(--muted-foreground)" }}>
              {hasScore ? "-" : "vs"}
            </span>
            <span className="font-heading font-black text-xl" style={{ color: hasScore ? (match.completed ? "var(--muted-foreground)" : "var(--neon-green)") : "var(--muted-foreground)" }}>
              {hasScore ? match.away_score : ""}
            </span>
          </div>
          <p className="font-heading font-bold text-sm truncate text-right" style={{ color: "var(--foreground)" }}>
            {match.away_team}
          </p>
        </div>
      </div>

      {/* CTAs */}
      <div className="flex gap-2 pt-1">
        <Link
          to={`/mac/${match.slug || match.id}`}
          className="flex-1 flex items-center justify-center gap-1 rounded-lg py-1.5 text-xs font-semibold transition-all hover:opacity-80"
          style={{ background: "rgba(255,255,255,0.07)", color: "var(--foreground)" }}
          data-testid={`match-detail-btn-${match.id}`}
        >
          <ChevronRight className="w-3 h-3" />
          Detayları Gör
        </Link>
        {partnerSite && (
          <a
            href={`${BACKEND_BASE}/api/go/${partnerSite.id}/${match.id}`}
            target="_blank"
            rel="noopener noreferrer sponsored"
            title="Önerilen platform — sponsorlu bağlantı"
            className="flex-1 flex items-center justify-center gap-1 rounded-lg py-1.5 text-xs font-semibold transition-all"
            style={{ background: "rgba(0,255,135,0.12)", color: "var(--neon-green)", border: "1px solid rgba(0,255,135,0.2)" }}
            data-testid={`match-bet-btn-${match.id}`}
          >
            <ExternalLink className="w-3 h-3" />
            Oranları Gör
          </a>
        )}
      </div>

      {/* Sponsored label */}
      {partnerSite && (
        <p className="text-center text-xs" style={{ color: "var(--muted-foreground)" }}>
          Önerilen: {partnerSite.name} · <span style={{ opacity: 0.6 }}>Sponsorlu</span>
        </p>
      )}
    </div>
  );
}

// AI insight box
function AiInsightBox({ insight, match }) {
  if (!insight) return null;
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-xl border p-4 mb-4"
      style={{ background: "rgba(0,240,255,0.04)", borderColor: "rgba(0,240,255,0.2)" }}
      data-testid="ai-insight-box"
    >
      <div className="flex items-center gap-2 mb-2">
        <Sparkles className="w-4 h-4" style={{ color: "#00F0FF" }} />
        <span className="text-xs font-bold uppercase tracking-widest" style={{ color: "#00F0FF" }}>
          AI Analiz · {match.home_team} vs {match.away_team}
        </span>
      </div>
      <p className="text-sm leading-relaxed" style={{ color: "var(--muted-foreground)" }}>{insight}</p>
      <Link
        to={`/mac/${match.slug || match.id}`}
        className="inline-flex items-center gap-1 mt-2 text-xs font-semibold hover:opacity-80"
        style={{ color: "#00F0FF" }}
      >
        Tam Analizi Gör <ChevronRight className="w-3 h-3" />
      </Link>
    </motion.div>
  );
}

export default function MatchHub() {
  const [matches, setMatches] = useState([]);
  const [featured, setFeatured] = useState(null);
  const [partnerSite, setPartnerSite] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [fromCache, setFromCache] = useState(false);
  const sliderRef = useRef(null);

  const fetchData = async () => {
    try {
      setError(null);
      const [scoresRes, featuredRes, partnerRes] = await Promise.all([
        axios.get(`${API}/sports/scores`),
        axios.get(`${API}/sports/featured`).catch(() => ({ data: null })),
        axios.get(`${API}/bonus-sites?limit=1`).catch(() => ({ data: [] })),
      ]);
      setMatches(scoresRes.data.matches || []);
      setFromCache(scoresRes.data.from_cache || false);
      setFeatured(featuredRes.data);
      setPartnerSite(partnerRes.data?.[0] || null);
    } catch (err) {
      setError("Veriler yüklenemedi. Lütfen tekrar deneyin.");
      console.error("MatchHub error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    // Auto-refresh every 90 seconds
    const interval = setInterval(fetchData, 90000);
    return () => clearInterval(interval);
  }, []);

  const scroll = (dir) => {
    sliderRef.current?.scrollBy({ left: dir * 280, behavior: "smooth" });
  };

  return (
    <section
      className="py-10 md:py-14 px-4 md:px-6"
      style={{ background: "linear-gradient(to bottom, rgba(0,0,0,0), rgba(0,255,135,0.02), rgba(0,0,0,0))" }}
      data-testid="match-hub"
    >
      <div className="container mx-auto max-w-7xl">

        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <Activity className="w-5 h-5 animate-pulse" style={{ color: "var(--neon-green)" }} />
              <h2 className="font-heading font-black uppercase tracking-tight text-xl" style={{ color: "var(--foreground)" }}>
                MAÇLAR
              </h2>
            </div>
            {fromCache && (
              <span className="text-xs px-2 py-0.5 rounded border" style={{ borderColor: "rgba(245,158,11,0.3)", color: "#F59E0B" }}>
                önbellek
              </span>
            )}
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={fetchData}
              className="w-8 h-8 rounded-full border flex items-center justify-center transition-all hover:bg-white/10"
              style={{ borderColor: "rgba(255,255,255,0.12)" }}
              title="Yenile"
              data-testid="match-hub-refresh"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
            <button onClick={() => scroll(-1)} className="w-8 h-8 rounded-full border flex items-center justify-center hover:bg-white/10" style={{ borderColor: "rgba(255,255,255,0.12)" }}>
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button onClick={() => scroll(1)} className="w-8 h-8 rounded-full border flex items-center justify-center hover:bg-white/10" style={{ borderColor: "rgba(255,255,255,0.12)" }}>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* AI Insight for Featured Match */}
        {featured?.ai_insight && <AiInsightBox insight={featured.ai_insight} match={featured} />}

        {/* Match Cards Slider */}
        {loading ? (
          <div className="flex gap-4 overflow-hidden">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="shrink-0 h-48 rounded-xl animate-pulse" style={{ width: "260px", background: "var(--card)" }} />
            ))}
          </div>
        ) : error ? (
          <div
            className="flex items-center gap-3 rounded-xl border px-5 py-4"
            style={{ borderColor: "rgba(239,68,68,0.25)", background: "rgba(239,68,68,0.06)" }}
            data-testid="match-hub-error"
          >
            <AlertCircle className="w-5 h-5 text-red-500 shrink-0" />
            <span className="text-sm" style={{ color: "var(--muted-foreground)" }}>{error}</span>
            <button onClick={fetchData} className="ml-auto text-xs font-semibold" style={{ color: "var(--neon-green)" }}>
              Tekrar Dene
            </button>
          </div>
        ) : matches.length === 0 ? (
          <div
            className="flex items-center justify-center gap-3 rounded-xl border px-5 py-8 text-center"
            style={{ borderColor: "rgba(255,255,255,0.06)", background: "var(--card)" }}
            data-testid="match-hub-empty"
          >
            <div>
              <Calendar className="w-8 h-8 mx-auto mb-2" style={{ color: "var(--muted-foreground)" }} />
              <p className="text-sm" style={{ color: "var(--muted-foreground)" }}>Şu an aktif veya yaklaşan maç bulunmuyor.</p>
              <button onClick={fetchData} className="mt-2 text-xs font-semibold" style={{ color: "var(--neon-green)" }}>Yenile</button>
            </div>
          </div>
        ) : (
          <div
            ref={sliderRef}
            className="flex gap-4 overflow-x-auto pb-2"
            style={{ scrollbarWidth: "none", scrollSnapType: "x mandatory" }}
            data-testid="match-cards-slider"
          >
            {matches.map((match) => (
              <MatchCard
                key={match.id}
                match={match}
                featured={featured?.id === match.id}
                partnerSite={partnerSite}
              />
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
