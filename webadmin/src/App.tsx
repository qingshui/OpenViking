import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import ResourceManagement from './pages/ResourceManagement'
import SessionManagement from './pages/SessionManagement'
import FileExplorer from './pages/FileExplorer'
import SemanticSearch from './pages/SemanticSearch'
import Layout from './components/common/Layout'

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-600">Loading...</div>
      </div>
    )
  }

  return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

const AppContent: React.FC = () => {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/resources" element={<ProtectedRoute><ResourceManagement /></ProtectedRoute>} />
        <Route path="/sessions" element={<ProtectedRoute><SessionManagement /></ProtectedRoute>} />
        <Route path="/filesystem" element={<ProtectedRoute><FileExplorer /></ProtectedRoute>} />
        <Route path="/search" element={<ProtectedRoute><SemanticSearch /></ProtectedRoute>} />
        <Route path="*" element={<ProtectedRoute><Navigate to="/" /></ProtectedRoute>} />
      </Routes>
    </Layout>
  )
}

const App: React.FC = () => {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/*" element={<AppContent />} />
      </Routes>
    </AuthProvider>
  )
}

export default App
