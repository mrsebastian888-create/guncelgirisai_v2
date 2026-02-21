import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import { motion } from "framer-motion";
import axios from "axios";
import { API } from "@/App";
import { Gift, Star, Shield, Check, ExternalLink, TrendingUp } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import BonusCard from "@/components/BonusCard";
import SEOHead from "@/components/SEOHead";

const bonusTypeLabels = {
  deneme: { title: "Deneme Bonusu Veren Siteler", description: "2026 yılının en güncel deneme bonusu veren güvenilir bahis siteleri listesi." },
  hosgeldin: { title: "Hoşgeldin Bonusu Veren Siteler", description: "En yüksek hoşgeldin bonusları ile kazançlı bir başlangıç yapın." },
  yatirim: { title: "Yatırım Bonusu Veren Siteler", description: "Her yatırımda ekstra bonus kazanın." },
  kayip: { title: "Kayıp Bonusu Veren Siteler", description: "Kayıplarınızı telafi eden bonus fırsatları." }
};

const BonusGuidePage = ({ type: propType }) => {
  const { type: paramType } = useParams();
  const bonusType = propType || paramType || "deneme";
  const [bonusSites, setBonusSites] = useState([]);
  const [allSites, setAllSites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedFilter, setSelectedFilter] = useState("all");

  const pageInfo = bonusTypeLabels[bonusType] || bonusTypeLabels.deneme;

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [filteredRes, allRes] = await Promise.all([
          axios.get(`${API}/bonus-sites?bonus_type=${bonusType}&limit=20`),
          axios.get(`${API}/bonus-sites?limit=50`)
        ]);
        setBonusSites(filteredRes.data);
        setAllSites(allRes.data);
      } catch (error) {
        console.error("Error fetching bonus sites:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [bonusType]);

  const displayedSites = selectedFilter === "all" ? allSites : bonusSites;

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.08 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <div className="min-h-screen" data-testid="bonus-guide-page">
      {/* Hero Section */}
      <section className="relative py-20 md:py-28 overflow-hidden">
        <div className="absolute inset-0 hero-pattern" />
        <div className="absolute inset-0 grid-pattern opacity-20" />
        
        <div className="relative z-10 container mx-auto px-6 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Badge className="mb-6 bg-neon-green/10 text-neon-green border-neon-green/30 px-4 py-2">
              <Gift className="w-4 h-4 mr-2" />
              2026 Güncel Liste
            </Badge>
            
            <h1 className="font-heading text-4xl md:text-6xl lg:text-7xl font-black tracking-tighter mb-6 leading-none uppercase">
              {pageInfo.title}
            </h1>
            
            <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto">
              {pageInfo.description}
            </p>
          </motion.div>

          {/* Quick Stats */}
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="mt-12 flex flex-wrap justify-center gap-6"
          >
            <div className="glass-card rounded-lg px-6 py-3 flex items-center gap-3">
              <Star className="w-5 h-5 text-yellow-500" />
              <span className="font-medium">{allSites.length}+ Site</span>
            </div>
            <div className="glass-card rounded-lg px-6 py-3 flex items-center gap-3">
              <Shield className="w-5 h-5 text-neon-green" />
              <span className="font-medium">Lisanslı</span>
            </div>
            <div className="glass-card rounded-lg px-6 py-3 flex items-center gap-3">
              <TrendingUp className="w-5 h-5 text-[#00F0FF]" />
              <span className="font-medium">Güncel</span>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Filter Tabs */}
      <section className="py-8 border-b border-white/5 sticky top-16 z-20 bg-background/80 backdrop-blur-md">
        <div className="container mx-auto px-6">
          <div className="flex flex-wrap gap-3 justify-center">
            <Button
              variant={selectedFilter === "all" ? "default" : "outline"}
              onClick={() => setSelectedFilter("all")}
              className={selectedFilter === "all" ? "bg-neon-green text-black" : ""}
              data-testid="filter-all"
            >
              Tüm Siteler
            </Button>
            <Button
              variant={selectedFilter === "type" ? "default" : "outline"}
              onClick={() => setSelectedFilter("type")}
              className={selectedFilter === "type" ? "bg-neon-green text-black" : ""}
              data-testid="filter-type"
            >
              {bonusTypeLabels[bonusType]?.title.split(" ")[0]} Bonusları
            </Button>
          </div>
        </div>
      </section>

      {/* Bonus Sites List */}
      <section className="py-16 px-6" data-testid="bonus-list-section">
        <div className="container mx-auto max-w-5xl">
          {loading ? (
            <div className="space-y-4">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="h-32 bg-card animate-pulse rounded-xl" />
              ))}
            </div>
          ) : (
            <motion.div 
              variants={containerVariants}
              initial="hidden"
              animate="visible"
              className="space-y-4"
            >
              {displayedSites.map((site, index) => (
                <motion.div key={site.id} variants={itemVariants}>
                  <BonusListItem site={site} rank={index + 1} />
                </motion.div>
              ))}
            </motion.div>
          )}
        </div>
      </section>

      {/* SEO Content */}
      <section className="py-16 px-6 bg-card/30" data-testid="seo-content-section">
        <div className="container mx-auto max-w-4xl">
          <div className="prose prose-invert max-w-none">
            <h2 className="font-heading text-2xl md:text-3xl font-bold tracking-tight mb-6 uppercase">
              {bonusType === "deneme" && "Deneme Bonusu Nedir?"}
              {bonusType === "hosgeldin" && "Hoşgeldin Bonusu Nedir?"}
              {bonusType === "yatirim" && "Yatırım Bonusu Nedir?"}
              {bonusType === "kayip" && "Kayıp Bonusu Nedir?"}
            </h2>
            
            <p className="text-muted-foreground text-lg leading-relaxed mb-6">
              {bonusType === "deneme" && "Deneme bonusu, bahis ve casino sitelerinin yeni üyelerine sunduğu yatırım yapmadan kazanç elde etme fırsatıdır. Bu bonus türü ile siteyi risksiz test edebilir, platformun özelliklerini keşfedebilirsiniz."}
              {bonusType === "hosgeldin" && "Hoşgeldin bonusu, yeni üyelerin ilk yatırımlarına eklenen ekstra bakiye veya free spin gibi avantajlardır. Genellikle %100 ile %200 arasında değişen oranlarda sunulur."}
              {bonusType === "yatirim" && "Yatırım bonusu, her para yatırma işleminizde hesabınıza eklenen ekstra bakiyedir. Düzenli oyuncular için sürekli avantaj sağlar."}
              {bonusType === "kayip" && "Kayıp bonusu, belirli bir dönemde yaşadığınız kayıpların bir kısmının size geri ödenmesidir. Genellikle %5 ile %20 arasında değişir."}
            </p>

            <h3 className="font-heading text-xl font-bold mb-4 uppercase">Bonus Kullanım Şartları</h3>
            <ul className="space-y-2 text-muted-foreground">
              <li className="flex items-start gap-2">
                <Check className="w-5 h-5 text-neon-green mt-0.5 shrink-0" />
                <span>Minimum çevrim şartlarını kontrol edin (genellikle 5x-15x)</span>
              </li>
              <li className="flex items-start gap-2">
                <Check className="w-5 h-5 text-neon-green mt-0.5 shrink-0" />
                <span>Maksimum kazanç ve çekim limitlerini öğrenin</span>
              </li>
              <li className="flex items-start gap-2">
                <Check className="w-5 h-5 text-neon-green mt-0.5 shrink-0" />
                <span>Bonus geçerlilik süresine dikkat edin</span>
              </li>
              <li className="flex items-start gap-2">
                <Check className="w-5 h-5 text-neon-green mt-0.5 shrink-0" />
                <span>Canlı destek üzerinden bonusu talep edin</span>
              </li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  );
};

