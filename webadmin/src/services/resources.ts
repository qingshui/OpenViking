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
    const response = await apiClient.post('', {
      method: 'GET',
      path: '/api/v1/fs/ls',
      query: { uri, simple: false, recursive: false, limit }
    })
    return response.data?.data?.result || []
  },

  add: async (path: string, parent: string = 'viking://resources/', reason: string = '') => {
    const response = await apiClient.post('', {
      method: 'POST',
      path: '/api/v1/resources',
      data: { path, parent, reason, wait: true }
    })
    return response.data?.data?.result
  },

  delete: async (uri: string, recursive: boolean = false) => {
    await apiClient.post('', {
      method: 'DELETE',
      path: '/api/v1/fs',
      data: { uri, recursive }
    })
  },

  read: async (uri: string, offset: number = 0, limit: number = -1) => {
    const response = await apiClient.post('', {
      method: 'GET',
      path: '/api/v1/content/read',
      query: { uri, offset, limit }
    })
    return response.data?.data?.result
  },

  getAbstract: async (uri: string) => {
    const response = await apiClient.post('', {
      method: 'GET',
      path: '/api/v1/content/abstract',
      query: { uri }
    })
    return response.data?.data?.result
  },

  getOverview: async (uri: string) => {
    const response = await apiClient.post('', {
      method: 'GET',
      path: '/api/v1/content/overview',
      query: { uri }
    })
    return response.data?.data?.result
  }
}
