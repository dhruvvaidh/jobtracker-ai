// src/pages/Login.tsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useGoogleLogin, type TokenResponse} from "@react-oauth/google";
import { googleAuth } from "../services/api";
import { isAuthenticated } from "../services/api";
import { useAuth } from "../AuthContext";
import { useMsal} from "@azure/msal-react";
//import {type AuthError, InteractionStatus} from "@azure/msal-browser";
import { loginRequest } from "../msalConfig";
import { microsoftAuth } from "../services/api";

export default function Login() {
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { setLoggedIn, setAuthChecked } = useAuth();
  const { instance, inProgress } = useMsal();

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

      console.log("Tokens Recieved from Google");

      setError(null);
      setLoading(true);

      console.log("Sending Tokens to backend");
      googleAuth(accessToken)
        .then(() => {
          console.log("Tokens Sent to backend → Now calling verify()");
          // Re‐check /auth/verify now that the cookie is set:
          return isAuthenticated();
        })
        .then((ok) => {
          console.log("Logged in? (after verify) →", ok);
          if (ok) {
            setLoggedIn(true);
            setAuthChecked(true);
            navigate("/dashboard");
          } else {
            setError("Unable to verify login.");
          }
        })
        .catch((e) => {
          console.error("Login flow error:", e);
          setError("Login failed. Please check console for details.");
        })
        .finally(() => {
          setLoading(false);
        });
        },
        onError: () => {
          setError("Google sign‑in was unsuccessful. Try again.");
        },
  });

  async function loginMicrosoft() {
    setError(null);
    setLoading(true);
    try {
      // Perform redirect-based login (hash will be handled in main.tsx)
      await instance.loginRedirect({
        scopes: loginRequest.scopes,
        prompt: "select_account",
      });
      // After redirect, control will not return here
    } catch (e) {
      console.error("loginMicrosoft error", e);
      setError("Microsoft sign-in failed.");
      setLoading(false);
    }
  }

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
        Get Started!!!
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
        <>
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
              src="../assets/google.svg"
              alt="Google"
              width={24}
              height={24}
              style={{ marginRight: "0.5rem" }}
            />
            Sign in with Google
          </button>
          <button
            onClick={loginMicrosoft}
            disabled={loading}
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
              marginTop: "1rem",
            }}
          >
            <img
              src="../assets/microsoft.svg"
              alt="Microsoft"
              width={24}
              height={24}
              style={{ marginRight: "0.5rem" }}
            />
            Sign in with Microsoft
          </button>
        </>
      )}
    </div>
  );
}