import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { QueryProvider } from './providers'
import { ToastProvider } from './components'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import ResourceManagement from './pages/ResourceManagement'
import ResourceDetail from './pages/ResourceDetail'
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

  return isAuthenticated ? <>{children}</> : <Login />
}

const AppContent: React.FC = () => {
  return (
    <Layout>
      <React.Suspense fallback={<div>Loading...</div>}>
        <Routes>
          <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/resources" element={<ProtectedRoute><ResourceManagement /></ProtectedRoute>} />
          <Route path="/resources/:uri" element={<ProtectedRoute><ResourceDetail /></ProtectedRoute>} />
          <Route path="/sessions" element={<ProtectedRoute><SessionManagement /></ProtectedRoute>} />
          <Route path="/filesystem" element={<ProtectedRoute><FileExplorer /></ProtectedRoute>} />
          <Route path="/search" element={<ProtectedRoute><SemanticSearch /></ProtectedRoute>} />
          <Route path="*" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        </Routes>
      </React.Suspense>
    </Layout>
  )
}

const App: React.FC = () => {
  return (
    <QueryProvider>
      <ToastProvider>
        <AuthProvider>
          <AppContent />
        </AuthProvider>
      </ToastProvider>
    </QueryProvider>
  )
}

export default App
