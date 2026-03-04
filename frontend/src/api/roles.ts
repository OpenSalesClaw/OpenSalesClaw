import apiClient from './client'
import type { PaginatedResponse, Role, RoleCreate, RoleList, RoleUpdate } from './types'

export interface RoleHierarchyItem {
  id: number
  name: string
  parent_role_id: number | null
  description: string | null
}

interface ListRolesParams {
  offset?: number
  limit?: number
}

export async function listRoles(params?: ListRolesParams): Promise<PaginatedResponse<RoleList>> {
  const { data } = await apiClient.get<PaginatedResponse<RoleList>>('/api/roles', { params })
  return data
}

export async function getRoleHierarchy(): Promise<RoleHierarchyItem[]> {
  const { data } = await apiClient.get<RoleHierarchyItem[]>('/api/roles/hierarchy')
  return data
}

export async function getRole(id: number): Promise<Role> {
  const { data } = await apiClient.get<Role>(`/api/roles/${id}`)
  return data
}

export async function createRole(payload: RoleCreate): Promise<Role> {
  const { data } = await apiClient.post<Role>('/api/roles', payload)
  return data
}

export async function updateRole(id: number, payload: RoleUpdate): Promise<Role> {
  const { data } = await apiClient.patch<Role>(`/api/roles/${id}`, payload)
  return data
}

export async function deleteRole(id: number): Promise<void> {
  await apiClient.delete(`/api/roles/${id}`)
}
