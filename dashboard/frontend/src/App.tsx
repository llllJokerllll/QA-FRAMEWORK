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
        {/* Public routes */}
        <Route path="/" element={<Landing />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        
        {/* Protected routes */}
        {isAuthenticated ? (
          <>
            <Route path="/dashboard" element={
              <Layout sidebarOpen={sidebarOpen} onSidebarToggle={() => setSidebarOpen(!sidebarOpen)}>
                <Dashboard />
              </Layout>
            } />
            <Route path="/suites" element={
              <Layout sidebarOpen={sidebarOpen} onSidebarToggle={() => setSidebarOpen(!sidebarOpen)}>
                <TestSuites />
              </Layout>
            } />
            <Route path="/suites/:suiteId/cases" element={
              <Layout sidebarOpen={sidebarOpen} onSidebarToggle={() => setSidebarOpen(!sidebarOpen)}>
                <TestCases />
              </Layout>
            } />
            <Route path="/executions" element={
              <Layout sidebarOpen={sidebarOpen} onSidebarToggle={() => setSidebarOpen(!sidebarOpen)}>
                <Executions />
              </Layout>
            } />
            <Route path="/integrations" element={
              <Layout sidebarOpen={sidebarOpen} onSidebarToggle={() => setSidebarOpen(!sidebarOpen)}>
                <Integrations />
              </Layout>
            } />
            <Route path="/billing" element={
              <Layout sidebarOpen={sidebarOpen} onSidebarToggle={() => setSidebarOpen(!sidebarOpen)}>
                <Billing />
              </Layout>
            } />
            <Route path="/self-healing" element={
              <Layout sidebarOpen={sidebarOpen} onSidebarToggle={() => setSidebarOpen(!sidebarOpen)}>
                <SelfHealing />
              </Layout>
            } />
            <Route path="/settings" element={
              <Layout sidebarOpen={sidebarOpen} onSidebarToggle={() => setSidebarOpen(!sidebarOpen)}>
                <Settings />
              </Layout>
            } />
          </>
        ) : (
          <Route path="*" element={<Navigate to="/login" replace />} />
        )}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  )
}

export default App