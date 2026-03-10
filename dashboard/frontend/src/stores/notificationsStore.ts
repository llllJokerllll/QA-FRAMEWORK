import { create } from 'zustand'
import { notificationsAPI, Notification } from '../api/notifications'

interface NotificationsState {
  notifications: Notification[]
  unreadCount: number
  isLoading: boolean
  error: string | null
  lastFetched: Date | null

  // Actions
  fetchNotifications: (unreadOnly?: boolean) => Promise<void>
  markAsRead: (id: string) => Promise<void>
  markAllAsRead: () => Promise<void>
  deleteNotification: (id: string) => Promise<void>
  addNotification: (notification: Notification) => void
  clearError: () => void
}

const useNotificationsStore = create<NotificationsState>((set, get) => ({
  notifications: [],
  unreadCount: 0,
  isLoading: false,
  error: null,
  lastFetched: null,

  fetchNotifications: async (unreadOnly = false) => {
    set({ isLoading: true, error: null })
    try {
      const response = await notificationsAPI.getAll({ unread_only: unreadOnly })
      set({
        notifications: response.data.notifications,
        unreadCount: response.data.unread_count,
        isLoading: false,
        lastFetched: new Date(),
      })
    } catch (error: any) {
      set({
        error: error.response?.data?.detail || 'Failed to fetch notifications',
        isLoading: false,
      })
    }
  },

  markAsRead: async (id: string) => {
    try {
      await notificationsAPI.markAsRead(id)
      set((state) => {
        const notification = state.notifications.find((n) => n.id === id)
        const wasUnread = notification && !notification.read
        return {
          notifications: state.notifications.map((n) =>
            n.id === id ? { ...n, read: true } : n
          ),
          unreadCount: wasUnread ? Math.max(0, state.unreadCount - 1) : state.unreadCount,
        }
      })
    } catch (error: any) {
      set({ error: error.response?.data?.detail || 'Failed to mark notification as read' })
      throw error
    }
  },

  markAllAsRead: async () => {
    try {
      const response = await notificationsAPI.markAllAsRead()
      set((state) => ({
        notifications: state.notifications.map((n) => ({ ...n, read: true })),
        unreadCount: 0,
      }))
    } catch (error: any) {
      set({ error: error.response?.data?.detail || 'Failed to mark all notifications as read' })
      throw error
    }
  },

  deleteNotification: async (id: string) => {
    try {
      await notificationsAPI.delete(id)
      set((state) => {
        const notification = state.notifications.find((n) => n.id === id)
        const wasUnread = notification && !notification.read
        return {
          notifications: state.notifications.filter((n) => n.id !== id),
          unreadCount: wasUnread ? Math.max(0, state.unreadCount - 1) : state.unreadCount,
        }
      })
    } catch (error: any) {
      set({ error: error.response?.data?.detail || 'Failed to delete notification' })
      throw error
    }
  },

  addNotification: (notification: Notification) => {
    set((state) => ({
      notifications: [notification, ...state.notifications],
      unreadCount: notification.read ? state.unreadCount : state.unreadCount + 1,
    }))
  },

  clearError: () => set({ error: null }),
}))

export default useNotificationsStore
