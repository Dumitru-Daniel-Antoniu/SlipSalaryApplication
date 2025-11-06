import React, { useState } from 'react';
import { login } from '../api/auth';
import './LoginPage.css';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    console.log("Start the handling of submit")
    try {
      // login() will POST to /login and return JSON { access, refresh, ... }
      const data = await login({ email, password });
      // persist tokens for later requests
      console.log("The data received from login:", data);
      localStorage.setItem('accessToken', data.access);
      localStorage.setItem('refreshToken', data.refresh);
      // optional: trigger navigation or app state change after login
      // window.location.href = '/';
    } catch (err) {
        console.log("Login failed")
      setError(err.message || 'Login failed');
    } finally {
        console.log("Final state")
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
