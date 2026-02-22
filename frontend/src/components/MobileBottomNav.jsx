import { Link, useLocation } from "react-router-dom";
import { Gift, Users, Target, Activity } from "lucide-react";

const navItems = [
  { label: "Bonuslar", href: "/deneme-bonusu", icon: Gift, color: "#FFD700" },
  { label: "Firmalar", href: "/#firma-rehberi", icon: Users, color: "#00F0FF", isAnchor: true },
  { label: "AI Analiz", href: "/ai-analiz", icon: Target, color: "#A78BFA" },
  { label: "Spor", href: "/spor-haberleri", icon: Activity, color: "#00FF87" },
];

const MobileBottomNav = () => {
  const location = useLocation();

  return (
    <nav
      className="fixed bottom-0 left-0 right-0 z-50 md:hidden border-t"
      style={{
        background: "rgba(10,10,10,0.95)",
        backdropFilter: "blur(12px)",
        borderColor: "rgba(255,255,255,0.06)",
      }}
      data-testid="mobile-bottom-nav"
    >
      <div className="flex items-center justify-around h-14 px-2">
        {navItems.map((item) => {
          const isActive = location.pathname === item.href;
          const Tag = item.isAnchor ? "a" : Link;
          const linkProps = item.isAnchor ? { href: item.href } : { to: item.href };

          return (
            <Tag
              key={item.label}
              {...linkProps}
              className="flex flex-col items-center justify-center gap-0.5 flex-1 py-1 transition-colors"
              data-testid={`mobile-nav-${item.label.toLowerCase()}`}
            >
              <item.icon
                className="w-5 h-5"
                style={{ color: isActive ? item.color : "rgba(255,255,255,0.4)" }}
              />
              <span
                className="text-[10px] font-semibold uppercase tracking-wide"
                style={{ color: isActive ? item.color : "rgba(255,255,255,0.4)" }}
              >
                {item.label}
              </span>
            </Tag>
          );
        })}
      </div>
    </nav>
  );
};

export default MobileBottomNav;
