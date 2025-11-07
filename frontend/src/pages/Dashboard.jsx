import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Dashboard.css';
import { getStoredTokens, parseJwt, clearStoredTokens } from '../hooks/useAuth';
import { logout as apiLogout } from '../api/auth';
import { fetchWithAuth } from '../api/fetchWithAuth';

export default function DashboardPage() {
  const navigate = useNavigate();
  const [user, setUser] = useState({ name: 'Unknown', surname: '' });
  const [employees, setEmployees] = useState([]);
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
    const { access } = getStoredTokens();
    const payload = parseJwt(access);
    if (payload) {
      const identity = payload.sub || payload;
      setUser({ name: identity.name || 'Unknown', surname: identity.surname || '' });
    }

    (async () => {
      try {
        const res = await fetchWithAuth('/employees/department');
        let data = null;
        let text = null;
        try { data = await res.json(); } catch { text = await res.text().catch(() => null); }

        if (!res.ok) {
          const msg = data?.message || data?.Message || text || 'Failed to load employees';
          setBackendError(msg);
          return;
        }

        // attach lastMessage to each row so we can show per-employee status
        setEmployees(Array.isArray(data) ? data.map((e) => ({ ...e, lastMessage: '' })) : []);
      } catch (err) {
        setBackendError(err.message || 'Network error while fetching employees');
      }
    })();
  }, []);

  const logout = async () => {
    try {
      await apiLogout();
    } catch {
      // ignore network errors
    } finally {
      clearStoredTokens();
      navigate('/login', { replace: true });
    }
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
      email: form.email,
    };

    try {
      const res = await fetchWithAuth('/salary', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      let json = null;
      let text = null;
      try {
        json = await res.json();
      } catch (err) {
        try { text = await res.text(); } catch { text = null; }
      }

      const extractMsg = (obj) => {
        if (!obj || typeof obj !== 'object') return null;
        return obj.message || obj.Message || obj.detail || obj.error || null;
      };

      if (!res.ok) {
        const msgFromJson = extractMsg(json);
        if (msgFromJson) setBackendError(msgFromJson);
        else if (text) setBackendError(text);
        else {
          const combined = json ? (Object.values(json).flat?.().join(' ') || JSON.stringify(json)) : 'Request failed';
          setBackendError(combined);
        }
        setLoading(false);
        return;
      }

      const successMsg = extractMsg(json) || text || 'Salary created successfully.';
      setSuccess(successMsg);
      setForm({ month: '', year: '', salary: '', bonus: '', work: '', vacation: '', email: '' });
    } catch (err) {
      setBackendError(err.message || 'Network error');
    } finally {
      setLoading(false);
    }
  };

  // Call backend endpoints with { email } and show response per-row
  const handleGeneratePdf = async (employee) => {
    setBackendError('');
    setSuccess('');
    // optimistic: clear lastMessage for this row
    setEmployees((prev) => prev.map((e) => (e.email === employee.email ? { ...e, lastMessage: '' } : e)));
    try {
      const res = await fetchWithAuth('/createPdfForEmployees', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: employee.email }),
      });

      let json = null;
      let text = null;
      try { json = await res.json(); } catch { text = await res.text().catch(() => null); }

      const msg = json?.message || json?.Message || text || (res.ok ? 'PDF generated' : 'Failed to generate PDF');

      // attach message to the specific employee row
      setEmployees((prev) => prev.map((e) => e.email === employee.email ? { ...e, lastMessage: msg } : e));

      if (!res.ok) setBackendError(msg);
      else setSuccess(msg);
    } catch (err) {
      const m = err?.message || 'Network error while generating PDF';
      setBackendError(m);
      setEmployees((prev) => prev.map((e) => e.email === employee.email ? { ...e, lastMessage: m } : e));
    }
  };

  const handleSendPdf = async (employee) => {
    setBackendError('');
    setSuccess('');
    setEmployees((prev) => prev.map((e) => (e.email === employee.email ? { ...e, lastMessage: '' } : e)));
    try {
      const res = await fetchWithAuth('/sendPdfToEmployees', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: employee.email }),
      });

      let json = null;
      let text = null;
      try { json = await res.json(); } catch { text = await res.text().catch(() => null); }

      const msg = json?.message || json?.Message || text || (res.ok ? 'PDF sent' : 'Failed to send PDF');

      setEmployees((prev) => prev.map((e) => e.email === employee.email ? { ...e, lastMessage: msg } : e));

      if (!res.ok) setBackendError(msg);
      else setSuccess(msg);
    } catch (err) {
      const m = err?.message || 'Network error while sending PDF';
      setBackendError(m);
      setEmployees((prev) => prev.map((e) => e.email === employee.email ? { ...e, lastMessage: m } : e));
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
                <label htmlFor="email">Email</label>
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

        <section className="salary-card" style={{ marginLeft: 24, width: 900 }} aria-labelledby="employees-title">
          <h2 id="employees-title" className="salary-title">Team employees</h2>

          {employees.length === 0 ? (
            <p>No employees found in your department.</p>
          ) : (
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr>
                  <th style={{ textAlign: 'left', padding: 8 }}>Name</th>
                  <th style={{ textAlign: 'left', padding: 8 }}>Surname</th>
                  <th style={{ textAlign: 'left', padding: 8 }}>Email</th>
                  <th style={{ textAlign: 'left', padding: 8 }}>Status</th>
                  <th style={{ textAlign: 'left', padding: 8 }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {employees.map((emp) => (
                  <tr key={emp.employee_id || emp.email}>
                    <td style={{ padding: 8 }}>{emp.name}</td>
                    <td style={{ padding: 8 }}>{emp.surname}</td>
                    <td style={{ padding: 8 }}>{emp.email}</td>
                    <td style={{ padding: 8 }}>{emp.lastMessage || ''}</td>
                    <td style={{ padding: 8 }}>
                      <button type="button" onClick={() => handleGeneratePdf(emp)} style={{ marginRight: 8 }}>
                        Generate PDF
                      </button>
                      <button type="button" onClick={() => handleSendPdf(emp)}>
                        Send PDF
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      </main>
    </div>
  );
}