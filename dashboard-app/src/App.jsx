import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './AuthContext'
import Layout from './Layout'
import Login from './Login'
import Overview from './Overview'
import APIKeys from './APIKeys'
import Billing from './Billing'

const Placeholder = ({ title }) => (
  <div>
    <h1 style={{ fontSize: 18, fontWeight: 500, marginBottom: 8 }}>{title}</h1>
    <p style={{ fontSize: 13, color: '#888' }}>Coming soon — this page is being built.</p>
  </div>
)

function Protected({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div style={{ padding: 40, color: '#888' }}>Loading...</div>
  if (!user) return <Navigate to="/login" replace />
  return <Layout>{children}</Layout>
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/" element={<Protected><Overview /></Protected>} />
          <Route path="/shield-id" element={<Protected><Placeholder title="Shield ID" /></Protected>} />
          <Route path="/shield-phish" element={<Protected><Placeholder title="Shield Phish" /></Protected>} />
          <Route path="/shield-dev" element={<Protected><Placeholder title="Shield Dev" /></Protected>} />
          <Route path="/shield-soc" element={<Protected><Placeholder title="Shield SOC" /></Protected>} />
          <Route path="/api-keys" element={<Protected><APIKeys /></Protected>} />
          <Route path="/billing" element={<Protected><Billing /></Protected>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
