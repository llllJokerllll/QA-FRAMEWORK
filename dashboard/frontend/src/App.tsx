import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useState } from 'react'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import TestSuites from './pages/TestSuites'
import TestCases from './pages/TestCases'
import Executions from './pages/Executions'
import Billing from './pages/Billing'
import Login from './pages/Login'
import useAuthStore from './stores/authStore'

function App() {
  const { isAuthenticated } = useAuthStore()
  const [sidebarOpen, setSidebarOpen] = useState(true)

  if (!isAuthenticated) {
    return (
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </Router>
    )
  }

  return (
    <Router>
      <Layout sidebarOpen={sidebarOpen} onSidebarToggle={() => setSidebarOpen(!sidebarOpen)}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/suites" element={<TestSuites />} />
          <Route path="/suites/:suiteId/cases" element={<TestCases />} />
          <Route path="/executions" element={<Executions />} />
          <Route path="/billing" element={<Billing />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App