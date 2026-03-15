import { useState, useEffect, useCallback } from "react";
import { Link as LinkIcon, Copy, Trash2, Edit2, Check, X, ExternalLink, Search } from "lucide-react";
import { toast } from "sonner";
import axios from "axios";
import SEOHead from "@/components/SEOHead";
import { API } from "@/App";

export default function LinkShortenerPage() {
  const [links, setLinks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [url, setUrl] = useState("");
  const [slug, setSlug] = useState("");
  const [creating, setCreating] = useState(false);
  const [editId, setEditId] = useState(null);
  const [editUrl, setEditUrl] = useState("");
  const [editSlug, setEditSlug] = useState("");
  const [deleteId, setDeleteId] = useState(null);
  const [search, setSearch] = useState("");

  const BASE = "https://guncelgiris.ai";

  const fetchLinks = useCallback(async () => {
    try {
      const res = await axios.get(`${API}/shortlinks`);
      setLinks(res.data.links || []);
    } catch { }
    setLoading(false);
  }, []);

  useEffect(() => { fetchLinks(); }, [fetchLinks]);

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!url || !slug) return;
    setCreating(true);
    try {
      const res = await axios.post(`${API}/shortlinks`, { original_url: url, slug: slug.toLowerCase() });
      setLinks(prev => [res.data, ...prev]);
      setUrl("");
      setSlug("");
      toast.success("Link basariyla olusturuldu!");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Link olusturulamadi");
    }
    setCreating(false);
  };

  const handleCopy = (shortUrl) => {
    navigator.clipboard.writeText(shortUrl);
    toast.success("Link kopyalandi!");
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      await axios.delete(`${API}/shortlinks/${deleteId}`);
      setLinks(prev => prev.filter(l => l.id !== deleteId));
      toast.success("Link silindi");
    } catch {
      toast.error("Silinemedi");
    }
    setDeleteId(null);
  };

  const handleUpdate = async (id) => {
    try {
      const res = await axios.put(`${API}/shortlinks/${id}`, { original_url: editUrl, slug: editSlug.toLowerCase() });
      setLinks(prev => prev.map(l => l.id === id ? res.data : l));
      setEditId(null);
      toast.success("Link guncellendi");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Guncellenemedi");
    }
  };

  const filtered = search
    ? links.filter(l => l.slug.includes(search.toLowerCase()) || l.original_url.toLowerCase().includes(search.toLowerCase()))
    : links;

  return (
    <div className="min-h-screen bg-background pt-20 pb-16" data-testid="link-shortener-page">
      <SEOHead title="Link Kisaltici" description="URL kisaltma araci. Ozel slug ile kisa linkler olusturun." canonical="https://guncelgiris.ai/link-kisaltici" />

      {/* Hero */}
      <section className="relative overflow-hidden py-12 md:py-16">
        <div className="absolute inset-0 bg-[#050505]" />
        <div className="absolute inset-0 opacity-[0.04]" style={{
          backgroundImage: "linear-gradient(rgba(0,255,135,0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(0,255,135,0.3) 1px, transparent 1px)",
          backgroundSize: "60px 60px"
        }} />
        <div className="relative z-10 container mx-auto max-w-4xl px-4">
          <div className="inline-flex items-center gap-2 rounded-full border px-4 py-1.5 mb-4 text-xs font-semibold uppercase tracking-widest"
            style={{ borderColor: "rgba(0,255,135,0.3)", color: "#00FF87", background: "rgba(0,255,135,0.08)" }}>
            <LinkIcon className="w-3.5 h-3.5" /> Link Kisaltici
          </div>
          <h1 className="font-heading font-black text-3xl md:text-5xl uppercase tracking-tight leading-none mb-3" data-testid="shortener-h1">
            <span className="text-white">LINK</span> <span className="text-neon-green">KISALTICI</span>
          </h1>
          <p className="text-muted-foreground max-w-xl">Ozel slug ile kisa linkler olusturun. guncelgiris.ai/slug formatinda.</p>
        </div>
      </section>

      <div className="container mx-auto max-w-4xl px-4 mt-8 space-y-8">
        {/* Create Form */}
        <form onSubmit={handleCreate} className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="shortener-form">
          <h2 className="font-heading text-lg font-bold uppercase mb-4 flex items-center gap-2">
            <LinkIcon className="w-5 h-5 text-neon-green" /> Yeni Link Olustur
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-muted-foreground mb-1 block">Orijinal URL</label>
              <input
                type="url"
                value={url}
                onChange={e => setUrl(e.target.value)}
                placeholder="https://www.example.com"
                required
                className="w-full px-4 py-3 rounded-xl border text-sm outline-none transition-all focus:ring-1 focus:ring-neon-green/50"
                style={{ background: "rgba(255,255,255,0.04)", borderColor: "rgba(255,255,255,0.1)", color: "var(--foreground)" }}
                data-testid="shortener-url-input"
              />
            </div>
            <div>
              <label className="text-xs text-muted-foreground mb-1 block">Ozel Slug</label>
              <div className="flex items-center gap-2">
                <span className="text-xs text-muted-foreground whitespace-nowrap hidden sm:block">guncelgiris.ai/</span>
                <input
                  type="text"
                  value={slug}
                  onChange={e => setSlug(e.target.value.replace(/[^a-zA-Z0-9-]/g, "").toLowerCase())}
                  placeholder="ornek-slug"
                  required
                  className="w-full px-4 py-3 rounded-xl border text-sm outline-none transition-all focus:ring-1 focus:ring-neon-green/50"
                  style={{ background: "rgba(255,255,255,0.04)", borderColor: "rgba(255,255,255,0.1)", color: "var(--foreground)" }}
                  data-testid="shortener-slug-input"
                />
              </div>
            </div>
          </div>
          {slug && (
            <div className="mt-2 text-xs text-muted-foreground">
              Kisaltilmis URL: <span className="text-neon-green font-mono">{BASE}/{slug}</span>
            </div>
          )}
          <button
            type="submit"
            disabled={creating || !url || !slug}
            className="mt-4 px-6 py-3 rounded-xl font-heading font-bold uppercase text-sm transition-all hover:scale-105 disabled:opacity-50 disabled:hover:scale-100 flex items-center gap-2"
            style={{ background: "#00FF87", color: "#000" }}
            data-testid="shortener-create-btn"
          >
            <LinkIcon className="w-4 h-4" /> {creating ? "Olusturuluyor..." : "Kisalt"}
          </button>
        </form>

        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Link ara..."
            className="w-full pl-10 pr-4 py-2.5 rounded-xl border text-sm outline-none transition-all focus:ring-1"
            style={{ background: "rgba(255,255,255,0.04)", borderColor: "rgba(255,255,255,0.1)", color: "var(--foreground)" }}
            data-testid="shortener-search"
          />
        </div>

        {/* Links Table */}
        <div className="rounded-2xl border border-white/10 bg-white/[0.02] overflow-hidden" data-testid="shortener-table">
          <div className="hidden md:grid grid-cols-[1fr_1fr_100px_80px_120px] gap-4 px-6 py-3 text-xs text-muted-foreground uppercase tracking-wider border-b border-white/5">
            <span>Orijinal URL</span>
            <span>Kisa Link</span>
            <span>Tarih</span>
            <span>Tik</span>
            <span>Islemler</span>
          </div>

          {loading ? (
            <div className="p-8 text-center text-muted-foreground">Yukleniyor...</div>
          ) : filtered.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground" data-testid="shortener-empty">
              <LinkIcon className="w-10 h-10 mx-auto mb-2 opacity-30" />
              {search ? "Sonuc bulunamadi" : "Henuz link olusturulmadi"}
            </div>
          ) : (
            <div className="divide-y divide-white/5">
              {filtered.map((link) => (
                <div key={link.id} className="px-4 md:px-6 py-4 hover:bg-white/[0.02] transition-colors" data-testid={`shortener-link-${link.slug}`}>
                  {editId === link.id ? (
                    /* Edit mode */
                    <div className="flex flex-col md:flex-row gap-3">
                      <input value={editUrl} onChange={e => setEditUrl(e.target.value)} className="flex-1 px-3 py-2 rounded-lg border text-sm"
                        style={{ background: "rgba(255,255,255,0.06)", borderColor: "rgba(255,255,255,0.15)", color: "var(--foreground)" }} />
                      <input value={editSlug} onChange={e => setEditSlug(e.target.value.replace(/[^a-zA-Z0-9-]/g, "").toLowerCase())} className="w-40 px-3 py-2 rounded-lg border text-sm"
                        style={{ background: "rgba(255,255,255,0.06)", borderColor: "rgba(255,255,255,0.15)", color: "var(--foreground)" }} />
                      <div className="flex gap-2">
                        <button onClick={() => handleUpdate(link.id)} className="p-2 rounded-lg bg-neon-green/20 text-neon-green hover:bg-neon-green/30"><Check className="w-4 h-4" /></button>
                        <button onClick={() => setEditId(null)} className="p-2 rounded-lg bg-red-500/20 text-red-400 hover:bg-red-500/30"><X className="w-4 h-4" /></button>
                      </div>
                    </div>
                  ) : (
                    /* View mode */
                    <div className="grid grid-cols-1 md:grid-cols-[1fr_1fr_100px_80px_120px] gap-2 md:gap-4 items-center">
                      <a href={link.original_url} target="_blank" rel="noopener noreferrer" className="text-sm text-muted-foreground truncate hover:text-foreground flex items-center gap-1">
                        <ExternalLink className="w-3 h-3 flex-shrink-0" /> {link.original_url}
                      </a>
                      <div className="text-sm font-mono text-neon-green truncate">{BASE}/{link.slug}</div>
                      <div className="text-xs text-muted-foreground">{new Date(link.created_at).toLocaleDateString("tr-TR")}</div>
                      <div className="text-sm font-bold text-foreground">{link.click_count}</div>
                      <div className="flex items-center gap-1.5">
                        <button onClick={() => handleCopy(`${BASE}/${link.slug}`)} className="p-2 rounded-lg hover:bg-white/10 transition-colors" title="Kopyala" data-testid={`copy-${link.slug}`}>
                          <Copy className="w-4 h-4 text-muted-foreground" />
                        </button>
                        <button onClick={() => { setEditId(link.id); setEditUrl(link.original_url); setEditSlug(link.slug); }} className="p-2 rounded-lg hover:bg-white/10 transition-colors" title="Duzenle" data-testid={`edit-${link.slug}`}>
                          <Edit2 className="w-4 h-4 text-muted-foreground" />
                        </button>
                        <button onClick={() => setDeleteId(link.id)} className="p-2 rounded-lg hover:bg-red-500/20 transition-colors" title="Sil" data-testid={`delete-${link.slug}`}>
                          <Trash2 className="w-4 h-4 text-red-400" />
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {deleteId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm" data-testid="delete-modal">
          <div className="rounded-2xl border border-white/10 bg-background p-6 max-w-sm w-full mx-4">
            <h3 className="font-heading text-lg font-bold uppercase mb-2">Link Silinecek</h3>
            <p className="text-sm text-muted-foreground mb-6">Bu linki silmek istediginizden emin misiniz? Bu islem geri alinamaz.</p>
            <div className="flex gap-3">
              <button onClick={handleDelete} className="flex-1 px-4 py-2.5 rounded-xl bg-red-500 text-white font-heading font-bold uppercase text-sm hover:bg-red-600" data-testid="delete-confirm-btn">Sil</button>
              <button onClick={() => setDeleteId(null)} className="flex-1 px-4 py-2.5 rounded-xl border border-white/15 font-heading font-bold uppercase text-sm hover:bg-white/5" data-testid="delete-cancel-btn">Iptal</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
