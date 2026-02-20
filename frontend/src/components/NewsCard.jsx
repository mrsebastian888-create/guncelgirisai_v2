import { motion } from "framer-motion";
import { Calendar, ArrowRight, ExternalLink } from "lucide-react";

const NewsCard = ({ article, index = 0 }) => {
  const isLarge = index === 0;

  // Perigon format (image, url external, published_at, topics, description)
  // DB format (image_url, slug, created_at, tags, excerpt)
  const imgSrc = article.image || article.image_url;
  const isExternal = Boolean(article.url && !article.slug);
  const href = isExternal ? article.url : `/makale/${article.slug}`;
  const dateStr = article.published_at || article.created_at;
  const excerpt = article.description || article.excerpt || "";
  const tags = article.topics?.length ? article.topics : (article.tags || []);
  const source = article.source;

  const formattedDate = dateStr
    ? new Date(dateStr).toLocaleDateString("tr-TR", { day: "numeric", month: "short", year: "numeric" })
    : "";

  const CardWrapper = ({ children }) =>
    isExternal ? (
      <a href={href} target="_blank" rel="noopener noreferrer" className="group block h-full" data-testid={`news-card-${article.id}`}>
        {children}
      </a>
    ) : (
      <a href={href} className="group block h-full" data-testid={`news-card-${article.id}`}>
        {children}
      </a>
    );

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.04 }}
      className="h-full"
    >
      <CardWrapper>
        <div
          className={`relative h-full rounded-xl overflow-hidden transition-all duration-300 group-hover:scale-[1.02] ${isLarge ? "min-h-[380px]" : "min-h-[260px]"}`}
          style={{ background: "var(--card)", border: "1px solid rgba(255,255,255,0.06)" }}
        >
          {/* Image */}
          {imgSrc && (
            <div className="absolute inset-0">
              <img
                src={imgSrc}
                alt={article.title}
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                onError={(e) => { e.target.style.display = "none"; }}
              />
              <div className="absolute inset-0" style={{ background: "linear-gradient(to top, rgba(0,0,0,0.95) 0%, rgba(0,0,0,0.5) 55%, rgba(0,0,0,0.1) 100%)" }} />
            </div>
          )}

          {/* Content */}
          <div className="relative h-full flex flex-col justify-end p-5">
            {/* Tags */}
            {tags.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mb-2">
                {tags.slice(0, 2).map((tag, i) => (
                  <span key={i} className="text-xs px-2 py-0.5 rounded-full font-medium"
                    style={{ background: "rgba(0,240,255,0.15)", color: "#00F0FF" }}>
                    {tag}
                  </span>
                ))}
              </div>
            )}

            {/* Title */}
            <h3
              className={`font-heading font-bold uppercase tracking-tight mb-2 line-clamp-2 transition-colors group-hover:text-neon-green ${isLarge ? "text-xl md:text-2xl" : "text-base md:text-lg"}`}
              style={{ color: "var(--foreground)" }}
            >
              {article.title}
            </h3>

            {/* Excerpt */}
            {excerpt && (
              <p className="text-sm line-clamp-2 mb-3" style={{ color: "rgba(156,163,175,0.8)" }}>
                {excerpt}
              </p>
            )}

            {/* Meta */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3 text-xs" style={{ color: "rgba(156,163,175,0.7)" }}>
                {formattedDate && (
                  <span className="flex items-center gap-1">
                    <Calendar className="w-3 h-3" />
                    {formattedDate}
                  </span>
                )}
                {source && <span className="truncate max-w-[100px]">{source}</span>}
              </div>
              <span className="flex items-center gap-1 text-xs font-semibold opacity-0 group-hover:opacity-100 transition-opacity"
                style={{ color: "var(--neon-green)" }}>
                {isExternal ? <><ExternalLink className="w-3 h-3" /> Oku</> : <><ArrowRight className="w-3 h-3" /> Oku</>}
              </span>
            </div>
          </div>

          {/* Hover border */}
          <div className="absolute inset-0 rounded-xl border-2 border-transparent group-hover:border-neon-green/20 transition-colors duration-300 pointer-events-none" />
        </div>
      </CardWrapper>
    </motion.div>
  );
};

export default NewsCard;
