import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { API } from "@/App";
import { toast } from "sonner";
import {
  Plus, Trash2, Wand2, BarChart3, FileText, Gift, RefreshCw,
  Globe, TrendingUp, Target, Link2, Calendar, Server, Check,
  AlertCircle, Loader2, Copy, ExternalLink, Settings, LogOut,
  Activity, Sparkles, ToggleLeft, ToggleRight, Star
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";

const AdminPage = () => {
  const navigate = useNavigate();
  const adminUser = localStorage.getItem("admin_user") || "admin";

  const handleLogout = () => {
    localStorage.removeItem("admin_token");
    localStorage.removeItem("admin_user");
    toast.success("Çıkış yapıldı");
    navigate("/admin-login");
  };
  const [stats, setStats] = useState(null);
  const [domains, setDomains] = useState([]);
  const [bonusSites, setBonusSites] = useState([]);
  const [articles, setArticles] = useState([]);
  const [selectedDomain, setSelectedDomain] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState("");

  // Form states
  const [newDomain, setNewDomain] = useState({ domain_name: "", display_name: "", focus: "bonus", meta_title: "" });
  const [newSite, setNewSite] = useState({ name: "", logo_url: "", bonus_type: "deneme", bonus_amount: "", affiliate_url: "", rating: 4.5, features: "", turnover_requirement: 10 });
  const [aiTopic, setAiTopic] = useState("");
  const [competitorUrl, setCompetitorUrl] = useState("");

  useEffect(() => { fetchData(); }, [selectedDomain]);

  const fetchData = async () => {
    try {
      const [statsRes, domainsRes, sitesRes, articlesRes] = await Promise.all([
        axios.get(`${API}/stats/dashboard${selectedDomain ? `?domain_id=${selectedDomain}` : ''}`),
        axios.get(`${API}/domains`),
        axios.get(`${API}/bonus-sites`),
        axios.get(`${API}/articles?limit=20`)
      ]);
      setStats(statsRes.data);
      setDomains(domainsRes.data);
      setBonusSites(sitesRes.data);
      setArticles(articlesRes.data);
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDomain = async () => {
    if (!newDomain.domain_name) return toast.error("Domain adı gerekli");
    try {
      setGenerating(true);
      const res = await axios.post(`${API}/domains`, newDomain);
      toast.success(`${res.data.domain_name} oluşturuldu!`);
      if (res.data.nameservers?.length > 0) {
        toast.info(`Nameservers: ${res.data.nameservers.join(', ')}`);
      }
      setNewDomain({ domain_name: "", display_name: "", focus: "bonus", meta_title: "" });
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || "Domain oluşturulamadı");
    } finally {
      setGenerating(false);
    }
  };

  const handleDeleteDomain = async (domainId) => {
    if (!confirm("Bu domain ve tüm verileri silinecek. Emin misiniz?")) return;
    try {
      await axios.delete(`${API}/domains/${domainId}`);
      toast.success("Domain silindi");
      fetchData();
    } catch (error) {
      toast.error("Silinemedi");
    }
  };

  const handleCreateSite = async () => {
    if (!newSite.name || !newSite.affiliate_url) return toast.error("Site adı ve URL gerekli");
    try {
      await axios.post(`${API}/bonus-sites`, {
        ...newSite,
        features: newSite.features.split(',').map(f => f.trim()).filter(f => f)
      });
      toast.success("Site eklendi");
      setNewSite({ name: "", logo_url: "", bonus_type: "deneme", bonus_amount: "", affiliate_url: "", rating: 4.5, features: "", turnover_requirement: 10 });
      fetchData();
    } catch (error) {
      toast.error("Site eklenemedi");
    }
  };

  const handleAutoGenerate = async (type) => {
    setGenerating(true);
    try {
      let res;
      if (type === "article") {
        res = await axios.post(`${API}/auto-content/generate-article`, null, { params: { domain_id: selectedDomain, topic: aiTopic || "Deneme Bonusu Rehberi 2026" } });
      } else if (type === "news") {
        res = await axios.post(`${API}/auto-content/generate-news`, null, { params: { domain_id: selectedDomain } });
      } else if (type === "bulk") {
        res = await axios.post(`${API}/auto-content/bulk-generate`, null, { params: { domain_id: selectedDomain, count: 5 } });
      }
      toast.success(`${res.data.status === "created" ? "İçerik oluşturuldu" : res.data.status}`);
      fetchData();
    } catch (error) {
      toast.error("Oluşturulamadı");
    } finally {
      setGenerating(false);
    }
  };

  const handleCompetitorAnalysis = async () => {
    if (!competitorUrl) return;
    setGenerating(true);
    try {
      const res = await axios.post(`${API}/ai/competitor-analysis`, { competitor_url: competitorUrl });
      setGeneratedContent(res.data.analysis);
      toast.success("Analiz tamamlandı");
    } catch (error) {
      toast.error("Analiz yapılamadı");
    } finally {
      setGenerating(false);
    }
  };

  const handleWeeklyReport = async () => {
    setGenerating(true);
    try {
      const res = await axios.get(`${API}/ai/weekly-seo-report${selectedDomain ? `?domain_id=${selectedDomain}` : ''}`);
      setGeneratedContent(res.data.report);
      toast.success("Rapor oluşturuldu");
    } catch (error) {
      toast.error("Rapor oluşturulamadı");
    } finally {
      setGenerating(false);
    }
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-neon-green" /></div>;

  return (
    <div className="min-h-screen py-8 px-6" data-testid="admin-page">
      <div className="container mx-auto max-w-7xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="font-heading text-3xl md:text-4xl font-bold tracking-tight uppercase">Multi-Tenant Admin</h1>
            <p className="text-muted-foreground mt-1">Çoklu domain yönetimi ve AI otomasyon</p>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm text-muted-foreground hidden md:block">
              Hoş geldin, <strong>{adminUser}</strong>
            </span>
            <Select value={selectedDomain || "all"} onValueChange={(v) => setSelectedDomain(v === "all" ? null : v)}>
              <SelectTrigger className="w-48">
                <SelectValue placeholder="Domain Seç" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tüm Domainler</SelectItem>
                {domains.map(d => <SelectItem key={d.id} value={d.id}>{d.domain_name}</SelectItem>)}
              </SelectContent>
            </Select>
            <Button onClick={fetchData} variant="outline" size="icon"><RefreshCw className="w-4 h-4" /></Button>
            <Button
              onClick={handleLogout}
              variant="outline"
              size="icon"
              data-testid="admin-logout-btn"
              title="Çıkış Yap"
            >
              <LogOut className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <Card className="glass-card border-white/10">
              <CardHeader className="pb-2"><CardTitle className="text-xs text-muted-foreground">Domainler</CardTitle></CardHeader>
              <CardContent><div className="text-3xl font-heading font-bold text-neon-green">{stats.total_domains}</div></CardContent>
            </Card>
            <Card className="glass-card border-white/10">
              <CardHeader className="pb-2"><CardTitle className="text-xs text-muted-foreground">Bonus Siteleri</CardTitle></CardHeader>
              <CardContent><div className="text-3xl font-heading font-bold">{stats.total_bonus_sites}</div></CardContent>
            </Card>
            <Card className="glass-card border-white/10">
              <CardHeader className="pb-2"><CardTitle className="text-xs text-muted-foreground">Makaleler</CardTitle></CardHeader>
              <CardContent><div className="text-3xl font-heading font-bold">{stats.total_articles}</div></CardContent>
            </Card>
            <Card className="glass-card border-white/10">
              <CardHeader className="pb-2"><CardTitle className="text-xs text-muted-foreground">Auto Generated</CardTitle></CardHeader>
              <CardContent><div className="text-3xl font-heading font-bold text-[#00F0FF]">{stats.auto_generated_articles}</div></CardContent>
            </Card>
          </div>
        )}

        {/* Tabs */}
        <Tabs defaultValue="domains" className="space-y-6">
          <TabsList className="grid grid-cols-6 w-full max-w-4xl">
            <TabsTrigger value="domains"><Globe className="w-4 h-4 mr-2" />Domainler</TabsTrigger>
            <TabsTrigger value="sites"><Gift className="w-4 h-4 mr-2" />Siteler</TabsTrigger>
            <TabsTrigger value="auto-content"><Wand2 className="w-4 h-4 mr-2" />Oto İçerik</TabsTrigger>
            <TabsTrigger value="articles"><FileText className="w-4 h-4 mr-2" />Makaleler</TabsTrigger>
            <TabsTrigger value="seo"><BarChart3 className="w-4 h-4 mr-2" />SEO</TabsTrigger>
            <TabsTrigger value="matches"><Activity className="w-4 h-4 mr-2" />Maçlar</TabsTrigger>
          </TabsList>

          {/* DOMAINS TAB */}
          <TabsContent value="domains" className="space-y-6">
            <Card className="glass-card border-white/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2"><Plus className="w-5 h-5" />Yeni Domain Ekle</CardTitle>
                <CardDescription>Domain eklendiğinde Cloudflare'da zone oluşturulur, DNS kayıtları ve SSL otomatik ayarlanır.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div>
                    <Label>Domain Adı</Label>
                    <Input value={newDomain.domain_name} onChange={(e) => setNewDomain({...newDomain, domain_name: e.target.value})} placeholder="example.com" />
                  </div>
                  <div>
                    <Label>Görünen Ad</Label>
                    <Input value={newDomain.display_name} onChange={(e) => setNewDomain({...newDomain, display_name: e.target.value})} placeholder="Example Site" />
                  </div>
                  <div>
                    <Label>Odak</Label>
                    <Select value={newDomain.focus} onValueChange={(v) => setNewDomain({...newDomain, focus: v})}>
                      <SelectTrigger><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="bonus">Bonus</SelectItem>
                        <SelectItem value="spor">Spor</SelectItem>
                        <SelectItem value="hibrit">Hibrit</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label>Meta Title</Label>
                    <Input value={newDomain.meta_title} onChange={(e) => setNewDomain({...newDomain, meta_title: e.target.value})} placeholder="SEO başlık" />
                  </div>
                </div>
                <Button onClick={handleCreateDomain} disabled={generating} className="bg-neon-green text-black hover:bg-neon-green/90">
                  {generating ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Oluşturuluyor...</> : <><Plus className="w-4 h-4 mr-2" />Domain Oluştur</>}
                </Button>
              </CardContent>
            </Card>

            <Card className="glass-card border-white/10">
              <CardHeader><CardTitle>Mevcut Domainler ({domains.length})</CardTitle></CardHeader>
              <CardContent>
                {domains.length === 0 ? (
                  <p className="text-muted-foreground text-center py-8">Henüz domain eklenmemiş</p>
                ) : (
                  <div className="space-y-3">
                    {domains.map((domain) => (
                      <div key={domain.id} className="flex items-center justify-between p-4 bg-background/50 rounded-lg">
                        <div className="flex items-center gap-4">
                          <div className={`w-3 h-3 rounded-full ${domain.cloudflare_status === 'active' ? 'bg-neon-green' : 'bg-yellow-500'}`} />
                          <div>
                            <div className="flex items-center gap-2">
                              <h4 className="font-medium">{domain.domain_name}</h4>
                              <Badge variant="outline">{domain.focus}</Badge>
                              <Badge className={domain.ssl_status === 'active' ? 'bg-neon-green/20 text-neon-green' : 'bg-yellow-500/20 text-yellow-500'}>
                                SSL: {domain.ssl_status}
                              </Badge>
                            </div>
                            {domain.nameservers?.length > 0 && (
                              <p className="text-xs text-muted-foreground mt-1">NS: {domain.nameservers.join(', ')}</p>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Button variant="outline" size="sm" onClick={() => navigator.clipboard.writeText(domain.nameservers?.join('\n') || '')}>
                            <Copy className="w-4 h-4" />
                          </Button>
                          <Button variant="destructive" size="sm" onClick={() => handleDeleteDomain(domain.id)}>
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* SITES TAB */}
          <TabsContent value="sites" className="space-y-6">
            <Card className="glass-card border-white/10">
              <CardHeader><CardTitle><Plus className="w-5 h-5 inline mr-2" />Yeni Bonus Sitesi</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Input placeholder="Site Adı" value={newSite.name} onChange={(e) => setNewSite({...newSite, name: e.target.value})} />
                  <Input placeholder="Logo URL" value={newSite.logo_url} onChange={(e) => setNewSite({...newSite, logo_url: e.target.value})} />
                  <Input placeholder="Affiliate URL" value={newSite.affiliate_url} onChange={(e) => setNewSite({...newSite, affiliate_url: e.target.value})} />
                  <Select value={newSite.bonus_type} onValueChange={(v) => setNewSite({...newSite, bonus_type: v})}>
                    <SelectTrigger><SelectValue /></SelectTrigger>
                    <SelectContent>
                      <SelectItem value="deneme">Deneme</SelectItem>
                      <SelectItem value="hosgeldin">Hoşgeldin</SelectItem>
                      <SelectItem value="yatirim">Yatırım</SelectItem>
                      <SelectItem value="kayip">Kayıp</SelectItem>
                    </SelectContent>
                  </Select>
                  <Input placeholder="Bonus Miktarı (500 TL)" value={newSite.bonus_amount} onChange={(e) => setNewSite({...newSite, bonus_amount: e.target.value})} />
                  <Input placeholder="Özellikler (virgülle)" value={newSite.features} onChange={(e) => setNewSite({...newSite, features: e.target.value})} />
                </div>
                <Button onClick={handleCreateSite} className="bg-neon-green text-black hover:bg-neon-green/90"><Plus className="w-4 h-4 mr-2" />Site Ekle</Button>
              </CardContent>
            </Card>

            <Card className="glass-card border-white/10">
              <CardHeader><CardTitle>Global Siteler ({bonusSites.length})</CardTitle></CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {bonusSites.map((site) => (
                    <div key={site.id} className="flex items-center justify-between p-3 bg-background/50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <img src={site.logo_url} alt={site.name} className="w-10 h-10 rounded-lg object-cover" />
                        <div>
                          <h4 className="font-medium">{site.name}</h4>
                          <div className="flex gap-2"><Badge variant="outline">{site.bonus_type}</Badge><span className="text-neon-green text-sm">{site.bonus_amount}</span></div>
                        </div>
                      </div>
                      <a href={site.affiliate_url} target="_blank" rel="noopener noreferrer" className="text-muted-foreground hover:text-foreground">
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* AUTO CONTENT TAB */}
          <TabsContent value="auto-content" className="space-y-6">
            <Card className="glass-card border-white/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2"><Wand2 className="w-5 h-5 text-neon-green" />Otomatik İçerik Motoru</CardTitle>
                <CardDescription>AI ile SEO uyumlu içerik üretin. %80 bilgilendirici, %20 doğal affiliate.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label>Makale Konusu</Label>
                    <Input value={aiTopic} onChange={(e) => setAiTopic(e.target.value)} placeholder="Deneme Bonusu Rehberi 2026" />
                  </div>
                  <div className="flex items-end gap-2">
                    <Button onClick={() => handleAutoGenerate("article")} disabled={generating} className="flex-1">
                      {generating ? <Loader2 className="w-4 h-4 animate-spin" /> : <><FileText className="w-4 h-4 mr-2" />Makale Üret</>}
                    </Button>
                    <Button onClick={() => handleAutoGenerate("news")} disabled={generating} variant="outline">
                      <TrendingUp className="w-4 h-4 mr-2" />Haber Üret
                    </Button>
                  </div>
                </div>
                <div className="border-t border-white/10 pt-4">
                  <Button onClick={() => handleAutoGenerate("bulk")} disabled={generating} variant="secondary" className="w-full">
                    {generating ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <><Wand2 className="w-4 h-4 mr-2" /></>}
                    Toplu İçerik Üret (5 Makale)
                  </Button>
                </div>
              </CardContent>
            </Card>

            {generatedContent && (
              <Card className="glass-card border-white/10">
                <CardHeader><CardTitle>Sonuç</CardTitle></CardHeader>
                <CardContent>
                  <div className="bg-background/50 rounded-lg p-4 max-h-96 overflow-y-auto whitespace-pre-wrap text-sm">{generatedContent}</div>
                  <Button variant="outline" className="mt-4" onClick={() => navigator.clipboard.writeText(generatedContent)}>Kopyala</Button>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* ARTICLES TAB */}
          <TabsContent value="articles" className="space-y-6">
            <Card className="glass-card border-white/10">
              <CardHeader><CardTitle>Son Makaleler ({articles.length})</CardTitle></CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {articles.map((article) => (
                    <div key={article.id} className="flex items-center justify-between p-3 bg-background/50 rounded-lg">
                      <div>
                        <h4 className="font-medium">{article.title}</h4>
                        <div className="flex gap-2 mt-1">
                          <Badge variant="outline">{article.category}</Badge>
                          {article.is_auto_generated && <Badge className="bg-[#00F0FF]/20 text-[#00F0FF]">Auto</Badge>}
                          <span className="text-xs text-muted-foreground">{article.view_count} görüntülenme</span>
                        </div>
                      </div>
                      <Badge>{article.schema_type}</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          {/* SEO TAB */}
          <TabsContent value="seo" className="space-y-6">
            <Card className="glass-card border-white/10">
              <CardHeader><CardTitle><Target className="w-5 h-5 inline mr-2 text-[#00F0FF]" />Rakip Analizi</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <div className="flex gap-4">
                  <Input value={competitorUrl} onChange={(e) => setCompetitorUrl(e.target.value)} placeholder="https://rakipsite.com" className="flex-1" />
                  <Button onClick={handleCompetitorAnalysis} disabled={generating} className="bg-[#00F0FF] text-black hover:bg-[#00F0FF]/90">
                    {generating ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Target className="w-4 h-4 mr-2" />Analiz</>}
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card className="glass-card border-white/10">
              <CardHeader><CardTitle><Calendar className="w-5 h-5 inline mr-2 text-yellow-500" />Haftalık SEO Raporu</CardTitle></CardHeader>
              <CardContent>
                <Button onClick={handleWeeklyReport} disabled={generating} className="bg-yellow-500 text-black hover:bg-yellow-500/90">
                  {generating ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <><FileText className="w-4 h-4 mr-2" /></>}
                  Rapor Oluştur
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </motion.div>
  );
      </div>
    </div>
  );
};

export default AdminPage;
