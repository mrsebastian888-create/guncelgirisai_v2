import { useEffect, useState } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import axios from "axios";
import { Toaster } from "@/components/ui/sonner";

// Pages
import HomePage from "@/pages/HomePage";
import BonusGuidePage from "@/pages/BonusGuidePage";
import SportsNewsPage from "@/pages/SportsNewsPage";
import ArticlePage from "@/pages/ArticlePage";
import AdminPage from "@/pages/AdminPage";
import LoginPage from "@/pages/LoginPage";

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
  // localhost/preview ortamında da çalışsın diye ADMIN_HOST boşsa izin ver
  if (!ADMIN_HOST) return true;
  return hostname === ADMIN_HOST;
}

const ADMIN_PATHS = ["/admin", "/admin-login"];

function AppLayout({ isLoading }) {
  const [showPopup, setShowPopup] = useState(true);
  const location = useLocation();
  const isAdminPath = ADMIN_PATHS.some((p) => location.pathname.startsWith(p));

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
      {!isAdminPath && showPopup && <WelcomePopup onClose={() => setShowPopup(false)} />}
      {!isAdminPath && <Navbar />}
      <main className={isAdminPath ? "" : "pt-16"}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/deneme-bonusu" element={<BonusGuidePage type="deneme" />} />
          <Route path="/hosgeldin-bonusu" element={<BonusGuidePage type="hosgeldin" />} />
          <Route path="/bonus/:type" element={<BonusGuidePage />} />
          <Route path="/spor-haberleri" element={<SportsNewsPage />} />
          <Route path="/makale/:slug" element={<ArticlePage />} />
          <Route path="/admin-login" element={<LoginPage />} />
          <Route
            path="/admin"
            element={
              <ProtectedRoute>
                <AdminPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </main>
      {!isAdminPath && <Footer />}
      <Toaster position="top-right" richColors />
    </div>
  );
}

function App() {
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const seedData = async () => {
      try {
        await axios.post(`${API}/seed`);
      } catch (e) {
        console.log("Seed completed or already seeded");
      } finally {
        setIsLoading(false);
      }
    };
    seedData();
  }, []);

  return (
    <BrowserRouter>
      <AppLayout isLoading={isLoading} />
    </BrowserRouter>
  );
}

export default App;
