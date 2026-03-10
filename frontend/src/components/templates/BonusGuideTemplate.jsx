import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Gift, Star, Shield, ChevronRight, CheckCircle2,
  XCircle, HelpCircle, Clock, Users, Globe,
  TrendingUp, Award, CreditCard, ListChecks
} from "lucide-react";

const fadeIn = { initial: { opacity: 0, y: 16 }, animate: { opacity: 1, y: 0 } };
const ACCENT = "#00FF87";

export default function BonusGuideTemplate({ data }) {
  const { site, sections, faq, hub_links, cross_cluster_links, last_updated } = data;
  const name = site.name;

  return (
    <div className="space-y-6" data-testid="bonus-guide-template">
      {/* Section: Company Overview */}
      <motion.section {...fadeIn} className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="section-overview">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-neon-green/10">
            <Award className="w-5 h-5 text-neon-green" />
          </div>
          <h2 className="font-heading text-lg font-bold uppercase">{sections.overview.title}</h2>
        </div>
        <p className="text-muted-foreground leading-relaxed">{sections.overview.content}</p>
      </motion.section>

      {/* Section: Bonus Availability */}
      <motion.section {...fadeIn} transition={{ delay: 0.05 }} className="rounded-2xl border border-neon-green/20 bg-neon-green/[0.03] p-6" data-testid="section-bonus-availability">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-neon-green/10">
            <TrendingUp className="w-5 h-5 text-neon-green" />
          </div>
          <h2 className="font-heading text-lg font-bold uppercase">{sections.bonus_availability.title}</h2>
        </div>
        <p className="text-muted-foreground leading-relaxed mb-4">{sections.bonus_availability.content}</p>
        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-xl p-4 text-center bg-neon-green/5 border border-neon-green/15">
            <div className="text-xs text-muted-foreground mb-1">Bonus Miktari</div>
            <div className="font-heading text-2xl font-black text-neon-green">{sections.bonus_availability.amount}</div>
          </div>
          <div className="rounded-xl p-4 text-center bg-neon-green/5 border border-neon-green/15">
            <div className="text-xs text-muted-foreground mb-1">Durum</div>
            <div className="font-heading text-lg font-bold flex items-center justify-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-neon-green" />
              <span className="text-neon-green uppercase">{sections.bonus_availability.status}</span>
            </div>
          </div>
        </div>
      </motion.section>

      {/* Section: Bonus Types */}
      <motion.section {...fadeIn} transition={{ delay: 0.1 }} className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="section-bonus-types">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-neon-green/10">
            <Gift className="w-5 h-5 text-neon-green" />
          </div>
          <h2 className="font-heading text-lg font-bold uppercase">{sections.bonus_types.title}</h2>
        </div>
        <div className="space-y-3">
          {sections.bonus_types.items.map((item, i) => (
            <div key={i} className="flex items-start gap-3 p-3 rounded-xl bg-white/[0.03] border border-white/5" data-testid={`bonus-type-${i}`}>
              <div className="w-8 h-8 rounded-lg bg-neon-green/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                <Star className="w-4 h-4 text-neon-green" />
              </div>
              <div>
                <h3 className="font-heading text-sm font-bold text-white">{item.type}</h3>
                <p className="text-xs text-muted-foreground mt-1">{item.description}</p>
              </div>
            </div>
          ))}
        </div>
      </motion.section>

      {/* Section: Wagering Requirements */}
      <motion.section {...fadeIn} transition={{ delay: 0.15 }} className="rounded-2xl border border-amber-500/20 bg-amber-500/[0.03] p-6" data-testid="section-wagering">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-amber-500/10">
            <ListChecks className="w-5 h-5 text-amber-400" />
          </div>
          <h2 className="font-heading text-lg font-bold uppercase">{sections.wagering.title}</h2>
        </div>
        <p className="text-muted-foreground leading-relaxed mb-4">{sections.wagering.content}</p>
        <div className="rounded-xl bg-amber-500/5 border border-amber-500/15 p-4 mb-4 text-center">
          <div className="text-xs text-muted-foreground mb-1">Cevrim Carti</div>
          <div className="font-heading text-3xl font-black text-amber-400">{sections.wagering.multiplier}</div>
        </div>
        <ul className="space-y-2">
          {sections.wagering.details.map((detail, i) => (
            <li key={i} className="flex items-start gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
              <span className="text-sm text-muted-foreground">{detail}</span>
            </li>
          ))}
        </ul>
      </motion.section>

      {/* Section: Pros & Cons */}
      <motion.section {...fadeIn} transition={{ delay: 0.2 }} className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="section-pros-cons">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-neon-green/10">
            <Shield className="w-5 h-5 text-neon-green" />
          </div>
          <h2 className="font-heading text-lg font-bold uppercase">{sections.pros_cons.title}</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <h4 className="text-xs font-semibold uppercase tracking-widest text-neon-green mb-3">Avantajlar</h4>
            {sections.pros_cons.pros.map((pro, i) => (
              <div key={i} className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-neon-green flex-shrink-0 mt-0.5" />
                <span className="text-sm text-muted-foreground">{pro}</span>
              </div>
            ))}
          </div>
          <div className="space-y-2">
            <h4 className="text-xs font-semibold uppercase tracking-widest text-red-400 mb-3">Dezavantajlar</h4>
            {sections.pros_cons.cons.map((con, i) => (
              <div key={i} className="flex items-start gap-2">
                <XCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
                <span className="text-sm text-muted-foreground">{con}</span>
              </div>
            ))}
          </div>
        </div>
      </motion.section>

      {/* Section: Who it suits */}
      <motion.section {...fadeIn} transition={{ delay: 0.25 }} className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="section-who-suits">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-neon-green/10">
            <Users className="w-5 h-5 text-neon-green" />
          </div>
          <h2 className="font-heading text-lg font-bold uppercase">{sections.who_suits.title}</h2>
        </div>
        <p className="text-muted-foreground leading-relaxed">{sections.who_suits.content}</p>
      </motion.section>

      {/* Section: Cross-Cluster Links (bonus → access pages for same company) */}
      {cross_cluster_links?.length > 0 && (
        <motion.section {...fadeIn} transition={{ delay: 0.3 }} className="rounded-2xl border border-[#00F0FF]/20 bg-[#00F0FF]/[0.02] p-6" data-testid="section-cross-cluster">
          <h3 className="font-heading text-lg font-bold uppercase mb-4 flex items-center gap-2">
            <Globe className="w-5 h-5 text-[#00F0FF]" /> {name} Giris Sayfalari
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {cross_cluster_links.map((link) => (
              <Link key={link.page_type} to={link.url} data-testid={`cross-link-${link.page_type}`}
                className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.03] border border-white/5 hover:border-[#00F0FF]/30 transition-all group">
                <div className="w-8 h-8 rounded-lg bg-[#00F0FF]/10 flex items-center justify-center flex-shrink-0">
                  <ChevronRight className="w-4 h-4 text-[#00F0FF]" />
                </div>
                <span className="text-sm font-medium group-hover:text-[#00F0FF] transition-colors">{link.label}</span>
              </Link>
            ))}
          </div>
        </motion.section>
      )}

      {/* Section: Hub Links */}
      {hub_links?.length > 0 && (
        <motion.section {...fadeIn} transition={{ delay: 0.35 }} className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="section-hub-links">
          <h3 className="font-heading text-lg font-bold uppercase mb-4 flex items-center gap-2">
            <Gift className="w-5 h-5 text-neon-green" /> Ilgili Rehberler
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {hub_links.map((link) => (
              <Link key={link.url} to={link.url} data-testid={`hub-link-${link.url.replace(/\//g, '')}`}
                className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.03] border border-white/5 hover:border-neon-green/30 transition-all group">
                <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                  style={{ background: link.type === "payment" ? "rgba(0,240,255,0.1)" : "rgba(0,255,135,0.1)" }}>
                  {link.type === "payment" ? <CreditCard className="w-4 h-4 text-[#00F0FF]" /> : <Gift className="w-4 h-4 text-neon-green" />}
                </div>
                <span className="text-sm font-medium group-hover:text-neon-green transition-colors">{link.title}</span>
              </Link>
            ))}
          </div>
        </motion.section>
      )}

      {/* Section: FAQ */}
      {faq?.length > 0 && (
        <motion.section {...fadeIn} transition={{ delay: 0.4 }} className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="section-faq">
          <div className="flex items-center gap-3 mb-5">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-neon-green/10">
              <HelpCircle className="w-5 h-5 text-neon-green" />
            </div>
            <h2 className="font-heading text-lg font-bold uppercase">Sikca Sorulan Sorular</h2>
          </div>
          <div className="space-y-4">
            {faq.map((item, i) => (
              <div key={i} className="border-b border-white/5 pb-4 last:border-0 last:pb-0" data-testid={`faq-item-${i}`}>
                <h3 className="font-heading text-sm font-bold mb-2 text-white">{item.question}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{item.answer}</p>
              </div>
            ))}
          </div>
        </motion.section>
      )}

      {/* Section: Last Updated */}
      {last_updated && (
        <motion.div {...fadeIn} transition={{ delay: 0.45 }}
          className="flex items-center gap-2 text-xs text-muted-foreground px-1" data-testid="section-last-updated">
          <Clock className="w-3.5 h-3.5" />
          <span>Son guncelleme: {new Date(last_updated).toLocaleDateString("tr-TR", { day: "numeric", month: "long", year: "numeric" })}</span>
        </motion.div>
      )}
    </div>
  );
}
