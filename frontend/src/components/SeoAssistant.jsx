import { useState, useEffect } from "react";
import axios from "axios";
import { API } from "@/App";
import { toast } from "sonner";
import {
  Search, BarChart3, FileText, Target, Link2, Wand2,
  TrendingUp, AlertTriangle, CheckCircle2, Loader2, RefreshCw,
  ArrowRight, ChevronDown, ChevronUp, Trash2, Eye, Zap,
  Globe, BookOpen, Hash, Award
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Label } from "@/components/ui/label";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";

/* ─── Score Ring ───────────────────────────────────── */
function ScoreRing({ score, size = 100, label }) {
  const r = (size - 12) / 2;
  const circ = 2 * Math.PI * r;
  const offset = circ - (score / 100) * circ;
  const color = score >= 75 ? "#00FF87" : score >= 50 ? "#FBBF24" : "#EF4444";

  return (
    <div className="flex flex-col items-center gap-1.5">
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none"
          stroke="rgba(255,255,255,0.06)" strokeWidth="6" />
        <circle cx={size / 2} cy={size / 2} r={r} fill="none"
          stroke={color} strokeWidth="6" strokeDasharray={circ}
          strokeDashoffset={offset} strokeLinecap="round"
          style={{ transition: "stroke-dashoffset 0.8s ease" }} />
        <text x={size / 2} y={size / 2} textAnchor="middle" dominantBaseline="central"
          fill={color} fontSize={size * 0.28} fontWeight="bold"
          transform={`rotate(90 ${size / 2} ${size / 2})`}>
          {score}
        </text>
      </svg>
      {label && <span className="text-xs text-muted-foreground">{label}</span>}
    </div>
  );
}

