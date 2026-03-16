import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'

interface AuthContextType {
  isAuthenticated: boolean
  username: string | null
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [username, setUsername] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('ov_api_key')
    const user = localStorage.getItem('ov_username')
    if (token && user) {
      setIsAuthenticated(true)
      setUsername(user)
    }
    setIsLoading(false)
  }, [])

  const login = async (username: string, password: string) => {
    const ADMIN_USER = import.meta.env.VITE_ADMIN_USERNAME || 'admin'
    const ADMIN_PASS = import.meta.env.VITE_ADMIN_PASSWORD || ''
    const ROOT_API_KEY = import.meta.env.VITE_ROOT_API_KEY || ''

    if (username === ADMIN_USER && password === ADMIN_PASS) {
      // Use the ROOT_API_KEY from environment or stored value
      const apiKey = ROOT_API_KEY || localStorage.getItem('ov_api_key')
      if (apiKey) {
        localStorage.setItem('ov_api_key', apiKey)
      }
      localStorage.setItem('ov_username', username)
      setIsAuthenticated(true)
      setUsername(username)
    } else {
      throw new Error('Invalid username or password')
    }
  }

  const logout = () => {
    localStorage.removeItem('ov_api_key')
    localStorage.removeItem('ov_username')
    setIsAuthenticated(false)
    setUsername(null)
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, username, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
