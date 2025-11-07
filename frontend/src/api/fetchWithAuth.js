import { getStoredTokens, refreshAccessToken } from '../hooks/useAuth';

export async function fetchWithAuth(input, init = {}) {
  const { access } = getStoredTokens();
  const headers = new Headers(init.headers || {});
  if (access) headers.set('Authorization', `Bearer ${access}`);
  const res = await fetch(input, { ...init, headers });
  if (res.status === 401) {
    const refreshed = await refreshAccessToken();
    if (!refreshed) return res;
    const { access: newAccess } = getStoredTokens();
    const retryHeaders = new Headers(init.headers || {});
    if (newAccess) retryHeaders.set('Authorization', `Bearer ${newAccess}`);
    return fetch(input, { ...init, headers: retryHeaders });
  }
  return res;
}