// Bonus List Item Component
const BonusListItem = ({ site, rank }) => {
  return (
    <div 
      className="glass-card rounded-xl p-4 md:p-6 flex flex-col md:flex-row items-center gap-4 md:gap-6 hover-lift group"
      data-testid={`bonus-item-${site.id}`}
    >
      {/* Rank */}
      <div className="hidden md:flex items-center justify-center w-12 h-12 rounded-full bg-neon-green/10 border border-neon-green/30 shrink-0">
        <span className="font-heading text-xl font-bold text-neon-green">#{rank}</span>
      </div>

      {/* Logo */}
      <div className="w-20 h-20 rounded-xl bg-card overflow-hidden shrink-0 border border-white/10">
        <img 
          src={site.logo_url} 
          alt={site.name}
          className="w-full h-full object-cover"
        />
      </div>

      {/* Info */}
      <div className="flex-1 text-center md:text-left">
        <div className="flex items-center justify-center md:justify-start gap-2 mb-1">
          <h3 className="font-heading text-xl font-bold">{site.name}</h3>
          {site.is_featured && (
            <Badge className="bg-yellow-500/20 text-yellow-500 border-yellow-500/30">
              <Star className="w-3 h-3 mr-1" /> Öne Çıkan
            </Badge>
          )}
        </div>
        
        <div className="flex items-center justify-center md:justify-start gap-1 mb-2">
          {[...Array(5)].map((_, i) => (
            <Star 
              key={i} 
              className={`w-4 h-4 ${i < Math.floor(site.rating) ? "text-yellow-500 fill-yellow-500" : "text-muted-foreground"}`}
            />
          ))}
          <span className="text-sm text-muted-foreground ml-1">({site.rating})</span>
        </div>

        <div className="flex flex-wrap gap-2 justify-center md:justify-start">
          {site.features.slice(0, 3).map((feature, i) => (
            <Badge key={i} variant="outline" className="text-xs">
              {feature}
            </Badge>
          ))}
        </div>
      </div>

      {/* Bonus Amount */}
      <div className="text-center shrink-0">
        <div className="font-heading text-3xl font-black text-neon-green neon-glow-text">
          {site.bonus_amount}
        </div>
        <div className="text-sm text-muted-foreground capitalize">{site.bonus_type} Bonusu</div>
      </div>

      {/* CTA */}
      <Button 
        className="bg-neon-green text-black font-bold uppercase tracking-wide hover:bg-neon-green/90 neon-glow press shrink-0"
        asChild
        data-testid={`bonus-cta-${site.id}`}
      >
        <a href={site.affiliate_url} target="_blank" rel="noopener noreferrer">
          <ExternalLink className="w-4 h-4 mr-2" />
          Siteye Git
        </a>
      </Button>
    </div>
  );
};

export default BonusGuidePage;
