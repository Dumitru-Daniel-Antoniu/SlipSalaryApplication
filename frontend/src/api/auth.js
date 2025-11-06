export async function login({ email, password }) {
  const res = await fetch('/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });

  console.log("Auth response status:", res.status);
  const json = await res.json().catch(() => ({}));

  console.log("Auth response JSON:", json);
  if (!res.ok) {
    // prefer readable message from backend
    const msg = json.detail || json.message || 'Login failed';
    throw new Error(msg);
  }

  // Expecting backend to return { access: "...", refresh: "..." }
  return json;
}

// read access token for future requests
export function getAuthHeaders() {
  const token = localStorage.getItem('accessToken');
  return token ? { Authorization: `Bearer ${token}` } : {};
}