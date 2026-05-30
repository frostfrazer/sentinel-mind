import { useState } from 'react'
import { useAuth } from './AuthContext'
import { useNavigate } from 'react-router-dom'

export default function Login() {
  const { login, register } = useAuth()
  const navigate = useNavigate()
  const [mode, setMode] = useState('login')
  const [form, setForm] = useState({ email: '', password: '', full_name: '', company: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const handle = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    const res = mode === 'login'
      ? await login(form.email, form.password)
      : await register(form.email, form.password, form.full_name, form.company)
    setLoading(false)
    if (res.ok) navigate('/')
    else setError(res.error)
  }

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }))

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: '#f9f8f5' }}>
      <div style={{ width: 380, background: '#fff', border: '0.5px solid #e0ded8', borderRadius: 16, padding: '32px 28px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 24 }}>
          <div style={{ width: 36, height: 36, borderRadius: 8, background: '#EEEDFE', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18, color: '#534AB7' }}>⚔</div>
          <span style={{ fontSize: 18, fontWeight: 500 }}>SentinelMind</span>
        </div>
        <h1 style={{ fontSize: 16, fontWeight: 500, marginBottom: 4 }}>{mode === 'login' ? 'Sign in' : 'Create account'}</h1>
        <p style={{ fontSize: 13, color: '#888', marginBottom: 20 }}>AI-native cybersecurity platform</p>

        {error && <div style={{ background: '#FCEBEB', color: '#791F1F', fontSize: 12, padding: '8px 12px', borderRadius: 8, marginBottom: 14 }}>{error}</div>}

        <form onSubmit={handle}>
          {mode === 'register' && (
            <>
              <input placeholder="Full name" value={form.full_name} onChange={set('full_name')} style={{ width: '100%', marginBottom: 10 }} />
              <input placeholder="Company (optional)" value={form.company} onChange={set('company')} style={{ width: '100%', marginBottom: 10 }} />
            </>
          )}
          <input type="email" placeholder="Email" value={form.email} onChange={set('email')} required style={{ width: '100%', marginBottom: 10 }} />
          <input type="password" placeholder="Password (min 8 chars)" value={form.password} onChange={set('password')} required style={{ width: '100%', marginBottom: 16 }} />
          <button type="submit" disabled={loading} style={{ width: '100%', background: '#534AB7', color: '#EEEDFE', border: 'none', borderRadius: 8, padding: '10px', fontSize: 14, fontWeight: 500, cursor: loading ? 'not-allowed' : 'pointer' }}>
            {loading ? 'Loading...' : mode === 'login' ? 'Sign in' : 'Create account'}
          </button>
        </form>

        <p style={{ fontSize: 12, color: '#888', marginTop: 16, textAlign: 'center' }}>
          {mode === 'login' ? "Don't have an account? " : 'Already have an account? '}
          <span style={{ color: '#534AB7', cursor: 'pointer' }} onClick={() => { setMode(mode === 'login' ? 'register' : 'login'); setError('') }}>
            {mode === 'login' ? 'Sign up' : 'Sign in'}
          </span>
        </p>
      </div>
    </div>
  )
}
