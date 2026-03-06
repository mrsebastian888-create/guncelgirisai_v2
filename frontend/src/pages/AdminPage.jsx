import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";
import { API } from "@/App";
import { toast } from "sonner";
import {
  Plus, Trash2, Wand2, BarChart3, FileText, RefreshCw,
  Globe, TrendingUp, Target, Server, AlertCircle, Loader2,
  Copy, ExternalLink, LogOut, Activity, Sparkles, Star,
  Search, Edit2, Save, X, Eye, ChevronDown, ChevronUp,
  Gift, Calendar, ArrowUp, ArrowDown, Layers, Image,
  Play, Pause, Clock, ListChecks, Zap, Download, Check, Building2,
  Send, Bot, Users, Radio, MessageSquare, Settings
} from "lucide-react";
import SeoAssistant from "@/components/SeoAssistant";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";


/* ── CATEGORIES TAB ──────────────────────────────── */
function CategoriesTab({ onRefresh }) {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState(null);
  const [editData, setEditData] = useState({});
  const [saving, setSaving] = useState(false);
  const [newCat, setNewCat] = useState({ name: "", type: "bonus", image: "", description: "" });

  useEffect(() => { fetchCats(); }, []);

  const fetchCats = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/categories`);
      setCategories(res.data);
    } catch { toast.error("Kategoriler yüklenemedi"); }
    finally { setLoading(false); }
  };

  const handleCreate = async () => {
    if (!newCat.name) return toast.error("Kategori adı gerekli");
    try {
      await axios.post(`${API}/categories`, newCat);
      toast.success("Kategori eklendi");
      setNewCat({ name: "", type: "bonus", image: "", description: "" });
      fetchCats();
    } catch { toast.error("Eklenemedi"); }
  };

  const handleDelete = async (id, name) => {
    if (!confirm(`"${name}" silinecek?`)) return;
    try {
      await axios.delete(`${API}/categories/${id}`);
      toast.success("Kategori silindi");
      fetchCats();
    } catch { toast.error("Silinemedi"); }
  };

  const startEdit = (cat) => {
    setEditingId(cat.id);
    setEditData({ name: cat.name, type: cat.type, image: cat.image || "", description: cat.description || "", is_active: cat.is_active !== false });
  };

  const handleSaveEdit = async () => {
    setSaving(true);
    try {
      await axios.put(`${API}/categories/${editingId}`, editData);
      toast.success("Kategori güncellendi");
      setEditingId(null);
      fetchCats();
    } catch { toast.error("Güncellenemedi"); }
    finally { setSaving(false); }
  };

  const handleMove = async (index, dir) => {
    const newOrder = [...categories];
    const targetIdx = index + dir;
    if (targetIdx < 0 || targetIdx >= newOrder.length) return;
    [newOrder[index], newOrder[targetIdx]] = [newOrder[targetIdx], newOrder[index]];
    try {
      await axios.post(`${API}/categories/reorder`, { order: newOrder.map(c => c.id) });
      fetchCats();
    } catch { toast.error("Sıralama başarısız"); }
  };

  if (loading) return <div className="flex justify-center py-10"><Loader2 className="w-6 h-6 animate-spin" /></div>;

  return (
    <div className="space-y-6" data-testid="categories-tab">
      {/* Create Form */}
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><Plus className="w-5 h-5" />Yeni Kategori</CardTitle>
          <CardDescription>Ana sayfadaki kategori slider'ına yeni kategori ekleyin.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Input value={newCat.name} onChange={(e) => setNewCat({ ...newCat, name: e.target.value })} placeholder="Kategori Adı" data-testid="new-category-name" />
            <Select value={newCat.type} onValueChange={(v) => setNewCat({ ...newCat, type: v })}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="bonus">Bonus</SelectItem>
                <SelectItem value="spor">Spor</SelectItem>
                <SelectItem value="casino">Casino</SelectItem>
              </SelectContent>
            </Select>
            <Input value={newCat.image} onChange={(e) => setNewCat({ ...newCat, image: e.target.value })} placeholder="Görsel URL" />
            <Input value={newCat.description} onChange={(e) => setNewCat({ ...newCat, description: e.target.value })} placeholder="Açıklama" />
          </div>
          <Button onClick={handleCreate} className="bg-neon-green text-black hover:bg-neon-green/90" data-testid="create-category-btn">
            <Plus className="w-4 h-4 mr-2" />Kategori Ekle
          </Button>
        </CardContent>
      </Card>

      {/* Categories List */}
      <Card className="glass-card border-white/10">
        <CardHeader><CardTitle>Kategoriler ({categories.length})</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-2">
            {categories.map((cat, idx) => (
              <div key={cat.id} className="rounded-lg border p-4" style={{ borderColor: "rgba(255,255,255,0.08)" }} data-testid={`category-row-${cat.id}`}>
                {editingId === cat.id ? (
                  <div className="space-y-3">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                      <Input value={editData.name} onChange={(e) => setEditData({ ...editData, name: e.target.value })} placeholder="Kategori Adı" />
                      <Select value={editData.type} onValueChange={(v) => setEditData({ ...editData, type: v })}>
                        <SelectTrigger><SelectValue /></SelectTrigger>
                        <SelectContent>
                          <SelectItem value="bonus">Bonus</SelectItem>
                          <SelectItem value="spor">Spor</SelectItem>
                          <SelectItem value="casino">Casino</SelectItem>
                        </SelectContent>
                      </Select>
                      <Input value={editData.image} onChange={(e) => setEditData({ ...editData, image: e.target.value })} placeholder="Görsel URL" />
                      <Input value={editData.description} onChange={(e) => setEditData({ ...editData, description: e.target.value })} placeholder="Açıklama" />
                    </div>
                    <div className="flex items-center gap-3">
                      <Switch checked={editData.is_active} onCheckedChange={(v) => setEditData({ ...editData, is_active: v })} />
                      <span className="text-sm">{editData.is_active ? "Aktif" : "Gizli"}</span>
                      <div className="flex gap-2 ml-auto">
                        <Button size="sm" onClick={handleSaveEdit} disabled={saving} className="bg-neon-green text-black">
                          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Save className="w-4 h-4 mr-1" />Kaydet</>}
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => setEditingId(null)}><X className="w-4 h-4 mr-1" />İptal</Button>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="flex flex-col gap-0.5 shrink-0">
                        <Button variant="ghost" size="icon" className="h-5 w-5" onClick={() => handleMove(idx, -1)} disabled={idx === 0}>
                          <ArrowUp className="w-3 h-3" />
                        </Button>
                        <span className="text-xs text-center text-muted-foreground">{idx + 1}</span>
                        <Button variant="ghost" size="icon" className="h-5 w-5" onClick={() => handleMove(idx, 1)} disabled={idx === categories.length - 1}>
                          <ArrowDown className="w-3 h-3" />
                        </Button>
                      </div>
                      {cat.image && <img src={cat.image} alt={cat.name} className="w-16 h-10 rounded-lg object-cover" onError={(e) => { e.target.style.display = "none"; }} />}
                      <div>
                        <div className="flex items-center gap-2">
                          <h4 className="font-medium">{cat.name}</h4>
                          <Badge variant="outline">{cat.type}</Badge>
                          {cat.is_active === false && <Badge className="bg-yellow-500/20 text-yellow-500 text-xs">Gizli</Badge>}
                        </div>
                        {cat.description && <p className="text-xs text-muted-foreground mt-0.5">{cat.description}</p>}
                      </div>
                    </div>
                    <div className="flex items-center gap-1 shrink-0">
                      <Button variant="ghost" size="sm" onClick={() => startEdit(cat)}><Edit2 className="w-4 h-4" /></Button>
                      <Button variant="ghost" size="sm" onClick={() => handleDelete(cat.id, cat.name)}><Trash2 className="w-4 h-4 text-red-400" /></Button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

/* ── MATCHES ADMIN TAB ───────────────────────────── */
function MatchesAdminTab() {
  const [status, setStatus] = useState(null);
  const [matches, setMatches] = useState([]);
  const [aiEnabled, setAiEnabled] = useState(true);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchStatus = async () => {
    try {
      const [statusRes, scoresRes] = await Promise.all([
        axios.get(`${API}/admin/api-status`),
        axios.get(`${API}/sports/scores`),
      ]);
      setStatus(statusRes.data);
      setMatches(scoresRes.data.matches || []);
      setAiEnabled(statusRes.data.ai_insight_enabled);
    } catch { toast.error("API durumu alınamadı"); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchStatus(); }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await axios.post(`${API}/admin/refresh-scores`);
      await fetchStatus();
      toast.success("Maç verileri yenilendi");
    } catch { toast.error("Yenileme başarısız"); }
    finally { setRefreshing(false); }
  };

  const handleAiToggle = async (val) => {
    try {
      await axios.post(`${API}/admin/ai-toggle`, { enabled: val });
      setAiEnabled(val);
      toast.success(`AI analiz ${val ? "açıldı" : "kapatıldı"}`);
    } catch { toast.error("Toggle başarısız"); }
  };

  const handleSetFeatured = async (matchId) => {
    try {
      await axios.post(`${API}/admin/featured-match`, { match_id: matchId });
      toast.success("Öne çıkan maç güncellendi");
      await fetchStatus();
    } catch { toast.error("İşlem başarısız"); }
  };

  if (loading) return <div className="flex justify-center py-10"><Loader2 className="w-6 h-6 animate-spin" /></div>;

  return (
    <div className="space-y-6">
      <Card className="glass-card border-white/10">
        <CardHeader><CardTitle className="flex items-center gap-2"><Server className="w-5 h-5" />API Durumu</CardTitle></CardHeader>
        <CardContent>
          {status && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              {[
                { label: "Durum", value: status.odds_api_configured ? "Aktif" : "Kapalı", dot: status.odds_api_configured },
                { label: "Cache Yaşı", value: `${status.cache_age_seconds}s${status.is_stale ? " (Eski)" : ""}` },
                { label: "Maç Sayısı", value: status.cached_match_count },
                { label: "Hata", value: status.error_count, isError: status.error_count > 0 },
              ].map((s, i) => (
                <div key={i} className="rounded-lg border p-3" style={{ borderColor: "rgba(255,255,255,0.08)" }}>
                  <p className="text-xs text-muted-foreground">{s.label}</p>
                  <div className="flex items-center gap-1.5 mt-1">
                    {s.dot !== undefined && <span className={`w-2 h-2 rounded-full ${s.dot ? "bg-green-500" : "bg-red-500"}`} />}
                    <span className="font-bold" style={s.isError ? { color: "#EF4444" } : {}}>{s.value}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
          <Button onClick={handleRefresh} disabled={refreshing} size="sm" variant="outline" className="mt-4">
            {refreshing ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <RefreshCw className="w-4 h-4 mr-2" />}Veriyi Yenile
          </Button>
        </CardContent>
      </Card>

      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><Sparkles className="w-5 h-5" />AI Analiz</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-3">
            <Switch checked={aiEnabled} onCheckedChange={handleAiToggle} data-testid="ai-toggle-switch" />
            <span className="text-sm">{aiEnabled ? "AI Analiz Açık" : "AI Analiz Kapalı"}</span>
          </div>
        </CardContent>
      </Card>

      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><Star className="w-5 h-5" />Öne Çıkan Maç</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <Button variant="outline" size="sm" onClick={() => handleSetFeatured(null)}>Otomatik Seçim</Button>
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {matches.map((m) => (
              <div key={m.id} className="flex items-center justify-between rounded-lg border p-3" data-testid={`featured-match-row-${m.id}`}
                style={{ borderColor: status?.featured_match_override === m.id ? "rgba(0,255,135,0.4)" : "rgba(255,255,255,0.08)", background: status?.featured_match_override === m.id ? "rgba(0,255,135,0.05)" : "transparent" }}>
                <div>
                  <p className="text-sm font-semibold">{m.home_team} vs {m.away_team}</p>
                  <p className="text-xs text-muted-foreground">{m.sport_title}</p>
                </div>
                <Button size="sm" variant="outline" onClick={() => handleSetFeatured(m.id)}
                  style={status?.featured_match_override === m.id ? { borderColor: "var(--neon-green)", color: "var(--neon-green)" } : {}}>
                  {status?.featured_match_override === m.id ? "Seçili" : "Seç"}
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

/* ── SITES TAB ───────────────────────────────────── */
function SitesTab({ bonusSites, onRefresh }) {
  const [newSite, setNewSite] = useState({ name: "", logo_url: "", bonus_type: "deneme", bonus_amount: "", affiliate_url: "", video_url: "", video_title: "", rating: 4.5, features: "", turnover_requirement: 10 });
  const [editingId, setEditingId] = useState(null);
  const [editData, setEditData] = useState({});
  const [saving, setSaving] = useState(false);
  const [reordering, setReordering] = useState(false);
  const [generatingVideoId, setGeneratingVideoId] = useState(null);

  const getAuthHeaders = () => {
    const token = localStorage.getItem("admin_token") || "";
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  const handleCreate = async () => {
    if (!newSite.name || !newSite.affiliate_url) return toast.error("Site adı ve URL gerekli");
    try {
      await axios.post(`${API}/bonus-sites`, { ...newSite, features: newSite.features.split(",").map(f => f.trim()).filter(Boolean), sort_order: bonusSites.length + 1 });
      toast.success("Site eklendi");
      setNewSite({ name: "", logo_url: "", bonus_type: "deneme", bonus_amount: "", affiliate_url: "", video_url: "", video_title: "", rating: 4.5, features: "", turnover_requirement: 10 });
      onRefresh();
    } catch { toast.error("Site eklenemedi"); }
  };

  const handleDelete = async (id, name) => {
    if (!confirm(`"${name}" silinecek. Emin misiniz?`)) return;
    try {
      await axios.delete(`${API}/bonus-sites/${id}`);
      toast.success("Site silindi");
      onRefresh();
    } catch { toast.error("Silinemedi"); }
  };

  const startEdit = (site) => {
    setEditingId(site.id);
    setEditData({
      name: site.name || "",
      bonus_type: site.bonus_type || "deneme",
      bonus_amount: site.bonus_amount || "",
      affiliate_url: site.affiliate_url || "",
      video_url: site.video_url || "",
      video_title: site.video_title || "",
      rating: site.rating || 4.5,
      features: Array.isArray(site.features) ? site.features.join(", ") : "",
      turnover_requirement: site.turnover_requirement || 10,
    });
  };

  const handleSaveEdit = async () => {
    setSaving(true);
    try {
      await axios.put(`${API}/bonus-sites/${editingId}`, editData);
      toast.success("Site güncellendi");
      setEditingId(null);
      onRefresh();
    } catch { toast.error("Güncellenemedi"); }
    finally { setSaving(false); }
  };

  const handleMoveUp = async (index) => {
    if (index === 0) return;
    setReordering(true);
    const newOrder = [...bonusSites];
    [newOrder[index - 1], newOrder[index]] = [newOrder[index], newOrder[index - 1]];
    try {
      await axios.post(`${API}/bonus-sites/reorder`, { order: newOrder.map(s => s.id) });
      onRefresh();
    } catch { toast.error("Sıralama başarısız"); }
    finally { setReordering(false); }
  };

  const handleMoveDown = async (index) => {
    if (index === bonusSites.length - 1) return;
    setReordering(true);
    const newOrder = [...bonusSites];
    [newOrder[index], newOrder[index + 1]] = [newOrder[index + 1], newOrder[index]];
    try {
      await axios.post(`${API}/bonus-sites/reorder`, { order: newOrder.map(s => s.id) });
      onRefresh();
    } catch { toast.error("Sıralama başarısız"); }
    finally { setReordering(false); }
  };

  const handleGenerateAIVideo = async (site) => {
    if (!site?.slug) return toast.error("Bu firmada slug eksik");
    setGeneratingVideoId(site.id);
    try {
      await axios.post(
        `${API}/firma/${site.slug}/video/generate`,
        { model: "sora-2", duration_seconds: 12, size: "1280x720" },
        { headers: getAuthHeaders() }
      );
      toast.success(`${site.name} için AI video üretimi başlatıldı`);
      onRefresh();
    } catch (e) {
      toast.error(e.response?.data?.detail || "AI video üretimi başlatılamadı");
    } finally {
      setGeneratingVideoId(null);
    }
  };

  return (
    <div className="space-y-6" data-testid="sites-tab">
      {/* Create Form */}
      <Card className="glass-card border-white/10">
        <CardHeader><CardTitle className="flex items-center gap-2"><Plus className="w-5 h-5" />Yeni Bonus Sitesi</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Input placeholder="Site Adı" value={newSite.name} onChange={(e) => setNewSite({ ...newSite, name: e.target.value })} data-testid="new-site-name" />
            <Input placeholder="Logo URL" value={newSite.logo_url} onChange={(e) => setNewSite({ ...newSite, logo_url: e.target.value })} />
            <Input placeholder="Affiliate URL" value={newSite.affiliate_url} onChange={(e) => setNewSite({ ...newSite, affiliate_url: e.target.value })} data-testid="new-site-url" />
            <Input placeholder="Video URL (opsiyonel)" value={newSite.video_url} onChange={(e) => setNewSite({ ...newSite, video_url: e.target.value })} data-testid="new-site-video-url" />
            <Select value={newSite.bonus_type} onValueChange={(v) => setNewSite({ ...newSite, bonus_type: v })}>
              <SelectTrigger><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="deneme">Deneme</SelectItem>
                <SelectItem value="hosgeldin">Hosgeldin</SelectItem>
                <SelectItem value="yatirim">Yatirim</SelectItem>
                <SelectItem value="kayip">Kayip</SelectItem>
              </SelectContent>
            </Select>
            <Input placeholder="Bonus Miktarı (500 TL)" value={newSite.bonus_amount} onChange={(e) => setNewSite({ ...newSite, bonus_amount: e.target.value })} />
            <Input placeholder="Video Başlığı (opsiyonel)" value={newSite.video_title} onChange={(e) => setNewSite({ ...newSite, video_title: e.target.value })} data-testid="new-site-video-title" />
            <Input placeholder="Özellikler (virgülle)" value={newSite.features} onChange={(e) => setNewSite({ ...newSite, features: e.target.value })} />
          </div>
          <Button onClick={handleCreate} className="bg-neon-green text-black hover:bg-neon-green/90" data-testid="create-site-btn">
            <Plus className="w-4 h-4 mr-2" />Site Ekle
          </Button>
        </CardContent>
      </Card>

      {/* Sites List */}
      <Card className="glass-card border-white/10">
        <CardHeader><CardTitle>Bonus Siteleri ({bonusSites.length})</CardTitle></CardHeader>
        <CardContent>
          <div className="space-y-2">
            {bonusSites.map((site) => (
              <div key={site.id} className="rounded-lg border p-4" style={{ borderColor: "rgba(255,255,255,0.08)" }} data-testid={`site-row-${site.id}`}>
                {editingId === site.id ? (
                  /* Edit Mode */
                  <div className="space-y-3">
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
                      <Input value={editData.name} onChange={(e) => setEditData({ ...editData, name: e.target.value })} placeholder="Site Adı" />
                      <Select value={editData.bonus_type} onValueChange={(v) => setEditData({ ...editData, bonus_type: v })}>
                        <SelectTrigger><SelectValue /></SelectTrigger>
                        <SelectContent>
                          <SelectItem value="deneme">Deneme</SelectItem>
                          <SelectItem value="hosgeldin">Hosgeldin</SelectItem>
                          <SelectItem value="yatirim">Yatirim</SelectItem>
                          <SelectItem value="kayip">Kayip</SelectItem>
                        </SelectContent>
                      </Select>
                      <Input value={editData.bonus_amount} onChange={(e) => setEditData({ ...editData, bonus_amount: e.target.value })} placeholder="Bonus Miktarı" />
                      <Input value={editData.affiliate_url} onChange={(e) => setEditData({ ...editData, affiliate_url: e.target.value })} placeholder="Affiliate URL" />
                      <Input value={editData.video_url} onChange={(e) => setEditData({ ...editData, video_url: e.target.value })} placeholder="Video URL" data-testid={`edit-site-video-url-${site.id}`} />
                      <Input value={editData.video_title} onChange={(e) => setEditData({ ...editData, video_title: e.target.value })} placeholder="Video Başlığı" data-testid={`edit-site-video-title-${site.id}`} />
                      <Input value={editData.features} onChange={(e) => setEditData({ ...editData, features: e.target.value })} placeholder="Özellikler" />
                      <Input type="number" value={editData.rating} onChange={(e) => setEditData({ ...editData, rating: parseFloat(e.target.value) })} placeholder="Rating" />
                    </div>
                    <div className="flex gap-2">
                      <Button size="sm" onClick={handleSaveEdit} disabled={saving} className="bg-neon-green text-black hover:bg-neon-green/90">
                        {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Save className="w-4 h-4 mr-1" />Kaydet</>}
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => setEditingId(null)}><X className="w-4 h-4 mr-1" />İptal</Button>
                    </div>
                  </div>
                ) : (
                  /* View Mode */
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="flex flex-col gap-0.5 shrink-0">
                        <Button variant="ghost" size="icon" className="h-5 w-5" onClick={() => handleMoveUp(bonusSites.indexOf(site))} disabled={reordering || bonusSites.indexOf(site) === 0} data-testid={`move-up-${site.id}`}>
                          <ArrowUp className="w-3 h-3" />
                        </Button>
                        <span className="text-xs text-center text-muted-foreground">{bonusSites.indexOf(site) + 1}</span>
                        <Button variant="ghost" size="icon" className="h-5 w-5" onClick={() => handleMoveDown(bonusSites.indexOf(site))} disabled={reordering || bonusSites.indexOf(site) === bonusSites.length - 1} data-testid={`move-down-${site.id}`}>
                          <ArrowDown className="w-3 h-3" />
                        </Button>
                      </div>
                      {site.logo_url && <img src={site.logo_url} alt={site.name} className="w-10 h-10 rounded-lg object-cover" onError={(e) => { e.target.style.display = "none"; }} />}
                      <div>
                        <h4 className="font-medium">{site.name}</h4>
                        <div className="flex gap-2 mt-1 flex-wrap">
                          <Badge variant="outline">{site.bonus_type}</Badge>
                          <span className="text-neon-green text-sm">{site.bonus_amount}</span>
                          <span className="text-xs text-muted-foreground">Rating: {site.rating}</span>
                          {site.video_url && <Badge className="bg-[#00F0FF]/20 text-[#00F0FF] text-xs">Video</Badge>}
                          {site.ai_video_status === "generating" && <Badge className="bg-yellow-500/20 text-yellow-400 text-xs">AI Üretiliyor</Badge>}
                          {site.ai_video_status === "ready" && <Badge className="bg-neon-green/20 text-neon-green text-xs">AI Hazır</Badge>}
                          {site.ai_video_status === "failed" && <Badge className="bg-red-500/20 text-red-400 text-xs">AI Hata</Badge>}
                          {site.features?.length > 0 && (
                            <span className="text-xs text-muted-foreground">{site.features.slice(0, 3).join(", ")}</span>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 shrink-0">
                      <a href={site.affiliate_url} target="_blank" rel="noopener noreferrer">
                        <Button variant="ghost" size="sm"><ExternalLink className="w-4 h-4" /></Button>
                      </a>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleGenerateAIVideo(site)}
                        disabled={generatingVideoId === site.id}
                        data-testid={`generate-ai-video-${site.id}`}
                        title="AI Video Üret"
                      >
                        {generatingVideoId === site.id ? <Loader2 className="w-4 h-4 animate-spin" /> : <Wand2 className="w-4 h-4" />}
                      </Button>
                      <Link to={`/${site.slug}/video`}>
                        <Button variant="ghost" size="sm" data-testid={`view-site-video-page-${site.id}`}><Play className="w-4 h-4" /></Button>
                      </Link>
                      <Button variant="ghost" size="sm" onClick={() => startEdit(site)} data-testid={`edit-site-${site.id}`}>
                        <Edit2 className="w-4 h-4" />
                      </Button>
                      <Button variant="ghost" size="sm" onClick={() => handleDelete(site.id, site.name)} data-testid={`delete-site-${site.id}`}>
                        <Trash2 className="w-4 h-4 text-red-400" />
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}


/* ── COMPANIES TAB ───────────────────────────────── */
function CompaniesTab() {
  const [companies, setCompanies] = useState([]);
  const [stats, setStats] = useState({ total: 0, approved: 0, featured: 0 });
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [query, setQuery] = useState("Top AI tools 2026");
  const [discovering, setDiscovering] = useState(false);
  const [actionId, setActionId] = useState(null);

  const getAuthHeaders = () => {
    const token = localStorage.getItem("admin_token") || "";
    return token ? { Authorization: `Bearer ${token}` } : {};
  };

  const fetchCompanies = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API}/admin/companies?limit=400${search ? `&search=${encodeURIComponent(search)}` : ""}`, {
        headers: getAuthHeaders(),
      });
      setCompanies(res.data.items || []);
      setStats(res.data.stats || { total: 0, approved: 0, featured: 0 });
    } catch {
      toast.error("Company listesi alınamadı");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCompanies();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const handleDiscover = async () => {
    if (!query.trim()) return toast.error("Keşif sorgusu gerekli");
    setDiscovering(true);
    try {
      const res = await axios.post(
        `${API}/admin/companies/discovery`,
        { query, limit: 12, auto_approve: false, run_async: true, deep_analysis: false },
        { headers: getAuthHeaders() }
      );
      if (res.status === 202 || res.data?.status === "queued") {
        toast.success("Company discovery kuyruğa alındı. Liste birazdan güncellenecek.");
        setTimeout(fetchCompanies, 3500);
      } else {
        toast.success(`Keşif tamamlandı. Yeni: ${res.data.created}, Atlanan: ${res.data.skipped}`);
        await fetchCompanies();
      }
    } catch (e) {
      toast.error(e.response?.data?.detail || "Keşif çalıştırılamadı");
    } finally {
      setDiscovering(false);
    }
  };

  const handleAction = async (companyId, action, body = null, okText = "Güncellendi") => {
    setActionId(companyId + action);
    try {
      if (action === "approve") {
        await axios.post(`${API}/admin/companies/${companyId}/approve`, {}, { headers: getAuthHeaders() });
      } else if (action === "refresh") {
        await axios.post(`${API}/admin/companies/${companyId}/refresh`, {}, { headers: getAuthHeaders() });
      } else if (action === "feature") {
        await axios.post(`${API}/admin/companies/${companyId}/feature`, body, { headers: getAuthHeaders() });
      } else if (action === "delete") {
        await axios.delete(`${API}/admin/companies/${companyId}`, { headers: getAuthHeaders() });
      }
      toast.success(okText);
      await fetchCompanies();
    } catch (e) {
      toast.error(e.response?.data?.detail || "İşlem başarısız");
    } finally {
      setActionId(null);
    }
  };

  return (
    <div className="space-y-6" data-testid="companies-tab">
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><Wand2 className="w-5 h-5" />AI Company Discovery</CardTitle>
          <CardDescription>Arama API key'leri eksik olsa bile fallback modda şirket keşfi çalışır.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Top AI tools 2026" data-testid="company-discovery-query-input" />
            <Input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Listede ara (name/domain/category)" data-testid="company-search-input" />
            <Button onClick={fetchCompanies} variant="outline" data-testid="refresh-companies-button"><RefreshCw className="w-4 h-4 mr-2" />Listeyi Yenile</Button>
          </div>

          <div className="flex flex-wrap gap-2">
            <Button onClick={handleDiscover} disabled={discovering} className="bg-[#00F0FF] text-black hover:bg-[#00F0FF]/90" data-testid="run-company-discovery-button">
              {discovering ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Sparkles className="w-4 h-4 mr-2" />}Keşfi Başlat
            </Button>
            <Button
              onClick={async () => {
                try {
                  await axios.post(`${API}/admin/companies/refresh-metrics`, {}, { headers: getAuthHeaders() });
                  toast.success("Metrikler yenilendi");
                  await fetchCompanies();
                } catch {
                  toast.error("Metrik yenileme başarısız");
                }
              }}
              variant="outline"
              data-testid="refresh-company-metrics-button"
            >
              <BarChart3 className="w-4 h-4 mr-2" />Metrikleri Yenile
            </Button>
          </div>

          <div className="grid grid-cols-3 gap-3 text-sm" data-testid="companies-stats-cards">
            <div className="rounded-lg border border-white/10 p-3"><p className="text-muted-foreground text-xs">Toplam</p><p className="text-xl font-heading" data-testid="companies-total-stat">{stats.total}</p></div>
            <div className="rounded-lg border border-white/10 p-3"><p className="text-muted-foreground text-xs">Onaylı</p><p className="text-xl font-heading text-neon-green" data-testid="companies-approved-stat">{stats.approved}</p></div>
            <div className="rounded-lg border border-white/10 p-3"><p className="text-muted-foreground text-xs">Featured</p><p className="text-xl font-heading text-[#00F0FF]" data-testid="companies-featured-stat">{stats.featured}</p></div>
          </div>
        </CardContent>
      </Card>

      <Card className="glass-card border-white/10">
        <CardHeader><CardTitle>Companies ({companies.length})</CardTitle></CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex justify-center py-10"><Loader2 className="w-6 h-6 animate-spin" /></div>
          ) : (
            <div className="space-y-2" data-testid="companies-list">
              {companies.map((company) => (
                <div key={company.id} className="rounded-lg border border-white/10 p-4" data-testid={`company-row-${company.id}`}>
                  <div className="flex items-center justify-between gap-4">
                    <div className="min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <h4 className="font-medium truncate" data-testid={`company-name-${company.id}`}>{company.name}</h4>
                        <Badge variant="outline">{company.category_id}</Badge>
                        {!company.is_approved && <Badge className="bg-yellow-500/20 text-yellow-400">Onay Bekliyor</Badge>}
                        {company.featured_boolean && <Badge className="bg-[#00F0FF]/20 text-[#00F0FF]">Featured</Badge>}
                      </div>
                      <p className="text-xs text-muted-foreground mt-1 truncate">{company.domain} • {company.subcategory_id}</p>
                      <div className="flex gap-3 mt-2 text-xs text-muted-foreground">
                        <span data-testid={`company-visits-${company.id}`}>Visits: {Math.round((company.estimated_visits || 0) / 1000)}K</span>
                        <span data-testid={`company-score-${company.id}`}>Score: {company.intelligence_score}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-1 shrink-0">
                      {!company.is_approved && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleAction(company.id, "approve", null, "Company onaylandı")}
                          disabled={actionId === company.id + "approve"}
                          data-testid={`approve-company-${company.id}`}
                        >
                          {actionId === company.id + "approve" ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
                        </Button>
                      )}
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleAction(company.id, "feature", { featured: !company.featured_boolean, reason: "manual-admin" }, company.featured_boolean ? "Featured kaldırıldı" : "Featured eklendi")}
                        disabled={actionId === company.id + "feature"}
                        data-testid={`feature-company-${company.id}`}
                      >
                        <Star className="w-4 h-4" />
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleAction(company.id, "refresh", null, "Şirket metrikleri yenilendi")}
                        disabled={actionId === company.id + "refresh"}
                        data-testid={`refresh-company-${company.id}`}
                      >
                        <RefreshCw className="w-4 h-4" />
                      </Button>
                      <Link to={`/companies/${company.slug}`}>
                        <Button size="sm" variant="ghost" data-testid={`view-company-page-${company.id}`}><Eye className="w-4 h-4" /></Button>
                      </Link>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleAction(company.id, "delete", null, "Company silindi")}
                        disabled={actionId === company.id + "delete"}
                        data-testid={`delete-company-${company.id}`}
                      >
                        <Trash2 className="w-4 h-4 text-red-400" />
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

/* ── ARTICLES TAB ────────────────────────────────── */
function ArticlesTab({ articles, onRefresh }) {
  const [searchQuery, setSearchQuery] = useState("");
  const [catFilter, setCatFilter] = useState("all");
  const [filtered, setFiltered] = useState(articles);
  const [showCreate, setShowCreate] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [editData, setEditData] = useState({});
  const [expandedId, setExpandedId] = useState(null);
  const [saving, setSaving] = useState(false);
  const [newArticle, setNewArticle] = useState({ title: "", content: "", category: "bonus", seo_title: "", seo_description: "", tags: "" });

  useEffect(() => {
    let f = articles;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      f = f.filter(a => a.title?.toLowerCase().includes(q) || a.content?.toLowerCase().includes(q));
    }
    if (catFilter !== "all") {
      f = f.filter(a => a.category === catFilter);
    }
    setFiltered(f);
  }, [articles, searchQuery, catFilter]);

  const handleCreate = async () => {
    if (!newArticle.title) return toast.error("Başlık gerekli");
    setSaving(true);
    try {
      await axios.post(`${API}/articles`, {
        ...newArticle,
        tags: newArticle.tags.split(",").map(t => t.trim()).filter(Boolean),
        is_published: true,
      });
      toast.success("Makale oluşturuldu");
      setNewArticle({ title: "", content: "", category: "bonus", seo_title: "", seo_description: "", tags: "" });
      setShowCreate(false);
      onRefresh();
    } catch { toast.error("Oluşturulamadı"); }
    finally { setSaving(false); }
  };

  const handleDelete = async (id, title) => {
    if (!confirm(`"${title}" silinecek. Emin misiniz?`)) return;
    try {
      await axios.delete(`${API}/articles/${id}`);
      toast.success("Makale silindi");
      onRefresh();
    } catch { toast.error("Silinemedi"); }
  };

  const startEdit = (article) => {
    setEditingId(article.id);
    setEditData({
      title: article.title || "",
      content: article.content || "",
      category: article.category || "bonus",
      seo_title: article.seo_title || "",
      seo_description: article.seo_description || "",
      tags: Array.isArray(article.tags) ? article.tags.join(", ") : "",
      is_published: article.is_published !== false,
    });
  };

  const handleSaveEdit = async () => {
    setSaving(true);
    try {
      await axios.put(`${API}/articles/${editingId}`, {
        ...editData,
        tags: editData.tags.split(",").map(t => t.trim()).filter(Boolean),
      });
      toast.success("Makale güncellendi");
      setEditingId(null);
      onRefresh();
    } catch { toast.error("Güncellenemedi"); }
    finally { setSaving(false); }
  };

  const categories = [...new Set(articles.map(a => a.category).filter(Boolean))];

  return (
    <div className="space-y-6" data-testid="articles-tab">
      {/* Search + Actions */}
      <div className="flex flex-col md:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} placeholder="Makale ara..." className="pl-10" data-testid="article-search" />
        </div>
        <Select value={catFilter} onValueChange={setCatFilter}>
          <SelectTrigger className="w-40"><SelectValue placeholder="Kategori" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Tümü</SelectItem>
            {categories.map(c => <SelectItem key={c} value={c}>{c}</SelectItem>)}
          </SelectContent>
        </Select>
        <Button onClick={() => setShowCreate(!showCreate)} className="bg-neon-green text-black hover:bg-neon-green/90" data-testid="new-article-btn">
          <Plus className="w-4 h-4 mr-2" />Yeni Makale
        </Button>
      </div>

      {/* Create Form */}
      {showCreate && (
        <Card className="glass-card border-white/10">
          <CardHeader><CardTitle className="flex items-center gap-2"><Plus className="w-5 h-5" />Yeni Makale</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label>Başlık</Label>
                <Input value={newArticle.title} onChange={(e) => setNewArticle({ ...newArticle, title: e.target.value })} placeholder="Makale başlığı" data-testid="new-article-title" />
              </div>
              <div>
                <Label>Kategori</Label>
                <Select value={newArticle.category} onValueChange={(v) => setNewArticle({ ...newArticle, category: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="bonus">Bonus</SelectItem>
                    <SelectItem value="spor">Spor</SelectItem>
                    <SelectItem value="rehber">Rehber</SelectItem>
                    <SelectItem value="haber">Haber</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>SEO Başlık</Label>
                <Input value={newArticle.seo_title} onChange={(e) => setNewArticle({ ...newArticle, seo_title: e.target.value })} placeholder="SEO başlık (max 60 karakter)" />
              </div>
              <div>
                <Label>Etiketler (virgülle)</Label>
                <Input value={newArticle.tags} onChange={(e) => setNewArticle({ ...newArticle, tags: e.target.value })} placeholder="bonus, deneme, rehber" />
              </div>
            </div>
            <div>
              <Label>SEO Açıklama</Label>
              <Input value={newArticle.seo_description} onChange={(e) => setNewArticle({ ...newArticle, seo_description: e.target.value })} placeholder="SEO açıklama (max 160 karakter)" />
            </div>
            <div>
              <Label>İçerik</Label>
              <Textarea value={newArticle.content} onChange={(e) => setNewArticle({ ...newArticle, content: e.target.value })} placeholder="Makale içeriği..." rows={8} data-testid="new-article-content" />
            </div>
            <div className="flex gap-2">
              <Button onClick={handleCreate} disabled={saving} className="bg-neon-green text-black hover:bg-neon-green/90" data-testid="save-article-btn">
                {saving ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Save className="w-4 h-4 mr-2" />}Kaydet
              </Button>
              <Button variant="outline" onClick={() => setShowCreate(false)}><X className="w-4 h-4 mr-1" />İptal</Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Articles List */}
      <Card className="glass-card border-white/10">
        <CardHeader><CardTitle>Makaleler ({filtered.length})</CardTitle></CardHeader>
        <CardContent>
          {filtered.length === 0 ? (
            <p className="text-muted-foreground text-center py-8">Makale bulunamadı</p>
          ) : (
            <div className="space-y-2">
              {filtered.map((article) => (
                <div key={article.id} className="rounded-lg border" style={{ borderColor: "rgba(255,255,255,0.08)" }} data-testid={`article-row-${article.id}`}>
                  {editingId === article.id ? (
                    /* Edit Mode */
                    <div className="p-4 space-y-3">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <Input value={editData.title} onChange={(e) => setEditData({ ...editData, title: e.target.value })} placeholder="Başlık" />
                        <Select value={editData.category} onValueChange={(v) => setEditData({ ...editData, category: v })}>
                          <SelectTrigger><SelectValue /></SelectTrigger>
                          <SelectContent>
                            <SelectItem value="bonus">Bonus</SelectItem>
                            <SelectItem value="spor">Spor</SelectItem>
                            <SelectItem value="rehber">Rehber</SelectItem>
                            <SelectItem value="haber">Haber</SelectItem>
                          </SelectContent>
                        </Select>
                        <Input value={editData.seo_title} onChange={(e) => setEditData({ ...editData, seo_title: e.target.value })} placeholder="SEO Başlık" />
                        <Input value={editData.tags} onChange={(e) => setEditData({ ...editData, tags: e.target.value })} placeholder="Etiketler" />
                      </div>
                      <Input value={editData.seo_description} onChange={(e) => setEditData({ ...editData, seo_description: e.target.value })} placeholder="SEO Açıklama" />
                      <Textarea value={editData.content} onChange={(e) => setEditData({ ...editData, content: e.target.value })} rows={6} />
                      <div className="flex items-center gap-3">
                        <div className="flex items-center gap-2">
                          <Switch checked={editData.is_published} onCheckedChange={(v) => setEditData({ ...editData, is_published: v })} />
                          <span className="text-sm">{editData.is_published ? "Yayında" : "Taslak"}</span>
                        </div>
                        <div className="flex gap-2 ml-auto">
                          <Button size="sm" onClick={handleSaveEdit} disabled={saving} className="bg-neon-green text-black hover:bg-neon-green/90">
                            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Save className="w-4 h-4 mr-1" />Kaydet</>}
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => setEditingId(null)}><X className="w-4 h-4 mr-1" />İptal</Button>
                        </div>
                      </div>
                    </div>
                  ) : (
                    /* View Mode */
                    <div className="p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex-1 min-w-0">
                          <h4 className="font-medium truncate">{article.title}</h4>
                          <div className="flex gap-2 mt-1 flex-wrap">
                            <Badge variant="outline">{article.category}</Badge>
                            {article.is_auto_generated && <Badge className="bg-[#00F0FF]/20 text-[#00F0FF] text-xs">Auto</Badge>}
                            {article.is_published === false && <Badge className="bg-yellow-500/20 text-yellow-500 text-xs">Taslak</Badge>}
                            <span className="text-xs text-muted-foreground">{article.view_count || 0} görüntülenme</span>
                            {article.created_at && (
                              <span className="text-xs text-muted-foreground">
                                {new Date(article.created_at).toLocaleDateString("tr-TR")}
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-1 shrink-0">
                          <Button variant="ghost" size="sm" onClick={() => setExpandedId(expandedId === article.id ? null : article.id)}>
                            {expandedId === article.id ? <ChevronUp className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                          </Button>
                          <Button variant="ghost" size="sm" onClick={() => startEdit(article)} data-testid={`edit-article-${article.id}`}>
                            <Edit2 className="w-4 h-4" />
                          </Button>
                          <Button variant="ghost" size="sm" onClick={() => handleDelete(article.id, article.title)} data-testid={`delete-article-${article.id}`}>
                            <Trash2 className="w-4 h-4 text-red-400" />
                          </Button>
                        </div>
                      </div>
                      {expandedId === article.id && (
                        <div className="mt-3 p-3 rounded-lg text-sm max-h-48 overflow-y-auto" style={{ background: "rgba(255,255,255,0.02)" }}>
                          {article.seo_title && <p className="text-xs text-muted-foreground mb-1">SEO: {article.seo_title}</p>}
                          {article.tags?.length > 0 && (
                            <div className="flex gap-1 mb-2 flex-wrap">
                              {article.tags.map((t, i) => <Badge key={i} variant="outline" className="text-xs">{t}</Badge>)}
                            </div>
                          )}
                          <div className="text-muted-foreground whitespace-pre-wrap text-xs" dangerouslySetInnerHTML={{ __html: (article.content || "").slice(0, 500) + (article.content?.length > 500 ? "..." : "") }} />
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}


/* ── TELEGRAM BOTS TAB ───────────────────────────── */
function TelegramTab() {
  const [stats, setStats] = useState({});
  const [bots, setBots] = useState([]);
  const [firmMap, setFirmMap] = useState(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [creating, setCreating] = useState(false);
  const [bulkCreating, setBulkCreating] = useState(false);
  const [broadcastMsg, setBroadcastMsg] = useState("");
  const [broadcastTarget, setBroadcastTarget] = useState("all");
  const [broadcasting, setBroadcasting] = useState(false);
  const [view, setView] = useState("bots"); // bots | firms | broadcast
  // Auth state
  const [authStatus, setAuthStatus] = useState(null); // null | true | false
  const [authPhone, setAuthPhone] = useState("");
  const [authCode, setAuthCode] = useState("");
  const [authPassword, setAuthPassword] = useState("");
  const [authStep, setAuthStep] = useState("phone"); // phone | code | password
  const [authLoading, setAuthLoading] = useState(false);

  const adminToken = localStorage.getItem("admin_token");
  const headers = { Authorization: `Bearer ${adminToken}` };

  useEffect(() => { checkAuthAndFetch(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const checkAuthAndFetch = async () => {
    setLoading(true);
    try {
      const authRes = await axios.get(`${API}/admin/telegram/auth/status`, { headers });
      setAuthStatus(authRes.data.authenticated);
      const [statsRes, botsRes] = await Promise.all([
        axios.get(`${API}/admin/telegram/stats`, { headers }),
        axios.get(`${API}/admin/telegram/bots`, { headers }),
      ]);
      setStats(statsRes.data);
      setBots(botsRes.data);
    } catch { toast.error("Telegram verileri yüklenemedi"); }
    finally { setLoading(false); }
  };

  const fetchAll = async () => {
    try {
      const [statsRes, botsRes] = await Promise.all([
        axios.get(`${API}/admin/telegram/stats`, { headers }),
        axios.get(`${API}/admin/telegram/bots`, { headers }),
      ]);
      setStats(statsRes.data);
      setBots(botsRes.data);
    } catch { toast.error("Veriler yüklenemedi"); }
  };

  const fetchFirmMap = async () => {
    try {
      const res = await axios.get(`${API}/admin/telegram/firm-bot-map`, { headers });
      setFirmMap(res.data);
    } catch { toast.error("Firma haritası yüklenemedi"); }
  };

  const createSingleBot = async (firmId) => {
    setCreating(true);
    try {
      const res = await axios.post(`${API}/admin/telegram/create-bot`, { firm_id: firmId }, { headers });
      toast.success(res.data.message);
      setTimeout(fetchAll, 3000);
    } catch (e) { toast.error(e.response?.data?.detail || "Bot oluşturulamadı"); }
    finally { setCreating(false); }
  };

  const createBulkBots = async () => {
    if (!confirm("Tüm firmalar için bot oluşturulacak. Devam?")) return;
    setBulkCreating(true);
    try {
      const res = await axios.post(`${API}/admin/telegram/create-bulk`, { all_firms: true, batch_size: 5, delay_seconds: 5 }, { headers });
      toast.success(res.data.message);
      setTimeout(fetchAll, 5000);
    } catch (e) { toast.error(e.response?.data?.detail || "Toplu oluşturma başarısız"); }
    finally { setBulkCreating(false); }
  };

  const deleteBot = async (botId, username) => {
    if (!confirm(`@${username} silinecek?`)) return;
    try {
      await axios.delete(`${API}/admin/telegram/bot/${botId}`, { headers });
      toast.success("Bot silindi");
      fetchAll();
    } catch { toast.error("Silinemedi"); }
  };

  const sendBroadcast = async () => {
    if (!broadcastMsg.trim()) return toast.error("Mesaj gerekli");
    setBroadcasting(true);
    try {
      const payload = { message: broadcastMsg, all_bots: broadcastTarget === "all" };
      if (broadcastTarget !== "all") payload.bot_id = broadcastTarget;
      const res = await axios.post(`${API}/admin/telegram/broadcast`, payload, { headers });
      toast.success(res.data.message);
      setBroadcastMsg("");
    } catch (e) { toast.error(e.response?.data?.detail || "Broadcast başarısız"); }
    finally { setBroadcasting(false); }
  };

  const filteredBots = bots.filter(b =>
    !search || b.firm_name?.toLowerCase().includes(search.toLowerCase()) ||
    b.bot_username?.toLowerCase().includes(search.toLowerCase())
  );

  const statusColor = (s) => {
    if (s === "active") return "bg-emerald-500/20 text-emerald-400 border-emerald-500/30";
    if (s === "creating") return "bg-amber-500/20 text-amber-400 border-amber-500/30";
    if (s === "pending") return "bg-blue-500/20 text-blue-400 border-blue-500/30";
    return "bg-red-500/20 text-red-400 border-red-500/30";
  };

  const sendAuthCode = async () => {
    if (!authPhone.trim()) return toast.error("Telefon numarası gerekli");
    setAuthLoading(true);
    try {
      await axios.post(`${API}/admin/telegram/auth/send-code`, { phone: authPhone }, { headers });
      toast.success("Doğrulama kodu gönderildi");
      setAuthStep("code");
    } catch (e) { toast.error(e.response?.data?.detail || "Kod gönderilemedi"); }
    finally { setAuthLoading(false); }
  };

  const verifyCode = async () => {
    if (!authCode.trim()) return toast.error("Kod gerekli");
    setAuthLoading(true);
    try {
      const res = await axios.post(`${API}/admin/telegram/auth/verify-code`, { phone: authPhone, code: authCode }, { headers });
      if (res.data.needs_password) {
        setAuthStep("password");
        toast.info("2FA şifre gerekli");
      } else if (res.data.authenticated) {
        setAuthStatus(true);
        toast.success("Telegram hesabı doğrulandı!");
      }
    } catch (e) { toast.error(e.response?.data?.detail || "Doğrulama başarısız"); }
    finally { setAuthLoading(false); }
  };

  const verifyPassword = async () => {
    if (!authPassword.trim()) return toast.error("Şifre gerekli");
    setAuthLoading(true);
    try {
      const res = await axios.post(`${API}/admin/telegram/auth/verify-password`, { password: authPassword }, { headers });
      if (res.data.authenticated) {
        setAuthStatus(true);
        toast.success("Telegram 2FA doğrulandı!");
      }
    } catch (e) { toast.error(e.response?.data?.detail || "Şifre doğrulaması başarısız"); }
    finally { setAuthLoading(false); }
  };

  if (loading) return <div className="flex items-center justify-center py-12"><Loader2 className="w-6 h-6 animate-spin text-[#00F0FF]" /></div>;

  // Auth required screen
  if (authStatus === false) {
    return (
      <div className="space-y-6" data-testid="telegram-auth">
        <Card className="glass-card border-[#00F0FF]/30 max-w-md mx-auto">
          <CardHeader>
            <CardTitle className="flex items-center gap-2"><Bot className="w-5 h-5 text-[#00F0FF]" />Telegram Hesap Doğrulama</CardTitle>
            <CardDescription>Bot oluşturmak için Telegram hesabınızı doğrulamanız gerekiyor</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {authStep === "phone" && (
              <div className="space-y-3">
                <Label>Telefon Numarası</Label>
                <Input placeholder="+90 5XX XXX XXXX" value={authPhone} onChange={e => setAuthPhone(e.target.value)} data-testid="auth-phone" />
                <Button onClick={sendAuthCode} disabled={authLoading} className="w-full bg-[#00F0FF] text-black hover:bg-[#00F0FF]/80" data-testid="auth-send-code">
                  {authLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Send className="w-4 h-4 mr-2" />}Kod Gönder
                </Button>
              </div>
            )}
            {authStep === "code" && (
              <div className="space-y-3">
                <Label>Doğrulama Kodu</Label>
                <Input placeholder="12345" value={authCode} onChange={e => setAuthCode(e.target.value)} data-testid="auth-code" />
                <Button onClick={verifyCode} disabled={authLoading} className="w-full bg-[#00F0FF] text-black hover:bg-[#00F0FF]/80" data-testid="auth-verify-code">
                  {authLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Check className="w-4 h-4 mr-2" />}Doğrula
                </Button>
              </div>
            )}
            {authStep === "password" && (
              <div className="space-y-3">
                <Label>2FA Şifresi</Label>
                <Input type="password" placeholder="Telegram 2FA şifreniz" value={authPassword} onChange={e => setAuthPassword(e.target.value)} data-testid="auth-password" />
                <Button onClick={verifyPassword} disabled={authLoading} className="w-full bg-[#00F0FF] text-black hover:bg-[#00F0FF]/80" data-testid="auth-verify-password">
                  {authLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Check className="w-4 h-4 mr-2" />}Doğrula
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="telegram-tab">
      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
        {[
          { label: "Toplam Bot", value: stats.total_bots || 0, icon: Bot, color: "text-[#00F0FF]" },
          { label: "Aktif", value: stats.active_bots || 0, icon: Radio, color: "text-emerald-400" },
          { label: "Bekleyen", value: stats.pending_bots || 0, icon: Clock, color: "text-amber-400" },
          { label: "Hatalı", value: stats.failed_bots || 0, icon: AlertCircle, color: "text-red-400" },
          { label: "Toplam Abone", value: stats.total_subscribers || 0, icon: Users, color: "text-purple-400" },
        ].map((s, i) => (
          <Card key={i} className="glass-card border-white/10">
            <CardContent className="pt-4 pb-3 px-4">
              <div className="flex items-center gap-2 mb-1">
                <s.icon className={`w-4 h-4 ${s.color}`} />
                <span className="text-xs text-muted-foreground">{s.label}</span>
              </div>
              <div className={`text-2xl font-bold ${s.color}`}>{s.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* View Switcher */}
      <div className="flex items-center gap-2 flex-wrap">
        <Button variant={view === "bots" ? "default" : "outline"} size="sm" onClick={() => setView("bots")} data-testid="telegram-view-bots">
          <Bot className="w-4 h-4 mr-1" />Botlar ({bots.length})
        </Button>
        <Button variant={view === "firms" ? "default" : "outline"} size="sm" onClick={() => { setView("firms"); if (!firmMap) fetchFirmMap(); }} data-testid="telegram-view-firms">
          <Target className="w-4 h-4 mr-1" />Firma Haritası
        </Button>
        <Button variant={view === "broadcast" ? "default" : "outline"} size="sm" onClick={() => setView("broadcast")} data-testid="telegram-view-broadcast">
          <Send className="w-4 h-4 mr-1" />Broadcast
        </Button>
        <div className="ml-auto flex gap-2">
          <Button variant="outline" size="sm" onClick={fetchAll} data-testid="telegram-refresh">
            <RefreshCw className="w-4 h-4 mr-1" />Yenile
          </Button>
          <Button size="sm" onClick={createBulkBots} disabled={bulkCreating} className="bg-[#00F0FF] text-black hover:bg-[#00F0FF]/80" data-testid="telegram-bulk-create">
            {bulkCreating ? <Loader2 className="w-4 h-4 mr-1 animate-spin" /> : <Zap className="w-4 h-4 mr-1" />}
            Toplu Bot Oluştur
          </Button>
        </div>
      </div>

      {/* Bot List View */}
      {view === "bots" && (
        <div className="space-y-3">
          <Input placeholder="Bot ara..." value={search} onChange={e => setSearch(e.target.value)} className="max-w-sm" data-testid="telegram-search" />
          {filteredBots.length === 0 ? (
            <Card className="glass-card border-white/10">
              <CardContent className="py-8 text-center text-muted-foreground">
                <Bot className="w-12 h-12 mx-auto mb-3 opacity-40" />
                <p>Henüz bot oluşturulmadı</p>
                <p className="text-sm mt-1">Yukarıdaki "Toplu Bot Oluştur" butonunu kullanabilirsiniz</p>
              </CardContent>
            </Card>
          ) : (
            <div className="grid gap-2">
              {filteredBots.map(bot => (
                <Card key={bot.bot_id} className="glass-card border-white/10 hover:border-[#00F0FF]/30 transition-colors" data-testid={`telegram-bot-${bot.bot_id}`}>
                  <CardContent className="py-3 px-4">
                    <div className="flex items-center justify-between flex-wrap gap-2">
                      <div className="flex items-center gap-3 min-w-0">
                        <Bot className="w-5 h-5 text-[#00F0FF] flex-shrink-0" />
                        <div className="min-w-0">
                          <div className="font-medium text-sm truncate">@{bot.bot_username}</div>
                          <div className="text-xs text-muted-foreground">{bot.firm_name}</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge className={`text-xs ${statusColor(bot.status)}`}>{bot.status}</Badge>
                        <div className="flex items-center gap-1 text-xs text-muted-foreground">
                          <Users className="w-3 h-3" />{bot.subscriber_count || 0}
                        </div>
                        {bot.status === "active" && (
                          <a href={`https://t.me/${bot.bot_username}`} target="_blank" rel="noreferrer">
                            <Button variant="ghost" size="sm" className="h-7 px-2"><ExternalLink className="w-3.5 h-3.5" /></Button>
                          </a>
                        )}
                        <Button variant="ghost" size="sm" className="h-7 px-2 text-red-400 hover:text-red-300" onClick={() => deleteBot(bot.bot_id, bot.bot_username)} data-testid={`delete-bot-${bot.bot_id}`}>
                          <Trash2 className="w-3.5 h-3.5" />
                        </Button>
                      </div>
                    </div>
                    {bot.error_message && (
                      <div className="mt-2 text-xs text-red-400 bg-red-500/10 rounded px-2 py-1">{bot.error_message}</div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Firm Map View */}
      {view === "firms" && (
        <div className="space-y-3">
          {!firmMap ? (
            <div className="flex items-center justify-center py-8"><Loader2 className="w-6 h-6 animate-spin text-[#00F0FF]" /></div>
          ) : (
            <>
              <div className="text-sm text-muted-foreground">
                {firmMap.with_bot}/{firmMap.total} firma bot sahibi
              </div>
              <div className="grid gap-2 max-h-[500px] overflow-y-auto pr-2">
                {firmMap.firms.map(f => (
                  <div key={f.firm_id} className="flex items-center justify-between py-2 px-3 rounded-lg bg-white/5 border border-white/5">
                    <div className="min-w-0">
                      <div className="text-sm font-medium truncate">{f.firm_name}</div>
                      <div className="text-xs text-muted-foreground">@{f.bot_username}</div>
                    </div>
                    <div className="flex items-center gap-2 flex-shrink-0">
                      {f.has_bot ? (
                        <Badge className={`text-xs ${statusColor(f.bot_status)}`}>{f.bot_status}</Badge>
                      ) : (
                        <Button size="sm" variant="outline" className="h-7 text-xs" disabled={creating} onClick={() => createSingleBot(f.firm_id)} data-testid={`create-bot-${f.firm_id}`}>
                          {creating ? <Loader2 className="w-3 h-3 animate-spin" /> : <Plus className="w-3 h-3 mr-1" />}Bot Oluştur
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}

      {/* Broadcast View */}
      {view === "broadcast" && (
        <Card className="glass-card border-white/10">
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2"><Send className="w-5 h-5 text-[#00F0FF]" />Broadcast Mesaj Gönder</CardTitle>
            <CardDescription>Tüm abonelere veya belirli bir botun abonelerine mesaj gönderin</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>Hedef</Label>
              <Select value={broadcastTarget} onValueChange={setBroadcastTarget}>
                <SelectTrigger data-testid="broadcast-target"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tüm Botlar</SelectItem>
                  {bots.filter(b => b.status === "active").map(b => (
                    <SelectItem key={b.bot_id} value={b.bot_id}>@{b.bot_username} ({b.subscriber_count || 0} abone)</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Mesaj (HTML destekli)</Label>
              <Textarea
                value={broadcastMsg}
                onChange={e => setBroadcastMsg(e.target.value)}
                placeholder="<b>Yeni promosyon!</b>&#10;Hemen giriş yapın..."
                rows={5}
                data-testid="broadcast-message"
              />
            </div>
            <Button onClick={sendBroadcast} disabled={broadcasting || !broadcastMsg.trim()} className="bg-[#00F0FF] text-black hover:bg-[#00F0FF]/80" data-testid="broadcast-send">
              {broadcasting ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Send className="w-4 h-4 mr-2" />}
              Gönder
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}


/* ── DOMAINS TAB ─────────────────────────────────── */
function DomainsTab({ domains, onRefresh }) {
  const [newDomain, setNewDomain] = useState({ domain_name: "", display_name: "", focus: "bonus", meta_title: "" });
  const [creating, setCreating] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [editData, setEditData] = useState({});
  const [saving, setSaving] = useState(false);
  const [siteStatus, setSiteStatus] = useState({});
  const [godaddyDomains, setGodaddyDomains] = useState([]);
  const [godaddyLoading, setGodaddyLoading] = useState(false);
  const [godaddyError, setGodaddyError] = useState("");
  const [godaddyFetched, setGodaddyFetched] = useState(false);
  const [importingDomain, setImportingDomain] = useState(null);
  const [godaddySearch, setGodaddySearch] = useState("");
  const [godaddyFilter, setGodaddyFilter] = useState("all");
  const [godaddyStats, setGodaddyStats] = useState({ total: 0, parked: 0, hosted: 0, platform: 0 });

  useEffect(() => {
    domains.forEach(async (d) => {
      try {
        const res = await axios.get(`${API}/site/${d.domain_name}`);
        setSiteStatus(prev => ({ ...prev, [d.id]: res.data }));
      } catch {
        setSiteStatus(prev => ({ ...prev, [d.id]: { is_ready: false, stats: { total_articles: 0 } } }));
      }
    });
  }, [domains]);

  const fetchGodaddyDomains = async () => {
    setGodaddyLoading(true);
    setGodaddyError("");
    try {
      const res = await axios.get(`${API}/godaddy/domains`);
      setGodaddyDomains(res.data.domains || []);
      setGodaddyStats(res.data.stats || { total: 0, parked: 0, hosted: 0, platform: 0 });
      setGodaddyFetched(true);
    } catch (e) {
      setGodaddyError(e.response?.data?.detail || "GoDaddy domainleri alınamadı");
    } finally {
      setGodaddyLoading(false);
    }
  };

  const handleImportDomain = async (gdDomain) => {
    setImportingDomain(gdDomain.domain);
    try {
      await axios.post(`${API}/godaddy/import`, {
        domain_name: gdDomain.domain,
        focus: "bonus"
      });
      toast.success(`${gdDomain.domain} platforma eklendi! AI içerik üretimi başladı.`);
      setGodaddyDomains(prev => prev.map(d => d.domain === gdDomain.domain ? { ...d, already_added: true } : d));
      onRefresh();
    } catch (e) {
      toast.error(e.response?.data?.detail || "Domain eklenemedi");
    } finally {
      setImportingDomain(null);
    }
  };

  const handleCreate = async () => {
    if (!newDomain.domain_name) return toast.error("Domain adı gerekli");
    setCreating(true);
    try {
      const res = await axios.post(`${API}/domains`, newDomain);
      toast.success(`${res.data.domain_name} oluşturuldu! AI içerik üretimi arka planda başladı.`);
      setNewDomain({ domain_name: "", display_name: "", focus: "bonus", meta_title: "" });
      onRefresh();
    } catch (e) { toast.error(e.response?.data?.detail || "Domain oluşturulamadı"); }
    finally { setCreating(false); }
  };

  const handleDelete = async (id) => {
    if (!confirm("Bu domain ve tüm verileri silinecek. Emin misiniz?")) return;
    try {
      await axios.delete(`${API}/domains/${id}`);
      toast.success("Domain silindi");
      onRefresh();
    } catch { toast.error("Silinemedi"); }
  };

  const startEdit = (d) => {
    setEditingId(d.id);
    setEditData({ display_name: d.display_name || "", focus: d.focus || "bonus", meta_title: d.meta_title || "" });
  };

  const handleSaveEdit = async () => {
    setSaving(true);
    try {
      await axios.put(`${API}/domains/${editingId}`, editData);
      toast.success("Domain güncellendi");
      setEditingId(null);
      onRefresh();
    } catch { toast.error("Güncellenemedi"); }
    finally { setSaving(false); }
  };

  const filteredGodaddyDomains = godaddyDomains.filter(d => {
    const matchesSearch = d.domain.toLowerCase().includes(godaddySearch.toLowerCase());
    if (!matchesSearch) return false;
    if (godaddyFilter === "all") return true;
    if (godaddyFilter === "parked") return d.hosting_status === "parked";
    if (godaddyFilter === "hosted") return d.hosting_status === "hosted";
    if (godaddyFilter === "platform") return d.hosting_status === "platform";
    return true;
  });

  const filterButtons = [
    { key: "all", label: "Tümü", count: godaddyStats.total, color: "text-white" },
    { key: "parked", label: "Boşta", count: godaddyStats.parked, color: "text-yellow-400" },
    { key: "hosted", label: "Farklı Sunucuda", count: godaddyStats.hosted, color: "text-blue-400" },
    { key: "platform", label: "Platformda", count: godaddyStats.platform, color: "text-neon-green" },
  ];

  return (
    <div className="space-y-6" data-testid="domains-tab">
      {/* GoDaddy Import Section */}
      <Card className="glass-card border-white/10 border-l-4 border-l-[#00F0FF]">
        <CardHeader>
          <CardTitle className="flex items-center gap-2" data-testid="godaddy-section-title">
            <Globe className="w-5 h-5 text-[#00F0FF]" />GoDaddy Domainleri
          </CardTitle>
          <CardDescription>GoDaddy hesabınızdaki domainleri görüntüleyin ve tek tıkla platforma ekleyin.</CardDescription>
        </CardHeader>
        <CardContent>
          {!godaddyFetched ? (
            <Button onClick={fetchGodaddyDomains} disabled={godaddyLoading} className="bg-[#00F0FF] text-black hover:bg-[#00F0FF]/80" data-testid="fetch-godaddy-btn">
              {godaddyLoading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Download className="w-4 h-4 mr-2" />}
              GoDaddy Domainlerini Getir
            </Button>
          ) : (
            <div className="space-y-4">
              {/* Stats Bar */}
              <div className="grid grid-cols-4 gap-3" data-testid="godaddy-stats">
                {filterButtons.map(fb => (
                  <button
                    key={fb.key}
                    onClick={() => setGodaddyFilter(fb.key)}
                    data-testid={`godaddy-filter-${fb.key}`}
                    className={`rounded-lg border p-3 text-left transition-all ${godaddyFilter === fb.key ? "border-[#00F0FF] bg-[#00F0FF]/10" : "border-white/10 hover:border-white/20"}`}
                  >
                    <div className={`text-xl font-bold ${fb.color}`}>{fb.count}</div>
                    <div className="text-xs text-muted-foreground">{fb.label}</div>
                  </button>
                ))}
              </div>

              {/* Search & Refresh */}
              <div className="flex items-center justify-between gap-4">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <span>{filteredGodaddyDomains.length} domain gösteriliyor</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="relative">
                    <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
                    <Input
                      value={godaddySearch}
                      onChange={(e) => setGodaddySearch(e.target.value)}
                      placeholder="Domain ara..."
                      className="pl-9 w-[220px]"
                      data-testid="godaddy-search-input"
                    />
                  </div>
                  <Button variant="outline" size="sm" onClick={fetchGodaddyDomains} disabled={godaddyLoading} data-testid="refresh-godaddy-btn">
                    <RefreshCw className={`w-4 h-4 ${godaddyLoading ? "animate-spin" : ""}`} />
                  </Button>
                </div>
              </div>

              {filteredGodaddyDomains.length === 0 ? (
                <p className="text-muted-foreground text-center py-6">Eşleşen domain bulunamadı</p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-[400px] overflow-y-auto pr-1">
                  {filteredGodaddyDomains.map((gd) => (
                    <div key={gd.domain} className={`rounded-lg border p-3 flex flex-col gap-2 ${gd.hosting_status === "platform" ? "border-neon-green/30" : gd.hosting_status === "hosted" ? "border-blue-500/30" : "border-yellow-500/20"}`} data-testid={`godaddy-domain-${gd.domain}`}>
                      <div className="flex items-center justify-between">
                        <span className="font-medium text-sm truncate">{gd.domain}</span>
                        <Badge variant="outline" className={`text-[10px] ${gd.hosting_status === "parked" ? "bg-yellow-500/15 text-yellow-400 border-yellow-500/30" : gd.hosting_status === "hosted" ? "bg-blue-500/15 text-blue-400 border-blue-500/30" : "bg-neon-green/15 text-neon-green border-neon-green/30"}`} data-testid={`godaddy-status-${gd.domain}`}>
                          {gd.hosting_status === "parked" ? "Boşta" : gd.hosting_status === "hosted" ? "Farklı Sunucu" : "Platformda"}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-3 text-[11px] text-muted-foreground flex-wrap">
                        {gd.expires && (
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            {new Date(gd.expires).toLocaleDateString("tr-TR")}
                          </span>
                        )}
                        {gd.renew_auto && <span className="text-neon-green">Oto-Yenileme</span>}
                        {gd.privacy && <span>Gizlilik</span>}
                        {gd.hosting_status === "hosted" && gd.nameServers?.length > 0 && (
                          <span className="text-blue-400 truncate max-w-[150px]" title={gd.nameServers.join(", ")}>
                            NS: {gd.nameServers[0]}
                          </span>
                        )}
                      </div>
                      {gd.already_added ? (
                        <Button size="sm" variant="outline" disabled className="w-full text-neon-green border-neon-green/30" data-testid={`godaddy-added-${gd.domain}`}>
                          <Check className="w-4 h-4 mr-1" />Platformda Mevcut
                        </Button>
                      ) : (
                        <Button size="sm" onClick={() => handleImportDomain(gd)} disabled={importingDomain === gd.domain} className="w-full bg-[#00F0FF] text-black hover:bg-[#00F0FF]/80" data-testid={`godaddy-import-${gd.domain}`}>
                          {importingDomain === gd.domain ? <Loader2 className="w-4 h-4 mr-1 animate-spin" /> : <Plus className="w-4 h-4 mr-1" />}
                          Platforma Ekle
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
          {godaddyError && (
            <div className="mt-3 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm flex items-center gap-2" data-testid="godaddy-error">
              <AlertCircle className="w-4 h-4" />{godaddyError}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Manual Domain Add */}
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><Plus className="w-5 h-5" />Manuel Domain Ekle</CardTitle>
          <CardDescription>Domain eklendiğinde bonus siteleri otomatik bağlanır ve AI ile 5 SEO makale üretilir.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div><Label>Domain Adı</Label><Input value={newDomain.domain_name} onChange={(e) => setNewDomain({ ...newDomain, domain_name: e.target.value })} placeholder="example.com" data-testid="new-domain-name" /></div>
            <div><Label>Görünen Ad</Label><Input value={newDomain.display_name} onChange={(e) => setNewDomain({ ...newDomain, display_name: e.target.value })} placeholder="Example Site" /></div>
            <div><Label>Odak</Label>
              <Select value={newDomain.focus} onValueChange={(v) => setNewDomain({ ...newDomain, focus: v })}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="bonus">Bonus</SelectItem>
                  <SelectItem value="spor">Spor</SelectItem>
                  <SelectItem value="hibrit">Hibrit</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div><Label>Meta Title</Label><Input value={newDomain.meta_title} onChange={(e) => setNewDomain({ ...newDomain, meta_title: e.target.value })} placeholder="SEO başlık" /></div>
          </div>
          <Button onClick={handleCreate} disabled={creating} className="bg-neon-green text-black hover:bg-neon-green/90" data-testid="create-domain-btn">
            {creating ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Plus className="w-4 h-4 mr-2" />}Domain Oluştur
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
                <div key={domain.id} className="rounded-lg border p-4" style={{ borderColor: "rgba(255,255,255,0.08)" }} data-testid={`domain-row-${domain.id}`}>
                  {editingId === domain.id ? (
                    <div className="space-y-3">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                        <Input value={editData.display_name} onChange={(e) => setEditData({ ...editData, display_name: e.target.value })} placeholder="Görünen Ad" />
                        <Select value={editData.focus} onValueChange={(v) => setEditData({ ...editData, focus: v })}>
                          <SelectTrigger><SelectValue /></SelectTrigger>
                          <SelectContent>
                            <SelectItem value="bonus">Bonus</SelectItem>
                            <SelectItem value="spor">Spor</SelectItem>
                            <SelectItem value="hibrit">Hibrit</SelectItem>
                          </SelectContent>
                        </Select>
                        <Input value={editData.meta_title} onChange={(e) => setEditData({ ...editData, meta_title: e.target.value })} placeholder="Meta Title" />
                      </div>
                      <div className="flex gap-2">
                        <Button size="sm" onClick={handleSaveEdit} disabled={saving} className="bg-neon-green text-black hover:bg-neon-green/90">
                          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <><Save className="w-4 h-4 mr-1" />Kaydet</>}
                        </Button>
                        <Button size="sm" variant="outline" onClick={() => setEditingId(null)}><X className="w-4 h-4 mr-1" />İptal</Button>
                      </div>
                    </div>
                  ) : (
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className={`w-3 h-3 rounded-full ${siteStatus[domain.id]?.is_ready ? "bg-neon-green" : "bg-yellow-500 animate-pulse"}`} />
                        <div>
                          <div className="flex items-center gap-2 flex-wrap">
                            <h4 className="font-medium">{domain.domain_name}</h4>
                            <Badge variant="outline">{domain.focus}</Badge>
                            {domain.display_name && <span className="text-xs text-muted-foreground">({domain.display_name})</span>}
                          </div>
                          <div className="flex items-center gap-3 mt-1 text-xs text-muted-foreground">
                            {siteStatus[domain.id]?.is_ready ? (
                              <>
                                <span className="text-neon-green">{siteStatus[domain.id]?.stats?.total_articles || 0} makale</span>
                                <span>{siteStatus[domain.id]?.stats?.total_bonus_sites || 0} bonus sitesi</span>
                                <a href={`https://${domain.domain_name}`} target="_blank" rel="noopener noreferrer" className="text-[#00F0FF] hover:underline flex items-center gap-1">
                                  <ExternalLink className="w-3 h-3" />Siteyi Gör
                                </a>
                              </>
                            ) : (
                              <span className="text-yellow-500">AI içerik üretiliyor...</span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Button variant="ghost" size="sm" onClick={() => startEdit(domain)} data-testid={`edit-domain-${domain.id}`}>
                          <Edit2 className="w-4 h-4" />
                        </Button>
                        <Button variant="ghost" size="sm" onClick={() => handleDelete(domain.id)} data-testid={`delete-domain-${domain.id}`}>
                          <Trash2 className="w-4 h-4 text-red-400" />
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

/* ── AUTO CONTENT SCHEDULER ────────────────────────── */
function AutoContentScheduler({ onRefresh }) {
  const [queue, setQueue] = useState([]);
  const [queueStats, setQueueStats] = useState({});
  const [scheduler, setScheduler] = useState({});
  const [bulkInput, setBulkInput] = useState("");
  const [defaultCompany, setDefaultCompany] = useState("");
  const [loading, setLoading] = useState(false);
  const [interval, setInterval_] = useState("5");

  const authHeaders = () => {
    const token = localStorage.getItem("admin_token");
    return token ? { headers: { Authorization: `Bearer ${token}` } } : {};
  };

  const fetchQueue = async () => {
    try {
      const [qRes, sRes] = await Promise.all([
        axios.get(`${API}/content-queue?limit=50`),
        axios.get(`${API}/scheduler/status`, authHeaders()),
      ]);
      setQueue(qRes.data.items || []);
      setQueueStats(qRes.data.stats || {});
      setScheduler(sRes.data);
      setInterval_(String(sRes.data.interval_minutes || 5));
    } catch (e) { console.error(e); }
  };

  useEffect(() => {
    fetchQueue();
    const pollId = window.setInterval(fetchQueue, 15000);
    return () => window.clearInterval(pollId);
  }, []);

  const handleBulkAdd = async () => {
    if (!bulkInput.trim()) return toast.error("Konu listesi boş");
    setLoading(true);
    try {
      const res = await axios.post(`${API}/content-queue/bulk-add`, {
        items: bulkInput,
        company: defaultCompany,
      });
      toast.success(`${res.data.added} konu eklendi`);
      setBulkInput("");
      fetchQueue();
    } catch { toast.error("Eklenemedi"); }
    finally { setLoading(false); }
  };

  const handleToggleScheduler = async () => {
    try {
      if (scheduler.is_running) {
        await axios.post(`${API}/scheduler/stop`, {}, authHeaders());
        toast.success("Zamanlayıcı durduruldu");
      } else {
        await axios.post(`${API}/scheduler/start`, {}, authHeaders());
        toast.success("Zamanlayıcı başlatıldı");
      }
      fetchQueue();
    } catch { toast.error("İşlem başarısız"); }
  };

  const handleIntervalChange = async (val) => {
    setInterval_(val);
    try {
      await axios.put(`${API}/scheduler/interval`, { minutes: parseInt(val) }, authHeaders());
      toast.success(`Süre ${val} dakika olarak ayarlandı`);
      fetchQueue();
    } catch { toast.error("Ayarlanamadı"); }
  };

  const handleRunNow = async () => {
    setLoading(true);
    try {
      await axios.post(`${API}/scheduler/run-now`, {}, authHeaders());
      toast.success("Makale üretimi başlatıldı");
      setTimeout(() => { fetchQueue(); onRefresh(); }, 3000);
    } catch { toast.error("Üretilemedi"); }
    finally { setLoading(false); }
  };

  const handleDeleteItem = async (id) => {
    try {
      await axios.delete(`${API}/content-queue/${id}`);
      fetchQueue();
    } catch { toast.error("Silinemedi"); }
  };

  const handleClearCompleted = async () => {
    try {
      await axios.delete(`${API}/content-queue?status=completed`);
      toast.success("Tamamlananlar temizlendi");
      fetchQueue();
    } catch { toast.error("Temizlenemedi"); }
  };

  const pendingItems = queue.filter(i => i.status === "pending");
  const completedItems = queue.filter(i => i.status === "completed");
  const failedItems = queue.filter(i => i.status === "failed");

  return (
    <div className="space-y-6" data-testid="auto-content-scheduler">
      {/* Scheduler Control */}
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-neon-green" />Otomatik İçerik Zamanlayıcı
          </CardTitle>
          <CardDescription>
            Firma ve konuları listeye ekleyin, zamanlayıcı otomatik olarak makale üretsin. Her makale en az 2000 kelime, firma önerileri ve SEO uyumlu.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap items-center gap-4">
            <Button
              onClick={handleToggleScheduler}
              className={scheduler.is_running ? "bg-red-500 hover:bg-red-600" : "bg-neon-green text-black hover:bg-neon-green/90"}
              data-testid="scheduler-toggle-btn"
            >
              {scheduler.is_running ? <><Pause className="w-4 h-4 mr-2" />Durdur</> : <><Play className="w-4 h-4 mr-2" />Başlat</>}
            </Button>
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-muted-foreground" />
              <Select value={interval} onValueChange={handleIntervalChange}>
                <SelectTrigger className="w-32"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">1 dakika</SelectItem>
                  <SelectItem value="5">5 dakika</SelectItem>
                  <SelectItem value="10">10 dakika</SelectItem>
                  <SelectItem value="30">30 dakika</SelectItem>
                  <SelectItem value="60">1 saat</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button variant="outline" onClick={handleRunNow} disabled={loading} data-testid="run-now-btn">
              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Wand2 className="w-4 h-4 mr-2" />}
              Şimdi Üret
            </Button>
            <div className="ml-auto flex items-center gap-3 text-sm">
              <div className="flex items-center gap-1.5">
                <div className={`w-2.5 h-2.5 rounded-full ${scheduler.is_running ? "bg-neon-green animate-pulse" : "bg-red-400"}`} />
                <span className="text-muted-foreground">{scheduler.is_running ? "Çalışıyor" : "Durdu"}</span>
              </div>
              <span className="text-muted-foreground">Üretilen: <strong className="text-foreground">{scheduler.total_generated || 0}</strong></span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Queue Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {[
          { label: "Bekleyen", value: queueStats.pending || 0, color: "text-yellow-400" },
          { label: "İşleniyor", value: queueStats.processing || 0, color: "text-blue-400" },
          { label: "Tamamlanan", value: queueStats.completed || 0, color: "text-neon-green" },
          { label: "Başarısız", value: queueStats.failed || 0, color: "text-red-400" },
        ].map((s, i) => (
          <Card key={i} className="glass-card border-white/10">
            <CardContent className="p-4 text-center">
              <p className="text-xs text-muted-foreground uppercase tracking-wider">{s.label}</p>
              <p className={`text-2xl font-bold ${s.color}`}>{s.value}</p>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Bulk Add */}
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><ListChecks className="w-5 h-5" />Toplu Konu Ekle</CardTitle>
          <CardDescription>
            Her satıra bir konu yazın. Firma belirtmek için "FIRMA|Konu" formatını kullanın. 
            Örn: MAXWIN|Maxwin Deneme Bonusu 2026 Detaylı İnceleme
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label>Varsayılan Firma (opsiyonel)</Label>
            <Input
              value={defaultCompany}
              onChange={(e) => setDefaultCompany(e.target.value)}
              placeholder="Firma adı (MAXWIN, HILTONBET vb.)"
              data-testid="default-company-input"
            />
          </div>
          <div>
            <Label>Konu Listesi (her satır bir konu)</Label>
            <Textarea
              value={bulkInput}
              onChange={(e) => setBulkInput(e.target.value)}
              placeholder={`MAXWIN|Maxwin Deneme Bonusu 2026 Detaylı İnceleme\nHILTONBET|Hiltonbet Güvenilir Mi Uzman Analizi\nEn İyi Bahis Siteleri 2026 Karşılaştırma\nDeneme Bonusu Nasıl Çevrilir Rehber`}
              rows={8}
              className="font-mono text-sm"
              data-testid="bulk-topics-input"
            />
          </div>
          <div className="flex gap-2">
            <Button onClick={handleBulkAdd} disabled={loading} className="bg-neon-green text-black hover:bg-neon-green/90" data-testid="bulk-add-btn">
              {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Plus className="w-4 h-4 mr-2" />}
              Listeye Ekle
            </Button>
            <span className="text-sm text-muted-foreground self-center">
              {bulkInput.split("\n").filter(l => l.trim()).length} konu
            </span>
          </div>
        </CardContent>
      </Card>

      {/* Pending Queue */}
      {pendingItems.length > 0 && (
        <Card className="glass-card border-white/10">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-yellow-400" />Bekleyen Konular ({pendingItems.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {pendingItems.map((item, i) => (
                <div key={item.id} className="flex items-center justify-between p-3 rounded-lg" style={{ background: "rgba(255,255,255,0.03)" }}>
                  <div className="flex items-center gap-3">
                    <span className="text-xs font-mono text-muted-foreground w-6">{i + 1}</span>
                    {item.company && <Badge variant="outline" className="text-xs">{item.company}</Badge>}
                    <span className="text-sm">{item.topic}</span>
                  </div>
                  <Button variant="ghost" size="sm" onClick={() => handleDeleteItem(item.id)}>
                    <Trash2 className="w-4 h-4 text-red-400" />
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Completed */}
      {completedItems.length > 0 && (
        <Card className="glass-card border-white/10">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2 text-neon-green">
                <Sparkles className="w-5 h-5" />Tamamlanan ({completedItems.length})
              </CardTitle>
              <Button variant="outline" size="sm" onClick={handleClearCompleted}>Temizle</Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {completedItems.slice(0, 10).map((item) => (
                <div key={item.id} className="flex items-center justify-between p-3 rounded-lg" style={{ background: "rgba(0,255,135,0.03)" }}>
                  <div className="flex items-center gap-3">
                    <Sparkles className="w-4 h-4 text-neon-green" />
                    {item.company && <Badge variant="outline" className="text-xs">{item.company}</Badge>}
                    <span className="text-sm">{item.topic}</span>
                  </div>
                  <span className="text-xs text-muted-foreground">{item.completed_at ? new Date(item.completed_at).toLocaleString("tr-TR") : ""}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Failed */}
      {failedItems.length > 0 && (
        <Card className="glass-card border-white/10">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-red-400">
              <AlertCircle className="w-5 h-5" />Başarısız ({failedItems.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {failedItems.map((item) => (
                <div key={item.id} className="p-3 rounded-lg" style={{ background: "rgba(255,0,0,0.03)" }}>
                  <div className="flex items-center gap-3">
                    <AlertCircle className="w-4 h-4 text-red-400" />
                    {item.company && <Badge variant="outline" className="text-xs">{item.company}</Badge>}
                    <span className="text-sm">{item.topic}</span>
                  </div>
                  {item.error && <p className="text-xs text-red-400 mt-1 ml-7">{item.error}</p>}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

/* ── SETTINGS TAB ────────────────────────────────── */
function SettingsTab() {
  const [wheelRedirectUrl, setWheelRedirectUrl] = useState("");
  const [delayedPopupUrl, setDelayedPopupUrl] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const adminToken = localStorage.getItem("admin_token");

  useEffect(() => {
    const headers = adminToken ? { Authorization: `Bearer ${adminToken}` } : {};
    const fn = async () => {
      try {
        const res = await axios.get(`${API}/admin/settings`, { headers });
        setWheelRedirectUrl(res.data.wheel_bonus_redirect_url || "");
        setDelayedPopupUrl(res.data.delayed_popup_url || "");
      } catch { toast.error("Ayarlar yüklenemedi"); }
      finally { setLoading(false); }
    };
    fn();
  }, [adminToken]);

  const handleSave = async () => {
    const token = localStorage.getItem("admin_token");
    const authHeaders = token ? { Authorization: `Bearer ${token}` } : {};
    setSaving(true);
    try {
      await axios.put(`${API}/admin/settings`, {
        wheel_bonus_redirect_url: wheelRedirectUrl.trim(),
        delayed_popup_url: delayedPopupUrl.trim(),
      }, { headers: authHeaders });
      toast.success("Ayarlar kaydedildi");
    } catch { toast.error("Kaydedilemedi"); }
    finally { setSaving(false); }
  };

  if (loading) return <div className="flex justify-center py-8"><Loader2 className="w-8 h-8 animate-spin text-neon-green" /></div>;

  return (
    <div className="space-y-6 max-w-2xl">
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><Gift className="w-5 h-5" /> Çark – Bonusu Al butonu</CardTitle>
          <CardDescription>Çarkı çevirip bonus kazandıktan sonra &quot;Bonusu Al&quot; butonuna basıldığında kullanıcı bu URL&apos;ye yönlendirilir. Boş bırakırsanız rastgele bir bonus sitesi açılır.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="wheel-redirect-url">Yönlendirme URL&apos;si</Label>
            <Input
              id="wheel-redirect-url"
              type="url"
              placeholder="https://..."
              value={wheelRedirectUrl}
              onChange={(e) => setWheelRedirectUrl(e.target.value)}
              className="max-w-xl"
            />
          </div>
          <Button onClick={handleSave} disabled={saving}>
            {saving ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Save className="w-4 h-4 mr-2" />}
            Kaydet
          </Button>
        </CardContent>
      </Card>

      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><Clock className="w-5 h-5" /> 30 saniye sonra açılacak URL</CardTitle>
          <CardDescription>Bir URL girerseniz, kullanıcı sitede 30 saniye kaldıktan sonra bu adres yeni sekmede otomatik açılır. Boş bırakırsanız bu özellik devre dışı kalır.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="delayed-popup-url">URL</Label>
            <Input
              id="delayed-popup-url"
              type="url"
              placeholder="https://..."
              value={delayedPopupUrl}
              onChange={(e) => setDelayedPopupUrl(e.target.value)}
              className="max-w-xl"
            />
          </div>
          <Button onClick={handleSave} disabled={saving}>
            {saving ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : <Save className="w-4 h-4 mr-2" />}
            Kaydet
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}

/* ── MAIN ADMIN PAGE ─────────────────────────────── */
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
  const [aiTopic, setAiTopic] = useState("");

  useEffect(() => { fetchData(); }, [selectedDomain]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchData = async () => {
    try {
      const [statsRes, domainsRes, sitesRes, articlesRes] = await Promise.all([
        axios.get(`${API}/stats/dashboard${selectedDomain ? `?domain_id=${selectedDomain}` : ""}`),
        axios.get(`${API}/domains`),
        axios.get(`${API}/bonus-sites`),
        axios.get(`${API}/articles?limit=50`),
      ]);
      setStats(statsRes.data);
      setDomains(domainsRes.data);
      setBonusSites(sitesRes.data);
      setArticles(articlesRes.data);
    } catch (e) { console.error("Error:", e); }
    finally { setLoading(false); }
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
    } catch { toast.error("Oluşturulamadı"); }
    finally { setGenerating(false); }
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
            <span className="text-sm text-muted-foreground hidden md:block">Hoş geldin, <strong>{adminUser}</strong></span>
            <Select value={selectedDomain || "all"} onValueChange={(v) => setSelectedDomain(v === "all" ? null : v)}>
              <SelectTrigger className="w-48"><SelectValue placeholder="Domain Seç" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Tüm Domainler</SelectItem>
                {domains.map(d => <SelectItem key={d.id} value={d.id}>{d.domain_name}</SelectItem>)}
              </SelectContent>
            </Select>
            <Button onClick={fetchData} variant="outline" size="icon"><RefreshCw className="w-4 h-4" /></Button>
            <Button onClick={handleLogout} variant="outline" size="icon" data-testid="admin-logout-btn" title="Çıkış Yap"><LogOut className="w-4 h-4" /></Button>
          </div>
        </div>

        {/* Stats */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {[
              { label: "Domainler", value: stats.total_domains, color: "text-neon-green" },
              { label: "Bonus Siteleri", value: stats.total_bonus_sites, color: "" },
              { label: "Makaleler", value: stats.total_articles, color: "" },
              { label: "Auto Generated", value: stats.auto_generated_articles, color: "text-[#00F0FF]" },
              { label: "Companies", value: stats.total_companies || 0, color: "text-[#00F0FF]" },
              { label: "Featured Company", value: stats.featured_companies || 0, color: "text-neon-green" },
              { label: "Telegram Bot", value: stats.telegram_bots || 0, color: "text-purple-400" },
            ].map((s, i) => (
              <Card key={i} className="glass-card border-white/10">
                <CardHeader className="pb-2"><CardTitle className="text-xs text-muted-foreground">{s.label}</CardTitle></CardHeader>
                <CardContent><div className={`text-3xl font-heading font-bold ${s.color}`}>{s.value}</div></CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Tabs */}
        <Tabs defaultValue="domains" className="space-y-6">
          <TabsList className="grid grid-cols-10 w-full max-w-6xl">
            <TabsTrigger value="domains"><Globe className="w-4 h-4 mr-1.5" />Domainler</TabsTrigger>
            <TabsTrigger value="sites"><Gift className="w-4 h-4 mr-1.5" />Siteler</TabsTrigger>
            <TabsTrigger value="companies" data-testid="admin-companies-tab"><Building2 className="w-4 h-4 mr-1.5" />Companies</TabsTrigger>
            <TabsTrigger value="categories" data-testid="admin-categories-tab"><Layers className="w-4 h-4 mr-1.5" />Kategoriler</TabsTrigger>
            <TabsTrigger value="seo" data-testid="admin-seo-tab"><Search className="w-4 h-4 mr-1.5" />SEO</TabsTrigger>
            <TabsTrigger value="auto-content"><Wand2 className="w-4 h-4 mr-1.5" />Oto İçerik</TabsTrigger>
            <TabsTrigger value="articles"><FileText className="w-4 h-4 mr-1.5" />Makaleler</TabsTrigger>
            <TabsTrigger value="matches"><Activity className="w-4 h-4 mr-1.5" />Maçlar</TabsTrigger>
            <TabsTrigger value="telegram" data-testid="admin-telegram-tab"><Bot className="w-4 h-4 mr-1.5" />Telegram</TabsTrigger>
            <TabsTrigger value="settings"><Settings className="w-4 h-4 mr-1.5" />Ayarlar</TabsTrigger>
          </TabsList>

          <TabsContent value="domains"><DomainsTab domains={domains} onRefresh={fetchData} /></TabsContent>
          <TabsContent value="sites"><SitesTab bonusSites={bonusSites} onRefresh={fetchData} /></TabsContent>
          <TabsContent value="companies"><CompaniesTab /></TabsContent>
          <TabsContent value="categories"><CategoriesTab onRefresh={fetchData} /></TabsContent>
          <TabsContent value="seo" className="space-y-6"><SeoAssistant domainId={selectedDomain} /></TabsContent>

          {/* AUTO CONTENT TAB - SCHEDULER */}
          <TabsContent value="auto-content" className="space-y-6">
            <AutoContentScheduler onRefresh={fetchData} />
          </TabsContent>

          <TabsContent value="articles"><ArticlesTab articles={articles} onRefresh={fetchData} /></TabsContent>
          <TabsContent value="matches" className="space-y-6"><MatchesAdminTab /></TabsContent>
          <TabsContent value="telegram"><TelegramTab /></TabsContent>
          <TabsContent value="settings"><SettingsTab /></TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default AdminPage;
