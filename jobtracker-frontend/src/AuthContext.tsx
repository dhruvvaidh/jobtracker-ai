// src/AuthContext.tsx
import React, { createContext, useContext, useEffect, useState } from "react";
import { isAuthenticated, microsoftAuth } from "./services/api";
import { useMsal } from "@azure/msal-react";
import { loginRequest } from "./msalConfig";

interface AuthContextValue {
  loggedIn: boolean;
  setLoggedIn: React.Dispatch<React.SetStateAction<boolean>>;
  authChecked: boolean;
  setAuthChecked: React.Dispatch<React.SetStateAction<boolean>>;
  loginWithMicrosoft: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [loggedIn, setLoggedIn] = useState(false);
  const [authChecked, setAuthChecked] = useState(false);

  const { instance } = useMsal();

  // On mount, handle MSAL redirect, send token to backend, then verify session
  useEffect(() => {
    (async () => {
      try {
        // Process redirect callback if present
        await instance.initialize()
        const response = await instance.handleRedirectPromise();
        if (response?.accessToken) {
          // Send Graph access token to backend to set JWT cookie
          await microsoftAuth(response.accessToken);
        }
      } catch (e) {
        console.error("MSAL redirect handling error:", e);
      }
      // Finally, verify our own JWT session
      const ok = await isAuthenticated();
      setLoggedIn(ok);
      setAuthChecked(true);
    })();
  }, [instance]);

  const loginWithMicrosoft = () => {
    instance.loginRedirect(loginRequest);
  };

  return (
    <AuthContext.Provider
      value={{ loggedIn, setLoggedIn, authChecked, setAuthChecked, loginWithMicrosoft }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return ctx;
}