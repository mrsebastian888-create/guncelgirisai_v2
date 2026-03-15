import { useEffect } from "react";

const SITE_NAME = "Bonus Rehberi";
const DEFAULT_IMAGE = "https://images.pexels.com/photos/12201296/pexels-photo-12201296.jpeg?w=1200&q=80";

function ensureAbsoluteImage(src) {
  if (!src) return null;
  if (typeof window === "undefined") return src;
  if (/^https?:\/\//i.test(src)) return src;
  const origin = window.location.origin;
  return src.startsWith("/") ? `${origin}${src}` : `${origin}/${src}`;
}

export default function SEOHead({
  title,
  description,
  canonical,
  type = "website",
  image,
  imageAlt,
  article,
  noindex = false,
  jsonLd,
  amphtml,
}) {
  const fullTitle = title ? title + " | " + SITE_NAME : SITE_NAME;
  const metaDesc = description || "En güvenilir bonus siteleri, deneme bonusları ve spor bahis rehberleri.";
  const metaImage = ensureAbsoluteImage(image) || DEFAULT_IMAGE;
  const url = canonical || (typeof window !== "undefined" ? window.location.href : "");
  const imgAlt = imageAlt || fullTitle;

  useEffect(() => {
    // Title
    document.title = fullTitle;

    // Helper to set/create meta tags
    const setMeta = (attr, key, content) => {
      let el = document.querySelector(`meta[${attr}="${key}"]`);
      if (!el) {
        el = document.createElement("meta");
        el.setAttribute(attr, key);
        document.head.appendChild(el);
      }
      el.setAttribute("content", content);
      el.setAttribute("data-seo", "true");
    };

    // Helper for link tags
    const setLink = (rel, href) => {
      let el = document.querySelector(`link[rel="${rel}"]`);
      if (!el) {
        el = document.createElement("link");
        el.setAttribute("rel", rel);
        document.head.appendChild(el);
      }
      el.setAttribute("href", href);
      el.setAttribute("data-seo", "true");
    };

    // Core meta
    setMeta("name", "description", metaDesc);
    if (url) setLink("canonical", url);
    if (amphtml) setLink("amphtml", amphtml);
    if (noindex) setMeta("name", "robots", "noindex, nofollow");

    // Open Graph
    setMeta("property", "og:type", type);
    setMeta("property", "og:title", fullTitle);
    setMeta("property", "og:description", metaDesc);
    setMeta("property", "og:image", metaImage);
    setMeta("property", "og:image:width", "1200");
    setMeta("property", "og:image:height", "630");
    setMeta("property", "og:image:alt", imgAlt);
    setMeta("property", "og:url", url);
    setMeta("property", "og:site_name", SITE_NAME);
    setMeta("property", "og:locale", "tr_TR");

    // Twitter Card
    setMeta("name", "twitter:card", "summary_large_image");
    setMeta("name", "twitter:site", "@guncelgirisai");
    setMeta("name", "twitter:title", fullTitle);
    setMeta("name", "twitter:description", metaDesc);
    setMeta("name", "twitter:image", metaImage);
    setMeta("name", "twitter:image:alt", imgAlt);

    // Article specific
    if (article) {
      if (article.publishedTime) setMeta("property", "article:published_time", article.publishedTime);
      if (article.modifiedTime) setMeta("property", "article:modified_time", article.modifiedTime);
      if (article.author) setMeta("property", "article:author", article.author);
      if (article.category) setMeta("property", "article:section", article.category);
    }

    // JSON-LD Structured Data
    const scripts = [];
    const ldData = jsonLd ? (Array.isArray(jsonLd) ? jsonLd : [jsonLd]).filter(Boolean) : [];
    ldData.forEach((ld) => {
      const script = document.createElement("script");
      script.type = "application/ld+json";
      script.setAttribute("data-seo", "true");
      script.textContent = JSON.stringify(ld);
      document.head.appendChild(script);
      scripts.push(script);
    });

    return () => {
      scripts.forEach((s) => s.remove());
    };
  }, [fullTitle, metaDesc, metaImage, url, type, noindex, imgAlt, article, jsonLd, amphtml]);

  return null;
}
