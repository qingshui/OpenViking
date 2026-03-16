import apiClient from './api'

export interface ResourceInfo {
  uri: string
  name: string
  type: string
  size: number
  created_at: string
  updated_at: string
}

export const resourceService = {
  list: async (uri: string = 'viking://resources/', limit: number = 50) => {
    const response = await apiClient.get('/fs/ls', {
      params: { uri, simple: false, recursive: false, limit }
    })
    return response.data?.result || []
  },

  add: async (path: string, parent: string = 'viking://resources/', reason: string = '') => {
    const response = await apiClient.post('/resources', {
      path,
      parent,
      reason,
      wait: true
    })
    return response.data?.result
  },

  delete: async (uri: string, recursive: boolean = false) => {
    await apiClient.delete('/fs', {
      params: { uri, recursive }
    })
  },

  read: async (uri: string, offset: number = 0, limit: number = -1) => {
    const response = await apiClient.get('/content/read', {
      params: { uri, offset, limit }
    })
    return response.data?.result
  },

  getAbstract: async (uri: string) => {
    const response = await apiClient.get('/content/abstract', {
      params: { uri }
    })
    return response.data?.result
  },

  getOverview: async (uri: string) => {
    const response = await apiClient.get('/content/overview', {
      params: { uri }
    })
    return response.data?.result
  }
}
