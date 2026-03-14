import { useState, useEffect } from "react";
import { useParams, Link } from "react-router-dom";
import { motion } from "framer-motion";
import axios from "axios";
import {
  ExternalLink, Shield, Gift, ChevronRight, Star, Globe,
  CreditCard, Smartphone, CheckCircle2, AlertTriangle, Clock,
  HeadphonesIcon, Award, Lock, ArrowRight, ThumbsUp, ThumbsDown,
  User, RefreshCw, FileText, ChevronDown, Zap
} from "lucide-react";
import {
  Accordion, AccordionContent, AccordionItem, AccordionTrigger,
} from "@/components/ui/accordion";
import SEOHead from "@/components/SEOHead";
import { API } from "@/App";

const CLUSTER_COLORS = {
  "company-guide": "#00F0FF",
  "bonus-guide": "#00FF87",
};

const PAGE_TYPE_ICONS = {
  "guncel-giris": Globe, "guncel-adresi": Globe, "yeni-giris-adresi": ArrowRight,
  "mobil-giris": Smartphone, "deneme-bonusu": Gift, "deneme-bonusu-2026": Gift,
  "hosgeldin-bonusu": Award, "yatirimsiz-deneme-bonusu": Gift,
  "bonus-sartlari": CheckCircle2, "odeme-yontemleri": CreditCard,
};

/* ──────────────────────────────────────────────
   COMPANY GUIDE TEMPLATE SECTIONS
   ────────────────────────────────────────────── */
function CompanyOverview({ site, accentColor }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="section-company-overview">
      <h2 className="font-heading text-lg font-bold uppercase mb-4 flex items-center gap-2">
        <FileText className="w-5 h-5" style={{ color: accentColor }} /> {site.name} Hakkinda
      </h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <div className="rounded-xl bg-white/[0.03] border border-white/5 p-3 text-center">
          <div className="text-xs text-muted-foreground">Kategori</div>
          <div className="font-heading font-bold text-sm mt-1">{site.category || "Turkiye"}</div>
        </div>
        <div className="rounded-xl bg-white/[0.03] border border-white/5 p-3 text-center">
          <div className="text-xs text-muted-foreground">Puan</div>
          <div className="font-heading font-bold text-sm mt-1 flex items-center justify-center gap-1">
            <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />{site.rating || 4.5}
          </div>
        </div>
        <div className="rounded-xl bg-white/[0.03] border border-white/5 p-3 text-center">
          <div className="text-xs text-muted-foreground">Bonus</div>
          <div className="font-heading font-bold text-sm mt-1" style={{ color: accentColor }}>{site.bonus_amount}</div>
        </div>
        <div className="rounded-xl bg-white/[0.03] border border-white/5 p-3 text-center">
          <div className="text-xs text-muted-foreground">Lisans</div>
          <div className="font-heading font-bold text-sm mt-1">Curacao</div>
        </div>
      </div>
      <p className="text-sm text-muted-foreground leading-relaxed">
        {site.name}, Turkiye'deki kullanicilara hitap eden lisansli bir platformdur. {site.bonus_amount} degerinde bonus firsatlari, hizli odeme yontemleri ve 7/24 canli destek hizmeti sunmaktadir.
      </p>
    </div>
  );
}

