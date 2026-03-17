import apiClient from './api'

export const sessionService = {
  create: async () => {
    const response = await apiClient.post('', {
      method: 'POST',
      path: '/api/v1/sessions'
    })
    return response.data?.result
  },

  list: async () => {
    const response = await apiClient.post('', {
      method: 'GET',
      path: '/api/v1/sessions'
    })
    return response.data?.result || []
  },

  get: async (session_id: string) => {
    const response = await apiClient.post('', {
      method: 'GET',
      path: `/api/v1/sessions/${session_id}`
    })
    return response.data?.result
  },

  addMessage: async (session_id: string, role: string, content: string) => {
    const response = await apiClient.post('', {
      method: 'POST',
      path: `/api/v1/sessions/${session_id}/messages`,
      data: { role, content }
    })
    return response.data?.result
  },

  commit: async (session_id: string, wait: boolean = true) => {
    const response = await apiClient.post('', {
      method: 'POST',
      path: `/api/v1/sessions/${session_id}/commit`,
      data: { wait }
    })
    return response.data?.result
  },

  delete: async (session_id: string) => {
    await apiClient.post('', {
      method: 'DELETE',
      path: `/api/v1/sessions/${session_id}`
    })
  }
}
