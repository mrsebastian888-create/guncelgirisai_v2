import SEOHead from "@/components/SEOHead";

export default function ContactPage() {
  const canonical =
    typeof window !== "undefined"
      ? `${window.location.origin}/iletisim`
      : undefined;

  const email = "support@guncelgiris.ai";

  return (
    <div className="min-h-screen pt-20 pb-16" data-testid="contact-page">
      <SEOHead
        title="Bize Ulaşın | guncelgiris.ai"
        description="guncelgiris.ai ile ilgili soru, öneri ve iş birlikleri için support@guncelgiris.ai adresinden bize ulaşabilirsiniz."
        canonical={canonical}
      />

      <section className="container mx-auto max-w-3xl px-4 md:px-6">
        <h1 className="font-heading text-3xl md:text-4xl font-black uppercase mb-4">
          Bize Ulaşın
        </h1>
        <p className="text-muted-foreground mb-6">
          guncelgiris.ai hakkında sorularınız, geri bildirimleriniz veya iş
          birliği talepleriniz için aşağıdaki e-posta adresinden bizimle
          iletişime geçebilirsiniz.
        </p>

        <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-6">
          <p className="text-sm text-muted-foreground mb-2">E-posta adresi:</p>
          <a
            href={`mailto:${email}`}
            className="text-neon-green text-lg font-mono break-all"
          >
            {email}
          </a>
        </div>
      </section>
    </div>
  );
}

