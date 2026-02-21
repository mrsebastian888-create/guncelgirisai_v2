import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { motion } from "framer-motion";
import axios from "axios";
import { API } from "@/App";
import { Calendar, User, Tag, ArrowLeft, Share2, Eye, Gift } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import BonusCard from "@/components/BonusCard";
import SEOHead from "@/components/SEOHead";

const ArticlePage = () => {
  const { slug } = useParams();
  const [article, setArticle] = useState(null);
  const [relatedArticles, setRelatedArticles] = useState([]);
  const [bonusSites, setBonusSites] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [articleRes, relatedRes, bonusRes] = await Promise.all([
          axios.get(`${API}/articles/slug/${slug}`),
          axios.get(`${API}/articles?limit=3`),
          axios.get(`${API}/bonus-sites?is_featured=true&limit=3`)
        ]);
        setArticle(articleRes.data);
        setRelatedArticles(relatedRes.data.filter(a => a.slug !== slug));
        setBonusSites(bonusRes.data);
      } catch (error) {
        console.error("Error fetching article:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [slug]);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("tr-TR", {
      day: "numeric",
      month: "long",
      year: "numeric"
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-neon-green border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!article) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center">
        <h1 className="font-heading text-3xl mb-4">Makale Bulunamadı</h1>
        <Button asChild>
          <Link to="/">Ana Sayfaya Dön</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="min-h-screen" data-testid="article-page">
      {/* Hero Section */}
      <section className="relative py-16 md:py-24 overflow-hidden">
        {article.image_url && (
          <>
            <div className="absolute inset-0">
              <img 
                src={article.image_url} 
                alt={article.title}
                className="w-full h-full object-cover opacity-20"
              />
              <div className="absolute inset-0 bg-gradient-to-b from-background/60 via-background/90 to-background" />
            </div>
          </>
        )}
        <div className="absolute inset-0 grid-pattern opacity-20" />
        
        <div className="relative z-10 container mx-auto px-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-4xl mx-auto"
          >
            {/* Back Button */}
            <Button variant="ghost" className="mb-6" asChild>
              <Link to={article.category === "spor" ? "/spor-haberleri" : "/deneme-bonusu"}>
                <ArrowLeft className="w-4 h-4 mr-2" />
                Geri Dön
              </Link>
            </Button>

            {/* Category Badge */}
            <Badge 
              className={`mb-4 ${
                article.category === "spor" 
                  ? "bg-[#00F0FF]/10 text-[#00F0FF] border-[#00F0FF]/30" 
                  : "bg-neon-green/10 text-neon-green border-neon-green/30"
              }`}
            >
              {article.category === "spor" ? "Spor Haberleri" : "Bonus Rehberi"}
            </Badge>
            
            <h1 className="font-heading text-3xl md:text-5xl lg:text-6xl font-black tracking-tighter mb-6 leading-tight uppercase">
              {article.title}
            </h1>

            {/* Meta Info */}
            <div className="flex flex-wrap items-center gap-4 text-muted-foreground mb-6">
              <div className="flex items-center gap-2">
                <User className="w-4 h-4" />
                <span>{article.author}</span>
              </div>
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4" />
                <span>{formatDate(article.created_at)}</span>
              </div>
              <div className="flex items-center gap-2">
                <Eye className="w-4 h-4" />
                <span>{article.view_count} görüntülenme</span>
              </div>
            </div>

            {/* Tags */}
            {article.tags.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-8">
                {article.tags.map((tag, index) => (
                  <Badge key={index} variant="outline" className="text-sm">
                    <Tag className="w-3 h-3 mr-1" />
                    {tag}
                  </Badge>
                ))}
              </div>
            )}

            {/* Share Button */}
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => navigator.clipboard.writeText(window.location.href)}
              data-testid="share-btn"
            >
              <Share2 className="w-4 h-4 mr-2" />
              Paylaş
            </Button>
          </motion.div>
        </div>
      </section>

      {/* Article Content */}
      <section className="py-12 px-6">
        <div className="container mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
            {/* Main Content */}
            <div className="lg:col-span-2">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="glass-card rounded-2xl p-6 md:p-10"
              >
                {/* Featured Image */}
                {article.image_url && (
                  <div className="mb-8 rounded-xl overflow-hidden">
                    <img 
                      src={article.image_url} 
                      alt={article.title}
                      className="w-full h-64 md:h-96 object-cover"
                    />
                  </div>
                )}

                {/* Excerpt */}
                <p className="text-lg md:text-xl text-muted-foreground mb-8 leading-relaxed border-l-4 border-neon-green pl-4">
                  {article.excerpt}
                </p>

                {/* Content */}
                <div 
                  className="prose prose-invert prose-lg max-w-none
                    prose-headings:font-heading prose-headings:uppercase prose-headings:tracking-tight
                    prose-h2:text-2xl prose-h2:mt-8 prose-h2:mb-4 prose-h2:text-foreground
                    prose-h3:text-xl prose-h3:mt-6 prose-h3:mb-3 prose-h3:text-foreground
                    prose-p:text-muted-foreground prose-p:leading-relaxed
                    prose-ul:text-muted-foreground
                    prose-li:marker:text-neon-green
                    prose-a:text-neon-green prose-a:no-underline hover:prose-a:underline
                    prose-strong:text-foreground"
                  dangerouslySetInnerHTML={{ __html: article.content }}
                  data-testid="article-content"
                />

                {/* AI Generated Badge */}
                {article.is_ai_generated && (
                  <div className="mt-8 pt-6 border-t border-white/10">
                    <Badge variant="outline" className="text-xs">
                      AI Destekli İçerik
                    </Badge>
                  </div>
                )}
              </motion.div>
            </div>

            {/* Sidebar */}
            <div className="lg:col-span-1">
              <div className="sticky top-24 space-y-8">
                {/* Bonus Sites Widget */}
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 }}
                  className="glass-card rounded-2xl p-6"
                >
                  <div className="flex items-center gap-2 mb-6">
                    <Gift className="w-5 h-5 text-neon-green" />
                    <h3 className="font-heading text-lg font-bold uppercase">Önerilen Siteler</h3>
                  </div>
                  <div className="space-y-4">
                    {bonusSites.map((site) => (
                      <div 
                        key={site.id}
                        className="flex items-center gap-3 p-3 bg-background/50 rounded-lg hover:bg-background/80 transition-colors"
                      >
                        <img 
                          src={site.logo_url} 
                          alt={site.name}
                          className="w-12 h-12 rounded-lg object-cover"
                        />
                        <div className="flex-1">
                          <h4 className="font-medium">{site.name}</h4>
                          <span className="text-sm text-neon-green font-bold">{site.bonus_amount}</span>
                        </div>
                        <Button size="sm" className="bg-neon-green text-black hover:bg-neon-green/90" asChild>
                          <a href={site.affiliate_url} target="_blank" rel="noopener noreferrer">
                            Git
                          </a>
                        </Button>
                      </div>
                    ))}
                  </div>
                  <Button className="w-full mt-4" variant="outline" asChild>
                    <Link to="/deneme-bonusu">Tüm Bonusları Gör</Link>
                  </Button>
                </motion.div>

                {/* Related Articles */}
                {relatedArticles.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.4 }}
                    className="glass-card rounded-2xl p-6"
                  >
                    <h3 className="font-heading text-lg font-bold uppercase mb-6">İlgili İçerikler</h3>
                    <div className="space-y-4">
                      {relatedArticles.slice(0, 3).map((relatedArticle) => (
                        <Link 
                          key={relatedArticle.id}
                          to={`/makale/${relatedArticle.slug}`}
                          className="flex gap-3 p-3 bg-background/50 rounded-lg hover:bg-background/80 transition-colors group"
                        >
                          {relatedArticle.image_url && (
                            <img 
                              src={relatedArticle.image_url} 
                              alt={relatedArticle.title}
                              className="w-16 h-16 rounded-lg object-cover shrink-0"
                            />
                          )}
                          <div>
                            <h4 className="font-medium text-sm group-hover:text-neon-green transition-colors line-clamp-2">
                              {relatedArticle.title}
                            </h4>
                            <span className="text-xs text-muted-foreground">
                              {formatDate(relatedArticle.created_at)}
                            </span>
                          </div>
                        </Link>
                      ))}
                    </div>
                  </motion.div>
                )}
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default ArticlePage;
