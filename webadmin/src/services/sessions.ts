import apiClient from './api'

export const sessionService = {
  create: async () => {
    const response = await apiClient.post('/sessions')
    return response.data?.result
  },

  list: async () => {
    const response = await apiClient.get('/sessions')
    return response.data?.result || []
  },

  get: async (session_id: string) => {
    const response = await apiClient.get(`/sessions/${session_id}`)
    return response.data?.result
  },

  addMessage: async (session_id: string, role: string, content: string) => {
    const response = await apiClient.post(`/sessions/${session_id}/messages`, {
      role,
      content
    })
    return response.data?.result
  },

  commit: async (session_id: string, wait: boolean = true) => {
    const response = await apiClient.post(`/sessions/${session_id}/commit`, null, {
      params: { wait }
    })
    return response.data?.result
  },

  delete: async (session_id: string) => {
    await apiClient.delete(`/sessions/${session_id}`)
  }
}
