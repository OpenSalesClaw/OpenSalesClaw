import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import apiClient from '../api/client'

export interface AuthUser {
  id: number
  email: string
  first_name: string | null
  last_name: string | null
  is_active: boolean
  is_superuser: boolean
}

interface AuthState {
  token: string | null
  user: AuthUser | null
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  fetchCurrentUser: () => Promise<void>
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      isAuthenticated: false,

      login: async (email: string, password: string) => {
        const params = new URLSearchParams()
        params.append('username', email)
        params.append('password', password)

        const { data } = await apiClient.post<{ access_token: string; token_type: string }>(
          '/api/auth/login',
          params,
          { headers: { 'Content-Type': 'application/x-www-form-urlencoded' } },
        )

        localStorage.setItem('access_token', data.access_token)
        set({ token: data.access_token, isAuthenticated: true })

        // Fetch and store the authenticated user's profile
        await get().fetchCurrentUser()
      },

      logout: () => {
        localStorage.removeItem('access_token')
        set({ token: null, user: null, isAuthenticated: false })
      },

      fetchCurrentUser: async () => {
        const { data } = await apiClient.get<AuthUser>('/api/auth/me')
        set({ user: data })
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ token: state.token, user: state.user, isAuthenticated: state.isAuthenticated }),
      onRehydrateStorage: () => (state) => {
        if (state?.token) {
          localStorage.setItem('access_token', state.token)
        }
      },
    },
  ),
)
