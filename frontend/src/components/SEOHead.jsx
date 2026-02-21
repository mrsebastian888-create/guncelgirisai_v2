import { Helmet } from "react-helmet-async";
import { useEffect } from "react";

const SITE_NAME = "Bonus Rehberi";
const DEFAULT_IMAGE = "https://images.pexels.com/photos/12201296/pexels-photo-12201296.jpeg?w=1200&q=80";

export default function SEOHead({
  title,
  description,
  canonical,
  type = "website",
  image,
  article,
  noindex = false,
  jsonLd,
}) {
  const fullTitle = title ? title + " | " + SITE_NAME : SITE_NAME;
  const metaDesc = description || "En güvenilir bonus siteleri, deneme bonusları ve spor bahis rehberleri.";
  const metaImage = image || DEFAULT_IMAGE;
  const url = canonical || (typeof window !== "undefined" ? window.location.href : "");

  // Handle JSON-LD via useEffect since Helmet doesn't support dynamic children well
  useEffect(() => {
    const scripts = [];
    const ldData = jsonLd ? (Array.isArray(jsonLd) ? jsonLd : [jsonLd]).filter(Boolean) : [];
    ldData.forEach((ld) => {
      const script = document.createElement("script");
      script.type = "application/ld+json";
      script.setAttribute("data-seo-head", "true");
      script.textContent = JSON.stringify(ld);
      document.head.appendChild(script);
      scripts.push(script);
    });
    return () => {
      scripts.forEach((s) => s.remove());
    };
  }, [jsonLd]);

  return (
    <Helmet defer={false}>
      <title>{String(fullTitle)}</title>
      <meta name="description" content={metaDesc} />
      <link rel="canonical" href={url} />
      {noindex && <meta name="robots" content="noindex, nofollow" />}
      <meta property="og:type" content={type} />
      <meta property="og:title" content={fullTitle} />
      <meta property="og:description" content={metaDesc} />
      <meta property="og:image" content={metaImage} />
      <meta property="og:url" content={url} />
      <meta property="og:site_name" content={SITE_NAME} />
      <meta property="og:locale" content="tr_TR" />
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={fullTitle} />
      <meta name="twitter:description" content={metaDesc} />
      <meta name="twitter:image" content={metaImage} />
      {article && article.publishedTime && <meta property="article:published_time" content={article.publishedTime} />}
      {article && article.modifiedTime && <meta property="article:modified_time" content={article.modifiedTime} />}
      {article && article.author && <meta property="article:author" content={article.author} />}
      {article && article.category && <meta property="article:section" content={article.category} />}
    </Helmet>
  );
}
