import apiClient from './api'

export interface SearchResult {
  uri: string
  context_type: string
  level: number
  abstract: string
  score: number
}

export const searchService = {
  find: async (query: string, limit: number = 10, target_uri?: string) => {
    const response = await apiClient.post('', {
      method: 'POST',
      path: '/api/v1/search/find',
      data: { query, limit, target_uri }
    })
    return response.data?.data?.result?.matched_contexts || []
  },

  search: async (query: string, session_id: string, limit: number = 10) => {
    const response = await apiClient.post('', {
      method: 'POST',
      path: '/api/v1/search/search',
      data: { query, session_id, limit }
    })
    return response.data?.data?.result?.matched_contexts || []
  },

  grep: async (uri: string, pattern: string) => {
    const response = await apiClient.post('', {
      method: 'POST',
      path: '/api/v1/search/grep',
      data: { uri, pattern }
    })
    return response.data?.data?.result
  },

  glob: async (pattern: string, uri: string = 'viking://') => {
    const response = await apiClient.post('', {
      method: 'POST',
      path: '/api/v1/search/glob',
      data: { pattern, uri }
    })
    return response.data?.data?.result
  }
}
