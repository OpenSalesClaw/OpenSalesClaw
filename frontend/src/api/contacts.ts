import apiClient from './client'
import type { Contact, ContactCreate, ContactUpdate, PaginatedResponse } from './types'

const BASE = '/api/contacts'

export const contactsApi = {
  list: (params?: { offset?: number; limit?: number; account_id?: number; email?: string }) =>
    apiClient.get<PaginatedResponse<Contact>>(BASE, { params }).then((r) => r.data),

  get: (id: number) => apiClient.get<Contact>(`${BASE}/${id}`).then((r) => r.data),

  create: (data: ContactCreate) => apiClient.post<Contact>(BASE, data).then((r) => r.data),

  update: (id: number, data: ContactUpdate) =>
    apiClient.patch<Contact>(`${BASE}/${id}`, data).then((r) => r.data),

  delete: (id: number) => apiClient.delete(`${BASE}/${id}`).then((r) => r.data),
}
