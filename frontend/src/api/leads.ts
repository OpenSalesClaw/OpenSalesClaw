import apiClient from './client'
import type { Lead, LeadCreate, LeadUpdate, PaginatedResponse } from './types'

const BASE = '/api/leads'

export const leadsApi = {
  list: (params?: { offset?: number; limit?: number; status?: string; is_converted?: boolean }) =>
    apiClient.get<PaginatedResponse<Lead>>(BASE, { params }).then((r) => r.data),

  get: (id: number) => apiClient.get<Lead>(`${BASE}/${id}`).then((r) => r.data),

  create: (data: LeadCreate) => apiClient.post<Lead>(BASE, data).then((r) => r.data),

  update: (id: number, data: LeadUpdate) =>
    apiClient.patch<Lead>(`${BASE}/${id}`, data).then((r) => r.data),

  delete: (id: number) => apiClient.delete(`${BASE}/${id}`).then((r) => r.data),
}
