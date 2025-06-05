// src/AuthContext.tsx
import React, { createContext, useContext, useEffect, useState } from "react";
import { isAuthenticated } from "./services/api";

interface AuthContextValue {
  loggedIn: boolean;
  setLoggedIn: React.Dispatch<React.SetStateAction<boolean>>;
  authChecked: boolean;
  setAuthChecked: React.Dispatch<React.SetStateAction<boolean>>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [loggedIn, setLoggedIn] = useState(false);
  const [authChecked, setAuthChecked] = useState(false);

  // On mount, do one initial verify
  useEffect(() => {
    isAuthenticated().then((ok) => {
      setLoggedIn(ok);
      setAuthChecked(true);
    });
  }, []);

  return (
    <AuthContext.Provider
      value={{ loggedIn, setLoggedIn, authChecked, setAuthChecked }}
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