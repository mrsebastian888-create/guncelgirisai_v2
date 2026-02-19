import { Link } from "react-router-dom";
import { Gift, Activity, Mail, MapPin } from "lucide-react";

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-card/50 border-t border-white/5 py-16 px-6" data-testid="footer">
      <div className="container mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12 mb-12">
          {/* Brand */}
          <div className="md:col-span-1">
            <Link to="/" className="flex items-center gap-2 mb-4">
              <div className="w-10 h-10 rounded-lg bg-neon-green flex items-center justify-center">
                <span className="font-heading text-black text-xl font-black">DS</span>
              </div>
              <span className="font-heading text-lg font-bold tracking-tight uppercase">
                DSBN
              </span>
            </Link>
            <p className="text-muted-foreground text-sm leading-relaxed">
              Türkiye'nin en güncel bonus rehberi ve spor haber platformu. 
              Güvenilir siteler, detaylı analizler.
            </p>
          </div>

          {/* Bonus Links */}
          <div>
            <h4 className="font-heading text-lg font-bold uppercase mb-4 flex items-center gap-2">
              <Gift className="w-5 h-5 text-neon-green" />
              Bonus Rehberi
            </h4>
            <ul className="space-y-3">
              <li>
                <Link to="/deneme-bonusu" className="text-muted-foreground hover:text-neon-green transition-colors text-sm">
                  Deneme Bonusu Veren Siteler
                </Link>
              </li>
              <li>
                <Link to="/hosgeldin-bonusu" className="text-muted-foreground hover:text-neon-green transition-colors text-sm">
                  Hoşgeldin Bonusları
                </Link>
              </li>
              <li>
                <Link to="/bonus/yatirim" className="text-muted-foreground hover:text-neon-green transition-colors text-sm">
                  Yatırım Bonusları
                </Link>
              </li>
              <li>
                <Link to="/bonus/kayip" className="text-muted-foreground hover:text-neon-green transition-colors text-sm">
                  Kayıp Bonusları
                </Link>
              </li>
            </ul>
          </div>

          {/* Sports Links */}
          <div>
            <h4 className="font-heading text-lg font-bold uppercase mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-[#00F0FF]" />
              Spor Haberleri
            </h4>
            <ul className="space-y-3">
              <li>
                <Link to="/spor-haberleri?category=super-lig" className="text-muted-foreground hover:text-[#00F0FF] transition-colors text-sm">
                  Süper Lig
                </Link>
              </li>
              <li>
                <Link to="/spor-haberleri?category=premier-lig" className="text-muted-foreground hover:text-[#00F0FF] transition-colors text-sm">
                  Premier Lig
                </Link>
              </li>
              <li>
                <Link to="/spor-haberleri?category=sampiyonlar-ligi" className="text-muted-foreground hover:text-[#00F0FF] transition-colors text-sm">
                  Şampiyonlar Ligi
                </Link>
              </li>
              <li>
                <Link to="/spor-haberleri" className="text-muted-foreground hover:text-[#00F0FF] transition-colors text-sm">
                  Tüm Haberler
                </Link>
              </li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="font-heading text-lg font-bold uppercase mb-4">
              İletişim
            </h4>
            <ul className="space-y-3">
              <li className="flex items-center gap-2 text-muted-foreground text-sm">
                <Mail className="w-4 h-4" />
                info@dsbn.com
              </li>
              <li className="flex items-center gap-2 text-muted-foreground text-sm">
                <MapPin className="w-4 h-4" />
                Türkiye
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-white/5 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-muted-foreground text-sm">
            © {currentYear} Dynamic Sports & Bonus Network. Tüm hakları saklıdır.
          </p>
          <div className="flex items-center gap-6">
            <Link to="/" className="text-muted-foreground hover:text-foreground text-sm">
              Gizlilik Politikası
            </Link>
            <Link to="/" className="text-muted-foreground hover:text-foreground text-sm">
              Kullanım Şartları
            </Link>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="mt-8 p-4 bg-background/50 rounded-lg border border-white/5">
          <p className="text-xs text-muted-foreground text-center">
            <strong>Sorumluluk Reddi:</strong> Bu site yalnızca bilgilendirme amaçlıdır. 
            Bahis ve kumar yasal yaş sınırına tabidir. Lütfen sorumlu oynayın. 
            Kumar bağımlılığı için yardım hattı: 182
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
