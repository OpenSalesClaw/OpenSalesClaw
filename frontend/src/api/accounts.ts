import apiClient from './client'
import type { Account, AccountCreate, AccountUpdate, PaginatedResponse } from './types'

const BASE = '/api/accounts'

export const accountsApi = {
  list: (params?: { offset?: number; limit?: number; name?: string; type?: string }) =>
    apiClient.get<PaginatedResponse<Account>>(BASE, { params }).then((r) => r.data),

  get: (id: number) => apiClient.get<Account>(`${BASE}/${id}`).then((r) => r.data),

  create: (data: AccountCreate) => apiClient.post<Account>(BASE, data).then((r) => r.data),

  update: (id: number, data: AccountUpdate) =>
    apiClient.patch<Account>(`${BASE}/${id}`, data).then((r) => r.data),

  delete: (id: number) => apiClient.delete(`${BASE}/${id}`).then((r) => r.data),
}
