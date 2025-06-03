import React, { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import { isAuthenticated } from "./services/api"; // changed to async

export default function AppRouter() {
  const [authChecked, setAuthChecked] = useState(false);
  const [loggedIn, setLoggedIn] = useState(false);

  useEffect(() => {
    // On mount, immediately check if the user is logged in
    console.log("Starting Authentication")
    isAuthenticated().then((ok) => {
      setLoggedIn(ok);
      console.log("Logged In")
      setAuthChecked(true);
    });
  }, []);

  if (!authChecked) {
    // Still waiting for /auth/verify
    console.log("Checking Authentication")
    return (
      <div style={{ textAlign: "center", marginTop: "4rem" }}>
        Checking authentication…
      </div>
    );
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={loggedIn ? <Navigate to="/dashboard" /> : <Login />}
        />
        <Route
          path="/login"
          element={loggedIn ? <Navigate to="/dashboard" /> : <Login />}
        />
        <Route
          path="/dashboard"
          element={loggedIn ? <Dashboard /> : <Navigate to="/login" />}
        />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}