import apiClient from './client'

export interface Notification {
  id: string
  type: 'test_completed' | 'test_failed' | 'suite_created' | 'billing' | 'system'
  title: string
  message: string
  data?: Record<string, any>
  read: boolean
  created_at: string
}

export interface NotificationsResponse {
  notifications: Notification[]
  total: number
  unread_count: number
}

export interface NotificationMarkReadResponse {
  success: boolean
}

export interface NotificationMarkAllReadResponse {
  updated_count: number
}

export const notificationsAPI = {
  /**
   * Get all notifications for current user
   */
  getAll: (params?: {
    unread_only?: boolean
    limit?: number
    offset?: number
  }) => apiClient.get<NotificationsResponse>('/notifications', { params }),

  /**
   * Mark a notification as read
   */
  markAsRead: (id: string) =>
    apiClient.post<NotificationMarkReadResponse>(`/notifications/${id}/read`),

  /**
   * Mark all notifications as read
   */
  markAllAsRead: () =>
    apiClient.post<NotificationMarkAllReadResponse>('/notifications/read-all'),

  /**
   * Delete a notification
   */
  delete: (id: string) =>
    apiClient.delete<{ success: boolean }>(`/notifications/${id}`),
}

export default notificationsAPI
