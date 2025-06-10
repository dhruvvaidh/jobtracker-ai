// src/services/api.ts
import type { ApplicationsByStatus } from "../types/status";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "https://localhost:8000";

function getCookie(name: string): string | null {
  // Simple helper to read a cookie by name
  const match = document.cookie.match(
    new RegExp("(^| )" + name + "=([^;]+)")
  );
  return match ? decodeURIComponent(match[2]) : null;
}

export async function googleAuth(
  accessToken: string
): Promise<any> {
  const res = await fetch(`${BASE_URL}/auth/google`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({
      access_token: accessToken,
    }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Google Auth failed (status ${res.status}): ${text}`);
  }
  return res.json();
}

export async function microsoftAuth(accessToken: string): Promise<any> {
  const res = await fetch(`${BASE_URL}/auth/microsoft`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ access_token: accessToken }),
  });
  if (!res.ok) {
    throw new Error(`Microsoft Auth failed (${res.status}): ${await res.text()}`);
  }
  return res.json();
}

export async function fetchApplicationsByStatus(): Promise<ApplicationsByStatus> {
  const res = await fetch(`${BASE_URL}/applications_by_status`, {
    method: "GET",
    credentials: "include", // send cookie
  });
  if (!res.ok) {
    throw new Error(`Failed to fetch statuses: ${res.statusText}`);
  }
  return (await res.json()) as ApplicationsByStatus;
}

export type Provider = "google" | "microsoft" | "both";

export async function classifyAndRefresh(
  provider: Provider,
  accessToken?: string
): Promise<ApplicationsByStatus> {
  const body: any = { provider };
  if (accessToken) {
    body.access_token = accessToken;
  }

  const res = await fetch(`${BASE_URL}/classify`, {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    throw new Error(`Classification failed: ${res.statusText}`);
  }
  return await fetchApplicationsByStatus();
}

export async function isAuthenticated(): Promise<boolean> {
  try {
    const res = await fetch(`${BASE_URL}/auth/verify`, {
      method: "GET",
      credentials: "include",
    });
    return res.ok;
  } catch {
    return false;
  }
}

export async function logout(): Promise<void> {
  const res = await fetch(`${BASE_URL}/auth/logout`, {
    method: "POST",
    credentials: "include",
  });
  if (!res.ok) {
    throw new Error(`Logout failed: ${res.statusText}`);
  }
}