import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import axios from "axios";
import { API } from "@/App";
import { 
  Trophy, Zap, TrendingUp, ChevronRight, Star, 
  Shield, Clock, Gift, Activity, ArrowRight
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import BonusCard from "@/components/BonusCard";
import NewsCard from "@/components/NewsCard";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const HomePage = () => {
  const [bonusSites, setBonusSites] = useState([]);
  const [articles, setArticles] = useState([]);
  const [categories, setCategories] = useState([]);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [sitesRes, articlesRes, categoriesRes, matchesRes] = await Promise.all([
          axios.get(`${API}/bonus-sites?is_featured=true&limit=6`),
          axios.get(`${API}/articles?limit=6`),
          axios.get(`${API}/categories`),
          axios.get(`${API}/sports/matches?league=PL`)
        ]);
        setBonusSites(sitesRes.data);
        setArticles(articlesRes.data);
        setCategories(categoriesRes.data);
        setMatches(matchesRes.data.matches || []);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  const faqItems = [
    {
      question: "Deneme bonusu nedir?",
      answer: "Deneme bonusu, bahis sitelerinin yeni üyelerine sunduğu yatırımsız bonus fırsatıdır. Hiç para yatırmadan bahis yapabilir ve kazanç elde edebilirsiniz."
    },
    {
      question: "Deneme bonusu nasıl alınır?",
      answer: "Sitemizde listelenen güvenilir bahis sitelerine üye olarak deneme bonusu alabilirsiniz. Üyelik sonrası canlı destek üzerinden bonusunuzu talep edebilirsiniz."
    },
    {
      question: "Deneme bonusu çevrim şartları nelerdir?",
      answer: "Her sitenin farklı çevrim şartları vardır. Genellikle bonus miktarının 5-15 katı çevrim yapmanız gerekmektedir. Detaylar site sayfalarında belirtilmektedir."
    },
    {
      question: "Hangi siteler güvenilir?",
      answer: "Sitemizde sadece lisanslı ve güvenilir bahis sitelerini listeliyoruz. Tüm siteler ödeme güvenliği ve müşteri memnuniyeti açısından test edilmiştir."
    }
  ];

  return (
    <div className="min-h-screen" data-testid="homepage">
      {/* Hero Section */}
      <section className="relative min-h-[85vh] flex items-center justify-center overflow-hidden hero-pattern">
        {/* Background Image */}
        <div className="absolute inset-0 z-0">
          <img 
            src="https://images.unsplash.com/photo-1762013315117-1c8005ad2b41?w=1920&q=80" 
            alt="Stadium"
            className="w-full h-full object-cover opacity-20"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-background/80 via-background/90 to-background" />
        </div>

        {/* Grid Pattern */}
        <div className="absolute inset-0 grid-pattern opacity-30" />

        {/* Content */}
        <div className="relative z-10 container mx-auto px-6 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Badge className="mb-6 bg-neon-green/10 text-neon-green border-neon-green/30 px-4 py-2">
              <Zap className="w-4 h-4 mr-2" />
              2026 Güncel Bonuslar
            </Badge>
            
            <h1 className="font-heading text-5xl md:text-7xl lg:text-8xl font-black tracking-tighter mb-6 leading-none">
              <span className="text-foreground">DENEME BONUSU</span>
              <br />
              <span className="gradient-text">VEREN SİTELER</span>
            </h1>
            
            <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-8">
              2026'nın en güvenilir bahis siteleri ve en yüksek deneme bonusları. 
              Güncel spor analizleri ve kazanç fırsatları.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button 
                size="lg" 
                className="bg-neon-green text-black font-bold uppercase tracking-wide hover:bg-neon-green/90 neon-glow press"
                asChild
                data-testid="hero-bonus-btn"
              >
                <Link to="/deneme-bonusu">
                  <Gift className="w-5 h-5 mr-2" />
                  Bonus Al
                </Link>
              </Button>
              <Button 
                size="lg" 
                variant="outline"
                className="border-white/20 hover:bg-white/10 font-bold uppercase tracking-wide press"
                asChild
                data-testid="hero-sports-btn"
              >
                <Link to="/spor-haberleri">
                  <Activity className="w-5 h-5 mr-2" />
                  Spor Haberleri
                </Link>
              </Button>
            </div>
          </motion.div>

          {/* Stats */}
          <motion.div 
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.6 }}
            className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto"
          >
            {[
              { icon: Trophy, value: "50+", label: "Güvenilir Site" },
              { icon: Gift, value: "1000 TL", label: "En Yüksek Bonus" },
              { icon: Shield, value: "7/24", label: "Destek" },
              { icon: Clock, value: "Anında", label: "Ödeme" }
            ].map((stat, index) => (
              <div key={index} className="glass-card rounded-xl p-4 text-center hover-lift">
                <stat.icon className="w-8 h-8 mx-auto mb-2 text-neon-green" />
                <div className="font-heading text-2xl md:text-3xl font-bold text-foreground">{stat.value}</div>
                <div className="text-sm text-muted-foreground">{stat.label}</div>
              </div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* Featured Bonus Sites */}
      <section className="py-20 md:py-28 px-6" data-testid="bonus-sites-section">
        <div className="container mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-12">
            <div>
              <Badge className="mb-3 bg-neon-green/10 text-neon-green border-neon-green/30">
                <Star className="w-4 h-4 mr-1" /> En Popüler
              </Badge>
              <h2 className="font-heading text-3xl md:text-5xl font-bold tracking-tight">
                ÖNE ÇIKAN BONUS SİTELERİ
              </h2>
            </div>
            <Button variant="ghost" className="text-neon-green hover:text-neon-green/80" asChild>
              <Link to="/deneme-bonusu" data-testid="view-all-bonuses-btn">
                Tümünü Gör <ChevronRight className="w-4 h-4 ml-1" />
              </Link>
            </Button>
          </div>

          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-48 bg-card animate-pulse rounded-xl" />
              ))}
            </div>
          ) : (
            <motion.div 
              variants={containerVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            >
              {bonusSites.slice(0, 6).map((site, index) => (
                <motion.div key={site.id} variants={itemVariants}>
                  <BonusCard site={site} index={index} />
                </motion.div>
              ))}
            </motion.div>
          )}
        </div>
      </section>

      {/* Live Matches Strip */}
      {matches.length > 0 && (
        <section className="py-8 bg-card/50 border-y border-white/5" data-testid="matches-section">
          <div className="container mx-auto px-6">
            <div className="flex items-center gap-4 overflow-x-auto no-scrollbar">
              <div className="flex items-center gap-2 text-neon-green shrink-0">
                <Activity className="w-5 h-5" />
                <span className="font-heading uppercase text-sm font-bold">Canlı Skorlar</span>
              </div>
              {matches.slice(0, 5).map((match, index) => (
                <div 
                  key={index} 
                  className="flex items-center gap-3 bg-background/50 rounded-lg px-4 py-2 shrink-0 border border-white/5"
                >
                  <span className="text-sm font-medium">{match.home_team}</span>
                  <span className="text-neon-green font-bold">
                    {match.home_score ?? "-"} - {match.away_score ?? "-"}
                  </span>
                  <span className="text-sm font-medium">{match.away_team}</span>
                  <Badge variant="outline" className="text-xs">{match.status}</Badge>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Latest Sports News */}
      <section className="py-20 md:py-28 px-6 bg-background-secondary/30" data-testid="news-section">
        <div className="container mx-auto">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-12">
            <div>
              <Badge className="mb-3 bg-cyber-blue/10 text-[#00F0FF] border-[#00F0FF]/30">
                <TrendingUp className="w-4 h-4 mr-1" /> Güncel Haberler
              </Badge>
              <h2 className="font-heading text-3xl md:text-5xl font-bold tracking-tight">
                SPOR HABERLERİ & ANALİZLER
              </h2>
            </div>
            <Button variant="ghost" className="text-[#00F0FF] hover:text-[#00F0FF]/80" asChild>
              <Link to="/spor-haberleri" data-testid="view-all-news-btn">
                Tümünü Gör <ChevronRight className="w-4 h-4 ml-1" />
              </Link>
            </Button>
          </div>

          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3].map((i) => (
                <div key={i} className="h-72 bg-card animate-pulse rounded-xl" />
              ))}
            </div>
          ) : (
            <motion.div 
              variants={containerVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true }}
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            >
              {articles.slice(0, 6).map((article, index) => (
                <motion.div key={article.id} variants={itemVariants}>
                  <NewsCard article={article} index={index} />
                </motion.div>
              ))}
            </motion.div>
          )}
        </div>
      </section>

      {/* Categories */}
      <section className="py-20 px-6" data-testid="categories-section">
        <div className="container mx-auto">
          <h2 className="font-heading text-3xl md:text-4xl font-bold tracking-tight text-center mb-12">
            KATEGORİLER
          </h2>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {categories.filter(c => c.type === "bonus").map((category) => (
              <Link 
                key={category.id} 
                to={`/bonus/${category.slug}`}
                className="glass-card rounded-xl p-6 text-center hover-lift group"
                data-testid={`category-${category.slug}`}
              >
                <Gift className="w-8 h-8 mx-auto mb-3 text-neon-green group-hover:scale-110 transition-transform" />
                <h3 className="font-heading text-lg font-bold uppercase">{category.name}</h3>
              </Link>
            ))}
            {categories.filter(c => c.type === "spor").map((category) => (
              <Link 
                key={category.id} 
                to={`/spor-haberleri?category=${category.slug}`}
                className="glass-card rounded-xl p-6 text-center hover-lift group"
                data-testid={`category-${category.slug}`}
              >
                <Trophy className="w-8 h-8 mx-auto mb-3 text-[#00F0FF] group-hover:scale-110 transition-transform" />
                <h3 className="font-heading text-lg font-bold uppercase">{category.name}</h3>
              </Link>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 md:py-28 px-6 bg-card/30" data-testid="faq-section">
        <div className="container mx-auto max-w-3xl">
          <h2 className="font-heading text-3xl md:text-4xl font-bold tracking-tight text-center mb-12">
            SIKÇA SORULAN SORULAR
          </h2>
          
          <Accordion type="single" collapsible className="space-y-4">
            {faqItems.map((item, index) => (
              <AccordionItem 
                key={index} 
                value={`item-${index}`}
                className="glass-card rounded-xl border-white/5 px-6 overflow-hidden"
                data-testid={`faq-item-${index}`}
              >
                <AccordionTrigger className="font-heading text-lg font-bold uppercase hover:text-neon-green hover:no-underline py-6">
                  {item.question}
                </AccordionTrigger>
                <AccordionContent className="text-muted-foreground pb-6">
                  {item.answer}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6" data-testid="cta-section">
        <div className="container mx-auto">
          <div className="relative glass-card rounded-2xl p-8 md:p-12 overflow-hidden">
            <div className="absolute inset-0 hero-pattern opacity-50" />
            <div className="relative z-10 text-center">
              <h2 className="font-heading text-3xl md:text-5xl font-bold tracking-tight mb-4">
                HEMEN BONUS AL
              </h2>
              <p className="text-lg text-muted-foreground max-w-xl mx-auto mb-8">
                En yüksek deneme bonuslarını kaçırma. Güvenilir sitelerde hemen oynamaya başla.
              </p>
              <Button 
                size="lg" 
                className="bg-neon-green text-black font-bold uppercase tracking-wide hover:bg-neon-green/90 neon-glow press"
                asChild
                data-testid="cta-bonus-btn"
              >
                <Link to="/deneme-bonusu">
                  <ArrowRight className="w-5 h-5 mr-2" />
                  Bonus Listesini Gör
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
