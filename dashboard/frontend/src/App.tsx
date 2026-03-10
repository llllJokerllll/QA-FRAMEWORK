import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useState } from 'react'
import Layout from './components/Layout'
import Dashboard from './pages/DashboardEnhanced'
import TestSuites from './pages/TestSuites'
import TestCases from './pages/TestCases'
import Executions from './pages/Executions'
import Integrations from './pages/Integrations'
import Billing from './pages/Billing'
import SelfHealing from './pages/SelfHealing'
import Settings from './pages/Settings'
import Login from './pages/Login'
import Register from './pages/Register'
import Landing from './pages/Landing'
import ForgotPassword from './pages/ForgotPassword'
import NotFound from './pages/NotFound'
import useAuthStore from './stores/authStore'

function App() {
  const { isAuthenticated } = useAuthStore()
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <Router>
      <Routes>
        {/* Public routes - ALWAYS accessible */}
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />

        {/* Protected routes - Require authentication */}
        <Route path="/dashboard" element={
          isAuthenticated ? (
            <Layout sidebarOpen={sidebarOpen} onSidebarToggle={() => setSidebarOpen(!sidebarOpen)}>
              <Dashboard />
            </Layout>
          ) : (
            <Navigate to="/login" replace />
          )
        } />
        <Route path="/suites" element={
          isAuthenticated ? (
            <Layout sidebarOpen={sidebarOpen} onSidebarToggle={() => setSidebarOpen(!sidebarOpen)}>
              <TestSuites />
            </Layout>
          ) : (
            <Navigate to="/login" replace />
          )
        } />
        <Route path="/suites/:suiteId/cases" element={
          isAuthenticated ? (
            <Layout sidebarOpen={sidebarOpen} onSidebarToggle={() => setSidebarOpen(!sidebarOpen)}>
              <TestCases />
            </Layout>
          ) : (
            <Navigate to="/login" replace />
          )
        } />
        <Route path="/executions" element={
          isAuthenticated ? (
            <Layout sidebarOpen={sidebarOpen} onSidebarToggle={() => setSidebarOpen(!sidebarOpen)}>
              <Executions />
            </Layout>
          ) : (
            <Navigate to="/login" replace />
          )
        } />
        <Route path="/integrations" element={
          isAuthenticated ? (
            <Layout sidebarOpen={sidebarOpen} onSidebarToggle={() => setSidebarOpen(!sidebarOpen)}>
              <Integrations />
            </Layout>
          ) : (
            <Navigate to="/login" replace />
          )
        } />
        <Route path="/billing" element={
          isAuthenticated ? (
            <Layout sidebarOpen={sidebarOpen} onSidebarToggle={() => setSidebarOpen(!sidebarOpen)}>
              <Billing />
            </Layout>
          ) : (
            <Navigate to="/login" replace />
          )
        } />
        <Route path="/self-healing" element={
          isAuthenticated ? (
            <Layout sidebarOpen={sidebarOpen} onSidebarToggle={() => setSidebarOpen(!sidebarOpen)}>
              <SelfHealing />
            </Layout>
          ) : (
            <Navigate to="/login" replace />
          )
        } />
        <Route path="/settings" element={
          isAuthenticated ? (
            <Layout sidebarOpen={sidebarOpen} onSidebarToggle={() => setSidebarOpen(!sidebarOpen)}>
              <Settings />
            </Layout>
          ) : (
            <Navigate to="/login" replace />
          )
        } />

        {/* Catch-all route - 404 */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  )
}

export default App