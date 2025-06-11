import React from "react";
import ReactDOM from "react-dom/client";
import AppRouter from "./AppRouter";
import "./styles/globals.css";
import { GoogleOAuthProvider } from "@react-oauth/google";
import { AuthProvider } from "./AuthContext";

// MSAL imports
import { PublicClientApplication } from "@azure/msal-browser";
import { MsalProvider, useMsal } from "@azure/msal-react";
import { useEffect } from "react";

const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID!;
const MICROSOFT_CLIENT_ID = import.meta.env.VITE_MICROSOFT_CLIENT_ID!;

// MSAL configuration
const msalConfig = {
  auth: {
    clientId: MICROSOFT_CLIENT_ID,
    authority: "https://login.microsoftonline.com/common",
    redirectUri: window.location.origin,
  },
  cache: {
    cacheLocation: "localStorage",
    storeAuthStateInCookie: false,
  },
};

const msalInstance = new PublicClientApplication(msalConfig);

// Handler to process redirect responses before rendering the app
function MsalHandler({ children }: { children: React.ReactNode }) {
  const { instance } = useMsal();
  useEffect(() => {
    (async () => {
      try {
        // Ensure the MSAL client is initialized before any other calls
        await instance.initialize();
        // Process the redirect response (if any)
        const resp = await instance.handleRedirectPromise();
        if (resp) {
          console.log("MSAL redirect response", resp);
        }
      } catch (e) {
        console.error("MSAL initialization or redirect error", e);
      }
    })();
  }, [instance]);
  return <>{children}</>;
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <MsalProvider instance={msalInstance}>
        <MsalHandler>
          <AuthProvider>
            <AppRouter />
          </AuthProvider>
        </MsalHandler>
      </MsalProvider>
    </GoogleOAuthProvider>
  </React.StrictMode>
);

//console.log(">>> import.meta.env.VITE_GOOGLE_CLIENT_ID:", import.meta.env.VITE_GOOGLE_CLIENT_ID);