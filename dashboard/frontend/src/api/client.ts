import axios from 'axios'
import useAuthStore from '../stores/authStore'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear auth and redirect to login
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient

// API Functions
export const authAPI = {
  login: (username: string, password: string) =>
    apiClient.post('/auth/login', { username, password }),
  
  getMe: () => apiClient.get('/auth/me'),
}

export const suitesAPI = {
  getAll: (skip = 0, limit = 100) => 
    apiClient.get('/suites', { params: { skip, limit } }),
  
  getById: (id: number) => 
    apiClient.get(`/suites/${id}`),
  
  create: (data: any) => 
    apiClient.post('/suites', data),
  
  update: (id: number, data: any) => 
    apiClient.put(`/suites/${id}`, data),
  
  delete: (id: number) => 
    apiClient.delete(`/suites/${id}`),
}

export const casesAPI = {
  getAll: (suiteId?: number, skip = 0, limit = 100) => 
    apiClient.get('/cases', { params: { suite_id: suiteId, skip, limit } }),
  
  getById: (id: number) => 
    apiClient.get(`/cases/${id}`),
  
  create: (data: any) => 
    apiClient.post('/cases', data),
  
  update: (id: number, data: any) => 
    apiClient.put(`/cases/${id}`, data),
  
  delete: (id: number) => 
    apiClient.delete(`/cases/${id}`),
}

export const executionsAPI = {
  getAll: (suiteId?: number, status?: string, skip = 0, limit = 100) => 
    apiClient.get('/executions', { params: { suite_id: suiteId, status, skip, limit } }),
  
  getById: (id: number) => 
    apiClient.get(`/executions/${id}`),
  
  create: (data: any) => 
    apiClient.post('/executions', data),
  
  start: (id: number) => 
    apiClient.post(`/executions/${id}/start`),
  
  stop: (id: number) => 
    apiClient.post(`/executions/${id}/stop`),
}

export const dashboardAPI = {
  getStats: () =>
    apiClient.get('/dashboard/stats'),

  getTrends: (days = 30) =>
    apiClient.get('/dashboard/trends', { params: { days } }),

  getRecentExecutions: (limit = 10) =>
    apiClient.get('/dashboard/recent-executions', { params: { limit } }),
}

export const billingAPI = {
  getPlans: () =>
    apiClient.get('/billing/plans'),

  getSubscription: () =>
    apiClient.get('/billing/subscription'),

  subscribe: (planId: string, paymentMethodId?: string) =>
    apiClient.post('/billing/subscribe', { plan_id: planId, payment_method_id: paymentMethodId }),

  cancel: () =>
    apiClient.post('/billing/cancel'),

  upgrade: (planId: string) =>
    apiClient.post('/billing/upgrade', { plan_id: planId }),

  createCustomer: (email: string, name: string) =>
    apiClient.post('/billing/customer', { email, name }),

  getInvoices: () =>
    apiClient.get('/billing/invoices'),

  getPaymentMethods: () =>
    apiClient.get('/billing/payment-methods'),

  addPaymentMethod: (paymentMethodId: string) =>
    apiClient.post('/billing/payment-methods', { payment_method_id: paymentMethodId }),

  removePaymentMethod: (paymentMethodId: string) =>
    apiClient.delete(`/billing/payment-methods/${paymentMethodId}`),

  setDefaultPaymentMethod: (paymentMethodId: string) =>
    apiClient.put(`/billing/payment-methods/${paymentMethodId}/default`),
}