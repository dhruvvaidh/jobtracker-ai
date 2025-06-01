// src/AppRouter.tsx
import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";

/**
 * A very simple “isAuthenticated” placeholder.
 * In reality, you’ll check for a valid JWT cookie.
 */
function isAuthenticated(): boolean {
  // For example, you might check document.cookie for “jwt=...”
  return document.cookie.includes("token="); 
}

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={
            isAuthenticated() ? <Navigate to="/dashboard" /> : <Login />
          }
        />
        <Route
          path="/login"
          element={isAuthenticated() ? <Navigate to="/dashboard" /> : <Login />}
        />
        <Route
          path="/dashboard"
          element={
            isAuthenticated() ? <Dashboard /> : <Navigate to="/login" />
          }
        />
        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}