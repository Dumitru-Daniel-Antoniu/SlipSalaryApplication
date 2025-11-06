import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';

function decodeJwt(token) {
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

export default function DashboardPage() {
  const navigate = useNavigate();
  const [user, setUser] = useState({ name: 'Unknown', surname: '' });
  const [form, setForm] = useState({
    month: '',
    year: '',
    salary: '',
    bonus: '',
    work: '',
    vacation: '',
    email: '',
  });
  const [errors, setErrors] = useState({});
  const [backendError, setBackendError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem('accessToken') || localStorage.getItem('access_token');
    const payload = decodeJwt(token);
    if (payload) {
      setUser({ name: payload.name || 'Unknown', surname: payload.surname || '' });
    }
  }, []);

  const logout = async () => {
    const token = localStorage.getItem('accessToken') || localStorage.getItem('access_token');
    // try to inform backend (if endpoint exists) but don't block logout
    if (token) {
      try {
        await fetch('/logout', {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        }).catch(() => {});
      } catch {}
    }
    localStorage.removeItem('accessToken');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('refresh_token');
    navigate('/login', { replace: true });
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setForm((s) => ({ ...s, [name]: value }));
    setErrors((prev) => ({ ...prev, [name]: '' }));
    setBackendError('');
    setSuccess('');
  };

  const validate = () => {
    const next = {};
    const required = ['month', 'year', 'salary', 'bonus', 'work', 'vacation', 'email'];
    required.forEach((f) => {
      if (!String(form[f] || '').trim()) next[f] = 'This field is required.';
    });

    const month = Number(form.month);
    if (form.month && (!Number.isInteger(month) || month < 1 || month > 12)) next.month = 'Month must be 1-12.';

    const year = Number(form.year);
    if (form.year && (!Number.isInteger(year) || year < 1970 || year > 2100)) next.year = 'Enter a valid year.';

    const salary = Number(form.salary);
    if (form.salary && (Number.isNaN(salary) || salary < 0)) next.salary = 'Salary must be a positive number.';

    const bonus = Number(form.bonus);
    if (form.bonus && (Number.isNaN(bonus) || bonus < 0)) next.bonus = 'Bonus must be a positive number.';

    const work = Number(form.work);
    if (form.work && (!Number.isInteger(work) || work < 0)) next.work = 'Work must be a non-negative integer.';

    const vacation = Number(form.vacation);
    if (form.vacation && (!Number.isInteger(vacation) || vacation < 0)) next.vacation = 'Vacation must be a non-negative integer.';

    if (form.email && !/\S+@\S+\.\S+/.test(form.email)) next.email = 'Enter a valid email.';

    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setBackendError('');
    setSuccess('');
    if (!validate()) return;
    setLoading(true);

    const payload = {
      month: Number(form.month),
      year: Number(form.year),
      salary: Number(form.salary),
      bonus: Number(form.bonus),
      work: Number(form.work),
      vacation: Number(form.vacation),
      // backend expects employeeId (or employee_id) - send email as identifier for now
      employeeId: form.email,
    };

    try {
      const token = localStorage.getItem('accessToken') || localStorage.getItem('access_token');
      const headers = { 'Content-Type': 'application/json' };
      if (token) headers.Authorization = `Bearer ${token}`;

      const res = await fetch('/salary', {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
      });

      let json;
      try {
        json = await res.json();
      } catch {
        json = null;
      }

      if (!res.ok) {
        // map validation-like responses or generic message
        if (json && typeof json === 'object') {
          const msg = json.message || json.detail || json.error;
          if (msg) setBackendError(msg);
          else {
            const combined = Object.values(json).flat?.().join(' ') || JSON.stringify(json);
            setBackendError(combined);
          }
        } else {
          setBackendError(json || 'Request failed');
        }
        setLoading(false);
        return;
      }

      setSuccess('Salary created successfully.');
      setForm({ month: '', year: '', salary: '', bonus: '', work: '', vacation: '', email: '' });
    } catch (err) {
      setBackendError(err.message || 'Network error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dash-background">
      <header className="dash-topbar">
        <div className="dash-user">
          {user.name} {user.surname}
        </div>
        <div className="dash-actions">
          <button className="dash-logout" onClick={logout}>Logout</button>
        </div>
      </header>

      <main className="dash-main">
        <section className="salary-card" aria-labelledby="salary-title">
          <h2 id="salary-title" className="salary-title">Create salary</h2>

          <form className="salary-form" onSubmit={handleSubmit} noValidate>
            {backendError && <div className="form-backend-error" role="alert">{backendError}</div>}
            {success && <div className="form-success" role="status">{success}</div>}

            <div className="salary-grid">
              <div className="field">
                <label htmlFor="month">Month</label>
                <input id="month" name="month" value={form.month} onChange={handleChange} className="register-input" />
                {errors.month && <div className="field-error">{errors.month}</div>}
              </div>

              <div className="field">
                <label htmlFor="year">Year</label>
                <input id="year" name="year" value={form.year} onChange={handleChange} className="register-input" />
                {errors.year && <div className="field-error">{errors.year}</div>}
              </div>

              <div className="field">
                <label htmlFor="salary">Salary</label>
                <input id="salary" name="salary" value={form.salary} onChange={handleChange} className="register-input" />
                {errors.salary && <div className="field-error">{errors.salary}</div>}
              </div>

              <div className="field">
                <label htmlFor="bonus">Bonus</label>
                <input id="bonus" name="bonus" value={form.bonus} onChange={handleChange} className="register-input" />
                {errors.bonus && <div className="field-error">{errors.bonus}</div>}
              </div>

              <div className="field">
                <label htmlFor="work">Work</label>
                <input id="work" name="work" value={form.work} onChange={handleChange} className="register-input" />
                {errors.work && <div className="field-error">{errors.work}</div>}
              </div>

              <div className="field">
                <label htmlFor="vacation">Vacation</label>
                <input id="vacation" name="vacation" value={form.vacation} onChange={handleChange} className="register-input" />
                {errors.vacation && <div className="field-error">{errors.vacation}</div>}
              </div>

              <div className="field" style={{ gridColumn: '1 / -1' }}>
                <label htmlFor="email">Email (employee identifier)</label>
                <input id="email" name="email" value={form.email} onChange={handleChange} className="register-input" />
                {errors.email && <div className="field-error">{errors.email}</div>}
              </div>
            </div>

            <div className="form-actions">
              <button type="submit" className="primary-btn" disabled={loading}>
                {loading ? <span className="btn-spinner" aria-hidden="true" /> : 'Create'}
              </button>
            </div>
          </form>
        </section>
      </main>
    </div>
  );
}
