import { Link } from "react-router-dom";
import { Star, ExternalLink, Shield } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

const BonusCard = ({ site, index = 0 }) => {
  return (
    <div 
      className="glass-card rounded-xl overflow-hidden group hover-lift"
      data-testid={`bonus-card-${site.id}`}
    >
      {/* Featured Badge */}
      {site.is_featured && (
        <div className="absolute top-3 right-3 z-10">
          <Badge className="bg-yellow-500/20 text-yellow-500 border-yellow-500/30">
            <Star className="w-3 h-3 mr-1 fill-yellow-500" /> Öne Çıkan
          </Badge>
        </div>
      )}

      <div className="p-6">
        {/* Header */}
        <div className="flex items-start gap-4 mb-4">
          <div className="w-16 h-16 rounded-xl bg-card overflow-hidden shrink-0 border border-white/10">
            <img 
              src={site.logo_url} 
              alt={site.name}
              className="w-full h-full object-cover"
            />
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="font-heading text-xl font-bold truncate">{site.name}</h3>
            <div className="flex items-center gap-1 mt-1">
              {[...Array(5)].map((_, i) => (
                <Star 
                  key={i} 
                  className={`w-4 h-4 ${i < Math.floor(site.rating) ? "text-yellow-500 fill-yellow-500" : "text-muted-foreground"}`}
                />
              ))}
              <span className="text-sm text-muted-foreground ml-1">({site.rating})</span>
            </div>
          </div>
        </div>

        {/* Bonus Amount */}
        <div className="mb-4 p-4 bg-background/50 rounded-lg text-center border border-neon-green/20">
          <div className="text-sm text-muted-foreground uppercase mb-1">{site.bonus_type} Bonusu</div>
          <div className="font-heading text-3xl font-black text-neon-green neon-glow-text">
            {site.bonus_amount}
          </div>
        </div>

        {/* Features */}
        <div className="flex flex-wrap gap-2 mb-4">
          {site.features.slice(0, 3).map((feature, i) => (
            <Badge key={i} variant="outline" className="text-xs">
              <Shield className="w-3 h-3 mr-1" />
              {feature}
            </Badge>
          ))}
        </div>

        {/* CTA */}
        <Button 
          className="w-full bg-neon-green text-black font-bold uppercase tracking-wide hover:bg-neon-green/90 neon-glow press"
          asChild
        >
          <a href={site.affiliate_url} target="_blank" rel="noopener noreferrer" data-testid={`bonus-cta-${site.id}`}>
            <ExternalLink className="w-4 h-4 mr-2" />
            Siteye Git
          </a>
        </Button>
      </div>
    </div>
  );
};

export default BonusCard;
