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
    // Backend returns {memories, resources, skills, total}
    const result = response.data?.result || {}
    // Combine all sources into a single array
    return [
      ...(result.resources || []),
      ...(result.memories || []),
      ...(result.skills || [])
    ]
  },

  search: async (query: string, session_id: string, limit: number = 10) => {
    const response = await apiClient.post('', {
      method: 'POST',
      path: '/api/v1/search/search',
      data: { query, session_id, limit }
    })
    // Backend returns {memories, resources, skills, total}
    const result = response.data?.result || {}
    return [
      ...(result.resources || []),
      ...(result.memories || []),
      ...(result.skills || [])
    ]
  },

  grep: async (uri: string, pattern: string) => {
    console.log('Calling grep API:', { uri, pattern })
    const response = await apiClient.post('', {
      method: 'POST',
      path: '/api/v1/search/grep',
      data: { uri, pattern }
    })
    console.log('Grep API response:', response.data)
    // Backend returns {matches: [...]}
    const result = response.data?.result || {}
    return result.matches || []
  },

  glob: async (pattern: string, uri: string = 'viking://') => {
    const response = await apiClient.post('', {
      method: 'POST',
      path: '/api/v1/search/glob',
      data: { pattern, uri }
    })
    return response.data?.result
  }
}
