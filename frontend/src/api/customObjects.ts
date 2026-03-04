import apiClient from './client'
import type {
  CustomObject,
  CustomObjectCreate,
  CustomObjectRecord,
  CustomObjectRecordCreate,
  CustomObjectRecordUpdate,
  CustomObjectUpdate,
  PaginatedResponse,
} from './types'

const BASE = '/api/custom-objects'

export const customObjectsApi = {
  list: (params?: { offset?: number; limit?: number; is_active?: boolean; label?: string }) =>
    apiClient.get<PaginatedResponse<CustomObject>>(BASE, { params }).then((r) => r.data),

  get: (apiName: string) => apiClient.get<CustomObject>(`${BASE}/${apiName}`).then((r) => r.data),

  create: (data: CustomObjectCreate) => apiClient.post<CustomObject>(BASE, data).then((r) => r.data),

  update: (apiName: string, data: CustomObjectUpdate) =>
    apiClient.patch<CustomObject>(`${BASE}/${apiName}`, data).then((r) => r.data),

  delete: (apiName: string) => apiClient.delete(`${BASE}/${apiName}`).then((r) => r.data),

  // Records
  listRecords: (apiName: string, params?: { offset?: number; limit?: number; name?: string }) =>
    apiClient
      .get<PaginatedResponse<CustomObjectRecord>>(`${BASE}/${apiName}/records`, { params })
      .then((r) => r.data),

  getRecord: (apiName: string, recordId: number) =>
    apiClient.get<CustomObjectRecord>(`${BASE}/${apiName}/records/${recordId}`).then((r) => r.data),

  createRecord: (apiName: string, data: CustomObjectRecordCreate) =>
    apiClient.post<CustomObjectRecord>(`${BASE}/${apiName}/records`, data).then((r) => r.data),

  updateRecord: (apiName: string, recordId: number, data: CustomObjectRecordUpdate) =>
    apiClient.patch<CustomObjectRecord>(`${BASE}/${apiName}/records/${recordId}`, data).then((r) => r.data),

  deleteRecord: (apiName: string, recordId: number) =>
    apiClient.delete(`${BASE}/${apiName}/records/${recordId}`).then((r) => r.data),
}
