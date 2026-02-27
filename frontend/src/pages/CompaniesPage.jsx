import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import axios from "axios";
import { BarChart3, Building2, Filter, Search } from "lucide-react";
import SEOHead from "@/components/SEOHead";

const API = process.env.REACT_APP_BACKEND_URL + "/api";

const formatVisits = (value) => {
  const visits = Number(value || 0);
  if (visits >= 1_000_000) return `${(visits / 1_000_000).toFixed(1)}M`;
  if (visits >= 1_000) return `${(visits / 1_000).toFixed(1)}K`;
  return `${visits}`;
};

export default function CompaniesPage() {
  const [searchParams] = useSearchParams();
  const [companies, setCompanies] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [activeCategory, setActiveCategory] = useState(searchParams.get("category") || "all");

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [companiesRes, categoriesRes] = await Promise.all([
          axios.get(`${API}/companies?limit=200`),
          axios.get(`${API}/company-categories`).catch(() => ({ data: [] })),
        ]);
        setCompanies(companiesRes.data || []);
        setCategories(categoriesRes.data || []);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const filteredCompanies = useMemo(() => {
    return (companies || []).filter((company) => {
      const categoryOk = activeCategory === "all" || company.category_id === activeCategory;
      const searchText = `${company.name} ${company.domain} ${company.description_short}`.toLowerCase();
      const searchOk = !search.trim() || searchText.includes(search.toLowerCase());
      return categoryOk && searchOk;
    });
  }, [companies, activeCategory, search]);

  return (
    <div className="min-h-screen bg-background pt-20 pb-16" data-testid="companies-page">
      <SEOHead
        title="AI Company Intelligence | Şirket Analizleri ve Trafik Verileri"
        description="AI Company Intelligence merkezi: trafik, teknoloji, kanal ve skor bazlı şirket profilleri."
        canonical="https://guncelgiris.ai/companies"
      />

      <section className="container mx-auto max-w-7xl px-4 md:px-6">
        <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-6 md:p-8 mb-6" data-testid="companies-page-hero">
          <div className="inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold uppercase tracking-widest mb-4"
            style={{ borderColor: "rgba(0,240,255,0.35)", color: "#00F0FF", background: "rgba(0,240,255,0.08)" }}>
            <Building2 className="w-3.5 h-3.5" /> AI Company Intelligence
          </div>
          <h1 className="font-heading font-black uppercase text-4xl md:text-5xl mb-3" data-testid="companies-page-title">Şirket İstihbarat Merkezi</h1>
          <p className="text-sm md:text-base text-muted-foreground max-w-3xl" data-testid="companies-page-description">
            Trafik, sıralama, teknoloji yığını ve kanal verilerine göre şirket profillerini karşılaştırın. En güçlü şirketleri skor bazlı keşfedin.
          </p>
        </div>

        <div className="rounded-xl border border-white/10 bg-white/[0.02] p-4 md:p-5 mb-6" data-testid="companies-filters-panel">
          <div className="grid grid-cols-1 lg:grid-cols-[1.5fr,2fr] gap-4">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Şirket ara (isim, domain, açıklama)"
                className="w-full pl-10 pr-4 py-2.5 rounded-lg border border-white/10 bg-black/20 text-sm"
                data-testid="companies-search-input"
              />
            </div>
            <div className="flex flex-wrap gap-2" data-testid="companies-category-filters">
              <button
                onClick={() => setActiveCategory("all")}
                className="px-3 py-2 rounded-full text-xs border"
                style={{ borderColor: activeCategory === "all" ? "#00F0FF" : "rgba(255,255,255,0.15)", color: activeCategory === "all" ? "#00F0FF" : "var(--foreground)" }}
                data-testid="companies-filter-all"
              >
                Tümü
              </button>
              {categories.map((category) => (
                <button
                  key={category.slug}
                  onClick={() => setActiveCategory(category.slug)}
                  className="px-3 py-2 rounded-full text-xs border"
                  style={{ borderColor: activeCategory === category.slug ? "#00F0FF" : "rgba(255,255,255,0.15)", color: activeCategory === category.slug ? "#00F0FF" : "var(--foreground)" }}
                  data-testid={`companies-filter-${category.slug}`}
                >
                  {category.name}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="mb-4 text-sm text-muted-foreground" data-testid="companies-results-count">
          {loading ? "Yükleniyor..." : `${filteredCompanies.length} şirket listeleniyor`}
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-48 rounded-xl border border-white/10 bg-white/[0.02] animate-pulse" />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4" data-testid="companies-grid">
            {filteredCompanies.map((company) => (
              <Link
                key={company.id}
                to={`/companies/${company.slug}`}
                className="rounded-xl border border-white/10 bg-white/[0.02] p-4 hover:border-[#00F0FF]/40 transition-colors"
                data-testid={`company-card-${company.id}`}
              >
                <div className="flex items-center gap-3 mb-3">
                  <img src={company.logo_url} alt={company.name} className="w-11 h-11 rounded-lg" data-testid={`company-card-logo-${company.id}`} />
                  <div className="min-w-0">
                    <h3 className="font-heading font-bold uppercase truncate" data-testid={`company-card-name-${company.id}`}>{company.name}</h3>
                    <p className="text-xs text-muted-foreground truncate" data-testid={`company-card-category-${company.id}`}>{company.category_id}</p>
                  </div>
                </div>

                <p className="text-xs text-muted-foreground line-clamp-2 mb-3" data-testid={`company-card-description-${company.id}`}>{company.description_short}</p>

                <div className="grid grid-cols-3 gap-2 text-xs mb-3">
                  <div className="rounded-md border border-white/10 p-2">
                    <p className="text-muted-foreground">Visits</p>
                    <p className="font-semibold text-neon-green" data-testid={`company-card-visits-${company.id}`}>{formatVisits(company.estimated_visits)}</p>
                  </div>
                  <div className="rounded-md border border-white/10 p-2">
                    <p className="text-muted-foreground">Global</p>
                    <p className="font-semibold" data-testid={`company-card-global-rank-${company.id}`}>#{company.global_rank || "-"}</p>
                  </div>
                  <div className="rounded-md border border-white/10 p-2">
                    <p className="text-muted-foreground">Score</p>
                    <p className="font-semibold text-[#00F0FF]" data-testid={`company-card-score-${company.id}`}>{company.intelligence_score}</p>
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs">
                  <span className="inline-flex items-center gap-1 text-muted-foreground">
                    <Filter className="w-3.5 h-3.5" /> {company.subcategory_id}
                  </span>
                  <span className="inline-flex items-center gap-1 text-[#00F0FF] font-semibold" data-testid={`company-card-cta-${company.id}`}>
                    <BarChart3 className="w-3.5 h-3.5" /> View Analysis
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
