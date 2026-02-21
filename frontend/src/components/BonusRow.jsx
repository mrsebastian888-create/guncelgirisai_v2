import { Star, ExternalLink, Trophy } from "lucide-react";
import { motion } from "framer-motion";
import { usePerformanceTracking } from "@/utils/performanceTracking";

const BONUS_TYPE_LABELS = {
  deneme: "Deneme Bonusu",
  hosgeldin: "Hoşgeldin Bonusu",
  kayip: "Kayıp Bonusu",
  freespin: "Free Spin",
};

const BonusRow = ({ site, rank }) => {
  const { handleCtaClick, handleAffiliateClick } = usePerformanceTracking(site.id);

  const handleClick = () => {
    handleCtaClick();
    handleAffiliateClick();
  };

  const isTop3 = rank <= 3;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: rank * 0.05 }}
      className="group relative flex items-center gap-3 md:gap-5 rounded-xl border p-3 md:p-4 transition-all duration-300 overflow-hidden"
      style={{
        background: "var(--card)",
        borderColor: isTop3 ? "rgba(0,255,135,0.15)" : "rgba(255,255,255,0.05)",
      }}
      data-testid={`bonus-row-${site.id}`}
    >
      {/* Hover glow */}
      <div
        className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"
        style={{ background: "linear-gradient(90deg, rgba(0,255,135,0.04) 0%, transparent 60%)" }}
      />

      {/* Rank */}
      <div
        className="shrink-0 w-9 h-9 rounded-full flex items-center justify-center font-bold text-sm"
        style={{
          border: isTop3 ? "1.5px solid rgba(0,255,135,0.5)" : "1.5px solid rgba(255,255,255,0.12)",
          color: isTop3 ? "var(--neon-green)" : "var(--muted-foreground)",
          background: isTop3 ? "rgba(0,255,135,0.08)" : "rgba(255,255,255,0.03)",
        }}
      >
        {isTop3 && rank === 1 ? (
          <Trophy className="w-4 h-4" style={{ color: "var(--neon-green)" }} />
        ) : (
          <span className="font-heading">#{rank}</span>
        )}
      </div>

      {/* Logo */}
      <div className="shrink-0 w-11 h-11 md:w-14 md:h-14 rounded-xl overflow-hidden bg-white/5 border border-white/10">
        <img
          src={site.logo_url}
          alt={site.name}
          className="w-full h-full object-cover"
          onError={(e) => { e.target.src = "https://placehold.co/100x100/1a1a1a/00FF87?text=BET"; }}
        />
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <h3 className="font-heading font-bold text-base md:text-lg tracking-tight truncate" style={{ color: "var(--foreground)" }}>
            {site.name}
          </h3>
          {site.is_featured && (
            <span
              className="hidden md:inline-flex text-xs px-2 py-0.5 rounded-full font-semibold"
              style={{ background: "rgba(0,255,135,0.15)", color: "var(--neon-green)" }}
            >
              Öne Çıkan
            </span>
          )}
        </div>

        {/* Stars */}
        <div className="flex items-center gap-1 mb-2">
          {[...Array(5)].map((_, i) => (
            <Star
              key={i}
              className="w-3.5 h-3.5"
              style={{ color: i < Math.floor(site.rating) ? "#FBBF24" : "#3F3F46", fill: i < Math.floor(site.rating) ? "#FBBF24" : "none" }}
            />
          ))}
          <span className="text-xs ml-1" style={{ color: "var(--muted-foreground)" }}>({site.rating})</span>
        </div>

        {/* Feature tags */}
        <div className="hidden md:flex flex-wrap gap-1.5">
          {site.features?.slice(0, 3).map((f, i) => (
            <span
              key={i}
              className="text-xs px-2 py-0.5 rounded-md"
              style={{ background: "rgba(255,255,255,0.06)", color: "var(--muted-foreground)" }}
            >
              {f}
            </span>
          ))}
        </div>
      </div>

      {/* Bonus Amount + CTA */}
      <div className="shrink-0 flex flex-col items-end gap-2 ml-2">
        <div className="text-right">
          <div
            className="font-heading font-black text-xl md:text-3xl leading-none"
            style={{
              color: "var(--neon-green)",
              textShadow: "0 0 20px rgba(0,255,135,0.4)",
            }}
          >
            {site.bonus_amount}
          </div>
          <div className="text-xs mt-0.5" style={{ color: "var(--muted-foreground)" }}>
            {BONUS_TYPE_LABELS[site.bonus_type] || site.bonus_type}
          </div>
        </div>

        <a
          href={site.affiliate_url}
          target="_blank"
          rel="noopener noreferrer"
          onClick={handleClick}
          data-testid={`bonus-cta-${site.id}`}
          className="flex items-center gap-1.5 px-5 py-2.5 rounded-lg font-heading font-bold uppercase tracking-wide text-sm transition-all duration-200 active:scale-95 hover:scale-105"
          style={{
            background: "var(--neon-green)",
            color: "#000",
            boxShadow: "0 0 20px rgba(0,255,135,0.4)",
          }}
        >
          <ExternalLink className="w-4 h-4" />
          <span>Siteye Git</span>
        </a>
      </div>
    </motion.div>
  );
};

export default BonusRow;
