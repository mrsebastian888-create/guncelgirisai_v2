import React, { useEffect, useState } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, useLocation, Navigate, Link } from "react-router-dom";
import axios from "axios";
import { Toaster } from "@/components/ui/sonner";
import { HelmetProvider } from "react-helmet-async";

class ErrorBoundary extends React.Component {
  constructor(props) { super(props); this.state = { hasError: false }; }
  static getDerivedStateFromError() { return { hasError: true }; }
  componentDidCatch(error, info) { console.error("App error:", error, info); }
  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-background text-foreground">
          <div className="text-center p-8">
            <h1 className="text-4xl font-bold mb-4">Bir Hata Olustu</h1>
            <p className="text-muted-foreground mb-6">Sayfa yuklenirken bir sorun olustu.</p>
            <button onClick={() => window.location.reload()} className="px-6 py-3 rounded-lg font-bold" style={{ background: "hsl(var(--neon-green))", color: "#000" }}>
              Sayfayi Yenile
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

function NotFoundPage() {
  return (
    <div className="min-h-[70vh] flex items-center justify-center">
      <div className="text-center p-8">
        <h1 className="font-heading text-8xl font-black mb-4" style={{ color: "hsl(var(--neon-green))" }}>404</h1>
        <h2 className="text-2xl font-bold mb-2">Sayfa Bulunamadi</h2>
        <p className="text-muted-foreground mb-6">Aradiginiz sayfa mevcut degil veya kaldirilmis olabilir.</p>
        <Link to="/" className="inline-flex px-6 py-3 rounded-lg font-bold" style={{ background: "hsl(var(--neon-green))", color: "#000" }}>
          Ana Sayfaya Don
        </Link>
      </div>
    </div>
  );
}

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
import CompanyProfilePage from "@/pages/CompanyProfilePage";
import CompaniesPage from "@/pages/CompaniesPage";

// Components
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import WelcomePopup from "@/components/WelcomePopup";
import MobileBottomNav from "@/components/MobileBottomNav";
import ProtectedRoute from "@/components/ProtectedRoute";

// Use REACT_APP_BACKEND_URL in dev, relative path in production
export const API = process.env.REACT_APP_BACKEND_URL
  ? `${process.env.REACT_APP_BACKEND_URL}/api`
  : "/api";

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
              <Route path="/:slug/video" element={<FirmVideoPage />} />
              <Route path="/:slug" element={<FirmPage />} />
              <Route path="*" element={<NotFoundPage />} />

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
    <ErrorBoundary>
      <HelmetProvider>
        <BrowserRouter>
          <AppLayout isLoading={isLoading} />
        </BrowserRouter>
      </HelmetProvider>
    </ErrorBoundary>
  );
}

export default App;
