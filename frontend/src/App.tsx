import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import AccountDetailPage from './pages/AccountDetailPage'
import AccountsPage from './pages/AccountsPage'
import CaseDetailPage from './pages/CaseDetailPage'
import CasesPage from './pages/CasesPage'
import ContactDetailPage from './pages/ContactDetailPage'
import ContactsPage from './pages/ContactsPage'
import DashboardPage from './pages/DashboardPage'
import LeadDetailPage from './pages/LeadDetailPage'
import LeadsPage from './pages/LeadsPage'
import LoginPage from './pages/LoginPage'
import OpportunitiesPage from './pages/OpportunitiesPage'
import OpportunityDetailPage from './pages/OpportunityDetailPage'
import { useAuthStore } from './stores/authStore'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  return <Layout>{children}</Layout>
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/accounts"
          element={
            <ProtectedRoute>
              <AccountsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/contacts"
          element={
            <ProtectedRoute>
              <ContactsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/leads"
          element={
            <ProtectedRoute>
              <LeadsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/accounts/:id"
          element={
            <ProtectedRoute>
              <AccountDetailPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/contacts/:id"
          element={
            <ProtectedRoute>
              <ContactDetailPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/leads/:id"
          element={
            <ProtectedRoute>
              <LeadDetailPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/opportunities"
          element={
            <ProtectedRoute>
              <OpportunitiesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/opportunities/:id"
          element={
            <ProtectedRoute>
              <OpportunityDetailPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/cases"
          element={
            <ProtectedRoute>
              <CasesPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/cases/:id"
          element={
            <ProtectedRoute>
              <CaseDetailPage />
            </ProtectedRoute>
          }
        />
        {/* Catch-all: redirect unknown paths to dashboard */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
