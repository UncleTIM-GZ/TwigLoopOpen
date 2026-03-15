/**
 * Client-side auth helpers.
 *
 * After the httpOnly-cookie migration (P1-4), the browser sends auth
 * cookies automatically. localStorage is kept as a transitional fallback
 * so that existing sessions are not immediately invalidated.
 */

const ACCESS_TOKEN_KEY = "twigloop_access_token";
const REFRESH_TOKEN_KEY = "twigloop_refresh_token";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Read access token from localStorage (transitional fallback).
 * After full migration this will be removed — cookies are sent automatically.
 */
export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

/**
 * Persist tokens to localStorage (transitional fallback).
 * The server also sets httpOnly cookies on login/register/refresh responses.
 */
export function setTokens(access: string, refresh: string): void {
  localStorage.setItem(ACCESS_TOKEN_KEY, access);
  localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
}

/**
 * Clear local token storage.
 * Prefer {@link logout} which also clears server-side cookies.
 */
export function clearTokens(): void {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

/**
 * Check whether the user appears to be logged in.
 * Uses localStorage as a quick check; the real auth is the httpOnly cookie
 * validated by the server on each request.
 */
export function isLoggedIn(): boolean {
  if (typeof window === "undefined") return false;
  return !!localStorage.getItem(ACCESS_TOKEN_KEY);
}

/**
 * Full logout: clear server-side httpOnly cookies + local storage.
 */
export async function logout(): Promise<void> {
  try {
    await fetch(`${API_BASE}/api/v1/auth/logout`, {
      method: "POST",
      credentials: "include",
    });
  } catch {
    // best effort — cookie might already be expired
  }
  clearTokens();
}
