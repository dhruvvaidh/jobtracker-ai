// src/pages/Login.tsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useGoogleLogin, type TokenResponse} from "@react-oauth/google";
import { googleAuth } from "../services/api";

export default function Login() {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Configure useGoogleLogin to ask for Gmail scope as well
  const login = useGoogleLogin({
    flow: "implicit", // Implicit flow returns an access_token directly to the browser
    scope:
      "openid email profile https://www.googleapis.com/auth/gmail.readonly",
    onSuccess: (tokenResponse: TokenResponse) => {
      const accessToken = tokenResponse.access_token;

      if (!accessToken) {
        setError("Failed to retrieve tokens from Google.");
        return;
      }

      setError(null);
      setLoading(true);

      // Send both tokens to the backend
      googleAuth(accessToken)
        .then(() => {
          // On success, navigate to dashboard
          navigate("/dashboard");
        })
        .catch((e) => {
          console.error("Login flow error:", e);
          setError("Login failed. Check console for details.");
        })
        .finally(() => setLoading(false));
    },
    onError: () => {
      setError("Google sign‑in was unsuccessful. Try again.");
    },
  });

  return (
    <div
      style={{
        maxWidth: 400,
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
        <button disabled style={{ padding: "0.5rem 1rem" }}>
          Signing you in…
        </button>
      ) : (
        <button
          onClick={() => login()}
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: "0.5rem",
            padding: "0.5rem 1rem",
            fontSize: "1rem",
            color: "#444",
            backgroundColor: "#fff",
            border: "1px solid #ddd",
            borderRadius: "4px",
            cursor: "pointer",
          }}
        >
          {/* You can replace with your own Google icon */}
          <img
            src="/google-icon.svg"
            alt="Google"
            width={24}
            height={24}
            style={{ marginRight: "0.5rem" }}
          />
          Sign in with Google
        </button>
      )}
    </div>
  );
}