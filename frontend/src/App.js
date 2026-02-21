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

// Components
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import WelcomePopup from "@/components/WelcomePopup";
import ProtectedRoute from "@/components/ProtectedRoute";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

// Admin sadece bu hostname'den erişilebilir
const ADMIN_HOST = process.env.REACT_APP_ADMIN_HOST || "";

export function isAdminDomain() {
  const hostname = window.location.hostname;
  if (!ADMIN_HOST) return true;
  // Yerel geliştirme ortamında her zaman izin ver
  if (hostname === "localhost" || hostname === "127.0.0.1") return true;
  // Preview ortamında izin ver
  if (hostname.endsWith(".preview.emergentagent.com")) return true;
  return hostname === ADMIN_HOST;
}

const ADMIN_PATHS = ["/admin", "/admin-login"];

function AppLayout({ isLoading }) {
  const [showPopup, setShowPopup] = useState(true);
  const location = useLocation();
  const adminDomain = isAdminDomain();
  const isAdminPath = ADMIN_PATHS.some((p) => location.pathname.startsWith(p));

  // Admin domainde ana sayfaya gelen kullanıcıyı admin-login'e yönlendir
  const isAdminOnlyDomain = ADMIN_HOST && window.location.hostname === ADMIN_HOST;

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

              {/* Admin routes — SADECE admin subdomainde */}
              {adminDomain && <Route path="/admin-login" element={<LoginPage />} />}
              {adminDomain && <Route path="/admin" element={<ProtectedRoute><AdminPage /></ProtectedRoute>} />}
              {!adminDomain && <Route path="/admin*" element={<Navigate to="/" replace />} />}
            </>
          )}
        </Routes>
      </main>
      {!isAdminPath && !isAdminOnlyDomain && <Footer />}
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
