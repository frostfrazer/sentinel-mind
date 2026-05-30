import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from './AuthContext'

const nav = [
  { to: '/', label: 'Overview', icon: '⊞' },
  { to: '/shield-id', label: 'Shield ID', icon: '👁' },
  { to: '/shield-phish', label: 'Shield Phish', icon: '✉' },
  { to: '/shield-dev', label: 'Shield Dev', icon: '⌨' },
  { to: '/shield-soc', label: 'Shield SOC', icon: '📡' },
  { to: '/api-keys', label: 'API Keys', icon: '🔑' },
  { to: '/billing', label: 'Billing', icon: '💳' },
]

const PLAN_COLORS = { free: '#888', starter: '#0F6E56', pro: '#534AB7', enterprise: '#854F0B' }

export default function Layout({ children }) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => { logout(); navigate('/login') }

  return (
    <div style={{ display: 'flex', minHeight: '100vh', fontFamily: 'system-ui, sans-serif', fontSize: 14 }}>
      <aside style={{ width: 210, flexShrink: 0, borderRight: '0.5px solid #e0ded8', display: 'flex', flexDirection: 'column', padding: '16px 0', background: '#fff' }}>
        <div style={{ padding: '0 16px 20px', fontSize: 16, fontWeight: 500, display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{ fontSize: 20 }}>⚔</span> SentinelMind
        </div>

        {nav.slice(0, 5).map(n => (
          <NavLink key={n.to} to={n.to} end={n.to === '/'} style={({ isActive }) => ({
            display: 'flex', alignItems: 'center', gap: 10, padding: '8px 16px',
            fontSize: 13, color: isActive ? '#111' : '#666', fontWeight: isActive ? 500 : 400,
            background: isActive ? '#f5f4f0' : 'transparent', textDecoration: 'none'
          })}>
            <span>{n.icon}</span>{n.label}
          </NavLink>
        ))}

        <div style={{ fontSize: 10, fontWeight: 500, letterSpacing: '0.06em', textTransform: 'uppercase', color: '#aaa', padding: '16px 16px 6px' }}>Account</div>

        {nav.slice(5).map(n => (
          <NavLink key={n.to} to={n.to} style={({ isActive }) => ({
            display: 'flex', alignItems: 'center', gap: 10, padding: '8px 16px',
            fontSize: 13, color: isActive ? '#111' : '#666', fontWeight: isActive ? 500 : 400,
            background: isActive ? '#f5f4f0' : 'transparent', textDecoration: 'none'
          })}>
            <span>{n.icon}</span>{n.label}
          </NavLink>
        ))}

        <div style={{ marginTop: 'auto', padding: '12px 16px', borderTop: '0.5px solid #e0ded8' }}>
          {user && (
            <>
              <span style={{ display: 'inline-block', fontSize: 11, fontWeight: 500, padding: '2px 8px', borderRadius: 20, background: '#EEEDFE', color: '#3C3489', marginBottom: 8 }}>
                {user.plan} plan
              </span>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ fontSize: 12, color: '#555' }}>{user.email?.split('@')[0]}</div>
                <button onClick={handleLogout} style={{ fontSize: 11, color: '#999', background: 'none', border: 'none', cursor: 'pointer' }}>Sign out</button>
              </div>
            </>
          )}
        </div>
      </aside>

      <main style={{ flex: 1, overflowY: 'auto', padding: 28, background: '#faf9f6' }}>
        {children}
      </main>
    </div>
  )
}
