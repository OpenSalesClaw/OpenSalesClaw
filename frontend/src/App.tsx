import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import AdminLayout from './components/AdminLayout'
import AdminRoute from './components/AdminRoute'
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
import AdminRoleCreatePage from './pages/admin/AdminRoleCreatePage'
import AdminRoleDetailPage from './pages/admin/AdminRoleDetailPage'
import AdminRolesPage from './pages/admin/AdminRolesPage'
import AdminUserCreatePage from './pages/admin/AdminUserCreatePage'
import AdminUserDetailPage from './pages/admin/AdminUserDetailPage'
import AdminUsersPage from './pages/admin/AdminUsersPage'
import { useAuthStore } from './stores/authStore'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  return <Layout>{children}</Layout>
}

function AdminPageRoute({ children }: { children: React.ReactNode }) {
  return (
    <AdminRoute>
      <AdminLayout>{children}</AdminLayout>
    </AdminRoute>
  )
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
        {/* Admin routes */}
        <Route path="/admin" element={<Navigate to="/admin/users" replace />} />
        <Route
          path="/admin/users"
          element={
            <AdminPageRoute>
              <AdminUsersPage />
            </AdminPageRoute>
          }
        />
        <Route
          path="/admin/users/new"
          element={
            <AdminPageRoute>
              <AdminUserCreatePage />
            </AdminPageRoute>
          }
        />
        <Route
          path="/admin/users/:id"
          element={
            <AdminPageRoute>
              <AdminUserDetailPage />
            </AdminPageRoute>
          }
        />
        <Route
          path="/admin/roles"
          element={
            <AdminPageRoute>
              <AdminRolesPage />
            </AdminPageRoute>
          }
        />
        <Route
          path="/admin/roles/new"
          element={
            <AdminPageRoute>
              <AdminRoleCreatePage />
            </AdminPageRoute>
          }
        />
        <Route
          path="/admin/roles/:id"
          element={
            <AdminPageRoute>
              <AdminRoleDetailPage />
            </AdminPageRoute>
          }
        />
        {/* Catch-all: redirect unknown paths to dashboard */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
