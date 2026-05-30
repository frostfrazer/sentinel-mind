import { createContext, useContext, useState, useEffect } from 'react'
import { auth, users } from './api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('sm_token')
    if (token) {
      users.me().then(data => {
        if (data.id) setUser(data)
        else localStorage.removeItem('sm_token')
      }).finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (email, password) => {
    const data = await auth.login({ email, password })
    if (data.access_token) {
      localStorage.setItem('sm_token', data.access_token)
      const me = await users.me()
      setUser(me)
      return { ok: true }
    }
    return { ok: false, error: data.detail || 'Login failed' }
  }

  const register = async (email, password, full_name, company) => {
    const data = await auth.register({ email, password, full_name, company })
    if (data.access_token) {
      localStorage.setItem('sm_token', data.access_token)
      const me = await users.me()
      setUser(me)
      return { ok: true }
    }
    return { ok: false, error: data.detail || 'Registration failed' }
  }

  const logout = () => {
    localStorage.removeItem('sm_token')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