/* ─── Dashboard Tab ────────────────────────────────── */
function DashboardTab({ domainId }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const res = await axios.get(`${API}/seo/dashboard${domainId ? `?domain_id=${domainId}` : ""}`);
        setData(res.data);
      } catch { toast.error("Dashboard yüklenemedi"); }
      finally { setLoading(false); }
    })();
  }, [domainId]);

  if (loading) return <div className="flex justify-center py-16"><Loader2 className="w-6 h-6 animate-spin" /></div>;
  if (!data) return null;

  return (
    <div className="space-y-6" data-testid="seo-dashboard">
      {/* Score + Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="glass-card border-white/10 flex items-center justify-center py-6 md:row-span-2">
          <ScoreRing score={data.health_score} size={140} label="SEO Skor" />
        </Card>

        {[
          { label: "Makaleler", value: data.total_articles, icon: FileText, accent: "#00FF87" },
          { label: "Bonus Siteleri", value: data.total_bonus_sites, icon: Gift, accent: "#00F0FF" },
          { label: "Toplam Görüntülenme", value: data.total_views, icon: Eye, accent: "#FBBF24" },
          { label: "AI İçerik", value: data.ai_generated_articles, icon: Wand2, accent: "#A78BFA" },
          { label: "Raporlar", value: data.total_reports, icon: BarChart3, accent: "#F472B6" },
          { label: "Domainler", value: data.total_domains, icon: Globe, accent: "#34D399" },
        ].map((s, i) => (
          <Card key={i} className="glass-card border-white/10">
            <CardContent className="p-4 flex items-center gap-3">
              <s.icon className="w-5 h-5 shrink-0" style={{ color: s.accent }} />
              <div>
                <p className="text-xs text-muted-foreground">{s.label}</p>
                <p className="text-xl font-heading font-bold" style={{ color: s.accent }}>{s.value}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Issues */}
      {data.issues && (
        <Card className="glass-card border-white/10">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-yellow-500" />Tespit Edilen Sorunlar
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {[
                { label: "Eksik Meta Etiket", value: data.issues.missing_meta, color: "#EF4444" },
                { label: "Kısa İçerik (<300 kelime)", value: data.issues.short_content, color: "#FBBF24" },
                { label: "Etiketsiz Makale", value: data.issues.no_tags, color: "#F97316" },
              ].map((issue, i) => (
                <div key={i} className="rounded-lg border p-3" style={{ borderColor: "rgba(255,255,255,0.08)" }}>
                  <p className="text-xs text-muted-foreground">{issue.label}</p>
                  <p className="text-2xl font-bold mt-1" style={{ color: issue.value > 0 ? issue.color : "#00FF87" }}>
                    {issue.value}
                  </p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Recommendations */}
      {data.recommendations?.filter(Boolean).length > 0 && (
        <Card className="glass-card border-white/10">
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <Zap className="w-4 h-4 text-[#00F0FF]" />Öneriler
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {data.recommendations.filter(Boolean).map((rec, i) => (
                <li key={i} className="flex items-start gap-2 text-sm">
                  <ArrowRight className="w-4 h-4 mt-0.5 shrink-0 text-[#00F0FF]" />
                  <span className="text-muted-foreground">{rec}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

/* ─── Keyword Research Tab ─────────────────────────── */
function KeywordTab() {
  const [keywords, setKeywords] = useState("");
  const [niche, setNiche] = useState("bonus");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleResearch = async () => {
    const kws = keywords.split(",").map(k => k.trim()).filter(Boolean);
    if (!kws.length) return toast.error("En az bir anahtar kelime girin");
    setLoading(true);
    try {
      const res = await axios.post(`${API}/seo/keyword-research`, { keywords: kws, niche, language: "tr" });
      setResult(res.data);
      toast.success("Anahtar kelime analizi tamamlandı");
    } catch { toast.error("Analiz başarısız"); }
    finally { setLoading(false); }
  };

  const difficultyColor = (score) => {
    if (typeof score !== "number") return "#888";
    if (score <= 30) return "#00FF87";
    if (score <= 60) return "#FBBF24";
    return "#EF4444";
  };

  return (
    <div className="space-y-6" data-testid="seo-keyword-tab">
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><Search className="w-5 h-5 text-[#00F0FF]" />Anahtar Kelime Araştırma</CardTitle>
          <CardDescription>AI destekli anahtar kelime analizi, arama hacmi tahmini ve içerik fikirleri.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2">
              <Label>Anahtar Kelimeler (virgülle ayırın)</Label>
              <Input
                value={keywords}
                onChange={(e) => setKeywords(e.target.value)}
                placeholder="deneme bonusu, bahis siteleri, canlı bahis"
                data-testid="keyword-input"
              />
            </div>
            <div>
              <Label>Niş</Label>
              <Select value={niche} onValueChange={setNiche}>
                <SelectTrigger data-testid="niche-select"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="bonus">Bonus/Bahis</SelectItem>
                  <SelectItem value="spor">Spor Haberleri</SelectItem>
                  <SelectItem value="casino">Casino</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <Button onClick={handleResearch} disabled={loading} className="bg-[#00F0FF] text-black hover:bg-[#00F0FF]/90" data-testid="keyword-search-btn">
            {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Search className="w-4 h-4 mr-2" />}
            Araştır
          </Button>
        </CardContent>
      </Card>

      {result && !result.raw_analysis && (
        <>
          {/* Keywords Table */}
          {result.keywords?.length > 0 && (
            <Card className="glass-card border-white/10">
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Anahtar Kelime Analizi</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-white/10 text-left text-xs text-muted-foreground uppercase tracking-wider">
                        <th className="pb-3 pr-4">Kelime</th>
                        <th className="pb-3 pr-4">Hacim</th>
                        <th className="pb-3 pr-4">Rekabet</th>
                        <th className="pb-3 pr-4">Zorluk</th>
                        <th className="pb-3 pr-4">Amaç</th>
                        <th className="pb-3">Öneri</th>
                      </tr>
                    </thead>
                    <tbody>
                      {result.keywords.map((kw, i) => (
                        <tr key={i} className="border-b border-white/5">
                          <td className="py-3 pr-4 font-medium">{kw.keyword}</td>
                          <td className="py-3 pr-4">
                            <Badge variant="outline" className="text-xs">{kw.search_volume_estimate}</Badge>
                          </td>
                          <td className="py-3 pr-4">
                            <Badge variant="outline" className="text-xs">{kw.competition}</Badge>
                          </td>
                          <td className="py-3 pr-4">
                            <span className="font-bold" style={{ color: difficultyColor(kw.difficulty_score) }}>
                              {kw.difficulty_score}
                            </span>
                          </td>
                          <td className="py-3 pr-4 text-xs text-muted-foreground">{kw.intent}</td>
                          <td className="py-3 text-xs text-muted-foreground max-w-[200px] truncate">{kw.recommendation}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Related + Long Tail + Ideas */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {result.related_keywords?.length > 0 && (
              <Card className="glass-card border-white/10">
                <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-1.5"><Hash className="w-4 h-4 text-[#00FF87]" />İlgili Kelimeler</CardTitle></CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-1.5">
                    {result.related_keywords.map((kw, i) => (
                      <Badge key={i} variant="outline" className="text-xs">{kw}</Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
            {result.long_tail_suggestions?.length > 0 && (
              <Card className="glass-card border-white/10">
                <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-1.5"><TrendingUp className="w-4 h-4 text-[#FBBF24]" />Uzun Kuyruk</CardTitle></CardHeader>
                <CardContent>
                  <ul className="space-y-1.5 text-sm text-muted-foreground">
                    {result.long_tail_suggestions.map((s, i) => <li key={i} className="flex items-start gap-1.5"><ArrowRight className="w-3 h-3 mt-1 shrink-0 text-[#FBBF24]" />{s}</li>)}
                  </ul>
                </CardContent>
              </Card>
            )}
            {result.content_ideas?.length > 0 && (
              <Card className="glass-card border-white/10">
                <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-1.5"><BookOpen className="w-4 h-4 text-[#A78BFA]" />İçerik Fikirleri</CardTitle></CardHeader>
                <CardContent>
                  <ul className="space-y-1.5 text-sm text-muted-foreground">
                    {result.content_ideas.map((s, i) => <li key={i} className="flex items-start gap-1.5"><Wand2 className="w-3 h-3 mt-1 shrink-0 text-[#A78BFA]" />{s}</li>)}
                  </ul>
                </CardContent>
              </Card>
            )}
          </div>

          {result.summary && (
            <Card className="glass-card border-white/10">
              <CardContent className="p-4 text-sm text-muted-foreground">{result.summary}</CardContent>
            </Card>
          )}
        </>
      )}

      {result?.raw_analysis && (
        <Card className="glass-card border-white/10">
          <CardContent className="p-4 whitespace-pre-wrap text-sm text-muted-foreground">{result.raw_analysis}</CardContent>
        </Card>
      )}
    </div>
  );
}

/* ─── Site Audit Tab ───────────────────────────────── */
function AuditTab({ domainId }) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleAudit = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API}/seo/site-audit`, { domain_id: domainId });
      setResult(res.data);
      toast.success("Site denetimi tamamlandı");
    } catch { toast.error("Denetim başarısız"); }
    finally { setLoading(false); }
  };

  const catColor = (score) => score >= 75 ? "#00FF87" : score >= 50 ? "#FBBF24" : "#EF4444";

  return (
    <div className="space-y-6" data-testid="seo-audit-tab">
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><BarChart3 className="w-5 h-5 text-[#00FF87]" />Site SEO Denetimi</CardTitle>
          <CardDescription>AI destekli kapsamlı SEO denetimi. Teknik SEO, içerik kalitesi ve kullanıcı deneyimini analiz eder.</CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={handleAudit} disabled={loading} className="bg-[#00FF87] text-black hover:bg-[#00FF87]/90" data-testid="run-audit-btn">
            {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <BarChart3 className="w-4 h-4 mr-2" />}
            Denetim Başlat
          </Button>
        </CardContent>
      </Card>

      {result && !result.raw_analysis && (
        <>
          {/* Overall Score */}
          <div className="flex justify-center">
            <ScoreRing score={result.overall_score || 0} size={160} label="Genel SEO Skoru" />
          </div>

          {/* Categories */}
          {result.categories?.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {result.categories.map((cat, i) => (
                <Card key={i} className="glass-card border-white/10">
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-sm">{cat.name}</CardTitle>
                      <span className="text-lg font-bold" style={{ color: catColor(cat.score) }}>{cat.score}</span>
                    </div>
                    <div className="w-full h-1.5 rounded-full mt-2" style={{ background: "rgba(255,255,255,0.06)" }}>
                      <div className="h-full rounded-full transition-all" style={{ width: `${cat.score}%`, background: catColor(cat.score) }} />
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {cat.issues?.length > 0 && (
                      <div>
                        <p className="text-xs text-muted-foreground mb-1.5">Sorunlar:</p>
                        <ul className="space-y-1">
                          {cat.issues.map((issue, j) => (
                            <li key={j} className="flex items-start gap-1.5 text-xs">
                              <AlertTriangle className="w-3 h-3 mt-0.5 shrink-0 text-yellow-500" />
                              <span className="text-muted-foreground">{issue}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {cat.fixes?.length > 0 && (
                      <div>
                        <p className="text-xs text-muted-foreground mb-1.5">Çözümler:</p>
                        <ul className="space-y-1">
                          {cat.fixes.map((fix, j) => (
                            <li key={j} className="flex items-start gap-1.5 text-xs">
                              <CheckCircle2 className="w-3 h-3 mt-0.5 shrink-0 text-[#00FF87]" />
                              <span className="text-muted-foreground">{fix}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {/* Priority Actions */}
          {result.priority_actions?.length > 0 && (
            <Card className="glass-card border-white/10">
              <CardHeader className="pb-3">
                <CardTitle className="text-base flex items-center gap-2"><Zap className="w-4 h-4 text-[#00F0FF]" />Öncelikli Aksiyonlar</CardTitle>
              </CardHeader>
              <CardContent>
                <ol className="space-y-2">
                  {result.priority_actions.map((action, i) => (
                    <li key={i} className="flex items-start gap-3 text-sm">
                      <span className="shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold" style={{ background: "rgba(0,240,255,0.15)", color: "#00F0FF" }}>{i + 1}</span>
                      <span className="text-muted-foreground">{action}</span>
                    </li>
                  ))}
                </ol>
              </CardContent>
            </Card>
          )}

          {result.summary && (
            <Card className="glass-card border-white/10">
              <CardContent className="p-4 text-sm text-muted-foreground">{result.summary}</CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}

/* ─── Competitor Tab ───────────────────────────────── */
function CompetitorTab() {
  const [url, setUrl] = useState("");
  const [ourDomain, setOurDomain] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleAnalyze = async () => {
    if (!url) return toast.error("Rakip URL gerekli");
    setLoading(true);
    try {
      const res = await axios.post(`${API}/seo/competitor-deep`, { competitor_url: url, our_domain: ourDomain });
      setResult(res.data);
      toast.success("Rakip analizi tamamlandı");
    } catch { toast.error("Analiz başarısız"); }
    finally { setLoading(false); }
  };

  const prioColor = { "yüksek": "#EF4444", "orta": "#FBBF24", "düşük": "#00FF87" };

  return (
    <div className="space-y-6" data-testid="seo-competitor-tab">
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><Target className="w-5 h-5 text-[#EF4444]" />Rakip Analizi</CardTitle>
          <CardDescription>AI destekli derin rakip analizi, anahtar kelime boşlukları ve aksiyon planı.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>Rakip URL</Label>
              <Input value={url} onChange={(e) => setUrl(e.target.value)} placeholder="https://rakipsite.com" data-testid="competitor-url-input" />
            </div>
            <div>
              <Label>Bizim Domain (opsiyonel)</Label>
              <Input value={ourDomain} onChange={(e) => setOurDomain(e.target.value)} placeholder="guncelgiris.ai" />
            </div>
          </div>
          <Button onClick={handleAnalyze} disabled={loading} className="bg-red-500 text-white hover:bg-red-500/90" data-testid="competitor-analyze-btn">
            {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Target className="w-4 h-4 mr-2" />}
            Analiz Et
          </Button>
        </CardContent>
      </Card>

      {result && !result.raw_analysis && (
        <>
          {/* Profile */}
          {result.competitor_profile && (
            <Card className="glass-card border-white/10">
              <CardHeader className="pb-3">
                <CardTitle className="text-base">Rakip Profili</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-3">
                  <Globe className="w-5 h-5 text-muted-foreground" />
                  <span className="font-medium">{result.competitor_profile.domain}</span>
                  <Badge variant="outline">{result.competitor_profile.estimated_authority}</Badge>
                </div>
                <p className="text-sm text-muted-foreground">{result.competitor_profile.content_strategy}</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3">
                  <div>
                    <p className="text-xs text-muted-foreground mb-2">Güçlü Yönler:</p>
                    <ul className="space-y-1">
                      {result.competitor_profile.strengths?.map((s, i) => (
                        <li key={i} className="flex items-start gap-1.5 text-xs"><CheckCircle2 className="w-3 h-3 mt-0.5 shrink-0 text-[#00FF87]" /><span className="text-muted-foreground">{s}</span></li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground mb-2">Zayıf Yönler:</p>
                    <ul className="space-y-1">
                      {result.competitor_profile.weaknesses?.map((w, i) => (
                        <li key={i} className="flex items-start gap-1.5 text-xs"><AlertTriangle className="w-3 h-3 mt-0.5 shrink-0 text-yellow-500" /><span className="text-muted-foreground">{w}</span></li>
                      ))}
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Keyword Gaps + Content Opportunities */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {result.keyword_gaps?.length > 0 && (
              <Card className="glass-card border-white/10">
                <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-1.5"><Search className="w-4 h-4 text-[#00F0FF]" />Anahtar Kelime Boşlukları</CardTitle></CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-1.5">
                    {result.keyword_gaps.map((kw, i) => <Badge key={i} className="bg-[#00F0FF]/10 text-[#00F0FF] border-[#00F0FF]/30">{kw}</Badge>)}
                  </div>
                </CardContent>
              </Card>
            )}
            {result.content_opportunities?.length > 0 && (
              <Card className="glass-card border-white/10">
                <CardHeader className="pb-2"><CardTitle className="text-sm flex items-center gap-1.5"><BookOpen className="w-4 h-4 text-[#A78BFA]" />İçerik Fırsatları</CardTitle></CardHeader>
                <CardContent>
                  <ul className="space-y-1.5 text-sm text-muted-foreground">
                    {result.content_opportunities.map((opp, i) => <li key={i} className="flex items-start gap-1.5"><Wand2 className="w-3 h-3 mt-1 shrink-0 text-[#A78BFA]" />{opp}</li>)}
                  </ul>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Action Plan */}
          {result.action_plan?.length > 0 && (
            <Card className="glass-card border-white/10">
              <CardHeader className="pb-3"><CardTitle className="text-base flex items-center gap-2"><Zap className="w-4 h-4 text-[#FBBF24]" />Aksiyon Planı</CardTitle></CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {result.action_plan.map((ap, i) => (
                    <div key={i} className="flex items-start gap-3 p-3 rounded-lg" style={{ background: "rgba(255,255,255,0.02)" }}>
                      <Badge className="shrink-0 text-xs" style={{ background: `${prioColor[ap.priority] || "#888"}20`, color: prioColor[ap.priority] || "#888", borderColor: `${prioColor[ap.priority] || "#888"}40` }}>
                        {ap.priority}
                      </Badge>
                      <div>
                        <p className="text-sm font-medium">{ap.action}</p>
                        <p className="text-xs text-muted-foreground mt-0.5">{ap.impact}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {result.summary && (
            <Card className="glass-card border-white/10">
              <CardContent className="p-4 text-sm text-muted-foreground">{result.summary}</CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}

/* ─── Meta Generator Tab ──────────────────────────── */
function MetaTab() {
  const [topic, setTopic] = useState("");
  const [pageType, setPageType] = useState("article");
  const [keywords, setKeywords] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleGenerate = async () => {
    if (!topic) return toast.error("Konu gerekli");
    setLoading(true);
    try {
      const kws = keywords.split(",").map(k => k.trim()).filter(Boolean);
      const res = await axios.post(`${API}/seo/meta-generator`, { topic, page_type: pageType, keywords: kws });
      setResult(res.data);
      toast.success("Meta etiketler oluşturuldu");
    } catch { toast.error("Oluşturulamadı"); }
    finally { setLoading(false); }
  };

  const copyMeta = (opt) => {
    navigator.clipboard.writeText(`Title: ${opt.meta_title}\nDescription: ${opt.meta_description}`);
    toast.success("Kopyalandı");
  };

  return (
    <div className="space-y-6" data-testid="seo-meta-tab">
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><FileText className="w-5 h-5 text-[#A78BFA]" />Meta Etiket Oluşturucu</CardTitle>
          <CardDescription>AI ile SEO uyumlu meta title ve meta description oluşturun.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2">
              <Label>Konu</Label>
              <Input value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="Deneme Bonusu Veren Siteler 2026" data-testid="meta-topic-input" />
            </div>
            <div>
              <Label>Sayfa Tipi</Label>
              <Select value={pageType} onValueChange={setPageType}>
                <SelectTrigger><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="article">Makale</SelectItem>
                  <SelectItem value="category">Kategori</SelectItem>
                  <SelectItem value="homepage">Ana Sayfa</SelectItem>
                  <SelectItem value="guide">Rehber</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <div>
            <Label>Anahtar Kelimeler (opsiyonel, virgülle)</Label>
            <Input value={keywords} onChange={(e) => setKeywords(e.target.value)} placeholder="deneme bonusu, bonus veren siteler" />
          </div>
          <Button onClick={handleGenerate} disabled={loading} className="bg-[#A78BFA] text-black hover:bg-[#A78BFA]/90" data-testid="meta-generate-btn">
            {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Wand2 className="w-4 h-4 mr-2" />}
            Oluştur
          </Button>
        </CardContent>
      </Card>

      {result?.options?.length > 0 && (
        <div className="space-y-3">
          {result.options.map((opt, i) => (
            <Card key={i} className="glass-card border-white/10 hover:border-white/20 transition-colors cursor-pointer" onClick={() => copyMeta(opt)}>
              <CardContent className="p-4">
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-muted-foreground mb-1">Seçenek {i + 1}</p>
                    {/* SERP Preview */}
                    <div className="rounded-lg p-3 mb-2" style={{ background: "rgba(255,255,255,0.03)" }}>
                      <p className="text-[#8AB4F8] text-base truncate">{opt.meta_title}</p>
                      <p className="text-xs text-[#BDC1C6] mt-0.5 truncate">{window.location.origin}/makale/...</p>
                      <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{opt.meta_description}</p>
                    </div>
                    <div className="flex items-center gap-3 text-xs text-muted-foreground">
                      <span>Title: {opt.meta_title?.length || 0}/60 karakter</span>
                      <span>Desc: {opt.meta_description?.length || 0}/160 karakter</span>
                      {opt.focus_keyword && <Badge variant="outline" className="text-xs">{opt.focus_keyword}</Badge>}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}

          {result.schema_suggestion && (
            <div className="text-xs text-muted-foreground flex items-center gap-2">
              <Award className="w-3 h-3" />Önerilen Schema: <Badge variant="outline" className="text-xs">{result.schema_suggestion}</Badge>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/* ─── Content Optimizer Tab ────────────────────────── */
function OptimizerTab() {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [keyword, setKeyword] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleOptimize = async () => {
    if (!content && !title) return toast.error("Başlık veya içerik gerekli");
    setLoading(true);
    try {
      const res = await axios.post(`${API}/seo/content-optimizer`, { title, content, target_keyword: keyword });
      setResult(res.data);
      toast.success("İçerik analizi tamamlandı");
    } catch { toast.error("Analiz başarısız"); }
    finally { setLoading(false); }
  };

  return (
    <div className="space-y-6" data-testid="seo-optimizer-tab">
      <Card className="glass-card border-white/10">
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><Wand2 className="w-5 h-5 text-[#FBBF24]" />İçerik Optimizer</CardTitle>
          <CardDescription>Mevcut içeriğinizi yapıştırın, AI optimize edilmiş öneriler alsın.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label>Başlık</Label>
              <Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Makale başlığı" data-testid="optimizer-title-input" />
            </div>
            <div>
              <Label>Hedef Anahtar Kelime</Label>
              <Input value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="deneme bonusu" />
            </div>
          </div>
          <div>
            <Label>İçerik</Label>
            <Textarea value={content} onChange={(e) => setContent(e.target.value)} placeholder="Makale içeriğini buraya yapıştırın..." rows={6} data-testid="optimizer-content-input" />
          </div>
          <Button onClick={handleOptimize} disabled={loading} className="bg-[#FBBF24] text-black hover:bg-[#FBBF24]/90" data-testid="optimizer-run-btn">
            {loading ? <Loader2 className="w-4 h-4 mr-2 animate-spin" /> : <Wand2 className="w-4 h-4 mr-2" />}
            Optimize Et
          </Button>
        </CardContent>
      </Card>

      {result && !result.raw_result && (
        <>
          {result.optimized_title && (
            <Card className="glass-card border-white/10">
              <CardHeader className="pb-2"><CardTitle className="text-sm">Optimize Başlık Önerisi</CardTitle></CardHeader>
              <CardContent>
                <p className="text-[#00FF87] font-medium">{result.optimized_title}</p>
                {result.title_improvements?.length > 0 && (
                  <ul className="mt-2 space-y-1">
                    {result.title_improvements.map((tip, i) => (
                      <li key={i} className="flex items-start gap-1.5 text-xs text-muted-foreground"><ArrowRight className="w-3 h-3 mt-0.5 shrink-0 text-[#00F0FF]" />{tip}</li>
                    ))}
                  </ul>
                )}
              </CardContent>
            </Card>
          )}

          {result.content_improvements?.length > 0 && (
            <Card className="glass-card border-white/10">
              <CardHeader className="pb-2"><CardTitle className="text-sm">İçerik İyileştirmeleri</CardTitle></CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {result.content_improvements.map((imp, i) => (
                    <div key={i} className="p-3 rounded-lg" style={{ background: "rgba(255,255,255,0.02)" }}>
                      <p className="text-xs font-medium text-[#00F0FF] mb-1">{imp.section}</p>
                      <p className="text-xs text-yellow-500 mb-1">Sorun: {imp.current_issue}</p>
                      <p className="text-xs text-[#00FF87]">Öneri: {imp.suggestion}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {result.keyword_suggestions?.length > 0 && (
              <Card className="glass-card border-white/10">
                <CardHeader className="pb-2"><CardTitle className="text-sm">Anahtar Kelime Önerileri</CardTitle></CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-1.5">
                    {result.keyword_suggestions.map((kw, i) => <Badge key={i} variant="outline">{kw}</Badge>)}
                  </div>
                </CardContent>
              </Card>
            )}
            {result.readability_tips?.length > 0 && (
              <Card className="glass-card border-white/10">
                <CardHeader className="pb-2"><CardTitle className="text-sm">Okunabilirlik</CardTitle></CardHeader>
                <CardContent>
                  <ul className="space-y-1.5 text-xs text-muted-foreground">
                    {result.readability_tips.map((tip, i) => <li key={i} className="flex items-start gap-1.5"><CheckCircle2 className="w-3 h-3 mt-0.5 shrink-0 text-[#00FF87]" />{tip}</li>)}
                  </ul>
                </CardContent>
              </Card>
            )}
          </div>

          {result.estimated_improvement && (
            <Card className="glass-card border-white/10">
              <CardContent className="p-4 text-sm text-muted-foreground flex items-start gap-2">
                <TrendingUp className="w-4 h-4 shrink-0 text-[#00FF87] mt-0.5" />
                {result.estimated_improvement}
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}

/* ─── Reports Tab ──────────────────────────────────── */
function ReportsTab() {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [expanded, setExpanded] = useState(null);

  useEffect(() => {
    fetchReports();
  }, [filter]);

  const fetchReports = async () => {
    setLoading(true);
    try {
      const param = filter !== "all" ? `?report_type=${filter}` : "";
      const res = await axios.get(`${API}/seo/reports${param}`);
      setReports(res.data.reports || []);
    } catch { toast.error("Raporlar yüklenemedi"); }
    finally { setLoading(false); }
  };

  const handleDelete = async (id) => {
    try {
      await axios.delete(`${API}/seo/reports/${id}`);
      setReports(reports.filter(r => r.id !== id));
      toast.success("Rapor silindi");
    } catch { toast.error("Silinemedi"); }
  };

  const typeLabel = { keyword_research: "Anahtar Kelime", site_audit: "Site Denetimi", competitor_analysis: "Rakip Analizi" };
  const typeColor = { keyword_research: "#00F0FF", site_audit: "#00FF87", competitor_analysis: "#EF4444" };

  return (
    <div className="space-y-6" data-testid="seo-reports-tab">
      <div className="flex items-center gap-3">
        <Select value={filter} onValueChange={setFilter}>
          <SelectTrigger className="w-48"><SelectValue placeholder="Filtre" /></SelectTrigger>
          <SelectContent>
            <SelectItem value="all">Tümü</SelectItem>
            <SelectItem value="keyword_research">Anahtar Kelime</SelectItem>
            <SelectItem value="site_audit">Site Denetimi</SelectItem>
            <SelectItem value="competitor_analysis">Rakip Analizi</SelectItem>
          </SelectContent>
        </Select>
        <Button variant="outline" size="sm" onClick={fetchReports}><RefreshCw className="w-4 h-4" /></Button>
      </div>

      {loading ? (
        <div className="flex justify-center py-12"><Loader2 className="w-6 h-6 animate-spin" /></div>
      ) : reports.length === 0 ? (
        <div className="text-center py-12 text-muted-foreground">Henüz rapor bulunmuyor.</div>
      ) : (
        <div className="space-y-3">
          {reports.map((report) => (
            <Card key={report.id} className="glass-card border-white/10">
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Badge style={{ background: `${typeColor[report.type] || "#888"}15`, color: typeColor[report.type] || "#888", borderColor: `${typeColor[report.type] || "#888"}40` }}>
                      {typeLabel[report.type] || report.type}
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      {new Date(report.created_at).toLocaleDateString("tr-TR", { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" })}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="ghost" size="sm" onClick={() => setExpanded(expanded === report.id ? null : report.id)}>
                      {expanded === report.id ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                    </Button>
                    <Button variant="ghost" size="sm" onClick={() => handleDelete(report.id)} data-testid={`delete-report-${report.id}`}>
                      <Trash2 className="w-4 h-4 text-red-400" />
                    </Button>
                  </div>
                </div>
                {expanded === report.id && (
                  <div className="mt-3 p-3 rounded-lg text-xs overflow-auto max-h-64" style={{ background: "rgba(255,255,255,0.02)" }}>
                    <pre className="whitespace-pre-wrap text-muted-foreground">{JSON.stringify(report.result, null, 2)}</pre>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

/* ─── Gift icon placeholder ───────────────────────── */
function Gift(props) {
  return (
    <svg {...props} xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="8" width="18" height="4" rx="1" /><rect x="3" y="12" width="18" height="8" rx="1" />
      <path d="M12 8v12" /><path d="M19 12v8" /><path d="M5 12v8" />
      <path d="M7.5 8a2.5 2.5 0 0 1 0-5A4.8 8 0 0 1 12 8a4.8 8 0 0 1 4.5-5 2.5 2.5 0 0 1 0 5" />
    </svg>
  );
}

/* ─── MAIN SEO ASSISTANT EXPORT ───────────────────── */
export default function SeoAssistant({ domainId }) {
  return (
    <div data-testid="seo-assistant">
      <Tabs defaultValue="dashboard" className="space-y-6">
        <TabsList className="grid grid-cols-3 md:grid-cols-6 w-full">
          <TabsTrigger value="dashboard" data-testid="seo-tab-dashboard"><BarChart3 className="w-4 h-4 mr-1.5" />Dashboard</TabsTrigger>
          <TabsTrigger value="keywords" data-testid="seo-tab-keywords"><Search className="w-4 h-4 mr-1.5" />Kelimeler</TabsTrigger>
          <TabsTrigger value="audit" data-testid="seo-tab-audit"><BarChart3 className="w-4 h-4 mr-1.5" />Denetim</TabsTrigger>
          <TabsTrigger value="competitor" data-testid="seo-tab-competitor"><Target className="w-4 h-4 mr-1.5" />Rakip</TabsTrigger>
          <TabsTrigger value="meta" data-testid="seo-tab-meta"><FileText className="w-4 h-4 mr-1.5" />Meta</TabsTrigger>
          <TabsTrigger value="optimizer" data-testid="seo-tab-optimizer"><Wand2 className="w-4 h-4 mr-1.5" />Optimizer</TabsTrigger>
        </TabsList>

        <TabsContent value="dashboard"><DashboardTab domainId={domainId} /></TabsContent>
        <TabsContent value="keywords"><KeywordTab /></TabsContent>
        <TabsContent value="audit"><AuditTab domainId={domainId} /></TabsContent>
        <TabsContent value="competitor"><CompetitorTab /></TabsContent>
        <TabsContent value="meta"><MetaTab /></TabsContent>
        <TabsContent value="optimizer"><OptimizerTab /></TabsContent>
      </Tabs>

      {/* Reports section below tabs */}
      <div className="mt-8">
        <h3 className="font-heading text-lg font-bold uppercase tracking-tight mb-4 flex items-center gap-2">
          <FileText className="w-5 h-5 text-muted-foreground" />Geçmiş Raporlar
        </h3>
        <ReportsTab />
      </div>
    </div>
  );
}
