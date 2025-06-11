// src/msalConfig.ts
export const msalConfig = {
  auth: {
    clientId: import.meta.env.VITE_MICROSOFT_CLIENT_ID as string,
    authority: "https://login.microsoftonline.com/common", // or your tenant ID
    redirectUri: window.location.origin,
    navigateToLoginRequestUrl: false,
  },
  cache: {
    cacheLocation: "localStorage",
    storeAuthStateInCookie: false,
  },
};

// For implicit‐flow scopes, use offline_access only if needed:
export const loginRequest = {
  scopes: [
    "openid",
    "profile",
    "email",
    "User.Read",
    "Mail.Read",
  ],
  // forceAcquireToken: false // implicit by default
};