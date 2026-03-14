import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import ProgrammaticPage from "@/pages/ProgrammaticPage";
import FirmPage from "@/pages/FirmPage";
import BonusHubPage from "@/pages/BonusHubPage";
import PaymentHubPage from "@/pages/PaymentHubPage";
import { API } from "@/App";

/**
 * Smart resolver: /api/resolve-slug/:slug returns type → render ProgrammaticPage,
 * BonusHubPage, PaymentHubPage, or FirmPage.
 */
export default function SlugResolver() {
  const { slug } = useParams();
  const [pageType, setPageType] = useState(null); // "programmatic" | "bonus_hub" | "payment_hub" | "firm" | null
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    setPageType(null);
    axios.get(`${API}/resolve-slug/${slug}`)
      .then((res) => {
        setPageType(res.data?.type || "firm");
        setLoading(false);
      })
      .catch(() => {
        setPageType("firm");
        setLoading(false);
      });
  }, [slug]);

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center pt-20">
      <div className="w-10 h-10 border-2 border-neon-green border-t-transparent rounded-full animate-spin" />
    </div>
  );

  if (pageType === "programmatic") return <ProgrammaticPage />;
  if (pageType === "bonus_hub") return <BonusHubPage />;
  if (pageType === "payment_hub") return <PaymentHubPage />;
  return <FirmPage />;
}
