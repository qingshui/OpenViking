import axios from 'axios'

// Backend service API base URL
const BACKEND_API_BASE = window.location.origin

export const apiClient = axios.create({
  baseURL: `${BACKEND_API_BASE}/api/proxy`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add API key header for proxy requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('ov_api_key')
  if (token) {
    // Add the API key to the request body for proxy
    if (config.data && typeof config.data === 'object') {
      config.data.headers = {
        'X-API-Key': token,
        ...config.data.headers
      }
    }
  }
  return config
})

// Handle 401 errors
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
