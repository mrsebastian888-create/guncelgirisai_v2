import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { API } from "@/App";
import { toast } from "sonner";
import {
  Plus, Trash2, Wand2, BarChart3, FileText, RefreshCw,
  Globe, TrendingUp, Target, Server, AlertCircle, Loader2,
  Copy, ExternalLink, LogOut, Activity, Sparkles, Star,
  Search, Edit2, Save, X, Eye, ChevronDown, ChevronUp,
  Gift, Calendar, ArrowUp, ArrowDown, Layers, Image,
  Play, Pause, Clock, ListChecks, Zap
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
  const [newSite, setNewSite] = useState({ name: "", logo_url: "", bonus_type: "deneme", bonus_amount: "", affiliate_url: "", rating: 4.5, features: "", turnover_requirement: 10 });
  const [editingId, setEditingId] = useState(null);
  const [editData, setEditData] = useState({});
  const [saving, setSaving] = useState(false);
  const [reordering, setReordering] = useState(false);

  const handleCreate = async () => {
    if (!newSite.name || !newSite.affiliate_url) return toast.error("Site adı ve URL gerekli");
    try {
      await axios.post(`${API}/bonus-sites`, { ...newSite, features: newSite.features.split(",").map(f => f.trim()).filter(Boolean), sort_order: bonusSites.length + 1 });
      toast.success("Site eklendi");
      setNewSite({ name: "", logo_url: "", bonus_type: "deneme", bonus_amount: "", affiliate_url: "", rating: 4.5, features: "", turnover_requirement: 10 });
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

  return (
    <div className="space-y-6" data-testid="sites-tab">
      {/* Create Form */}
      <Card className="glass-card border-white/10">
        <CardHeader><CardTitle className="flex items-center gap-2"><Plus className="w-5 h-5" />Yeni Bonus Sitesi</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Input placeholder="Site Adı" value={newSite.name} onChange={(e) => setNewSite({ ...newSite, name: e.target.value })} data-testid="new-site-name" />
            <Input placeholder="Logo URL" value={newSite.logo_url} onChange={(e) => setNewSite({ ...newSite, logo_url: e.target.value })} />
            <Input placeholder="Affiliate URL" value={newSite.affiliate_url} onChange={(e) => setNewSite({ ...newSite, affiliate_url: e.target.value })} data-testid="new-site-url" />
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
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
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

/* ── DOMAINS TAB ─────────────────────────────────── */
function DomainsTab({ domains, onRefresh }) {
  const [newDomain, setNewDomain] = useState({ domain_name: "", display_name: "", focus: "bonus", meta_title: "" });
  const [creating, setCreating] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [editData, setEditData] = useState({});
  const [saving, setSaving] = useState(false);
  const [siteStatus, setSiteStatus] = useState({});

  // Domain site durumlarını kontrol et
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

  return (
    <div className="space-y-6" data-testid="domains-tab">
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><Plus className="w-5 h-5" />Yeni Domain Ekle</CardTitle>
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

  useEffect(() => { fetchData(); }, [selectedDomain]);

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
          <TabsList className="grid grid-cols-7 w-full max-w-5xl">
            <TabsTrigger value="domains"><Globe className="w-4 h-4 mr-1.5" />Domainler</TabsTrigger>
            <TabsTrigger value="sites"><Gift className="w-4 h-4 mr-1.5" />Siteler</TabsTrigger>
            <TabsTrigger value="categories" data-testid="admin-categories-tab"><Layers className="w-4 h-4 mr-1.5" />Kategoriler</TabsTrigger>
            <TabsTrigger value="seo" data-testid="admin-seo-tab"><Search className="w-4 h-4 mr-1.5" />SEO</TabsTrigger>
            <TabsTrigger value="auto-content"><Wand2 className="w-4 h-4 mr-1.5" />Oto İçerik</TabsTrigger>
            <TabsTrigger value="articles"><FileText className="w-4 h-4 mr-1.5" />Makaleler</TabsTrigger>
            <TabsTrigger value="matches"><Activity className="w-4 h-4 mr-1.5" />Maçlar</TabsTrigger>
          </TabsList>

          <TabsContent value="domains"><DomainsTab domains={domains} onRefresh={fetchData} /></TabsContent>
          <TabsContent value="sites"><SitesTab bonusSites={bonusSites} onRefresh={fetchData} /></TabsContent>
          <TabsContent value="categories"><CategoriesTab onRefresh={fetchData} /></TabsContent>
          <TabsContent value="seo" className="space-y-6"><SeoAssistant domainId={selectedDomain} /></TabsContent>

          {/* AUTO CONTENT TAB */}
          <TabsContent value="auto-content" className="space-y-6">
            <Card className="glass-card border-white/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2"><Wand2 className="w-5 h-5 text-neon-green" />Otomatik İçerik Motoru</CardTitle>
                <CardDescription>AI ile SEO uyumlu içerik üretin. %80 bilgilendirici, %20 doğal affiliate.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div><Label>Makale Konusu</Label><Input value={aiTopic} onChange={(e) => setAiTopic(e.target.value)} placeholder="Deneme Bonusu Rehberi 2026" data-testid="ai-topic-input" /></div>
                  <div className="flex items-end gap-2">
                    <Button onClick={() => handleAutoGenerate("article")} disabled={generating} className="flex-1" data-testid="generate-article-btn">
                      {generating ? <Loader2 className="w-4 h-4 animate-spin" /> : <><FileText className="w-4 h-4 mr-2" />Makale Üret</>}
                    </Button>
                    <Button onClick={() => handleAutoGenerate("news")} disabled={generating} variant="outline">
                      <TrendingUp className="w-4 h-4 mr-2" />Haber Üret
                    </Button>
                  </div>
                </div>
                <div className="border-t border-white/10 pt-4">
                  <Button onClick={() => handleAutoGenerate("bulk")} disabled={generating} variant="secondary" className="w-full" data-testid="bulk-generate-btn">
                    {generating ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Wand2 className="w-4 h-4 mr-2" />}
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
                  <Button variant="outline" className="mt-4" onClick={() => { navigator.clipboard.writeText(generatedContent); toast.success("Kopyalandı"); }}>Kopyala</Button>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="articles"><ArticlesTab articles={articles} onRefresh={fetchData} /></TabsContent>
          <TabsContent value="matches" className="space-y-6"><MatchesAdminTab /></TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default AdminPage;