function AccessInstructions({ site, pageType, accentColor }) {
  const instructions = {
    "guncel-giris": [
      "Bu sayfadaki guncel linke tiklayin",
      "Acilan sayfada kullanici adi ve sifrenizi girin",
      "Hesabiniza basariyla giris yapin",
      "Sorun yasarsaniz 7/24 canli destek ile iletisime gecin",
    ],
    "guncel-adresi": [
      "Asagidaki guncel adres linkini kullanin",
      "Adresi tarayicinizin yer imllerine ekleyin",
      "Domain degisikliklerinde bu sayfayi kontrol edin",
      "VPN kullanarak alternatif erisim saglayabilirsiniz",
    ],
    "yeni-giris-adresi": [
      "Yeni giris adresine asagidaki linkten ulasin",
      "Eski hesap bilgilerinizle giris yapin (bilgiler korunur)",
      "Yeni adresi kaydedin, eski adres kapanabilir",
      "Alternatif olarak mobil uygulama kullanabilirsiniz",
    ],
    "mobil-giris": [
      "Telefonunuzun tarayicisinda guncel adresi acin",
      "Mobil uyumlu arayuz otomatik olarak yuklenecektir",
      "Ana ekrana kisayol ekleyerek hizli erisim saglayin",
      "Mobil uygulama mevcutsa indirip kullanabilirsiniz",
    ],
  };
  const steps = instructions[pageType] || instructions["guncel-giris"];
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="section-access-instructions">
      <h2 className="font-heading text-lg font-bold uppercase mb-4 flex items-center gap-2">
        <ArrowRight className="w-5 h-5" style={{ color: accentColor }} /> Erisim Adimlari
      </h2>
      <div className="space-y-3">
        {steps.map((step, i) => (
          <div key={i} className="flex items-start gap-3">
            <div className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0 font-heading font-bold text-xs"
              style={{ background: `${accentColor}15`, color: accentColor }}>{i + 1}</div>
            <p className="text-sm text-muted-foreground pt-1">{step}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function AddressChangeExplanation({ site, accentColor }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="section-address-change">
      <h2 className="font-heading text-lg font-bold uppercase mb-4 flex items-center gap-2">
        <RefreshCw className="w-5 h-5" style={{ color: accentColor }} /> Adres Degisikligi Neden Olur?
      </h2>
      <div className="space-y-3 text-sm text-muted-foreground leading-relaxed">
        <p>BTK (Bilgi Teknolojileri ve Iletisim Kurumu) kararlari nedeniyle bazi bahis sitelerinin domain adresleri engellenebilir. Bu durumda {site.name} yonetimi yeni bir domain adresi uzerinden hizmet vermeye devam eder.</p>
        <p>Adres degisiklikleri sirasinda mevcut hesap bilgileriniz, bakiyeniz ve bonus durumunuz korunur. Yeni adrese giris yaptiginizda tum verilerinize erisebilirsiniz.</p>
        <p>Bu sayfayi yer imlerinize ekleyerek {site.name} adres degisikliklerinden aninda haberdar olabilirsiniz.</p>
      </div>
    </div>
  );
}

function MobileLoginInfo({ site, accentColor }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="section-mobile-info">
      <h2 className="font-heading text-lg font-bold uppercase mb-4 flex items-center gap-2">
        <Smartphone className="w-5 h-5" style={{ color: accentColor }} /> Mobil Erisim Bilgileri
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {[
          { label: "iOS Uyumluluk", value: "Safari, Chrome", icon: Smartphone },
          { label: "Android Uyumluluk", value: "Chrome, Firefox", icon: Smartphone },
          { label: "Mobil Uygulama", value: "Mevcut", icon: CheckCircle2 },
          { label: "Mobil Odeme", value: "Destekleniyor", icon: CreditCard },
        ].map((item, i) => (
          <div key={i} className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.03] border border-white/5">
            <item.icon className="w-4 h-4 flex-shrink-0" style={{ color: accentColor }} />
            <div>
              <div className="text-xs text-muted-foreground">{item.label}</div>
              <div className="text-sm font-medium">{item.value}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function SecurityNotes({ site, accentColor }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="section-security-notes">
      <h2 className="font-heading text-lg font-bold uppercase mb-4 flex items-center gap-2">
        <Shield className="w-5 h-5" style={{ color: accentColor }} /> Guvenlik Bilgileri
      </h2>
      <div className="space-y-2">
        {[
          "256-bit SSL sifreleme ile korunan baglanti",
          "Curacao eGaming lisansi altinda denetlenmis platform",
          "Iki faktorlu kimlik dogrulama (2FA) destegi",
          "Kisisel ve finansal veriler GDPR uyumlu sekilde saklanir",
          "7/24 canli destek ile anlik yardim imkani",
        ].map((note, i) => (
          <div key={i} className="flex items-start gap-2.5 p-2">
            <CheckCircle2 className="w-4 h-4 flex-shrink-0 mt-0.5" style={{ color: accentColor }} />
            <span className="text-sm text-muted-foreground">{note}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ──────────────────────────────────────────────
   BONUS GUIDE TEMPLATE SECTIONS
   ────────────────────────────────────────────── */
function CompanySummary({ site, accentColor }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="section-company-summary">
      <h2 className="font-heading text-lg font-bold uppercase mb-4 flex items-center gap-2">
        <FileText className="w-5 h-5" style={{ color: accentColor }} /> {site.name} Ozet
      </h2>
      <p className="text-sm text-muted-foreground leading-relaxed mb-4">
        {site.name}, lisansli bir bahis platformu olarak {site.bonus_amount} degerinde bonus firsatlari sunmaktadir. {site.rating || 4.5}/5 puan ile kullanicilari tarafindan yuksek derecede degerlendirilen platform, guvenilir odeme yontemleri ve 7/24 musteri destegi saglamaktadir.
      </p>
      <div className="grid grid-cols-3 gap-3">
        <div className="rounded-xl p-3 text-center" style={{ background: `${accentColor}08`, border: `1px solid ${accentColor}20` }}>
          <div className="text-xs text-muted-foreground mb-1">Bonus</div>
          <div className="font-heading text-lg font-bold" style={{ color: accentColor }}>{site.bonus_amount}</div>
        </div>
        <div className="rounded-xl bg-yellow-500/5 border border-yellow-500/20 p-3 text-center">
          <div className="text-xs text-muted-foreground mb-1">Puan</div>
          <div className="font-heading text-lg font-bold text-yellow-400 flex items-center justify-center gap-1">
            <Star className="w-3.5 h-3.5 fill-yellow-400" />{site.rating || 4.5}
          </div>
        </div>
        <div className="rounded-xl bg-blue-500/5 border border-blue-500/20 p-3 text-center">
          <div className="text-xs text-muted-foreground mb-1">Cevrim</div>
          <div className="font-heading text-lg font-bold text-blue-400">{site.turnover_requirement || 10}x</div>
        </div>
      </div>
    </div>
  );
}

function BonusAvailability({ site, pageType, accentColor }) {
  const bonusTypes = {
    "deneme-bonusu": { type: "Deneme Bonusu", available: true, amount: site.bonus_amount, desc: "Yeni uyelere ozel, yatirim gerektirmeyen bonus" },
    "deneme-bonusu-2026": { type: "2026 Deneme Bonusu", available: true, amount: site.bonus_amount, desc: "2026 yili guncel deneme bonusu" },
    "hosgeldin-bonusu": { type: "Hosgeldin Bonusu", available: true, amount: site.bonus_amount, desc: "Ilk yatiriminiza ozel bonus" },
    "yatirimsiz-deneme-bonusu": { type: "Yatirimsiz Bonus", available: true, amount: site.bonus_amount, desc: "Para yatirmadan alinan bonus" },
    "bonus-sartlari": { type: "Tum Bonuslar", available: true, amount: site.bonus_amount, desc: "Mevcut tum bonus firsatlari" },
  };
  const info = bonusTypes[pageType] || bonusTypes["deneme-bonusu"];
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="section-bonus-availability">
      <h2 className="font-heading text-lg font-bold uppercase mb-4 flex items-center gap-2">
        <Gift className="w-5 h-5" style={{ color: accentColor }} /> Bonus Durumu
      </h2>
      <div className="flex items-center gap-3 p-4 rounded-xl" style={{ background: `${accentColor}08`, border: `1px solid ${accentColor}20` }}>
        <div className="w-3 h-3 rounded-full" style={{ background: info.available ? "#00FF87" : "#FF4444" }} />
        <div className="flex-1">
          <div className="text-sm font-bold">{info.type}: <span style={{ color: accentColor }}>{info.available ? "Aktif" : "Pasif"}</span></div>
          <div className="text-xs text-muted-foreground">{info.desc}</div>
        </div>
        <div className="font-heading font-black text-xl" style={{ color: accentColor }}>{info.amount}</div>
      </div>
    </div>
  );
}

function BonusTypesSection({ site, accentColor }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="section-bonus-types">
      <h2 className="font-heading text-lg font-bold uppercase mb-4 flex items-center gap-2">
        <Zap className="w-5 h-5" style={{ color: accentColor }} /> Mevcut Bonus Turleri
      </h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {[
          { name: "Deneme Bonusu", desc: "Yatirim gerektirmeyen ucretsiz bonus", icon: Gift, color: "#00FF87" },
          { name: "Hosgeldin Bonusu", desc: "Ilk yatiriminiza %100 ek bonus", icon: Award, color: "#FFD700" },
          { name: "Kayip Bonusu", desc: "Kayiplarinizin bir kisminin iadesi", icon: RefreshCw, color: "#00F0FF" },
          { name: "Yatirim Bonusu", desc: "Her yatirimda ekstra bonus", icon: CreditCard, color: "#FF6B6B" },
        ].map((bt, i) => (
          <div key={i} className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.03] border border-white/5">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: `${bt.color}15` }}>
              <bt.icon className="w-4 h-4" style={{ color: bt.color }} />
            </div>
            <div>
              <div className="text-sm font-bold">{bt.name}</div>
              <div className="text-xs text-muted-foreground">{bt.desc}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function WageringExplanation({ site, accentColor }) {
  const turnover = site.turnover_requirement || 10;
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="section-wagering">
      <h2 className="font-heading text-lg font-bold uppercase mb-4 flex items-center gap-2">
        <RefreshCw className="w-5 h-5" style={{ color: accentColor }} /> Cevrim Sartlari
      </h2>
      <div className="space-y-3 text-sm text-muted-foreground leading-relaxed">
        <p><strong className="text-foreground">Cevrim Kati:</strong> {turnover}x — Bonus miktarinin {turnover} kati kadar bahis yapmaniz gerekmektedir.</p>
        <p><strong className="text-foreground">Ornek:</strong> {site.bonus_amount} bonus aldiyseniz, {turnover} x bonus degeri kadar toplam bahis yapmaniz gerekir.</p>
        <p><strong className="text-foreground">Gecerli Oyunlar:</strong> Spor bahisleri (minimum 1.50 oran), canli bahis, slot oyunlari genellikle cevrime dahildir.</p>
        <p><strong className="text-foreground">Sure Siniri:</strong> Cevrim genellikle 7-30 gun icerisinde tamamlanmalidir.</p>
      </div>
    </div>
  );
}

function AdvantagesDisadvantages({ site, accentColor }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="section-pros-cons">
      <h2 className="font-heading text-lg font-bold uppercase mb-4">Avantajlar ve Dezavantajlar</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <h3 className="text-sm font-bold mb-2 flex items-center gap-2 text-neon-green"><ThumbsUp className="w-4 h-4" /> Avantajlar</h3>
          <div className="space-y-1.5">
            {[
              `${site.bonus_amount} degerinde bonus`,
              "7/24 canli destek",
              "Hizli odeme islemleri",
              "Mobil uyumlu arayuz",
              "Guvenilir lisans",
            ].map((a, i) => (
              <div key={i} className="flex items-center gap-2 text-xs text-muted-foreground">
                <CheckCircle2 className="w-3.5 h-3.5 text-neon-green flex-shrink-0" /> {a}
              </div>
            ))}
          </div>
        </div>
        <div>
          <h3 className="text-sm font-bold mb-2 flex items-center gap-2 text-red-400"><ThumbsDown className="w-4 h-4" /> Dezavantajlar</h3>
          <div className="space-y-1.5">
            {[
              `${site.turnover_requirement || 10}x cevrim sarti`,
              "Adres degisiklikleri olabilir",
              "Bazi odeme yontemlerinde limit",
            ].map((d, i) => (
              <div key={i} className="flex items-center gap-2 text-xs text-muted-foreground">
                <AlertTriangle className="w-3.5 h-3.5 text-red-400 flex-shrink-0" /> {d}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function RecommendedProfile({ accentColor }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="section-recommended-profile">
      <h2 className="font-heading text-lg font-bold uppercase mb-4 flex items-center gap-2">
        <User className="w-5 h-5" style={{ color: accentColor }} /> Kimler Icin Uygun?
      </h2>
      <div className="space-y-2">
        {[
          "Bahis dunyasini risksiz denemek isteyen yeni kullanicilar",
          "Yatirim yapmadan once platform kalitesini test etmek isteyenler",
          "Farkli sitelerin bonuslarini karsilastirmak isteyen deneyimli oyuncular",
          "Mobil cihazlardan bahis yapmak isteyen kullanicilar",
        ].map((p, i) => (
          <div key={i} className="flex items-center gap-2.5 p-2 text-sm text-muted-foreground">
            <User className="w-4 h-4 flex-shrink-0" style={{ color: accentColor }} /> {p}
          </div>
        ))}
      </div>
    </div>
  );
}

/* ──────────────────────────────────────────────
   SHARED SECTIONS
   ────────────────────────────────────────────── */
function FAQSection({ faq, accentColor, siteName }) {
  if (!faq?.length) return null;
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="section-faq">
      <h2 className="font-heading text-lg font-bold uppercase mb-4">Sikca Sorulan Sorular</h2>
      <Accordion type="single" collapsible className="space-y-2">
        {faq.map((item, i) => (
          <AccordionItem
            key={i}
            value={`faq-${i}`}
            className="rounded-xl border px-4 overflow-hidden"
            style={{ background: "rgba(255,255,255,0.02)", borderColor: "rgba(255,255,255,0.06)" }}
            data-testid={`faq-item-${i}`}
          >
            <AccordionTrigger className="font-medium text-sm py-4 hover:no-underline text-left">
              {item.question}
            </AccordionTrigger>
            <AccordionContent className="pb-4 text-sm text-muted-foreground leading-relaxed">
              {item.answer}
            </AccordionContent>
          </AccordionItem>
        ))}
      </Accordion>
    </div>
  );
}

function RelatedPagesBlock({ internal_links, site, accentColor }) {
  const guideLinks = internal_links?.company_guide || [];
  const bonusLinks = internal_links?.bonus_guide || [];
  if (!guideLinks.length && !bonusLinks.length) return null;
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-6" data-testid="section-related-pages">
      <h2 className="font-heading text-lg font-bold uppercase mb-4">Ilgili Sayfalar</h2>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {guideLinks.map((link) => (
          <Link key={link.page_type} to={link.url} data-testid={`related-guide-${link.page_type}`}
            className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.03] border border-white/5 hover:border-[#00F0FF]/30 transition-all group">
            <Globe className="w-4 h-4 text-[#00F0FF] flex-shrink-0" />
            <span className="text-sm group-hover:text-[#00F0FF] transition-colors">{link.label}</span>
            <ChevronRight className="w-3 h-3 text-muted-foreground ml-auto" />
          </Link>
        ))}
        {bonusLinks.map((link) => (
          <Link key={link.page_type} to={link.url} data-testid={`related-bonus-${link.page_type}`}
            className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.03] border border-white/5 hover:border-neon-green/30 transition-all group">
            <Gift className="w-4 h-4 text-neon-green flex-shrink-0" />
            <span className="text-sm group-hover:text-neon-green transition-colors">{link.label}</span>
            <ChevronRight className="w-3 h-3 text-muted-foreground ml-auto" />
          </Link>
        ))}
      </div>
    </div>
  );
}

function RelatedCompaniesBlock({ related_companies, pageType, accentColor }) {
  if (!related_companies?.length) return null;
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-5" data-testid="section-related-companies">
      <h3 className="font-heading text-base font-bold uppercase mb-3">Benzer Siteler</h3>
      <div className="space-y-2">
        {related_companies.map((c) => (
          <div key={c.name} className="rounded-xl bg-white/[0.02] border border-white/5 p-3">
            <Link to={c.same_page} className="flex items-center gap-3 group">
              <img src={c.logo_url} alt={c.name} className="w-8 h-8 rounded-lg" />
              <div className="flex-1 min-w-0">
                <div className="text-sm font-medium truncate group-hover:text-neon-green transition-colors">{c.name}</div>
                <div className="text-xs" style={{ color: accentColor }}>{c.bonus_amount}</div>
              </div>
              <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
              <span className="text-xs text-yellow-400">{c.rating}</span>
            </Link>
            <div className="flex flex-wrap gap-1.5 mt-2 pt-2 border-t border-white/5">
              <Link to={c.guncel_giris} className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-[#00F0FF] hover:bg-[#00F0FF]/10">Giris</Link>
              <Link to={c.deneme_bonusu} className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-neon-green hover:bg-neon-green/10">Bonus</Link>
              <Link to={c.odeme_yontemleri} className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-muted-foreground hover:bg-white/10">Odeme</Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function LastUpdatedBlock({ lastUpdated }) {
  const formatted = lastUpdated ? new Date(lastUpdated).toLocaleDateString("tr-TR", { day: "numeric", month: "long", year: "numeric" }) : "";
  if (!formatted) return null;
  return (
    <div className="flex items-center gap-2 text-xs text-muted-foreground mt-2" data-testid="last-updated">
      <Clock className="w-3.5 h-3.5" /> Son guncelleme: {formatted}
    </div>
  );
}

/* ──────────────────────────────────────────────
   MAIN PAGE COMPONENT
   ────────────────────────────────────────────── */
export default function CompanySubPage() {
  const { companySlug, pageType } = useParams();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await axios.get(`${API}/firma-sub/${companySlug}/${pageType}`);
        setData(res.data);
      } catch (e) {
        setError(e.response?.status === 404 ? "Sayfa bulunamadi" : "Bir hata olustu");
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [companySlug, pageType]);

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center pt-20" data-testid="company-sub-loading">
      <div className="w-10 h-10 border-2 border-neon-green border-t-transparent rounded-full animate-spin" />
    </div>
  );

  if (error || !data) return (
    <div className="min-h-screen flex flex-col items-center justify-center pt-20 gap-4" data-testid="company-sub-error">
      <AlertTriangle className="w-16 h-16 text-yellow-500" />
      <h1 className="font-heading text-2xl">{error || "Sayfa bulunamadi"}</h1>
      <Link to="/" className="text-neon-green hover:underline">Ana Sayfaya Don</Link>
    </div>
  );

  const { site, seo, breadcrumb, internal_links, similar_same_page, cluster, faq, last_updated, hub_links, related_companies } = data;
  const accentColor = CLUSTER_COLORS[cluster] || "#00FF87";
  const PageIcon = PAGE_TYPE_ICONS[pageType] || Globe;
  const baseSlug = companySlug;
  const isCompanyGuide = cluster === "company-guide";

  // JSON-LD schemas
  const breadcrumbJsonLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": breadcrumb.map((b, i) => ({
      "@type": "ListItem", "position": i + 1, "name": b.name,
      "item": `https://guncelgiris.ai${b.url}`
    }))
  };

  const faqJsonLd = faq?.length ? {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": faq.map((item) => ({
      "@type": "Question", "name": item.question,
      "acceptedAnswer": { "@type": "Answer", "text": item.answer }
    }))
  } : null;

  const articleJsonLd = {
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": seo.title,
    "description": seo.description,
    "dateModified": last_updated,
    "datePublished": last_updated,
    "author": { "@type": "Organization", "name": "guncelgiris.ai" },
    "publisher": {
      "@type": "Organization", "name": "guncelgiris.ai",
      "logo": { "@type": "ImageObject", "url": "https://guncelgiris.ai/logo.png" }
    },
    "mainEntityOfPage": { "@type": "WebPage", "@id": seo.canonical }
  };

  return (
    <div className="min-h-screen bg-background pt-20 pb-16" data-testid="company-sub-page">
      <SEOHead
        title={seo.title}
        description={seo.description}
        canonical={seo.canonical}
        jsonLd={[breadcrumbJsonLd, faqJsonLd, articleJsonLd].filter(Boolean)}
      />

      {/* Breadcrumb */}
      <div className="container mx-auto max-w-6xl px-4 mb-6" data-testid="company-sub-breadcrumb">
        <div className="flex items-center gap-2 text-xs text-muted-foreground flex-wrap">
          {breadcrumb.map((b, i) => (
            <span key={i} className="flex items-center gap-2">
              {i > 0 && <ChevronRight className="w-3 h-3" />}
              {i < breadcrumb.length - 1 ? (
                <Link to={b.url} className="hover:text-neon-green transition-colors">{b.name}</Link>
              ) : (
                <span style={{ color: accentColor }}>{b.name}</span>
              )}
            </span>
          ))}
        </div>
      </div>

      {/* Hero */}
      <section className="relative overflow-hidden py-12 md:py-16" data-testid="company-sub-hero">
        <div className="absolute inset-0 bg-[#050505]" />
        <div className="absolute inset-0 opacity-[0.04]" style={{
          backgroundImage: `linear-gradient(${accentColor}4D 1px, transparent 1px), linear-gradient(90deg, ${accentColor}4D 1px, transparent 1px)`,
          backgroundSize: "60px 60px"
        }} />
        <div className="relative z-10 container mx-auto max-w-6xl px-4">
          <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
            <div className="flex items-center gap-4">
              <img src={site.logo_url} alt={site.name} className="w-16 h-16 rounded-xl border-2" style={{ borderColor: `${accentColor}50` }} />
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs uppercase tracking-widest font-semibold px-2 py-0.5 rounded-full border"
                    style={{ borderColor: `${accentColor}40`, color: accentColor, background: `${accentColor}10` }}>
                    {isCompanyGuide ? "Firma Rehberi" : "Bonus Rehberi"}
                  </span>
                  <LastUpdatedBlock lastUpdated={last_updated} />
                </div>
                <h1 className="font-heading font-black text-2xl md:text-4xl uppercase tracking-tight" data-testid="company-sub-h1">
                  <span className="text-white">{site.name}</span>{" "}
                  <span style={{ color: accentColor }}>{seo.h1.replace(site.name, "").trim()}</span>
                </h1>
              </div>
            </div>
            <div className="md:ml-auto flex gap-3">
              <a href={site.affiliate_url} target="_blank" rel="noopener noreferrer" data-testid="company-sub-cta"
                className="inline-flex items-center gap-2 rounded-xl px-6 py-3 font-heading font-bold uppercase text-sm transition-all hover:scale-105"
                style={{ background: accentColor, color: "#000", boxShadow: `0 0 24px ${accentColor}40` }}>
                <ExternalLink className="w-4 h-4" /> Siteye Git
              </a>
              <Link to={`/${site.slug || `${baseSlug}-guncelgiris`}`} data-testid="company-sub-profile-link"
                className="inline-flex items-center gap-2 rounded-xl px-6 py-3 font-heading font-bold uppercase text-sm border transition-all hover:bg-white/5"
                style={{ borderColor: "rgba(255,255,255,0.15)" }}>
                Firma Profili
              </Link>
            </div>
          </div>
        </div>
      </section>

      <div className="container mx-auto max-w-6xl px-4 mt-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* COMPANY GUIDE TEMPLATE */}
            {isCompanyGuide && (
              <>
                <CompanyOverview site={site} accentColor={accentColor} />
                <AccessInstructions site={site} pageType={pageType} accentColor={accentColor} />
                <AddressChangeExplanation site={site} accentColor={accentColor} />
                {pageType === "mobil-giris" && <MobileLoginInfo site={site} accentColor={accentColor} />}
                <SecurityNotes site={site} accentColor={accentColor} />
              </>
            )}

            {/* BONUS GUIDE TEMPLATE */}
            {!isCompanyGuide && (
              <>
                <CompanySummary site={site} accentColor={accentColor} />
                <BonusAvailability site={site} pageType={pageType} accentColor={accentColor} />
                <BonusTypesSection site={site} accentColor={accentColor} />
                <WageringExplanation site={site} accentColor={accentColor} />
                <AdvantagesDisadvantages site={site} accentColor={accentColor} />
                <RecommendedProfile accentColor={accentColor} />
              </>
            )}

            {/* FAQ (shared) */}
            <FAQSection faq={faq} accentColor={accentColor} siteName={site.name} />

            {/* Related Pages (shared - internal linking engine) */}
            <RelatedPagesBlock internal_links={internal_links} site={site} accentColor={accentColor} />
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* CTA Card */}
            <div className="rounded-2xl border p-6 text-center sticky top-24" style={{ borderColor: `${accentColor}30`, background: `${accentColor}05` }} data-testid="company-sub-sidebar-cta">
              <img src={site.logo_url} alt={site.name} className="w-16 h-16 rounded-xl mx-auto mb-3" />
              <h3 className="font-heading text-lg font-bold uppercase">{site.name}</h3>
              <div className="font-heading text-3xl font-black mt-2" style={{ color: accentColor }}>{site.bonus_amount}</div>
              <a href={site.affiliate_url} target="_blank" rel="noopener noreferrer" data-testid="company-sub-sidebar-cta-btn"
                className="flex items-center justify-center gap-2 mt-4 w-full px-6 py-3.5 rounded-xl font-heading font-bold uppercase tracking-wide text-sm transition-all hover:scale-105"
                style={{ background: accentColor, color: "#000", boxShadow: `0 0 24px ${accentColor}40` }}>
                <ExternalLink className="w-4 h-4" /> Siteye Git
              </a>
              <p className="text-[11px] text-muted-foreground mt-3">18+ | Sorumlu oyun oynayiniz</p>
            </div>

            {/* Related Companies */}
            <RelatedCompaniesBlock related_companies={related_companies} pageType={pageType} accentColor={accentColor} />

            {/* Hub Links */}
            <div className="rounded-2xl border border-white/10 bg-white/[0.02] p-5" data-testid="company-sub-hub-links">
              <h3 className="font-heading text-base font-bold uppercase mb-3">Rehberler</h3>
              <div className="space-y-1.5">
                {(hub_links || []).slice(0, 6).map((hub) => (
                  <Link key={hub.slug} to={hub.url} className="flex items-center gap-2 text-sm p-2 rounded-lg hover:bg-white/5 transition-colors group">
                    <Gift className="w-4 h-4" style={{ color: accentColor }} />
                    <span className="group-hover:text-neon-green transition-colors text-muted-foreground">{hub.title}</span>
                    <ChevronRight className="w-3 h-3 text-muted-foreground ml-auto" />
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Legal Footer */}
      <div className="container mx-auto max-w-6xl px-4 mt-12">
        <div className="rounded-xl border border-yellow-500/20 bg-yellow-500/5 p-4 text-center text-xs text-muted-foreground">
          <AlertTriangle className="w-4 h-4 inline-block text-yellow-500 mr-1.5" />
          18+ | Kumar bagimliligi yardim hatti: 182. Bu sayfa bilgilendirme amaclidir.
        </div>
      </div>
    </div>
  );
}
