// src/pages/Dashboard.tsx
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  fetchApplicationsByStatus,
  classifyAndRefresh,
  logout,
} from "../services/api";
import type { ApplicationsByStatus } from "../types/status";
import StatusTile from "../components/StatusTile";
import RefreshButton from "../components/RefreshButton";
import { useAuth } from "../AuthContext";

export default function Dashboard() {
  const [data, setData] = useState<ApplicationsByStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { setLoggedIn } = useAuth();

  useEffect(() => {
    setLoading(true);
    console.log("Fetching Applications by Status")
    fetchApplicationsByStatus()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((e) => {
        console.error(e);
        setError("Failed to load data.");
        setLoading(false);
      });
  }, []);

  async function handleRefresh() {
    setLoading(true);
    setError(null);
    try {
      console.log("Classifying Emails")
      const refreshed = await classifyAndRefresh();
      console.log("Recieved Classified Emails")
      setData(refreshed);
    } catch (e) {
      console.error(e);
      setError("Refresh failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handleLogout() {
    try {
      await logout();
      setLoggedIn(false);
      console.log("Logging Out")
      // Once the server has deleted the HttpOnly cookie, we can redirect:
      navigate("/login");
    } catch (e) {
      console.error("Logout error:", e);
      // Optionally show a user‐facing error message here
    }
  }

  if (loading) {
    return (
      <div className="container">
        <p>Loading applications…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container" style={{ marginTop: "2rem" }}>
        <p style={{ color: "red" }}>{error}</p>
        <button onClick={() => window.location.reload()}>
          Reload page
        </button>
      </div>
    );
  }

  if (!data) {
    return null; // Should not happen
  }

  return (
    <div className="container" style={{ paddingTop: "2rem" }}>
      <header style={{ display: "flex", justifyContent: "space-between" }}>
        <h1 style={{ fontSize: "1.75rem" }}>Dashboard</h1>
        <button onClick={handleLogout} style={{ fontSize: "0.9rem" }}>
          Logout
        </button>
      </header>

      <div style={{ marginTop: "1rem", marginBottom: "1rem" }}>
        <RefreshButton onClick={handleRefresh} />
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
          gap: "1rem",
        }}
      >
        <StatusTile title="Applied" records={data.Applied} />
        <StatusTile title="Interview" records={data.Interview} />
        <StatusTile title="Offer" records={data.Offer} />
        <StatusTile title="Rejected" records={data.Rejected} />
      </div>
    </div>
  );
}