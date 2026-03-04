import apiClient from './client'
import type { AdminUserCreate, PaginatedResponse, PasswordReset, User, UserList, UserUpdate } from './types'

interface ListUsersParams {
  offset?: number
  limit?: number
  email?: string
  is_active?: boolean
  role_id?: number
}

export async function listUsers(params?: ListUsersParams): Promise<PaginatedResponse<UserList>> {
  const { data } = await apiClient.get<PaginatedResponse<UserList>>('/api/users', { params })
  return data
}

export async function getUser(id: number): Promise<User> {
  const { data } = await apiClient.get<User>(`/api/users/${id}`)
  return data
}

export async function createUser(payload: AdminUserCreate): Promise<User> {
  const { data } = await apiClient.post<User>('/api/users', payload)
  return data
}

export async function updateUser(id: number, payload: UserUpdate): Promise<User> {
  const { data } = await apiClient.patch<User>(`/api/users/${id}`, payload)
  return data
}

export async function resetUserPassword(id: number, payload: PasswordReset): Promise<User> {
  const { data } = await apiClient.patch<User>(`/api/users/${id}/reset-password`, payload)
  return data
}

export async function deleteUser(id: number): Promise<void> {
  await apiClient.delete(`/api/users/${id}`)
}
