import { Link } from "react-router-dom";
import { Calendar, ArrowRight, Tag } from "lucide-react";
import { Badge } from "@/components/ui/badge";

const NewsCard = ({ article, index = 0 }) => {
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString("tr-TR", {
      day: "numeric",
      month: "short",
      year: "numeric"
    });
  };

  // Determine card size based on index for bento grid effect
  const isLarge = index === 0;

  return (
    <Link 
      to={`/makale/${article.slug}`}
      className={`group block h-full`}
      data-testid={`news-card-${article.id}`}
    >
      <div className={`relative h-full rounded-xl overflow-hidden glass-card hover-lift ${isLarge ? "min-h-[400px]" : "min-h-[280px]"}`}>
        {/* Background Image */}
        {article.image_url && (
          <div className="absolute inset-0">
            <img 
              src={article.image_url} 
              alt={article.title}
              className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent" />
          </div>
        )}

        {/* Content */}
        <div className="relative h-full flex flex-col justify-end p-6">
          {/* Category Badge */}
          <Badge 
            className={`mb-3 w-fit ${
              article.category === "spor" 
                ? "bg-[#00F0FF]/20 text-[#00F0FF] border-[#00F0FF]/30" 
                : "bg-neon-green/20 text-neon-green border-neon-green/30"
            }`}
          >
            {article.category === "spor" ? "Spor" : "Bonus"}
          </Badge>

          {/* Title */}
          <h3 className={`font-heading font-bold uppercase tracking-tight mb-2 group-hover:text-neon-green transition-colors line-clamp-2 ${
            isLarge ? "text-2xl md:text-3xl" : "text-lg md:text-xl"
          }`}>
            {article.title}
          </h3>

          {/* Excerpt */}
          <p className="text-sm text-muted-foreground line-clamp-2 mb-4">
            {article.excerpt}
          </p>

          {/* Meta */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Calendar className="w-4 h-4" />
              <span>{formatDate(article.created_at)}</span>
            </div>
            <span className="flex items-center gap-1 text-xs text-neon-green font-medium opacity-0 group-hover:opacity-100 transition-opacity">
              Oku <ArrowRight className="w-4 h-4" />
            </span>
          </div>

          {/* Tags */}
          {article.tags.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-3">
              {article.tags.slice(0, 2).map((tag, i) => (
                <span key={i} className="text-xs text-muted-foreground flex items-center gap-1">
                  <Tag className="w-3 h-3" />
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Hover Border Effect */}
        <div className="absolute inset-0 border-2 border-transparent group-hover:border-neon-green/30 rounded-xl transition-colors duration-300 pointer-events-none" />
      </div>
    </Link>
  );
};

export default NewsCard;
