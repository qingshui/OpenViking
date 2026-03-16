import apiClient from './api'

export interface FileNode {
  uri: string
  name: string
  type: 'file' | 'directory'
  children?: FileNode[]
}

export const filesystemService = {
  list: async (uri: string, recursive: boolean = false) => {
    const response = await apiClient.get('/fs/ls', {
      params: { uri, recursive }
    })
    return response.data?.result || []
  },

  tree: async (uri: string = 'viking://', level_limit: number = 3) => {
    const response = await apiClient.get('/fs/tree', {
      params: { uri, level_limit }
    })
    return response.data?.result
  },

  stat: async (uri: string) => {
    const response = await apiClient.get('/fs/stat', {
      params: { uri }
    })
    return response.data?.result
  },

  mkdir: async (uri: string) => {
    const response = await apiClient.post('/fs/mkdir', { uri })
    return response.data?.result
  },

  mv: async (from_uri: string, to_uri: string) => {
    const response = await apiClient.post('/fs/mv', {
      from_uri,
      to_uri
    })
    return response.data?.result
  }
}
