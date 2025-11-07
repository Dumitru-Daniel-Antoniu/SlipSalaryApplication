import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../api/auth';
import { setStoredTokens } from '../hooks/useAuth';
import './LoginPage.css';

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // login() will POST to /login and return JSON { access, refresh, ... }
      const data = await login({ email, password });

      const access = data.access || data.access_token;
      const refresh = data.refresh || data.refresh_token;

      if (!access || !refresh) {
        setError('No tokens received from server.');
        setLoading(false);
        return;
      }

      setStoredTokens(access, refresh);
      navigate('/dashboard', { replace: true });
    } catch (err) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-background">
      <div className="login-container">
        <h1 className="login-title">Employees evidence</h1>

        <form className="login-form" onSubmit={handleSubmit}>
          {error && <div className="error-message">{error}</div>}

          <label className="login-label" htmlFor="email">Email</label>
          <input
            id="email"
            className="login-input"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            autoComplete="username"
          />

          <label className="login-label" htmlFor="password">Password</label>
          <input
            id="password"
            className="login-input"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
          />

          <button
            className="login-button"
            type="submit"
            disabled={loading}
          >
            {loading ? <span className="btn-spinner" /> : 'Login'}
          </button>
        </form>

        <div className="login-register">
          Don't have an account? <a href="/register">Register</a>
        </div>
      </div>
    </div>
  );
}
