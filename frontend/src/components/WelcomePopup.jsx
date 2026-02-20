import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Gift, AlertTriangle, Check } from "lucide-react";
import { Button } from "@/components/ui/button";

const WelcomePopup = ({ onClose }) => {
  const [step, setStep] = useState(1); // 1: age verification, 2: bonus popup
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Check if popup was shown this session
    const popupShown = sessionStorage.getItem("popup_shown");
    if (!popupShown) {
      setIsVisible(true);
    }
  }, []);

  const handleAgeConfirm = (isAdult) => {
    if (isAdult) {
      setStep(2);
    } else {
      // Redirect or show warning
      window.location.href = "https://www.google.com";
    }
  };

  const handleClose = () => {
    sessionStorage.setItem("popup_shown", "true");
    setIsVisible(false);
    onClose?.();
  };

  if (!isVisible) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[100] flex items-center justify-center p-4"
        data-testid="welcome-popup"
      >
        {/* Backdrop */}
        <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" onClick={step === 2 ? handleClose : undefined} />

        {/* Popup Content */}
        <motion.div
          initial={{ scale: 0.9, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.9, opacity: 0 }}
          className="relative z-10 w-full max-w-md"
        >
          {step === 1 ? (
            // Age Verification
            <div className="glass-card rounded-2xl p-8 text-center border border-yellow-500/30">
              <div className="w-16 h-16 mx-auto mb-6 rounded-full bg-yellow-500/20 flex items-center justify-center">
                <AlertTriangle className="w-8 h-8 text-yellow-500" />
              </div>
              
              <h2 className="font-heading text-2xl font-bold uppercase mb-4">
                Yaş Doğrulama
              </h2>
              
              <p className="text-muted-foreground mb-6">
                Bu site yalnızca 18 yaş ve üzeri kullanıcılar içindir. 
                Devam etmek için yaşınızı doğrulayın.
              </p>

              <div className="flex gap-4">
                <Button
                  onClick={() => handleAgeConfirm(false)}
                  variant="outline"
                  className="flex-1 border-red-500/50 text-red-500 hover:bg-red-500/10"
                >
                  18 Yaşından Küçüğüm
                </Button>
                <Button
                  onClick={() => handleAgeConfirm(true)}
                  className="flex-1 bg-neon-green text-black hover:bg-neon-green/90"
                >
                  18 Yaşından Büyüğüm
                </Button>
              </div>

              <p className="text-xs text-muted-foreground mt-4">
                Kumar bağımlılığı yardım hattı: 182
              </p>
            </div>
          ) : (
            // Bonus Popup
            <div className="glass-card rounded-2xl overflow-hidden border border-neon-green/30">
              {/* Close Button */}
              <button
                onClick={handleClose}
                className="absolute top-4 right-4 w-8 h-8 rounded-full bg-white/10 flex items-center justify-center hover:bg-white/20 transition-colors z-10"
              >
                <X className="w-4 h-4" />
              </button>

              {/* Header */}
              <div className="bg-gradient-to-r from-neon-green/20 to-[#00F0FF]/20 p-6 text-center">
                <div className="w-20 h-20 mx-auto mb-4 rounded-full bg-neon-green/20 flex items-center justify-center animate-pulse">
                  <Gift className="w-10 h-10 text-neon-green" />
                </div>
                <h2 className="font-heading text-3xl font-black uppercase gradient-text">
                  Hoş Geldiniz!
                </h2>
              </div>

              {/* Content */}
              <div className="p-6 text-center">
                <p className="text-lg mb-2">Özel Bonus Fırsatı</p>
                <div className="font-heading text-5xl font-black text-neon-green mb-4 neon-glow-text">
                  1000 TL
                </div>
                <p className="text-muted-foreground mb-6">
                  Deneme bonusu fırsatını kaçırmayın! En güncel bonus 
                  listesi için hemen göz atın.
                </p>

                <div className="space-y-3">
                  <Button
                    onClick={handleClose}
                    className="w-full bg-neon-green text-black font-bold uppercase hover:bg-neon-green/90 neon-glow"
                    size="lg"
                  >
                    <Check className="w-5 h-5 mr-2" />
                    Bonusları Gör
                  </Button>
                  
                  <button
                    onClick={handleClose}
                    className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                  >
                    Daha sonra hatırlat
                  </button>
                </div>
              </div>

              {/* Features */}
              <div className="border-t border-white/10 p-4 flex justify-around text-center">
                <div>
                  <div className="text-neon-green font-bold">50+</div>
                  <div className="text-xs text-muted-foreground">Güvenilir Site</div>
                </div>
                <div>
                  <div className="text-neon-green font-bold">7/24</div>
                  <div className="text-xs text-muted-foreground">Destek</div>
                </div>
                <div>
                  <div className="text-neon-green font-bold">Anında</div>
                  <div className="text-xs text-muted-foreground">Ödeme</div>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default WelcomePopup;
