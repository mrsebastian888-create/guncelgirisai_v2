import { useEffect, useState } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { Toaster } from "@/components/ui/sonner";

// Pages
import HomePage from "@/pages/HomePage";
import BonusGuidePage from "@/pages/BonusGuidePage";
import SportsNewsPage from "@/pages/SportsNewsPage";
import ArticlePage from "@/pages/ArticlePage";
import AdminPage from "@/pages/AdminPage";

// Components
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import WelcomePopup from "@/components/WelcomePopup";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [showPopup, setShowPopup] = useState(true);

  useEffect(() => {
    // Seed database on first load
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
      <BrowserRouter>
        {showPopup && <WelcomePopup onClose={() => setShowPopup(false)} />}
        <Navbar />
        <main className="pt-16">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/deneme-bonusu" element={<BonusGuidePage type="deneme" />} />
            <Route path="/hosgeldin-bonusu" element={<BonusGuidePage type="hosgeldin" />} />
            <Route path="/bonus/:type" element={<BonusGuidePage />} />
            <Route path="/spor-haberleri" element={<SportsNewsPage />} />
            <Route path="/makale/:slug" element={<ArticlePage />} />
            <Route path="/admin" element={<AdminPage />} />
          </Routes>
        </main>
        <Footer />
        <Toaster position="top-right" richColors />
      </BrowserRouter>
    </div>
  );
}

export default App;
