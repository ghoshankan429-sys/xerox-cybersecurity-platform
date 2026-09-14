/**
 * Safe token storage helper for XEROX.
 * 
 * Provides resilient storage for opaque session tokens across:
 * - In-memory cache (for iOS Safari Private Browsing where storage throws QuotaExceededError)
 * - sessionStorage (for standard per-tab sessions)
 * - localStorage (preserves session when iOS Safari terminates background WebKit processes)
 * 
 * Note: Only stores high-entropy random session tokens. Never stores credentials or passwords.
 */

const TOKEN_KEY = "xerox_session_token";
let inMemoryToken: string | null = null;

export function getStoredToken(): string | null {
  if (inMemoryToken) {
    return inMemoryToken;
  }
  if (typeof window === "undefined") {
    return null;
  }

  // 1. Try sessionStorage first
  try {
    const fromSession = sessionStorage.getItem(TOKEN_KEY);
    if (fromSession) {
      inMemoryToken = fromSession;
      return fromSession;
    }
  } catch {
    // Handled: Private browsing mode or storage disabled
  }

  // 2. Try localStorage fallback (WebKit process recycle recovery)
  try {
    const fromLocal = localStorage.getItem(TOKEN_KEY);
    if (fromLocal) {
      inMemoryToken = fromLocal;
      return fromLocal;
    }
  } catch {
    // Handled: Private browsing mode or storage disabled
  }

  return null;
}

export function setStoredToken(token: string): void {
  inMemoryToken = token;
  if (typeof window === "undefined") {
    return;
  }

  try {
    sessionStorage.setItem(TOKEN_KEY, token);
  } catch {
    // Handled: iOS Safari Private Browsing quota/security error
  }

  try {
    localStorage.setItem(TOKEN_KEY, token);
  } catch {
    // Handled: iOS Safari Private Browsing quota/security error
  }
}

export function clearStoredToken(): void {
  inMemoryToken = null;
  if (typeof window === "undefined") {
    return;
  }

  try {
    sessionStorage.removeItem(TOKEN_KEY);
  } catch {
    // Ignore errors on clear
  }

  try {
    localStorage.removeItem(TOKEN_KEY);
  } catch {
    // Ignore errors on clear
  }
}
