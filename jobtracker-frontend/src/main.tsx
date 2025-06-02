// src/main.tsx
import React from "react";
import ReactDOM from "react-dom/client";
import AppRouter from "./AppRouter";
import "./styles/globals.css";
import { GoogleOAuthProvider } from "@react-oauth/google";

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID;

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <AppRouter />
    </GoogleOAuthProvider>
  </React.StrictMode>
);

console.log(">>> import.meta.env:", import.meta.env);