import apiClient from './api'

export interface FileNode {
  uri: string
  name: string
  type: 'file' | 'directory'
  children?: FileNode[]
}

export const filesystemService = {
  list: async (uri: string, recursive: boolean = false) => {
    const response = await apiClient.post('', {
      method: 'GET',
      path: '/api/v1/fs/ls',
      query: { uri, recursive }
    })
    return response.data?.data?.result || []
  },

  tree: async (uri: string = 'viking://', level_limit: number = 3) => {
    const response = await apiClient.post('', {
      method: 'GET',
      path: '/api/v1/fs/tree',
      query: { uri, level_limit }
    })
    return response.data?.data?.result
  },

  stat: async (uri: string) => {
    const response = await apiClient.post('', {
      method: 'GET',
      path: '/api/v1/fs/stat',
      query: { uri }
    })
    return response.data?.data?.result
  },

  mkdir: async (uri: string) => {
    const response = await apiClient.post('', {
      method: 'POST',
      path: '/api/v1/fs/mkdir',
      data: { uri }
    })
    return response.data?.data?.result
  },

  mv: async (from_uri: string, to_uri: string) => {
    const response = await apiClient.post('', {
      method: 'POST',
      path: '/api/v1/fs/mv',
      data: { from_uri, to_uri }
    })
    return response.data?.data?.result
  }
}
