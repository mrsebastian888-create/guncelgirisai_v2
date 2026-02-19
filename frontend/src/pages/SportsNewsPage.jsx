import { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { motion } from "framer-motion";
import axios from "axios";
import { API } from "@/App";
import { Activity, TrendingUp, Trophy, Calendar, Filter } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import NewsCard from "@/components/NewsCard";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const SportsNewsPage = () => {
  const [searchParams] = useSearchParams();
  const [articles, setArticles] = useState([]);
  const [matches, setMatches] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState(searchParams.get("category") || "all");
  const [selectedLeague, setSelectedLeague] = useState("PL");

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const categoryFilter = selectedCategory !== "all" ? `&tag=${selectedCategory}` : "";
        const [articlesRes, matchesRes, categoriesRes] = await Promise.all([
          axios.get(`${API}/articles?category=spor${categoryFilter}&limit=20`),
          axios.get(`${API}/sports/matches?league=${selectedLeague}`),
          axios.get(`${API}/categories?type=spor`)
        ]);
        setArticles(articlesRes.data);
        setMatches(matchesRes.data.matches || []);
        setCategories(categoriesRes.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [selectedCategory, selectedLeague]);

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

  const leagues = [
    { code: "PL", name: "Premier Lig" },
    { code: "BL1", name: "Bundesliga" },
    { code: "SA", name: "Serie A" },
    { code: "PD", name: "La Liga" },
    { code: "FL1", name: "Ligue 1" }
  ];

  return (
    <div className="min-h-screen" data-testid="sports-news-page">
      {/* Hero Section */}
      <section className="relative py-20 md:py-24 overflow-hidden">
        <div className="absolute inset-0">
          <img 
            src="https://images.unsplash.com/photo-1706675780107-7c43cc487928?w=1920&q=80" 
            alt="Football"
            className="w-full h-full object-cover opacity-15"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-background/70 via-background/90 to-background" />
        </div>
        <div className="absolute inset-0 grid-pattern opacity-20" />
        
        <div className="relative z-10 container mx-auto px-6 text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <Badge className="mb-6 bg-[#00F0FF]/10 text-[#00F0FF] border-[#00F0FF]/30 px-4 py-2">
              <Activity className="w-4 h-4 mr-2" />
              Güncel Haberler
            </Badge>
            
            <h1 className="font-heading text-4xl md:text-6xl lg:text-7xl font-black tracking-tighter mb-6 leading-none uppercase">
              SPOR HABERLERİ
            </h1>
            
            <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto">
              En güncel maç sonuçları, lig analizleri ve spor haberleri. 
              AI destekli içerik analizi ile derinlemesine yorumlar.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Live Scores Section */}
      <section className="py-8 bg-card/50 border-y border-white/5" data-testid="live-scores-section">
        <div className="container mx-auto px-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <Trophy className="w-6 h-6 text-[#00F0FF]" />
              <h2 className="font-heading text-xl font-bold uppercase">Canlı Skorlar</h2>
            </div>
            <Select value={selectedLeague} onValueChange={setSelectedLeague}>
              <SelectTrigger className="w-40" data-testid="league-select">
                <SelectValue placeholder="Lig Seç" />
              </SelectTrigger>
              <SelectContent>
                {leagues.map((league) => (
                  <SelectItem key={league.code} value={league.code}>
                    {league.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {matches.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {matches.slice(0, 6).map((match, index) => (
                <div 
                  key={index}
                  className="glass-card rounded-xl p-4 flex items-center justify-between"
                  data-testid={`match-${index}`}
                >
                  <div className="flex-1 text-right">
                    <span className="font-medium text-sm">{match.home_team}</span>
                  </div>
                  <div className="px-4 text-center">
                    <div className="font-heading text-2xl font-bold text-neon-green">
                      {match.home_score ?? "-"} - {match.away_score ?? "-"}
                    </div>
                    <Badge variant="outline" className="text-xs mt-1">
                      {match.status === "FINISHED" ? "Bitti" : match.status}
                    </Badge>
                  </div>
                  <div className="flex-1 text-left">
                    <span className="font-medium text-sm">{match.away_team}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>Şu an aktif maç bulunmuyor</p>
            </div>
          )}
        </div>
      </section>

      {/* Filters */}
      <section className="py-6 border-b border-white/5 sticky top-16 z-20 bg-background/80 backdrop-blur-md">
        <div className="container mx-auto px-6">
          <div className="flex items-center gap-4">
            <Filter className="w-5 h-5 text-muted-foreground" />
            <div className="flex flex-wrap gap-2">
              <Button
                size="sm"
                variant={selectedCategory === "all" ? "default" : "outline"}
                onClick={() => setSelectedCategory("all")}
                className={selectedCategory === "all" ? "bg-[#00F0FF] text-black" : ""}
                data-testid="filter-all"
              >
                Tümü
              </Button>
              {categories.map((cat) => (
                <Button
                  key={cat.id}
                  size="sm"
                  variant={selectedCategory === cat.slug ? "default" : "outline"}
                  onClick={() => setSelectedCategory(cat.slug)}
                  className={selectedCategory === cat.slug ? "bg-[#00F0FF] text-black" : ""}
                  data-testid={`filter-${cat.slug}`}
                >
                  {cat.name}
                </Button>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Articles Grid */}
      <section className="py-16 px-6" data-testid="articles-section">
        <div className="container mx-auto">
          {loading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <div key={i} className="h-72 bg-card animate-pulse rounded-xl" />
              ))}
            </div>
          ) : articles.length > 0 ? (
            <motion.div 
              variants={containerVariants}
              initial="hidden"
              animate="visible"
              className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6"
            >
              {articles.map((article, index) => (
                <motion.div key={article.id} variants={itemVariants}>
                  <NewsCard article={article} index={index} />
                </motion.div>
              ))}
            </motion.div>
          ) : (
            <div className="text-center py-16">
              <TrendingUp className="w-16 h-16 mx-auto mb-4 text-muted-foreground opacity-50" />
              <h3 className="font-heading text-xl mb-2">Henüz içerik yok</h3>
              <p className="text-muted-foreground">Bu kategoride henüz haber bulunmuyor.</p>
            </div>
          )}
        </div>
      </section>

      {/* SEO Content */}
      <section className="py-16 px-6 bg-card/30" data-testid="seo-section">
        <div className="container mx-auto max-w-4xl">
          <h2 className="font-heading text-2xl md:text-3xl font-bold tracking-tight mb-6 uppercase">
            Spor Haberleri ve Analizler
          </h2>
          <div className="prose prose-invert max-w-none text-muted-foreground">
            <p className="text-lg leading-relaxed mb-4">
              Güncel spor haberleri, maç analizleri ve lig değerlendirmeleri ile futbol dünyasını yakından takip edin. 
              Süper Lig, Premier Lig, Şampiyonlar Ligi ve daha fazlası için detaylı içerikler.
            </p>
            <p className="leading-relaxed">
              Yapay zeka destekli analiz sistemimiz ile maç tahminleri, istatistik yorumları ve derinlemesine 
              taktiksel değerlendirmeler sunuyoruz. Spor bahisleri için doğru bilgiye ulaşın.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default SportsNewsPage;
