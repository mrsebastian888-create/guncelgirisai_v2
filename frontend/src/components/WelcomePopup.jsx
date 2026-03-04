import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, AlertTriangle, RotateCw, ExternalLink, Users, Clock } from "lucide-react";
import axios from "axios";
import { API } from "@/App";

const PRIZES = [
  { label: "500 TL", value: 500, color: "#00FF87", isPass: false },
  { label: "PAS", value: 0, color: "#FF6B6B", isPass: true },
  { label: "1.000 TL", value: 1000, color: "#FFD700", isPass: false },
  { label: "2.500 TL", value: 2500, color: "#00F0FF", isPass: false },
  { label: "PAS", value: 0, color: "#FF6B6B", isPass: true },
  { label: "2.000 TL", value: 2000, color: "#A78BFA", isPass: false },
];

const WelcomePopup = ({ onClose }) => {
  const [step, setStep] = useState(1);
  const [isVisible, setIsVisible] = useState(false);
  const [spinning, setSpinning] = useState(false);
  const [rotation, setRotation] = useState(0);
  const [result, setResult] = useState(null);
  const [spinsLeft, setSpinsLeft] = useState(1);
  const [showConfetti, setShowConfetti] = useState(false);
  const [winnerCount] = useState(Math.floor(Math.random() * 400) + 600);
  const [topSites, setTopSites] = useState([]);
  const [wheelRedirectUrl, setWheelRedirectUrl] = useState("");
  const [countdown, setCountdown] = useState({ h: 23, m: 59, s: 59 });
  const canvasRef = useRef(null);

  useEffect(() => {
    const ageVerified = localStorage.getItem("age_verified_v2");
    const wheelShownThisSession = sessionStorage.getItem("wheel_shown");
    if (!ageVerified) {
      setIsVisible(true);
    } else if (!wheelShownThisSession) {
      setStep(2);
      setIsVisible(true);
    } else {
      onClose?.();
    }
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    axios.get(`${API}/bonus-sites?limit=20`).then(r => setTopSites(r.data)).catch(() => {});
    axios.get(`${API}/settings/public`).then(r => setWheelRedirectUrl(r.data.wheel_bonus_redirect_url || "")).catch(() => {});
  }, []);

  useEffect(() => {
    if (!isVisible) return;
    const timer = setInterval(() => {
      setCountdown(prev => {
        let { h, m, s } = prev;
        s--;
        if (s < 0) { s = 59; m--; }
        if (m < 0) { m = 59; h--; }
        if (h < 0) { h = 23; m = 59; s = 59; }
        return { h, m, s };
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [isVisible]);

  // Draw wheel on canvas
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || step !== 2) return;
    const ctx = canvas.getContext("2d");
    const size = canvas.width;
    const center = size / 2;
    const radius = center - 8;
    const sliceAngle = (2 * Math.PI) / PRIZES.length;

    ctx.clearRect(0, 0, size, size);

    PRIZES.forEach((prize, i) => {
      const startAngle = i * sliceAngle - Math.PI / 2;
      const endAngle = startAngle + sliceAngle;

      // Slice
      ctx.beginPath();
      ctx.moveTo(center, center);
      ctx.arc(center, center, radius, startAngle, endAngle);
      ctx.closePath();
      ctx.fillStyle = i % 2 === 0 ? "rgba(255,255,255,0.06)" : "rgba(255,255,255,0.02)";
      ctx.fill();
      ctx.strokeStyle = "rgba(255,255,255,0.1)";
      ctx.lineWidth = 1;
      ctx.stroke();

      // Text
      ctx.save();
      ctx.translate(center, center);
      ctx.rotate(startAngle + sliceAngle / 2);
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.font = `bold ${prize.isPass ? 14 : 16}px sans-serif`;
      ctx.fillStyle = prize.color;
      ctx.fillText(prize.label, radius * 0.6, 0);
      ctx.restore();
    });

    // Center circle
    ctx.beginPath();
    ctx.arc(center, center, 28, 0, 2 * Math.PI);
    ctx.fillStyle = "#111";
    ctx.fill();
    ctx.strokeStyle = "#00FF87";
    ctx.lineWidth = 3;
    ctx.stroke();

    // Outer ring glow
    ctx.beginPath();
    ctx.arc(center, center, radius, 0, 2 * Math.PI);
    ctx.strokeStyle = "rgba(0,255,135,0.3)";
    ctx.lineWidth = 4;
    ctx.stroke();
  }, [step, rotation]);

  const spin = () => {
    if (spinning || spinsLeft <= 0) return;
    setSpinning(true);
    setResult(null);
    setShowConfetti(false);

    // Determine result - weighted toward prizes, but PAS can happen
    const rand = Math.random();
    let selectedIndex;
    if (rand < 0.15) selectedIndex = 1; // PAS
    else if (rand < 0.25) selectedIndex = 4; // PAS
    else if (rand < 0.45) selectedIndex = 0; // 500
    else if (rand < 0.65) selectedIndex = 2; // 1000
    else if (rand < 0.85) selectedIndex = 5; // 2000
    else selectedIndex = 3; // 2500

    const sliceAngle = 360 / PRIZES.length;
    const targetAngle = 360 - (selectedIndex * sliceAngle + sliceAngle / 2);
    const fullSpins = 5 + Math.floor(Math.random() * 3);
    const finalRotation = rotation + fullSpins * 360 + targetAngle - (rotation % 360);

    setRotation(finalRotation);

    setTimeout(() => {
      setSpinning(false);
      const prize = PRIZES[selectedIndex];
      if (prize.isPass) {
        setSpinsLeft(prev => prev); // keep spins, give extra
        setResult({ ...prize, extraSpin: true });
        setSpinsLeft(1);
      } else {
        setResult(prize);
        setSpinsLeft(0);
        setShowConfetti(true);
      }
    }, 4500);
  };

  const handleClose = () => {
    localStorage.setItem("age_verified_v2", "true");
    sessionStorage.setItem("wheel_shown", "true");
    setIsVisible(false);
    onClose?.();
  };

  const handleClaim = () => {
    const url = (wheelRedirectUrl || "").trim();
    if (url) {
      window.open(url, "_blank", "noopener,noreferrer");
    } else if (topSites.length > 0) {
      const site = topSites[Math.floor(Math.random() * topSites.length)];
      window.open(site.affiliate_url, "_blank", "noopener,noreferrer");
    }
    handleClose();
  };

  if (!isVisible) return null;

  const pad = (n) => String(n).padStart(2, "0");

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[100] flex items-center justify-center p-3"
        data-testid="welcome-popup"
      >
        <div className="absolute inset-0 bg-black/85 backdrop-blur-sm" />

        {/* Confetti */}
        {showConfetti && (
          <div className="absolute inset-0 pointer-events-none overflow-hidden z-20">
            {Array.from({ length: 50 }).map((_, i) => (
              <motion.div
                key={i}
                initial={{
                  x: Math.random() * window.innerWidth,
                  y: -20,
                  rotate: 0,
                  scale: Math.random() * 0.5 + 0.5,
                }}
                animate={{
                  y: window.innerHeight + 20,
                  rotate: Math.random() * 720,
                  x: Math.random() * window.innerWidth,
                }}
                transition={{
                  duration: Math.random() * 2 + 2,
                  delay: Math.random() * 0.5,
                  ease: "easeOut",
                }}
                className="absolute w-3 h-3 rounded-sm"
                style={{
                  background: ["#00FF87", "#FFD700", "#00F0FF", "#FF6B6B", "#A78BFA"][i % 5],
                }}
              />
            ))}
          </div>
        )}

        <motion.div
          initial={{ scale: 0.85, opacity: 0, y: 20 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.85, opacity: 0 }}
          className="relative z-10 w-full max-w-sm"
        >
          {step === 1 ? (
            /* ── AGE VERIFICATION ── */
            <div className="rounded-2xl p-6 text-center border"
              style={{ background: "rgba(17,17,17,0.97)", borderColor: "rgba(255,200,0,0.25)" }}>
              <div className="w-14 h-14 mx-auto mb-4 rounded-full flex items-center justify-center"
                style={{ background: "rgba(255,200,0,0.12)" }}>
                <AlertTriangle className="w-7 h-7 text-yellow-500" />
              </div>
              <h2 className="font-heading text-xl font-bold uppercase mb-2" style={{ color: "var(--foreground)" }}>
                Yas Dogrulama
              </h2>
              <p className="text-sm mb-5" style={{ color: "var(--muted-foreground)" }}>
                Bu site 18 yas ve uzeri kullanicilar icindir.
              </p>
              <div className="flex gap-3">
                <button
                  onClick={() => window.location.href = "https://www.google.com"}
                  className="flex-1 py-2.5 rounded-xl text-sm font-bold uppercase border transition-colors hover:bg-red-500/10"
                  style={{ borderColor: "rgba(255,100,100,0.4)", color: "#FF6B6B" }}
                  data-testid="age-under-btn"
                >
                  18 Altindayim
                </button>
                <button
                  onClick={() => setStep(2)}
                  className="flex-1 py-2.5 rounded-xl text-sm font-bold uppercase transition-all hover:scale-105"
                  style={{ background: "#00FF87", color: "#000" }}
                  data-testid="age-over-btn"
                >
                  18 Ustundeyim
                </button>
              </div>
              <p className="text-[10px] mt-3" style={{ color: "var(--muted-foreground)" }}>
                Kumar bagimliligi yardim hatti: 182
              </p>
            </div>
          ) : result && !result.isPass ? (
            /* ── WIN RESULT ── */
            <div className="rounded-2xl overflow-hidden border"
              style={{ background: "rgba(17,17,17,0.97)", borderColor: `${result.color}40` }}>
              <button onClick={handleClose}
                className="absolute top-3 right-3 w-7 h-7 rounded-full bg-white/10 flex items-center justify-center hover:bg-white/20 z-20">
                <X className="w-3.5 h-3.5" />
              </button>

              <div className="p-6 text-center">
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ type: "spring", stiffness: 200, delay: 0.2 }}
                  className="text-5xl mb-3"
                >
                  🎉
                </motion.div>
                <h2 className="font-heading text-2xl font-black uppercase mb-1" style={{ color: "var(--foreground)" }}>
                  Tebrikler!
                </h2>
                <motion.div
                  initial={{ scale: 0.5, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: 0.3, type: "spring" }}
                  className="font-heading text-5xl font-black my-4"
                  style={{ color: result.color, textShadow: `0 0 30px ${result.color}66` }}
                >
                  {result.label}
                </motion.div>
                <p className="text-sm mb-5" style={{ color: "var(--muted-foreground)" }}>
                  Bonus kazandiniz! Hemen kayit olun ve bonusunuzu alin.
                </p>

                <button
                  onClick={handleClaim}
                  data-testid="claim-bonus-btn"
                  className="w-full py-3.5 rounded-xl font-heading font-bold uppercase text-sm tracking-wide transition-all hover:scale-105 flex items-center justify-center gap-2"
                  style={{ background: result.color, color: "#000", boxShadow: `0 0 24px ${result.color}50` }}
                >
                  <ExternalLink className="w-4 h-4" />
                  Bonusunu Al
                </button>

                <div className="flex items-center justify-center gap-4 mt-4 text-[11px]" style={{ color: "var(--muted-foreground)" }}>
                  <span className="flex items-center gap-1">
                    <Users className="w-3 h-3" /> {winnerCount} kisi kazandi
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-3 h-3" /> {pad(countdown.h)}:{pad(countdown.m)}:{pad(countdown.s)}
                  </span>
                </div>

                <button onClick={handleClose} className="text-xs mt-3 transition-colors hover:text-white"
                  style={{ color: "var(--muted-foreground)" }}>
                  Daha sonra
                </button>
              </div>
            </div>
          ) : (
            /* ── SPIN WHEEL ── */
            <div className="rounded-2xl overflow-hidden border"
              style={{ background: "rgba(17,17,17,0.97)", borderColor: "rgba(0,255,135,0.2)" }}>
              <button onClick={handleClose}
                className="absolute top-3 right-3 w-7 h-7 rounded-full bg-white/10 flex items-center justify-center hover:bg-white/20 z-20">
                <X className="w-3.5 h-3.5" />
              </button>

              {/* Header */}
              <div className="pt-5 pb-2 text-center px-4">
                <h2 className="font-heading text-xl font-black uppercase" style={{ color: "var(--foreground)" }}>
                  {result?.extraSpin ? "Bir Hakkin Daha Var!" : "Sans Carki"}
                </h2>
                <p className="text-xs mt-1" style={{ color: "var(--muted-foreground)" }}>
                  {result?.extraSpin ? "PAS geldi ama sans sana guldu! Tekrar cevir!" : "Carki cevir, bonus kazan!"}
                </p>
              </div>

              {/* Wheel Container */}
              <div className="relative flex justify-center py-4">
                {/* Pointer */}
                <div className="absolute top-2 left-1/2 -translate-x-1/2 z-10">
                  <div className="w-0 h-0 border-l-[10px] border-r-[10px] border-t-[18px] border-l-transparent border-r-transparent"
                    style={{ borderTopColor: "#00FF87" }} />
                </div>

                {/* Wheel */}
                <motion.div
                  animate={{ rotate: rotation }}
                  transition={{ duration: 4.5, ease: [0.17, 0.67, 0.12, 0.99] }}
                  className="relative"
                >
                  <canvas
                    ref={canvasRef}
                    width={280}
                    height={280}
                    className="rounded-full"
                    style={{ filter: spinning ? "brightness(1.1)" : "none" }}
                  />
                  {/* Center button */}
                  <button
                    onClick={spin}
                    disabled={spinning || (spinsLeft <= 0 && !result?.extraSpin)}
                    data-testid="spin-btn"
                    className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-14 h-14 rounded-full flex items-center justify-center transition-all disabled:opacity-50"
                    style={{
                      background: spinning ? "#333" : "#00FF87",
                      boxShadow: spinning ? "none" : "0 0 20px rgba(0,255,135,0.5)",
                    }}
                  >
                    <RotateCw className={`w-6 h-6 ${spinning ? "animate-spin text-white/50" : "text-black"}`} />
                  </button>
                </motion.div>

                {/* Decorative dots */}
                {Array.from({ length: 16 }).map((_, i) => {
                  const angle = (i / 16) * 2 * Math.PI;
                  const r = 148;
                  return (
                    <motion.div
                      key={i}
                      className="absolute w-2 h-2 rounded-full"
                      style={{
                        left: `calc(50% + ${Math.cos(angle) * r}px - 4px)`,
                        top: `calc(50% + ${Math.sin(angle) * r}px - 4px)`,
                        background: spinning
                          ? i % 2 === 0 ? "#00FF87" : "#FFD700"
                          : "rgba(255,255,255,0.15)",
                      }}
                      animate={spinning ? {
                        opacity: [0.3, 1, 0.3],
                        scale: [0.8, 1.2, 0.8],
                      } : {}}
                      transition={{
                        duration: 0.5,
                        repeat: spinning ? Infinity : 0,
                        delay: i * 0.05,
                      }}
                    />
                  );
                })}
              </div>

              {/* Social Proof + Timer */}
              <div className="px-5 pb-4">
                <div className="flex items-center justify-between text-[11px] mb-3 px-2"
                  style={{ color: "var(--muted-foreground)" }}>
                  <span className="flex items-center gap-1">
                    <Users className="w-3 h-3 text-neon-green" /> Bugun {winnerCount} kisi kazandi
                  </span>
                  <span className="flex items-center gap-1 font-mono">
                    <Clock className="w-3 h-3 text-red-400" />
                    <span style={{ color: "#FF6B6B" }}>{pad(countdown.h)}:{pad(countdown.m)}:{pad(countdown.s)}</span>
                  </span>
                </div>

                {!spinning && spinsLeft > 0 && !result?.extraSpin && (
                  <button
                    onClick={spin}
                    data-testid="spin-main-btn"
                    className="w-full py-3 rounded-xl font-heading font-bold uppercase text-sm tracking-wide transition-all hover:scale-105"
                    style={{ background: "#00FF87", color: "#000", boxShadow: "0 0 20px rgba(0,255,135,0.4)" }}
                  >
                    Carki Cevir!
                  </button>
                )}

                {result?.extraSpin && !spinning && (
                  <motion.button
                    initial={{ scale: 0.9 }}
                    animate={{ scale: [0.95, 1.05, 0.95] }}
                    transition={{ repeat: Infinity, duration: 1.5 }}
                    onClick={() => { setResult(null); spin(); }}
                    data-testid="extra-spin-btn"
                    className="w-full py-3 rounded-xl font-heading font-bold uppercase text-sm tracking-wide"
                    style={{ background: "#FFD700", color: "#000", boxShadow: "0 0 20px rgba(255,215,0,0.4)" }}
                  >
                    Tekrar Cevir - Ekstra Hak!
                  </motion.button>
                )}

                <button onClick={handleClose}
                  className="w-full text-xs text-center mt-2 py-1 transition-colors hover:text-white"
                  style={{ color: "var(--muted-foreground)" }}>
                  Gecmek istiyorum
                </button>
              </div>
            </div>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default WelcomePopup;
