import apiClient from './client'
import type { Case, CaseCreate, CaseUpdate, PaginatedResponse } from './types'

const BASE = '/api/cases'

export const casesApi = {
  list: (params?: {
    offset?: number
    limit?: number
    account_id?: number
    status?: string
    priority?: string
  }) => apiClient.get<PaginatedResponse<Case>>(BASE, { params }).then((r) => r.data),

  get: (id: number) => apiClient.get<Case>(`${BASE}/${id}`).then((r) => r.data),

  create: (data: CaseCreate) => apiClient.post<Case>(BASE, data).then((r) => r.data),

  update: (id: number, data: CaseUpdate) =>
    apiClient.patch<Case>(`${BASE}/${id}`, data).then((r) => r.data),

  delete: (id: number) => apiClient.delete(`${BASE}/${id}`).then((r) => r.data),
}
