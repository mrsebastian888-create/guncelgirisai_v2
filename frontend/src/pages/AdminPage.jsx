import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import axios from "axios";
import { API } from "@/App";
import { toast } from "sonner";
import {
  Settings, Plus, Trash2, Edit, Save, Wand2, BarChart3,
  FileText, Gift, Activity, RefreshCw, ChevronDown, ChevronUp
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";

const AdminPage = () => {
  const [stats, setStats] = useState(null);
  const [bonusSites, setBonusSites] = useState([]);
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState("");

  // Form states
  const [newSite, setNewSite] = useState({
    name: "", logo_url: "", bonus_type: "deneme", bonus_amount: "",
    affiliate_url: "", rating: 4.5, features: [], is_featured: false, order: 0
  });
  const [newArticle, setNewArticle] = useState({
    title: "", excerpt: "", content: "", category: "bonus",
    tags: [], image_url: "", seo_title: "", seo_description: ""
  });
  const [aiRequest, setAiRequest] = useState({
    topic: "", content_type: "article", keywords: "", tone: "professional", word_count: 800
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [statsRes, sitesRes, articlesRes] = await Promise.all([
        axios.get(`${API}/stats/dashboard`),
        axios.get(`${API}/bonus-sites?limit=50`),
        axios.get(`${API}/articles?limit=50`)
      ]);
      setStats(statsRes.data);
      setBonusSites(sitesRes.data);
      setArticles(articlesRes.data);
    } catch (error) {
      console.error("Error fetching data:", error);
      toast.error("Veri yüklenirken hata oluştu");
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSite = async () => {
    try {
      const siteData = {
        ...newSite,
        features: newSite.features.length > 0 ? newSite.features : []
      };
      await axios.post(`${API}/bonus-sites`, siteData);
      toast.success("Bonus sitesi eklendi");
      fetchData();
      setNewSite({
        name: "", logo_url: "", bonus_type: "deneme", bonus_amount: "",
        affiliate_url: "", rating: 4.5, features: [], is_featured: false, order: 0
      });
    } catch (error) {
      toast.error("Site eklenirken hata oluştu");
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

  const handleGetSeoSuggestions = async (articleId) => {
    try {
      const response = await axios.post(`${API}/ai/seo-suggestions?article_id=${articleId}`);
      toast.success("SEO önerileri alındı");
      setGeneratedContent(response.data.suggestions);
    } catch (error) {
      toast.error("SEO analizi yapılırken hata oluştu");
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
            <p className="text-muted-foreground mt-1">İçerik yönetimi ve AI araçları</p>
          </div>
          <Button onClick={fetchData} variant="outline" data-testid="refresh-btn">
            <RefreshCw className="w-4 h-4 mr-2" />
            Yenile
          </Button>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <Card className="glass-card border-white/10">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Toplam Makale
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-heading font-bold">{stats.total_articles}</div>
              </CardContent>
            </Card>
            <Card className="glass-card border-white/10">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Bonus Siteleri
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-heading font-bold">{stats.total_bonus_sites}</div>
              </CardContent>
            </Card>
            <Card className="glass-card border-white/10">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Yayında
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-heading font-bold text-neon-green">{stats.published_articles}</div>
              </CardContent>
            </Card>
            <Card className="glass-card border-white/10">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Toplam Görüntülenme
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-heading font-bold">{stats.total_views}</div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Main Tabs */}
        <Tabs defaultValue="sites" className="space-y-6">
          <TabsList className="grid grid-cols-4 w-full max-w-xl">
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
              SEO
            </TabsTrigger>
          </TabsList>

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
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
                      placeholder="500 TL"
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
                </div>
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <Switch
                      checked={newSite.is_featured}
                      onCheckedChange={(v) => setNewSite({ ...newSite, is_featured: v })}
                    />
                    <Label>Öne Çıkan</Label>
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
                        <img 
                          src={site.logo_url} 
                          alt={site.name}
                          className="w-12 h-12 rounded-lg object-cover"
                        />
                        <div>
                          <h4 className="font-medium">{site.name}</h4>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline">{site.bonus_type}</Badge>
                            <span className="text-sm text-neon-green">{site.bonus_amount}</span>
                          </div>
                        </div>
                      </div>
                      <Button 
                        variant="destructive" 
                        size="sm"
                        onClick={() => handleDeleteSite(site.id)}
                        data-testid={`delete-site-${site.id}`}
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* Articles Tab */}
          <TabsContent value="articles" className="space-y-6">
            {/* Add New Article Form */}
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
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => handleGetSeoSuggestions(article.id)}
                        >
                          <BarChart3 className="w-4 h-4" />
                        </Button>
                        <Button 
                          variant="destructive" 
                          size="sm"
                          onClick={() => handleDeleteArticle(article.id)}
                          data-testid={`delete-article-${article.id}`}
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
                <CardDescription>GPT-5.2 ile SEO uyumlu içerik üretin</CardDescription>
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
                  <CardTitle>Üretilen İçerik</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="bg-background/50 rounded-lg p-6 whitespace-pre-wrap text-sm">
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
            <Card className="glass-card border-white/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-[#00F0FF]" />
                  SEO Analiz Araçları
                </CardTitle>
                <CardDescription>Makaleleriniz için AI destekli SEO önerileri alın</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground mb-4">
                  Mevcut makaleler listesinden bir makale seçin ve SEO analizi butonuna tıklayın.
                  AI, içeriğiniz için başlık iyileştirmeleri, iç link önerileri ve anahtar kelime 
                  tavsiyeleri sunacaktır.
                </p>
                <div className="space-y-3">
                  {articles.slice(0, 5).map((article) => (
                    <div 
                      key={article.id}
                      className="flex items-center justify-between p-4 bg-background/50 rounded-lg"
                    >
                      <div>
                        <h4 className="font-medium">{article.title}</h4>
                        <span className="text-xs text-muted-foreground">{article.slug}</span>
                      </div>
                      <Button 
                        variant="outline"
                        onClick={() => handleGetSeoSuggestions(article.id)}
                        data-testid={`seo-analyze-${article.id}`}
                      >
                        <BarChart3 className="w-4 h-4 mr-2" />
                        Analiz Et
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
