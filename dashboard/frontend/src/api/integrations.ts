import apiClient from './client'

export interface Provider {
  id: string
  name: string
  description: string
  icon: string
  status: 'connected' | 'disconnected' | 'error'
  config?: any
}

export interface IntegrationConfig {
  enabled: boolean
  api_key?: string
  api_url?: string
  project_id?: string
  organization?: string
  // Additional provider-specific fields
  [key: string]: any
}

export interface SyncResponse {
  success: boolean
  message: string
  test_ids: number[]
  synced_count: number
  failed_count: number
}

export const integrationsAPI = {
  getProviders: () =>
    apiClient.get<Provider[]>('/integrations/providers'),

  configure: (provider: string, config: IntegrationConfig) =>
    apiClient.post(`/integrations/configure`, { provider, config }),

  sync: (testIds: number[], providers: string[]) =>
    apiClient.post<SyncResponse>('/integrations/sync', {
      test_ids: testIds,
      providers,
    }),

  health: (integrationId: string) =>
    apiClient.get(`/integrations/health/${integrationId}`),

  delete: (integrationId: string) =>
    apiClient.delete(`/integrations/${integrationId}`),

  testConnection: (integrationId: string) =>
    apiClient.post(`/integrations/${integrationId}/test`),
}
