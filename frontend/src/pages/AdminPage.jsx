import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import axios from "axios";
import { API } from "@/App";
import { toast } from "sonner";
import {
  Settings, Plus, Trash2, Edit, Save, Wand2, BarChart3,
  FileText, Gift, Activity, RefreshCw, ChevronDown, ChevronUp,
  TrendingUp, Target, Globe, Link2, Calendar, Award, Archive
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Progress } from "@/components/ui/progress";

const AdminPage = () => {
  const [stats, setStats] = useState(null);
  const [bonusSites, setBonusSites] = useState([]);
  const [articles, setArticles] = useState([]);
  const [rankingReport, setRankingReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState("");

  // Form states
  const [newSite, setNewSite] = useState({
    name: "", logo_url: "", bonus_type: "deneme", bonus_amount: "",
    affiliate_url: "", rating: 4.5, features: [], is_featured: false, 
    order: 0, turnover_requirement: 10.0
  });
  const [newArticle, setNewArticle] = useState({
    title: "", excerpt: "", content: "", category: "bonus",
    tags: [], image_url: "", seo_title: "", seo_description: ""
  });
  const [aiRequest, setAiRequest] = useState({
    topic: "", content_type: "article", keywords: "", tone: "professional", 
    word_count: 800, target_url: ""
  });
  const [competitorUrl, setCompetitorUrl] = useState("");
  const [keywordGapInput, setKeywordGapInput] = useState("");

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, sitesRes, articlesRes, rankingRes] = await Promise.all([
        axios.get(`${API}/stats/dashboard`),
        axios.get(`${API}/bonus-sites?limit=50`),
        axios.get(`${API}/articles?limit=50`),
        axios.get(`${API}/ai/ranking-report`)
      ]);
      setStats(statsRes.data);
      setBonusSites(sitesRes.data);
      setArticles(articlesRes.data);
      setRankingReport(rankingRes.data);
    } catch (error) {
      console.error("Error fetching data:", error);
      toast.error("Veri yüklenirken hata oluştu");
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateRankings = async () => {
    try {
      await axios.post(`${API}/ai/update-rankings`);
      toast.success("Sıralamalar güncellendi");
      fetchData();
    } catch (error) {
      toast.error("Sıralama güncellenirken hata oluştu");
    }
  };

  const handleCreateSite = async () => {
    try {
      const siteData = {
        ...newSite,
        features: typeof newSite.features === 'string' 
          ? newSite.features.split(',').map(f => f.trim()).filter(f => f)
          : newSite.features
      };
      await axios.post(`${API}/bonus-sites`, siteData);
      toast.success("Bonus sitesi eklendi");
      fetchData();
      setNewSite({
        name: "", logo_url: "", bonus_type: "deneme", bonus_amount: "",
        affiliate_url: "", rating: 4.5, features: [], is_featured: false, 
        order: 0, turnover_requirement: 10.0
      });
    } catch (error) {
      toast.error("Site eklenirken hata oluştu");
    }
  };

  const handleArchiveSite = async (id) => {
    try {
      await axios.post(`${API}/bonus-sites/${id}/archive`);
      toast.success("Site arşivlendi");
      fetchData();
    } catch (error) {
      toast.error("Site arşivlenirken hata oluştu");
    }
  };

  const handleDeleteSite = async (id) => {
    try {
      await axios.delete(`${API}/bonus-sites/${id}`);
      toast.success("Site silindi");
      fetchData();
    } catch (error) {
      toast.error("Site silinirken hata oluştu");
    }
  };

  const handleCreateArticle = async () => {
    try {
      const articleData = {
        ...newArticle,
        tags: typeof newArticle.tags === "string" 
          ? newArticle.tags.split(",").map(t => t.trim()).filter(t => t)
          : newArticle.tags
      };
      await axios.post(`${API}/articles`, articleData);
      toast.success("Makale eklendi");
      fetchData();
      setNewArticle({
        title: "", excerpt: "", content: "", category: "bonus",
        tags: [], image_url: "", seo_title: "", seo_description: ""
      });
    } catch (error) {
      toast.error("Makale eklenirken hata oluştu");
    }
  };

  const handleDeleteArticle = async (id) => {
    try {
      await axios.delete(`${API}/articles/${id}`);
      toast.success("Makale silindi");
      fetchData();
    } catch (error) {
      toast.error("Makale silinirken hata oluştu");
    }
  };

  const handleGenerateContent = async () => {
    setGenerating(true);
    try {
      const response = await axios.post(`${API}/ai/generate-content`, {
        ...aiRequest,
        keywords: aiRequest.keywords.split(",").map(k => k.trim()).filter(k => k)
      });
      setGeneratedContent(response.data.content);
      toast.success("İçerik üretildi");
    } catch (error) {
      toast.error("İçerik üretilirken hata oluştu");
    } finally {
      setGenerating(false);
    }
  };

  const handleCompetitorAnalysis = async () => {
    if (!competitorUrl) return;
    setGenerating(true);
    try {
      const response = await axios.post(`${API}/ai/competitor-analysis`, {
        competitor_url: competitorUrl,
        analysis_depth: "detailed"
      });
      setGeneratedContent(response.data.analysis);
      toast.success("Rakip analizi tamamlandı");
    } catch (error) {
      toast.error("Rakip analizi yapılırken hata oluştu");
    } finally {
      setGenerating(false);
    }
  };

  const handleKeywordGapAnalysis = async () => {
    if (!keywordGapInput) return;
    setGenerating(true);
    try {
      const keywords = keywordGapInput.split(",").map(k => k.trim()).filter(k => k);
      const response = await axios.post(`${API}/ai/keyword-gap-analysis`, keywords);
      setGeneratedContent(response.data.analysis);
      toast.success("Anahtar kelime analizi tamamlandı");
    } catch (error) {
      toast.error("Analiz yapılırken hata oluştu");
    } finally {
      setGenerating(false);
    }
  };

  const handleWeeklyReport = async () => {
    setGenerating(true);
    try {
      const response = await axios.get(`${API}/ai/weekly-seo-report`);
      setGeneratedContent(response.data.report);
      toast.success("Haftalık rapor oluşturuldu");
    } catch (error) {
      toast.error("Rapor oluşturulurken hata oluştu");
    } finally {
      setGenerating(false);
    }
  };

  const handleInternalLinkSuggestions = async (articleId) => {
    setGenerating(true);
    try {
      const response = await axios.post(`${API}/ai/internal-link-suggestions?article_id=${articleId}`);
      setGeneratedContent(response.data.suggestions);
      toast.success("İç link önerileri hazırlandı");
    } catch (error) {
      toast.error("İç link analizi yapılırken hata oluştu");
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-neon-green border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen py-8 px-6" data-testid="admin-page">
      <div className="container mx-auto max-w-7xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="font-heading text-3xl md:text-4xl font-bold tracking-tight uppercase">
              Admin Panel
            </h1>
            <p className="text-muted-foreground mt-1">AI destekli içerik yönetimi ve performans optimizasyonu</p>
          </div>
          <div className="flex gap-2">
            <Button onClick={handleUpdateRankings} variant="outline" data-testid="update-rankings-btn">
              <TrendingUp className="w-4 h-4 mr-2" />
              Sıralamayı Güncelle
            </Button>
            <Button onClick={fetchData} variant="outline" data-testid="refresh-btn">
              <RefreshCw className="w-4 h-4 mr-2" />
              Yenile
            </Button>
          </div>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4 mb-8">
            <Card className="glass-card border-white/10">
              <CardHeader className="pb-2">
                <CardTitle className="text-xs font-medium text-muted-foreground">Makale</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-heading font-bold">{stats.total_articles}</div>
              </CardContent>
            </Card>
            <Card className="glass-card border-white/10">
              <CardHeader className="pb-2">
                <CardTitle className="text-xs font-medium text-muted-foreground">Aktif Site</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-heading font-bold text-neon-green">{stats.total_bonus_sites}</div>
              </CardContent>
            </Card>
            <Card className="glass-card border-white/10">
              <CardHeader className="pb-2">
                <CardTitle className="text-xs font-medium text-muted-foreground">Arşivli</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-heading font-bold text-muted-foreground">{stats.archived_sites}</div>
              </CardContent>
            </Card>
            <Card className="glass-card border-white/10">
              <CardHeader className="pb-2">
                <CardTitle className="text-xs font-medium text-muted-foreground">Görüntülenme</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-heading font-bold">{stats.total_views}</div>
              </CardContent>
            </Card>
            <Card className="glass-card border-white/10">
              <CardHeader className="pb-2">
                <CardTitle className="text-xs font-medium text-muted-foreground">İmpresyon</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-heading font-bold text-[#00F0FF]">{stats.total_impressions}</div>
              </CardContent>
            </Card>
            <Card className="glass-card border-white/10">
              <CardHeader className="pb-2">
                <CardTitle className="text-xs font-medium text-muted-foreground">Tıklama</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-heading font-bold text-neon-green">{stats.total_clicks}</div>
              </CardContent>
            </Card>
            <Card className="glass-card border-white/10">
              <CardHeader className="pb-2">
                <CardTitle className="text-xs font-medium text-muted-foreground">CTR</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-heading font-bold">
                  {stats.total_impressions > 0 
                    ? ((stats.total_clicks / stats.total_impressions) * 100).toFixed(1) 
                    : 0}%
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Main Tabs */}
        <Tabs defaultValue="performance" className="space-y-6">
          <TabsList className="grid grid-cols-5 w-full max-w-3xl">
            <TabsTrigger value="performance" data-testid="tab-performance">
              <TrendingUp className="w-4 h-4 mr-2" />
              Performans
            </TabsTrigger>
            <TabsTrigger value="sites" data-testid="tab-sites">
              <Gift className="w-4 h-4 mr-2" />
              Siteler
            </TabsTrigger>
            <TabsTrigger value="articles" data-testid="tab-articles">
              <FileText className="w-4 h-4 mr-2" />
              Makaleler
            </TabsTrigger>
            <TabsTrigger value="ai" data-testid="tab-ai">
              <Wand2 className="w-4 h-4 mr-2" />
              AI Araçları
            </TabsTrigger>
            <TabsTrigger value="seo" data-testid="tab-seo">
              <BarChart3 className="w-4 h-4 mr-2" />
              SEO Analiz
            </TabsTrigger>
          </TabsList>

          {/* Performance Tab */}
          <TabsContent value="performance" className="space-y-6">
            <Card className="glass-card border-white/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Award className="w-5 h-5 text-neon-green" />
                  AI Performans Sıralaması
                </CardTitle>
                <CardDescription>
                  Siteler performans verilerine göre otomatik sıralanmaktadır. 
                  Yeterli veri yoksa heuristic skor (bonus miktarı, çevrim şartı, popülerlik) kullanılır.
                </CardDescription>
              </CardHeader>
              <CardContent>
                {rankingReport && (
                  <div className="space-y-4">
                    {rankingReport.report.map((site, index) => (
                      <div 
                        key={index}
                        className="flex items-center gap-4 p-4 bg-background/50 rounded-lg"
                      >
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center shrink-0 ${
                          site.rank <= 2 ? 'bg-neon-green/20 border-2 border-neon-green' : 'bg-muted'
                        }`}>
                          <span className={`font-heading font-bold ${site.rank <= 2 ? 'text-neon-green' : ''}`}>
                            #{site.rank}
                          </span>
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <h4 className="font-medium">{site.name}</h4>
                            {site.is_featured && (
                              <Badge className="bg-yellow-500/20 text-yellow-500 text-xs">Öne Çıkan</Badge>
                            )}
                            <Badge variant="outline" className="text-xs">
                              {site.data_source === 'performance' ? 'Gerçek Veri' : 'Heuristic'}
                            </Badge>
                          </div>
                          <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                            <span>İmpresyon: {site.metrics.impressions}</span>
                            <span>Tıklama: {site.metrics.cta_clicks}</span>
                            <span>CTR: {site.metrics.ctr}%</span>
                            <span>Ort. Süre: {site.metrics.avg_time}s</span>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="font-heading text-2xl font-bold text-neon-green">
                            {site.performance_score}
                          </div>
                          <div className="text-xs text-muted-foreground">Performans Skoru</div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Bonus Sites Tab */}
          <TabsContent value="sites" className="space-y-6">
            {/* Add New Site Form */}
            <Card className="glass-card border-white/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Plus className="w-5 h-5" />
                  Yeni Site Ekle
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <Label>Site Adı</Label>
                    <Input
                      value={newSite.name}
                      onChange={(e) => setNewSite({ ...newSite, name: e.target.value })}
                      placeholder="Site adı"
                      data-testid="site-name-input"
                    />
                  </div>
                  <div>
                    <Label>Logo URL</Label>
                    <Input
                      value={newSite.logo_url}
                      onChange={(e) => setNewSite({ ...newSite, logo_url: e.target.value })}
                      placeholder="https://..."
                    />
                  </div>
                  <div>
                    <Label>Affiliate URL</Label>
                    <Input
                      value={newSite.affiliate_url}
                      onChange={(e) => setNewSite({ ...newSite, affiliate_url: e.target.value })}
                      placeholder="https://..."
                    />
                  </div>
                  <div>
                    <Label>Bonus Tipi</Label>
                    <Select 
                      value={newSite.bonus_type} 
                      onValueChange={(v) => setNewSite({ ...newSite, bonus_type: v })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="deneme">Deneme Bonusu</SelectItem>
                        <SelectItem value="hosgeldin">Hoşgeldin Bonusu</SelectItem>
                        <SelectItem value="yatirim">Yatırım Bonusu</SelectItem>
                        <SelectItem value="kayip">Kayıp Bonusu</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Bonus Miktarı</Label>
                    <Input
                      value={newSite.bonus_amount}
                      onChange={(e) => setNewSite({ ...newSite, bonus_amount: e.target.value })}
                      placeholder="500 TL veya %100"
                    />
                  </div>
                  <div>
                    <Label>Çevrim Şartı (x)</Label>
                    <Input
                      type="number"
                      value={newSite.turnover_requirement}
                      onChange={(e) => setNewSite({ ...newSite, turnover_requirement: parseFloat(e.target.value) })}
                    />
                  </div>
                  <div>
                    <Label>Rating (1-5)</Label>
                    <Input
                      type="number"
                      min="1"
                      max="5"
                      step="0.1"
                      value={newSite.rating}
                      onChange={(e) => setNewSite({ ...newSite, rating: parseFloat(e.target.value) })}
                    />
                  </div>
                  <div className="md:col-span-2">
                    <Label>Özellikler (virgülle ayırın)</Label>
                    <Input
                      value={newSite.features}
                      onChange={(e) => setNewSite({ ...newSite, features: e.target.value })}
                      placeholder="Hızlı Ödeme, 7/24 Destek, Mobil Uyumlu"
                    />
                  </div>
                </div>
                <Button onClick={handleCreateSite} className="bg-neon-green text-black hover:bg-neon-green/90" data-testid="create-site-btn">
                  <Plus className="w-4 h-4 mr-2" />
                  Site Ekle
                </Button>
              </CardContent>
            </Card>

            {/* Sites List */}
            <Card className="glass-card border-white/10">
              <CardHeader>
                <CardTitle>Mevcut Siteler ({bonusSites.length})</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {bonusSites.map((site) => (
                    <div 
                      key={site.id}
                      className="flex items-center justify-between p-4 bg-background/50 rounded-lg"
                    >
                      <div className="flex items-center gap-4">
                        <div className="w-8 h-8 rounded-full bg-neon-green/10 flex items-center justify-center">
                          <span className="font-heading text-sm font-bold text-neon-green">#{site.order}</span>
                        </div>
                        <img 
                          src={site.logo_url} 
                          alt={site.name}
                          className="w-12 h-12 rounded-lg object-cover"
                        />
                        <div>
                          <div className="flex items-center gap-2">
                            <h4 className="font-medium">{site.name}</h4>
                            {site.is_featured && (
                              <Badge className="bg-yellow-500/20 text-yellow-500 text-xs">Öne Çıkan</Badge>
                            )}
                          </div>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline">{site.bonus_type}</Badge>
                            <span className="text-sm text-neon-green">{site.bonus_amount}</span>
                            <span className="text-xs text-muted-foreground">Çevrim: {site.turnover_requirement}x</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleArchiveSite(site.id)}
                        >
                          <Archive className="w-4 h-4" />
                        </Button>
                        <Button 
                          variant="destructive" 
                          size="sm"
                          onClick={() => handleDeleteSite(site.id)}
                          data-testid={`delete-site-${site.id}`}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Articles Tab */}
          <TabsContent value="articles" className="space-y-6">
            <Card className="glass-card border-white/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Plus className="w-5 h-5" />
                  Yeni Makale Ekle
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="md:col-span-2">
                    <Label>Başlık</Label>
                    <Input
                      value={newArticle.title}
                      onChange={(e) => setNewArticle({ ...newArticle, title: e.target.value })}
                      placeholder="Makale başlığı"
                      data-testid="article-title-input"
                    />
                  </div>
                  <div>
                    <Label>Kategori</Label>
                    <Select 
                      value={newArticle.category} 
                      onValueChange={(v) => setNewArticle({ ...newArticle, category: v })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="bonus">Bonus</SelectItem>
                        <SelectItem value="spor">Spor</SelectItem>
                        <SelectItem value="analiz">Analiz</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Görsel URL</Label>
                    <Input
                      value={newArticle.image_url}
                      onChange={(e) => setNewArticle({ ...newArticle, image_url: e.target.value })}
                      placeholder="https://..."
                    />
                  </div>
                  <div className="md:col-span-2">
                    <Label>Özet</Label>
                    <Textarea
                      value={newArticle.excerpt}
                      onChange={(e) => setNewArticle({ ...newArticle, excerpt: e.target.value })}
                      placeholder="Kısa açıklama"
                      rows={2}
                    />
                  </div>
                  <div className="md:col-span-2">
                    <Label>İçerik (HTML destekli)</Label>
                    <Textarea
                      value={newArticle.content}
                      onChange={(e) => setNewArticle({ ...newArticle, content: e.target.value })}
                      placeholder="<h2>Başlık</h2><p>İçerik...</p>"
                      rows={6}
                    />
                  </div>
                  <div>
                    <Label>Etiketler (virgülle ayırın)</Label>
                    <Input
                      value={newArticle.tags}
                      onChange={(e) => setNewArticle({ ...newArticle, tags: e.target.value })}
                      placeholder="bonus, bahis, 2026"
                    />
                  </div>
                  <div>
                    <Label>SEO Başlık</Label>
                    <Input
                      value={newArticle.seo_title}
                      onChange={(e) => setNewArticle({ ...newArticle, seo_title: e.target.value })}
                      placeholder="SEO başlığı"
                    />
                  </div>
                </div>
                <Button onClick={handleCreateArticle} className="bg-neon-green text-black hover:bg-neon-green/90" data-testid="create-article-btn">
                  <Plus className="w-4 h-4 mr-2" />
                  Makale Ekle
                </Button>
              </CardContent>
            </Card>

            {/* Articles List */}
            <Card className="glass-card border-white/10">
              <CardHeader>
                <CardTitle>Mevcut Makaleler ({articles.length})</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {articles.map((article) => (
                    <div 
                      key={article.id}
                      className="flex items-center justify-between p-4 bg-background/50 rounded-lg"
                    >
                      <div className="flex items-center gap-4">
                        {article.image_url && (
                          <img 
                            src={article.image_url} 
                            alt={article.title}
                            className="w-16 h-12 rounded-lg object-cover"
                          />
                        )}
                        <div>
                          <h4 className="font-medium line-clamp-1">{article.title}</h4>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline">{article.category}</Badge>
                            <span className="text-xs text-muted-foreground">{article.view_count} görüntülenme</span>
                            {article.content_updated_at && (
                              <span className="text-xs text-neon-green">
                                Güncellendi: {new Date(article.content_updated_at).toLocaleDateString('tr-TR')}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleInternalLinkSuggestions(article.id)}
                        >
                          <Link2 className="w-4 h-4" />
                        </Button>
                        <Button 
                          variant="destructive" 
                          size="sm"
                          onClick={() => handleDeleteArticle(article.id)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* AI Tools Tab */}
          <TabsContent value="ai" className="space-y-6">
            <Card className="glass-card border-white/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Wand2 className="w-5 h-5 text-neon-green" />
                  AI İçerik Üretici
                </CardTitle>
                <CardDescription>
                  GPT-5.2 ile SEO uyumlu içerik üretin. İçeriklerin %80'i bilgilendirici, %20'si doğal affiliate yönlendirme içerir.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="md:col-span-2">
                    <Label>Konu</Label>
                    <Input
                      value={aiRequest.topic}
                      onChange={(e) => setAiRequest({ ...aiRequest, topic: e.target.value })}
                      placeholder="Hangi konuda içerik üretilsin?"
                      data-testid="ai-topic-input"
                    />
                  </div>
                  <div>
                    <Label>İçerik Tipi</Label>
                    <Select 
                      value={aiRequest.content_type} 
                      onValueChange={(v) => setAiRequest({ ...aiRequest, content_type: v })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="article">Makale</SelectItem>
                        <SelectItem value="match_summary">Maç Özeti</SelectItem>
                        <SelectItem value="seo_analysis">SEO Analizi</SelectItem>
                        <SelectItem value="competitor_analysis">Rakip Analizi</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Ton</Label>
                    <Select 
                      value={aiRequest.tone} 
                      onValueChange={(v) => setAiRequest({ ...aiRequest, tone: v })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="professional">Profesyonel</SelectItem>
                        <SelectItem value="casual">Samimi</SelectItem>
                        <SelectItem value="exciting">Heyecanlı</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Anahtar Kelimeler (virgülle ayırın)</Label>
                    <Input
                      value={aiRequest.keywords}
                      onChange={(e) => setAiRequest({ ...aiRequest, keywords: e.target.value })}
                      placeholder="deneme bonusu, bahis, 2026"
                    />
                  </div>
                  <div>
                    <Label>Kelime Sayısı</Label>
                    <Input
                      type="number"
                      value={aiRequest.word_count}
                      onChange={(e) => setAiRequest({ ...aiRequest, word_count: parseInt(e.target.value) })}
                    />
                  </div>
                </div>
                <Button 
                  onClick={handleGenerateContent} 
                  disabled={generating || !aiRequest.topic}
                  className="bg-neon-green text-black hover:bg-neon-green/90"
                  data-testid="generate-content-btn"
                >
                  {generating ? (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      Üretiliyor...
                    </>
                  ) : (
                    <>
                      <Wand2 className="w-4 h-4 mr-2" />
                      İçerik Üret
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Generated Content */}
            {generatedContent && (
              <Card className="glass-card border-white/10">
                <CardHeader>
                  <CardTitle>Üretilen İçerik / Analiz Sonucu</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="bg-background/50 rounded-lg p-6 whitespace-pre-wrap text-sm max-h-[500px] overflow-y-auto">
                    {generatedContent}
                  </div>
                  <Button 
                    variant="outline" 
                    className="mt-4"
                    onClick={() => navigator.clipboard.writeText(generatedContent)}
                  >
                    Kopyala
                  </Button>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* SEO Tab */}
          <TabsContent value="seo" className="space-y-6">
            {/* Competitor Analysis */}
            <Card className="glass-card border-white/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Globe className="w-5 h-5 text-[#00F0FF]" />
                  Rakip Domain Analizi
                </CardTitle>
                <CardDescription>
                  Rakip siteleri analiz edin, yapısal öneriler ve fırsat alanları keşfedin.
                  Kopyalama değil, özgün strateji önerileri alın.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-4">
                  <Input
                    value={competitorUrl}
                    onChange={(e) => setCompetitorUrl(e.target.value)}
                    placeholder="https://rakipsite.com"
                    className="flex-1"
                  />
                  <Button 
                    onClick={handleCompetitorAnalysis}
                    disabled={generating || !competitorUrl}
                    className="bg-[#00F0FF] text-black hover:bg-[#00F0FF]/90"
                  >
                    {generating ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Target className="w-4 h-4 mr-2" />}
                    Analiz Et
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Keyword Gap Analysis */}
            <Card className="glass-card border-white/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-neon-green" />
                  Anahtar Kelime Boşluğu Analizi
                </CardTitle>
                <CardDescription>
                  Mevcut anahtar kelimelerinizi girin, kaçırılan fırsatları ve içerik önerilerini alın.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-4">
                  <Input
                    value={keywordGapInput}
                    onChange={(e) => setKeywordGapInput(e.target.value)}
                    placeholder="deneme bonusu, bahis siteleri, casino bonusu"
                    className="flex-1"
                  />
                  <Button 
                    onClick={handleKeywordGapAnalysis}
                    disabled={generating || !keywordGapInput}
                  >
                    {generating ? <RefreshCw className="w-4 h-4 animate-spin" /> : <TrendingUp className="w-4 h-4 mr-2" />}
                    Analiz Et
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Weekly Report */}
            <Card className="glass-card border-white/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-yellow-500" />
                  Haftalık SEO Raporu
                </CardTitle>
                <CardDescription>
                  Performans özeti, içerik önerileri ve gelecek hafta için aksiyon planı.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button 
                  onClick={handleWeeklyReport}
                  disabled={generating}
                  className="bg-yellow-500 text-black hover:bg-yellow-500/90"
                >
                  {generating ? (
                    <>
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      Rapor Oluşturuluyor...
                    </>
                  ) : (
                    <>
                      <FileText className="w-4 h-4 mr-2" />
                      Haftalık Rapor Oluştur
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Internal Link Suggestions */}
            <Card className="glass-card border-white/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Link2 className="w-5 h-5 text-purple-500" />
                  İç Link Önerileri
                </CardTitle>
                <CardDescription>
                  Makaleler listesinden bir makale seçin, AI doğal iç link stratejisi önerecek.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {articles.slice(0, 5).map((article) => (
                    <div 
                      key={article.id}
                      className="flex items-center justify-between p-4 bg-background/50 rounded-lg"
                    >
                      <div>
                        <h4 className="font-medium">{article.title}</h4>
                        <span className="text-xs text-muted-foreground">{article.category}</span>
                      </div>
                      <Button 
                        variant="outline"
                        size="sm"
                        onClick={() => handleInternalLinkSuggestions(article.id)}
                        disabled={generating}
                      >
                        <Link2 className="w-4 h-4 mr-2" />
                        Link Öner
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default AdminPage;
