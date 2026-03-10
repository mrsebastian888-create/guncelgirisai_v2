import { Link } from "react-router-dom";
import { motion } from "framer-motion";
import {
  Globe, Shield, Lock, Clock, ChevronRight, ExternalLink,
  CheckCircle2, AlertTriangle, HelpCircle, Smartphone,
  ArrowRight, Eye, RefreshCw
} from "lucide-react";

const fadeIn = { initial: { opacity: 0, y: 16 }, animate: { opacity: 1, y: 0 } };
const ACCENT = "#00F0FF";

export default function CompanyGuideTemplate({ data }) {
  const { site, sections, faq, hub_links, cross_cluster_links, last_updated } = data;
  const name = site.name;

  return (
    <div className="space-y-6" data-testid="company-guide-template">
      {/* Section: Company Overview */}
      <motion.section {...fadeIn} className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="section-overview">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-[#00F0FF]/10">
            <Eye className="w-5 h-5 text-[#00F0FF]" />
          </div>
          <h2 className="font-heading text-lg font-bold uppercase">{sections.overview.title}</h2>
        </div>
        <p className="text-muted-foreground leading-relaxed">{sections.overview.content}</p>
        <div className="flex items-center gap-4 mt-4 text-xs text-muted-foreground">
          <span className="flex items-center gap-1.5"><Shield className="w-3.5 h-3.5 text-[#00F0FF]" /> Lisansli</span>
          <span className="flex items-center gap-1.5"><Clock className="w-3.5 h-3.5 text-[#00F0FF]" /> 7/24 Erisim</span>
          <span className="flex items-center gap-1.5"><Lock className="w-3.5 h-3.5 text-[#00F0FF]" /> SSL Guvenli</span>
        </div>
      </motion.section>

      {/* Section: Access Instructions */}
      <motion.section {...fadeIn} transition={{ delay: 0.05 }} className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="section-access-instructions">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-[#00F0FF]/10">
            <ArrowRight className="w-5 h-5 text-[#00F0FF]" />
          </div>
          <h2 className="font-heading text-lg font-bold uppercase">{sections.access_instructions.title}</h2>
        </div>
        <ol className="space-y-3">
          {sections.access_instructions.steps.map((step, i) => (
            <li key={i} className="flex items-start gap-3">
              <span className="flex-shrink-0 w-7 h-7 rounded-lg bg-[#00F0FF]/10 text-[#00F0FF] font-heading font-bold text-sm flex items-center justify-center">{i + 1}</span>
              <span className="text-sm text-muted-foreground pt-1">{step}</span>
            </li>
          ))}
        </ol>
      </motion.section>

      {/* Section: Address Change Explanation */}
      <motion.section {...fadeIn} transition={{ delay: 0.1 }} className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="section-address-change">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-[#00F0FF]/10">
            <RefreshCw className="w-5 h-5 text-[#00F0FF]" />
          </div>
          <h2 className="font-heading text-lg font-bold uppercase">{sections.address_change.title}</h2>
        </div>
        <p className="text-muted-foreground leading-relaxed">{sections.address_change.content}</p>
      </motion.section>

      {/* Section: Mobile Login */}
      <motion.section {...fadeIn} transition={{ delay: 0.15 }} className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="section-mobile-login">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-[#00F0FF]/10">
            <Smartphone className="w-5 h-5 text-[#00F0FF]" />
          </div>
          <h2 className="font-heading text-lg font-bold uppercase">{sections.mobile_login.title}</h2>
        </div>
        <p className="text-muted-foreground leading-relaxed">{sections.mobile_login.content}</p>
      </motion.section>

      {/* Section: Safety Notes */}
      <motion.section {...fadeIn} transition={{ delay: 0.2 }} className="rounded-2xl border border-yellow-500/20 bg-yellow-500/[0.03] p-6" data-testid="section-safety-notes">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-yellow-500/10">
            <Shield className="w-5 h-5 text-yellow-400" />
          </div>
          <h2 className="font-heading text-lg font-bold uppercase">{sections.safety_notes.title}</h2>
        </div>
        <ul className="space-y-2.5">
          {sections.safety_notes.items.map((item, i) => (
            <li key={i} className="flex items-start gap-2.5">
              <CheckCircle2 className="w-4 h-4 text-yellow-400 flex-shrink-0 mt-0.5" />
              <span className="text-sm text-muted-foreground">{item}</span>
            </li>
          ))}
        </ul>
      </motion.section>

      {/* Section: Cross-Cluster Links (access → bonus pages for same company) */}
      {cross_cluster_links?.length > 0 && (
        <motion.section {...fadeIn} transition={{ delay: 0.25 }} className="rounded-2xl border border-neon-green/20 bg-neon-green/[0.02] p-6" data-testid="section-cross-cluster">
          <h3 className="font-heading text-lg font-bold uppercase mb-4 flex items-center gap-2">
            <Globe className="w-5 h-5 text-neon-green" /> {name} Bonus Sayfalari
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {cross_cluster_links.map((link) => (
              <Link key={link.page_type} to={link.url} data-testid={`cross-link-${link.page_type}`}
                className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.03] border border-white/5 hover:border-neon-green/30 transition-all group">
                <div className="w-8 h-8 rounded-lg bg-neon-green/10 flex items-center justify-center flex-shrink-0">
                  <ChevronRight className="w-4 h-4 text-neon-green" />
                </div>
                <span className="text-sm font-medium group-hover:text-neon-green transition-colors">{link.label}</span>
              </Link>
            ))}
          </div>
        </motion.section>
      )}

      {/* Section: Hub Links */}
      {hub_links?.length > 0 && (
        <motion.section {...fadeIn} transition={{ delay: 0.3 }} className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="section-hub-links">
          <h3 className="font-heading text-lg font-bold uppercase mb-4 flex items-center gap-2">
            <Globe className="w-5 h-5 text-[#00F0FF]" /> Ilgili Rehberler
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {hub_links.map((link) => (
              <Link key={link.url} to={link.url} data-testid={`hub-link-${link.url.replace(/\//g, '')}`}
                className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.03] border border-white/5 hover:border-[#00F0FF]/30 transition-all group">
                <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0"
                  style={{ background: link.type === "bonus" ? "rgba(0,255,135,0.1)" : "rgba(0,240,255,0.1)" }}>
                  <ChevronRight className="w-4 h-4" style={{ color: link.type === "bonus" ? "#00FF87" : "#00F0FF" }} />
                </div>
                <span className="text-sm font-medium group-hover:text-[#00F0FF] transition-colors">{link.title}</span>
              </Link>
            ))}
          </div>
        </motion.section>
      )}

      {/* Section: FAQ */}
      {faq?.length > 0 && (
        <motion.section {...fadeIn} transition={{ delay: 0.35 }} className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="section-faq">
          <div className="flex items-center gap-3 mb-5">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-[#00F0FF]/10">
              <HelpCircle className="w-5 h-5 text-[#00F0FF]" />
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
        <motion.div {...fadeIn} transition={{ delay: 0.4 }}
          className="flex items-center gap-2 text-xs text-muted-foreground px-1" data-testid="section-last-updated">
          <Clock className="w-3.5 h-3.5" />
          <span>Son guncelleme: {new Date(last_updated).toLocaleDateString("tr-TR", { day: "numeric", month: "long", year: "numeric" })}</span>
        </motion.div>
      )}
    </div>
  );
}
