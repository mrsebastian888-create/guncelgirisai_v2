import { Link, useParams } from "react-router-dom";
import SEOHead from "@/components/SEOHead";
import { providers } from "@/data/providers";

export default function ProviderDetailPage() {
  const { slug } = useParams();
  const provider = providers.find((p) => p.slug === slug);

  if (!provider) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center pt-20 gap-4">
        <h1 className="font-heading text-2xl">Sağlayıcı bulunamadı</h1>
        <Link to="/saglayicilar" className="text-neon-green hover:underline">
          Sağlayıcı listesine dön
        </Link>
      </div>
    );
  }

  const title = `${provider.name} Oyun Sağlayıcısı`;
  const description = `${provider.name} sağlayıcısının slot ve casino oyunları hakkında genel bilgiler. Bu sayfa, ${provider.name} için kısa tanıtım ve temel bilgileri içerir.`;
  const canonical =
    typeof window !== "undefined"
      ? `${window.location.origin}/saglayicilar/${provider.slug}`
      : undefined;

  return (
    <div className="min-h-screen pt-20 pb-16" data-testid="provider-detail-page">
      <SEOHead
        title={title}
        description={description}
        canonical={canonical}
        type="article"
      />

      <section className="container mx-auto max-w-3xl px-4 md:px-6">
        <nav className="text-xs text-muted-foreground mb-4">
          <Link to="/" className="hover:text-neon-green">
            Ana Sayfa
          </Link>{" "}
          /{" "}
          <Link to="/saglayicilar" className="hover:text-neon-green">
            Sağlayıcılar
          </Link>{" "}
          / <span>{provider.name}</span>
        </nav>

        <h1 className="font-heading text-3xl md:text-4xl font-black uppercase mb-4">
          {provider.name}
        </h1>

        <p className="text-muted-foreground mb-6">{description}</p>

        <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-6 space-y-3">
          <h2 className="font-heading text-xl font-bold uppercase">
            Genel Bakış
          </h2>
          <p className="text-sm text-muted-foreground">
            Bu bölümde {provider.name} sağlayıcısının oyun portföyü, öne çıkan
            slot ve casino oyunları, RTP değerleri ve desteklediği platformlar
            gibi bilgiler yer alabilir. İçerik henüz taslak aşamasında; ihtiyaç
            oldukça detaylandırılabilir.
          </p>
        </div>
      </section>
    </div>
  );
}

