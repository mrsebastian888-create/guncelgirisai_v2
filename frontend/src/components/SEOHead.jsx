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

  // Handle JSON-LD via useEffect since Helmet doesn't support .map() well
  useEffect(() => {
    const scripts = [];
    const ldData = jsonLd ? (Array.isArray(jsonLd) ? jsonLd : [jsonLd]).filter(Boolean) : [];
    ldData.forEach((ld, i) => {
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

  const metaTags = [
    { name: "description", content: metaDesc },
    { property: "og:type", content: type },
    { property: "og:title", content: fullTitle },
    { property: "og:description", content: metaDesc },
    { property: "og:image", content: metaImage },
    { property: "og:url", content: url },
    { property: "og:site_name", content: SITE_NAME },
    { property: "og:locale", content: "tr_TR" },
    { name: "twitter:card", content: "summary_large_image" },
    { name: "twitter:title", content: fullTitle },
    { name: "twitter:description", content: metaDesc },
    { name: "twitter:image", content: metaImage },
  ];

  if (noindex) metaTags.push({ name: "robots", content: "noindex, nofollow" });
  if (article) {
    if (article.publishedTime) metaTags.push({ property: "article:published_time", content: article.publishedTime });
    if (article.modifiedTime) metaTags.push({ property: "article:modified_time", content: article.modifiedTime });
    if (article.author) metaTags.push({ property: "article:author", content: article.author });
    if (article.category) metaTags.push({ property: "article:section", content: article.category });
  }

  return (
    <Helmet
      title={fullTitle}
      meta={metaTags}
      link={url ? [{ rel: "canonical", href: url }] : []}
    />
  );
}
