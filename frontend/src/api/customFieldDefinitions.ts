import apiClient from './client'
import type {
  CustomFieldDefinition,
  CustomFieldDefinitionCreate,
  CustomFieldDefinitionUpdate,
  PaginatedResponse,
} from './types'

const BASE = '/api/custom-field-definitions'

export const customFieldDefinitionsApi = {
  list: (params?: { offset?: number; limit?: number; object_name?: string }) =>
    apiClient.get<PaginatedResponse<CustomFieldDefinition>>(BASE, { params }).then((r) => r.data),

  get: (id: number) => apiClient.get<CustomFieldDefinition>(`${BASE}/${id}`).then((r) => r.data),

  create: (data: CustomFieldDefinitionCreate) =>
    apiClient.post<CustomFieldDefinition>(BASE, data).then((r) => r.data),

  update: (id: number, data: CustomFieldDefinitionUpdate) =>
    apiClient.patch<CustomFieldDefinition>(`${BASE}/${id}`, data).then((r) => r.data),

  delete: (id: number) => apiClient.delete(`${BASE}/${id}`).then((r) => r.data),
}

/** Convenience function to list all definitions for a given object name. */
export function listCustomFieldDefinitions(params?: { offset?: number; limit?: number; object_name?: string }) {
  return customFieldDefinitionsApi.list(params)
}

export function getCustomFieldDefinition(id: number) {
  return customFieldDefinitionsApi.get(id)
}

export function createCustomFieldDefinition(data: CustomFieldDefinitionCreate) {
  return customFieldDefinitionsApi.create(data)
}

export function updateCustomFieldDefinition(id: number, data: CustomFieldDefinitionUpdate) {
  return customFieldDefinitionsApi.update(id, data)
}

export function deleteCustomFieldDefinition(id: number) {
  return customFieldDefinitionsApi.delete(id)
}
