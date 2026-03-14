import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import ProgrammaticPage from "@/pages/ProgrammaticPage";
import FirmPage from "@/pages/FirmPage";
import { API } from "@/App";

/**
 * Smart resolver: checks if a top-level slug is a programmatic page.
 * If yes → renders ProgrammaticPage. If no → falls back to FirmPage.
 */
export default function SlugResolver() {
  const { slug } = useParams();
  const [pageType, setPageType] = useState(null); // "programmatic" | "firm" | null
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    setPageType(null);
    // Try programmatic page first (fast check)
    axios.get(`${API}/programmatic/page/${slug}`)
      .then(() => {
        setPageType("programmatic");
        setLoading(false);
      })
      .catch(() => {
        // Not a programmatic page → it's a firm page
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
  return <FirmPage />;
}
