import { useEffect, useState } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, useLocation, Navigate } from "react-router-dom";
import axios from "axios";
import { Toaster } from "@/components/ui/sonner";
import { HelmetProvider } from "react-helmet-async";

// Pages
import HomePage from "@/pages/HomePage";
import BonusGuidePage from "@/pages/BonusGuidePage";
import SportsNewsPage from "@/pages/SportsNewsPage";
import ArticlePage from "@/pages/ArticlePage";
import AdminPage from "@/pages/AdminPage";
import LoginPage from "@/pages/LoginPage";
import MatchDetailPage from "@/pages/MatchDetailPage";
import FirmPage from "@/pages/FirmPage";
import FirmVideoPage from "@/pages/FirmVideoPage";
import SlugResolver from "@/pages/SlugResolver";
import CompanyProfilePage from "@/pages/CompanyProfilePage";
import CompaniesPage from "@/pages/CompaniesPage";
import CompanySubPage from "@/pages/CompanySubPage";
import BonusHubPage from "@/pages/BonusHubPage";
import PaymentHubPage from "@/pages/PaymentHubPage";
import CompanyArticlesListPage from "@/pages/CompanyArticlesListPage";
import CompanyArticlePage from "@/pages/CompanyArticlePage";
import ProgrammaticPage from "@/pages/ProgrammaticPage";
import VideoGalleryPage from "@/pages/VideoGalleryPage";
import VideoPlayerPage from "@/pages/VideoPlayerPage";
import WallpaperGalleryPage from "@/pages/WallpaperGalleryPage";
import WallpaperDetailPage from "@/pages/WallpaperDetailPage";

// Components
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import WelcomePopup from "@/components/WelcomePopup";
import MobileBottomNav from "@/components/MobileBottomNav";
import ProtectedRoute from "@/components/ProtectedRoute";

// Always use relative API path - works on any domain
export const API = "/api";

// Admin her domainden /admin-login path'i ile erişilebilir
export function isAdminDomain() {
  return true;
}

const ADMIN_PATHS = ["/admin", "/admin-login"];

function AppLayout({ isLoading }) {
  const [showPopup, setShowPopup] = useState(true);
  const location = useLocation();
  const adminDomain = isAdminDomain();
  const isAdminPath = ADMIN_PATHS.some((p) => location.pathname.startsWith(p));

  // Admin artık path-based: /admin-login her domainde çalışır
  const isAdminOnlyDomain = false;

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 border-4 border-neon-green border-t-transparent rounded-full animate-spin" />
          <p className="text-muted-foreground font-heading uppercase tracking-wider">Yükleniyor...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="App min-h-screen bg-background text-foreground">
      {!isAdminPath && !isAdminOnlyDomain && showPopup && <WelcomePopup onClose={() => setShowPopup(false)} />}
      {!isAdminPath && !isAdminOnlyDomain && <Navbar />}
      <main className={isAdminPath ? "" : "pt-16"}>
        <Routes>
          {/* Admin-only domain: tüm public sayfaları admin-login'e yönlendir */}
          {isAdminOnlyDomain ? (
            <>
              <Route path="/admin-login" element={<LoginPage />} />
              <Route path="/admin" element={<ProtectedRoute><AdminPage /></ProtectedRoute>} />
              <Route path="*" element={<Navigate to="/admin-login" replace />} />
            </>
          ) : (
            <>
              {/* Public routes */}
              <Route path="/" element={<HomePage />} />
              <Route path="/deneme-bonusu" element={<BonusGuidePage type="deneme" />} />
              <Route path="/hosgeldin-bonusu" element={<BonusGuidePage type="hosgeldin" />} />
              <Route path="/bonus/:type" element={<BonusGuidePage />} />
              <Route path="/spor-haberleri" element={<SportsNewsPage />} />
              <Route path="/makale/:slug" element={<ArticlePage />} />
              <Route path="/mac/:slug" element={<MatchDetailPage />} />
              <Route path="/companies" element={<CompaniesPage />} />
              <Route path="/companies/:slug" element={<CompanyProfilePage />} />

              {/* Video Gallery & Player */}
              <Route path="/videolar" element={<VideoGalleryPage />} />
              <Route path="/videolar/:videoId" element={<VideoPlayerPage />} />

              {/* Wallpaper Gallery */}
              <Route path="/gorseller" element={<WallpaperGalleryPage />} />
              <Route path="/gorseller/:seoSlug" element={<WallpaperDetailPage />} />

              {/* GG2026 SEO: Bonus Hub Pages */}
              <Route path="/deneme-bonusu-veren-siteler" element={<BonusHubPage />} />
              <Route path="/guncel-deneme-bonusu" element={<BonusHubPage />} />
              <Route path="/yatirimsiz-deneme-bonusu" element={<BonusHubPage />} />
              <Route path="/bonus-veren-siteler" element={<BonusHubPage />} />

              {/* GG2026 SEO: Payment Hub Pages */}
              <Route path="/odeme-yontemleri" element={<PaymentHubPage />} />
              <Route path="/mobil-odeme-ile-bahis" element={<PaymentHubPage />} />
              <Route path="/kredi-karti-ile-bahis" element={<PaymentHubPage />} />
              <Route path="/papel-ile-bahis" element={<PaymentHubPage />} />
              <Route path="/havale-ile-bahis" element={<PaymentHubPage />} />
              <Route path="/kripto-ile-bahis" element={<PaymentHubPage />} />
              <Route path="/bddk-onayli-odeme-yontemleri" element={<PaymentHubPage />} />
              <Route path="/guvenli-odeme-yontemleri" element={<PaymentHubPage />} />

              {/* GG2026 SEO: Company Articles (must be before /:companySlug/:pageType) */}
              <Route path="/:companySlug/makaleler" element={<CompanyArticlesListPage />} />
              <Route path="/:companySlug/makaleler/:articleSlug" element={<CompanyArticlePage />} />

              {/* GG2026 Phase 6: Programmatic SEO — guide pages */}
              <Route path="/rehber/:slug" element={<ProgrammaticPage />} />

              {/* GG2026 SEO: Company Sub-Pages (must be before /:slug catch-all) */}
              <Route path="/:companySlug/:pageType" element={<CompanySubPage />} />

              <Route path="/:slug/video" element={<FirmVideoPage />} />
              <Route path="/:slug" element={<SlugResolver />} />

              {/* Admin routes — SADECE admin subdomainde */}
              {adminDomain && <Route path="/admin-login" element={<LoginPage />} />}
              {adminDomain && <Route path="/admin" element={<ProtectedRoute><AdminPage /></ProtectedRoute>} />}
              {!adminDomain && <Route path="/admin*" element={<Navigate to="/" replace />} />}
            </>
          )}
        </Routes>
      </main>
      {!isAdminPath && !isAdminOnlyDomain && <Footer />}
      {!isAdminPath && !isAdminOnlyDomain && <MobileBottomNav />}
      <Toaster position="top-right" richColors />
    </div>
  );
}

function App() {
  const [isLoading, setIsLoading] = useState(false);

  return (
    <HelmetProvider>
      <BrowserRouter>
        <AppLayout isLoading={isLoading} />
      </BrowserRouter>
    </HelmetProvider>
  );
}

export default App;
