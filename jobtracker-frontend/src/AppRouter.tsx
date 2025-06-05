import React, { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import { useAuth } from "./AuthContext";

export default function AppRouter() {
  const { loggedIn, authChecked } = useAuth();
  return (
    <BrowserRouter>
      {!authChecked ? (
        <div style={{ textAlign: "center", marginTop: "4rem" }}>
          Checking authentication…
        </div>
      ) : (
        <Routes>
          <Route
            path="/"
            element={loggedIn ? <Navigate to="/dashboard" /> : <Navigate to="/login" />}
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
      )}
    </BrowserRouter>
  );
}