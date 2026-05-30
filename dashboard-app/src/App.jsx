import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './AuthContext'
import Layout from './Layout'
import Login from './Login'
import Overview from './Overview'
import APIKeys from './APIKeys'
import Billing from './Billing'
import ShieldID from './ShieldID'
import ShieldPhish from './ShieldPhish'
import ShieldDev from './ShieldDev'
import ShieldSOC from './ShieldSOC'

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
          <Route path="/shield-id" element={<Protected><ShieldID /></Protected>} />
          <Route path="/shield-phish" element={<Protected><ShieldPhish /></Protected>} />
          <Route path="/shield-dev" element={<Protected><ShieldDev /></Protected>} />
          <Route path="/shield-soc" element={<Protected><ShieldSOC /></Protected>} />
          <Route path="/api-keys" element={<Protected><APIKeys /></Protected>} />
          <Route path="/billing" element={<Protected><Billing /></Protected>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
