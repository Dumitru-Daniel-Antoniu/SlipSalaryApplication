import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './RegisterPage.css';

export default function RegisterPage() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    cnp: '',
    name: '',
    surname: '',
    password: '',
    position: '',
    department: '',
    dateOfBirth: '',
    dateOfHire: '',
    email: '',
  });
  const [errors, setErrors] = useState({});
  const [backendError, setBackendError] = useState('');
  const [loading, setLoading] = useState(false);

  // If tokens exist, redirect to main page
  useEffect(() => {
    const access = localStorage.getItem('accessToken') || localStorage.getItem('access_token');
    if (access) navigate('/');
  }, [navigate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((s) => ({ ...s, [name]: value }));
    setErrors((prev) => ({ ...prev, [name]: '' }));
    setBackendError('');
  };

  const validate = () => {
    const next = {};
    // required
    Object.keys(form).forEach((field) => {
      if (!String(form[field] || '').trim()) next[field] = 'This field is required.';
    });

    // email
    if (form.email && !/\S+@\S+\.\S+/.test(form.email)) next.email = 'Enter a valid email.';

    // password min length
    if (form.password && form.password.length < 6) next.password = 'Password must be at least 6 characters.';

    // simple CNP check (13 digits)
    if (form.cnp && !/^\d{13}$/.test(form.cnp)) next.cnp = 'CNP must be 13 digits.';

    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setBackendError('');
    if (!validate()) return;
    setLoading(true);

    try {
      const res = await fetch('/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });

      const json = await res.json().catch(() => ({}));

      if (!res.ok) {
        // backend may return a message string or a JSON with details
        const msg = json.message || json.detail || json.error || (typeof json === 'string' ? json : null);
        // If validation errors returned as an object, try to map them
        if (json && typeof json === 'object' && !msg) {
          // fallback: show combined messages
          const combined = Object.values(json).flat().join(' ');
          setBackendError(combined || 'Registration failed.');
        } else {
          setBackendError(msg || 'Registration failed.');
        }
        setLoading(false);
        return;
      }

      // Accept different token key styles
      const access = json.access || json.access_token;
      const refresh = json.refresh || json.refresh_token;

      if (!access || !refresh) {
        setBackendError('No tokens received from server.');
        setLoading(false);
        return;
      }

      localStorage.setItem('accessToken', access);
      localStorage.setItem('refreshToken', refresh);

      // Redirect to main page
      navigate('/');
    } catch (err) {
      setBackendError(err.message || 'Network error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-background">
      <main className="register-card" role="main" aria-labelledby="register-title">
        <h1 id="register-title" className="register-title">Employees evidence</h1>

        <form className="register-form" onSubmit={handleSubmit} noValidate>
          {backendError && <div className="form-backend-error" role="alert">{backendError}</div>}

          <div className="register-grid">
            <div className="field">
              <label htmlFor="cnp">CNP</label>
              <input id="cnp" name="cnp" value={form.cnp} onChange={handleChange} className="register-input" />
              {errors.cnp && <div className="field-error">{errors.cnp}</div>}
            </div>

            <div className="field">
              <label htmlFor="name">Name</label>
              <input id="name" name="name" value={form.name} onChange={handleChange} className="register-input" />
              {errors.name && <div className="field-error">{errors.name}</div>}
            </div>

            <div className="field">
              <label htmlFor="surname">Surname</label>
              <input id="surname" name="surname" value={form.surname} onChange={handleChange} className="register-input" />
              {errors.surname && <div className="field-error">{errors.surname}</div>}
            </div>

            <div className="field">
              <label htmlFor="email">Email</label>
              <input id="email" name="email" type="email" value={form.email} onChange={handleChange} className="register-input" />
              {errors.email && <div className="field-error">{errors.email}</div>}
            </div>

            <div className="field">
              <label htmlFor="password">Password</label>
              <input id="password" name="password" type="password" value={form.password} onChange={handleChange} className="register-input" />
              {errors.password && <div className="field-error">{errors.password}</div>}
            </div>

            <div className="field">
              <label htmlFor="position">Position</label>
              <input id="position" name="position" value={form.position} onChange={handleChange} className="register-input" />
              {errors.position && <div className="field-error">{errors.position}</div>}
            </div>

            <div className="field">
              <label htmlFor="department">Department</label>
              <input id="department" name="department" value={form.department} onChange={handleChange} className="register-input" />
              {errors.department && <div className="field-error">{errors.department}</div>}
            </div>

            <div className="field">
              <label htmlFor="dateOfBirth">Date of Birth</label>
              <input id="dateOfBirth" name="dateOfBirth" type="date" value={form.dateOfBirth} onChange={handleChange} className="register-input" />
              {errors.dateOfBirth && <div className="field-error">{errors.dateOfBirth}</div>}
            </div>

            <div className="field">
              <label htmlFor="dateOfHire">Date of Hire</label>
              <input id="dateOfHire" name="dateOfHire" type="date" value={form.dateOfHire} onChange={handleChange} className="register-input" />
              {errors.dateOfHire && <div className="field-error">{errors.dateOfHire}</div>}
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="primary-btn" disabled={loading}>
              {loading ? <span className="btn-spinner" aria-hidden="true" /> : 'Register'}
            </button>
            <Link to="/login" className="link-btn">Back to login</Link>
          </div>
        </form>
      </main>
    </div>
  );
}
