const express = require('express')
const cors = require('cors')
const axios = require('axios')

const app = express()
const PORT = process.env.PORT || 3000

// Middleware
app.use(cors())
app.use(express.json())

// Request logging middleware
app.use((req, res, next) => {
  console.log(`[${new Date().toISOString()}] ${req.method} ${req.path}`)
  next()
})

// Configuration storage (in-memory, could be persisted to file or database)
let config = {
  host: 'localhost',
  port: 1933,
  workers: 1,
  root_api_key: '',
  cors_origins: ['*'],
  with_bot: false,
  bot_api_url: 'http://localhost:18790',
}

// API client for calling OpenViking server
const getApiBaseUrl = () => `http://${config.host}:${config.port}/api/v1`

// Routes
app.get('/api/config', async (req, res) => {
  try {
    res.json({
      success: true,
      config: config
    })
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

app.put('/api/config', async (req, res) => {
  try {
    const updates = req.body
    config = { ...config, ...updates }
    res.json({
      success: true,
      config: config
    })
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    })
  }
})

app.post('/api/proxy', async (req, res) => {
  try {
    const { method, path, data, query, headers } = req.body
    console.log(`Proxying ${method} ${path} with data:`, data)
    // path already includes /api/v1 prefix, use directly
    let url = `http://${config.host}:${config.port}${path}`

    // Add query parameters if provided
    if (query && Object.keys(query).length > 0) {
      const queryString = new URLSearchParams(query).toString()
      url += '?' + queryString
    }

    console.log(`Full URL: ${url}`)

    // Build headers with API key from config
    const requestHeaders = {
      'Content-Type': 'application/json',
      ...headers
    }

    // Add API key from config if configured
    if (config.root_api_key) {
      requestHeaders['X-API-Key'] = config.root_api_key
    }

    const response = await axios({
      method: method,
      url: url,
      data: data,
      headers: requestHeaders
    })

    res.json({
      success: true,
      data: response.data
    })
  } catch (error) {
    console.error('Proxy error:', error.message)
    console.error('Error response:', error.response?.data)
    res.status(error.response?.status || 500).json({
      success: false,
      error: error.message,
      data: error.response?.data
    })
  }
})

app.get('/api/health', async (req, res) => {
  try {
    const response = await axios.get(`http://${config.host}:${config.port}/health`, {
      timeout: 5000
    })
    res.json({
      success: true,
      message: 'Server is healthy',
      serverUrl: `http://${config.host}:${config.port}`
    })
  } catch (error) {
    res.json({
      success: false,
      message: error.message
    })
  }
})

app.listen(PORT, '0.0.0.0', () => {
  console.log(`Webadmin backend server running on port ${PORT}`)
  console.log(`API Proxy configured for: http://${config.host}:${config.port}`)
})
