// src/services/api.ts
import type { ApplicationsByStatus } from "../types/status";

const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

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

export async function classifyAndRefresh(): Promise<ApplicationsByStatus> {
  // 1. POST to /classify
  const postRes = await fetch(`${BASE_URL}/classify`, {
    method: "POST",
    credentials: "include",
  });
  if (!postRes.ok) {
    throw new Error(`Classification failed: ${postRes.statusText}`);
  }
  // 2. Refetch updated statuses
  return await fetchApplicationsByStatus();
}

export async function logout() {
  // Optionally, if you implement a logout endpoint
  await fetch(`${BASE_URL}/auth/logout`, {
    method: "POST",
    credentials: "include",
  });
  // Remove any client‑side state as needed
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