// src/pages/Login.tsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { GoogleLogin} from "@react-oauth/google";
import type {CredentialResponse} from "@react-oauth/google"
import { googleAuth } from "../services/api";
import { isAuthenticated } from "../services/api";

export default function Login() {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  /**
   * onSuccess is called when Google returns an ID token successfully.
   * We then POST it to our backend (/auth/google). On 200, we navigate to /dashboard.
   * The AppRouter will immediately trigger /auth/verify before rendering Dashboard.
   */
  function onSuccess(credentialResponse: CredentialResponse) {
    const idToken = credentialResponse.credential;
    if (!idToken) {
      setError("No credential returned by Google.");
      return;
    }

    setError(null);
    setLoading(true);

    googleAuth(idToken)
      .then(() => {
        // After Google login succeeded, re‑verify with the server:
        return isAuthenticated();
      })
      .then((ok) => {
        if (ok) {
          navigate("/dashboard");
        } else {
          setError("Could not verify login. Please try again.");
        }
      })
      .catch((e) => {
        console.error("Login flow error:", e);
        setError("Login failed. Please check console for details.");
      })
      .finally(() => {
        setLoading(false);
      });
  }

  function onError() {
    setError("Google sign‑in was unsuccessful. Try again.");
  }

  return (
    <div
      style={{
        maxWidth: "400px",
        margin: "4rem auto",
        padding: "2rem",
        border: "1px solid #ddd",
        borderRadius: "8px",
        textAlign: "center",
        backgroundColor: "#fff",
      }}
    >
      <h1 style={{ fontSize: "1.5rem", marginBottom: "1rem" }}>
        Sign in with Google
      </h1>

      {error && (
        <p style={{ color: "red", marginBottom: "1rem", fontSize: "0.9rem" }}>
          {error}
        </p>
      )}

      {loading ? (
        <button
          disabled
          style={{
            padding: "0.5rem 1rem",
            fontSize: "1rem",
            backgroundColor: "#eee",
            border: "1px solid #ccc",
            borderRadius: "4px",
            cursor: "not-allowed",
          }}
        >
          Signing you in…
        </button>
      ) : (
        <GoogleLogin onSuccess={onSuccess} onError={onError} />
      )}
    </div>
  );
}