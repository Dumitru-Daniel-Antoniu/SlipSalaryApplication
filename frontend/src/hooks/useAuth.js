export function getStoredTokens() {
  const access = localStorage.getItem('accessToken') || localStorage.getItem('access_token');
  const refresh = localStorage.getItem('refreshToken') || localStorage.getItem('refresh_token');
  return { access, refresh };
}

export function setStoredTokens(access, refresh) {
  if (access) {
    localStorage.setItem('accessToken', access);
    localStorage.setItem('access_token', access);
  }
  if (refresh) {
    localStorage.setItem('refreshToken', refresh);
    localStorage.setItem('refresh_token', refresh);
  }
}

export function clearStoredTokens() {
  localStorage.removeItem('accessToken');
  localStorage.removeItem('access_token');
  localStorage.removeItem('refreshToken');
  localStorage.removeItem('refresh_token');
}

export function parseJwt(token) {
  if (!token) return null;
  try {
    const parts = token.split('.');
    if (parts.length < 2) return null;
    const payload = parts[1].replace(/-/g, '+').replace(/_/g, '/');
    const pad = payload.length % 4 === 0 ? '' : '='.repeat(4 - (payload.length % 4));
    const decoded = atob(payload + pad);
    return JSON.parse(decoded);
  } catch {
    return null;
  }
}

export function isAuthenticated() {
  const { access } = getStoredTokens();
  if (!access) return false;
  const payload = parseJwt(access);
  if (!payload) return false;
  if (payload.exp && typeof payload.exp === 'number') {
    const now = Math.floor(Date.now() / 1000);
    return payload.exp > now;
  }
  return true;
}

export async function refreshAccessToken() {
  const { refresh } = getStoredTokens();
  if (!refresh) return false;
  try {
    const res = await fetch('/refresh', {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${refresh}`,
        'Content-Type': 'application/json',
      },
    });
    if (!res.ok) return false;
    const json = await res.json().catch(() => ({}));
    const access = json.access || json.access_token;
    const refreshNew = json.refresh || json.refresh_token || refresh;
    if (access) {
      setStoredTokens(access, refreshNew);
      return true;
    }
    return false;
  } catch {
    return false;
  }
}