import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:1933/api/v1'

export const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('ov_api_key')
  if (token) {
    config.headers['X-API-Key'] = token
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('ov_api_key')
      localStorage.removeItem('ov_username')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient
