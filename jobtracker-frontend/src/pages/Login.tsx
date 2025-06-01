// src/pages/Login.tsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { GoogleLogin} from "@react-oauth/google";
import type { CredentialResponse } from "@react-oauth/google";
import { googleAuth } from "../services/api";

export default function Login() {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);

  function onSuccess(credentialResponse: CredentialResponse) {
    if (credentialResponse.credential) {
      googleAuth(credentialResponse.credential)
        .then(() => {
          // Backend should set HttpOnly cookie “token”; now redirect to dashboard
          navigate("/dashboard");
        })
        .catch((e) => {
          console.error("Google auth error:", e);
          // for quick debugging, you could do:
          alert("Error calling /auth/google:\n" + (e instanceof Error ? e.message : JSON.stringify(e)));
          setError("Login failed. Please check console for details.");
        });
    } else {
      setError("No credential returned by Google.");
    }
  }

  function onError() {
    setError("Google sign‑in was unsuccessful. Try again.");
  }

  return (
    <div className="container" style={{ paddingTop: "4rem" }}>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "1rem" }}>
        Sign in with Google
      </h1>
      {error && (
        <p style={{ color: "red", marginBottom: "1rem" }}>{error}</p>
      )}
      <GoogleLogin onSuccess={onSuccess} onError={onError} />
    </div>
  );
}