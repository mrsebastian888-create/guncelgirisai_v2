import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import axios from "axios";
import { API, isAdminDomain } from "@/App";

export default function ProtectedRoute({ children }) {
  const [status, setStatus] = useState("checking"); // checking | ok | fail

  useEffect(() => {
    // İlk kontrol: doğru subdomainde mi?
    if (!isAdminDomain()) {
      setStatus("fail");
      return;
    }

    const token = localStorage.getItem("admin_token");
    if (!token) {
      setStatus("fail");
      return;
    }
    axios
      .get(`${API}/auth/verify`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then(() => setStatus("ok"))
      .catch(() => {
        localStorage.removeItem("admin_token");
        localStorage.removeItem("admin_user");
        setStatus("fail");
      });
  }, []);

  if (status === "checking") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="w-10 h-10 border-4 border-neon-green border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (status === "fail") {
    // Admin domaininde değilse 404 gibi davran, değilse login sayfasına gönder
    if (!isAdminDomain()) return <Navigate to="/" replace />;
    return <Navigate to="/admin-login" replace />;
  }

  return children;
}
