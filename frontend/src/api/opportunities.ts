import apiClient from './client'
import type { Opportunity, OpportunityCreate, OpportunityUpdate, PaginatedResponse, PipelineStage } from './types'

const BASE = '/api/opportunities'

export const opportunitiesApi = {
  list: (params?: {
    offset?: number
    limit?: number
    account_id?: number
    stage?: string
    is_closed?: boolean
  }) => apiClient.get<PaginatedResponse<Opportunity>>(BASE, { params }).then((r) => r.data),

  get: (id: number) => apiClient.get<Opportunity>(`${BASE}/${id}`).then((r) => r.data),

  create: (data: OpportunityCreate) =>
    apiClient.post<Opportunity>(BASE, data).then((r) => r.data),

  update: (id: number, data: OpportunityUpdate) =>
    apiClient.patch<Opportunity>(`${BASE}/${id}`, data).then((r) => r.data),

  delete: (id: number) => apiClient.delete(`${BASE}/${id}`).then((r) => r.data),

  pipeline: () => apiClient.get<PipelineStage[]>(`${BASE}/pipeline`).then((r) => r.data),
}
