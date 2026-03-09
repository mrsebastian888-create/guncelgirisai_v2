import { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X, Gift, Activity, ChevronDown, Globe, Brain, Building2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import axios from "axios";
import { API } from "@/App";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const Navbar = () => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [topSites, setTopSites] = useState([]);
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    axios.get(`${API}/bonus-sites?limit=20`).then(res => setTopSites(res.data)).catch(() => {});
  }, []);

  const handleBonusClick = (e) => {
    e.preventDefault();
    if (topSites.length > 0) {
      const randomSite = topSites[Math.floor(Math.random() * topSites.length)];
      if (randomSite.affiliate_url) {
        window.open(randomSite.affiliate_url, '_blank', 'noopener,noreferrer');
      }
    } else {
      navigate('/deneme-bonusu');
    }
  };

  const navLinks = [
    { label: "AI Company Intelligence", href: "/companies", icon: Building2, pinned: true },
    { 
      label: "Bonuslar", 
      icon: Gift,
      children: [
        { label: "Deneme Bonusu", href: "/deneme-bonusu" },
        { label: "Hosgeldin Bonusu", href: "/hosgeldin-bonusu" },
        { label: "Tum Bonuslar", href: "/bonus/deneme" }
      ]
    },
    { label: "Firma Rehberi", href: "/#firma-rehberi", icon: Globe },
    { label: "Guncel Giris", href: "/bonus/guncel-giris-adresleri", icon: Globe },
    { label: "Spor Haberleri", href: "/spor-haberleri", icon: Activity },
    { label: "Sağlayıcılar", href: "/saglayicilar", icon: Globe },
    { label: "AI Analiz", href: "/companies", icon: Brain },
  ];

  const isActive = (href) => {
    if (href === "/companies") return location.pathname.startsWith("/companies");
    return location.pathname === href;
  };

  const mobileLinks = [
    { label: "Firma Rehberi", href: "/#firma-rehberi" },
    { label: "AI Company Intelligence", href: "/companies" },
    { label: "Bonuslar", href: "/bonus/deneme" },
    { label: "Deneme Bonusu", href: "/deneme-bonusu" },
    { label: "Hosgeldin Bonusu", href: "/hosgeldin-bonusu" },
    { label: "Guncel Giris Adresleri", href: "/bonus/guncel-giris-adresleri" },
    { label: "Spor Haberleri", href: "/spor-haberleri" },
    { label: "Sağlayıcılar", href: "/saglayicilar" },
    { label: "AI Analiz Araci", href: "/ai-analiz" },
  ];

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-background/80 backdrop-blur-md border-b border-white/5 h-16" data-testid="navbar">
      <div className="container mx-auto h-full px-6 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2 group" data-testid="nav-logo">
          <div className="w-10 h-10 rounded-lg bg-neon-green flex items-center justify-center">
            <span className="font-heading text-black text-xl font-black">DS</span>
          </div>
          <div className="hidden sm:block">
            <span className="font-heading text-lg font-bold tracking-tight uppercase group-hover:text-neon-green transition-colors">
              DSBN
            </span>
          </div>
        </Link>

        <div className="hidden md:flex items-center gap-1">
          {navLinks.map((link, index) => (
            link.children ? (
              <DropdownMenu key={index}>
                <DropdownMenuTrigger asChild>
                  <Button 
                    variant="ghost" 
                    className="font-heading uppercase tracking-wide text-sm hover:text-neon-green"
                    data-testid={`nav-dropdown-${link.label.toLowerCase()}`}
                  >
                    <link.icon className="w-4 h-4 mr-1.5" />
                    {link.label}
                    <ChevronDown className="w-3.5 h-3.5 ml-1" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48">
                  {link.children.map((child, childIndex) => (
                    <DropdownMenuItem key={childIndex} asChild>
                      <Link 
                        to={child.href}
                        className={isActive(child.href) ? "text-neon-green" : ""}
                        data-testid={`nav-link-${child.label.toLowerCase().replace(/\s+/g, '-')}`}
                      >
                        {child.label}
                      </Link>
                    </DropdownMenuItem>
                  ))}
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <Button
                key={index}
                variant="ghost"
                asChild
                className={`font-heading uppercase tracking-wide text-sm ${
                  link.pinned
                    ? "border border-[#00F0FF]/40 bg-[#00F0FF]/10 text-[#00F0FF] hover:bg-[#00F0FF]/20"
                    : isActive(link.href)
                      ? "text-neon-green"
                      : "hover:text-neon-green"
                }`}
              >
                {link.href.startsWith('/#') ? (
                  <a href={link.href} data-testid={`nav-link-${link.label.toLowerCase().replace(/\s+/g, '-')}`}>
                    <link.icon className="w-4 h-4 mr-1.5" />
                    {link.label}
                  </a>
                ) : (
                  <Link to={link.href} data-testid={`nav-link-${link.label.toLowerCase().replace(/\s+/g, '-')}`}>
                    <link.icon className="w-4 h-4 mr-1.5" />
                    {link.label}
                  </Link>
                )}
              </Button>
            )
          ))}
        </div>

        <div className="hidden md:block">
          <Button 
            className="bg-neon-green text-black font-bold uppercase tracking-wide text-sm hover:bg-neon-green/90 neon-glow press"
            onClick={handleBonusClick}
            data-testid="nav-cta-btn"
          >
            <Gift className="w-4 h-4 mr-2" />
            Bonus Al
          </Button>
        </div>

        <div className="relative md:hidden">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            data-testid="mobile-menu-btn"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </Button>
          <AnimatePresence>
            {mobileMenuOpen && (
              <motion.div
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.15 }}
                className="absolute right-0 top-full mt-2 w-[min(280px,calc(100vw-2rem))] rounded-xl border border-white/10 bg-background shadow-xl md:hidden z-50 overflow-hidden"
                data-testid="mobile-menu"
              >
                <nav className="flex flex-col py-2 max-h-[70vh] overflow-y-auto" aria-label="Mobil menü">
                  {mobileLinks.map((link, i) => (
                    <Link
                      key={i}
                      to={link.href}
                      onClick={() => setMobileMenuOpen(false)}
                      className="font-heading text-sm font-semibold uppercase tracking-wide py-3 px-4 hover:bg-white/10 hover:text-neon-green transition-colors text-foreground"
                      data-testid={`mobile-link-${link.label.toLowerCase().replace(/\s+/g, "-")}`}
                    >
                      {link.label}
                    </Link>
                  ))}
                  <div className="border-t border-white/10 p-3 mt-1">
                    <Button
                      className="w-full bg-neon-green text-black font-heading font-bold uppercase text-sm py-5 hover:bg-neon-green/90"
                      onClick={(e) => { setMobileMenuOpen(false); handleBonusClick(e); }}
                      data-testid="mobile-bonus-btn"
                    >
                      <Gift className="w-4 h-4 mr-2 shrink-0" />
                      Bonus Al
                    </Button>
                  </div>
                </nav>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
