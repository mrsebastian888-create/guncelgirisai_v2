import { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import axios from "axios";
import ProgrammaticPage from "@/pages/ProgrammaticPage";
import FirmPage from "@/pages/FirmPage";
import { API } from "@/App";

/**
 * Smart resolver: checks short link → programmatic → firm page.
 * Short links redirect immediately via window.location.
 */
export default function SlugResolver() {
  const { slug } = useParams();
  const [pageType, setPageType] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    setPageType(null);

    // 1. Check short link first
    axios.get(`${API}/shortlinks/resolve/${slug}`)
      .then(res => {
        // Redirect to original URL
        window.location.href = res.data.original_url;
      })
      .catch(() => {
        // 2. Not a short link → check programmatic
        axios.get(`${API}/programmatic/page/${slug}`)
          .then(() => {
            setPageType("programmatic");
            setLoading(false);
          })
          .catch(() => {
            // 3. Not programmatic → firm page
            setPageType("firm");
            setLoading(false);
          });
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
