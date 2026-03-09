import { Link } from "react-router-dom";
import SEOHead from "@/components/SEOHead";
import { providers } from "@/data/providers";

export default function ProvidersPage() {
  const canonical =
    typeof window !== "undefined"
      ? `${window.location.origin}/saglayicilar`
      : undefined;

  return (
    <div className="min-h-screen pt-20 pb-16" data-testid="providers-page">
      <SEOHead
        title="Sağlayıcılar | Oyun Sağlayıcıları Listesi"
        description="Online casino ve bahis sitelerinde kullanılan tüm oyun sağlayıcılarının listesi. Pragmatic Play, NetEnt, Evolution, Push Gaming ve daha fazlası."
        canonical={canonical}
      />

      <section className="container mx-auto max-w-5xl px-4 md:px-6">
        <h1 className="font-heading text-3xl md:text-4xl font-black uppercase mb-4">
          Sağlayıcılar
        </h1>
        <p className="text-muted-foreground mb-8">
          Guncelgiris.ai üzerinde yer alan sitelerde kullanılan tüm oyun
          sağlayıcılarını aşağıda bulabilirsiniz. Her sağlayıcının detay
          sayfasında kısa tanıtım ve temel bilgiler yer alır.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          {providers.map((p) => (
            <Link
              key={p.slug}
              to={`/saglayicilar/${p.slug}`}
              className="group rounded-xl border border-white/10 bg-white/[0.02] p-4 hover:border-neon-green/40 transition-colors"
              data-testid={`provider-card-${p.slug}`}
            >
              <div className="font-heading text-lg font-bold mb-1 group-hover:text-neon-green">
                {p.name}
              </div>
              <div className="text-xs text-muted-foreground">
                Oyun sağlayıcısı
              </div>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}

