import { getStoredTokens, setStoredTokens, clearStoredTokens } from '../hooks/useAuth';
import { fetchWithAuth } from './fetchWithAuth';

export async function login({ email, password }) {
   const res = await fetch('/login', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({ email, password })
   });
 
   const json = await res.json().catch(() => ({}));
   if (!res.ok) {
     const msg = json.detail || json.message || 'Login failed';
     throw new Error(msg);
   }
 
   const access = json.access || json.access_token;
   const refresh = json.refresh || json.refresh_token;
   if (access && refresh) setStoredTokens(access, refresh);

   return json;
 }

export function getAuthHeaders() {
  const { access } = getStoredTokens();
  return access ? { Authorization: `Bearer ${access}` } : {};
}

export async function logout() {
  try {
    await fetchWithAuth('/logout', { method: 'POST' });
  } catch {
    // ignore network errors; still clear local tokens
  } finally {
    clearStoredTokens();
  }
}
