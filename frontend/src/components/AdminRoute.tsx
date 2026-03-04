import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

/**
 * Route guard for admin-only pages.
 * - Unauthenticated → redirect to /login
 * - Authenticated but not superuser → redirect to /
 * - Superuser → render children as-is (AdminLayout is applied outside)
 */
export default function AdminRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, user } = useAuthStore()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }
  if (!user?.is_superuser) {
    return <Navigate to="/" replace />
  }
  return <>{children}</>
}
