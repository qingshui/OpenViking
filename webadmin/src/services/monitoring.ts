import apiClient, { handleAPI, APIResponse } from './api'

// Monitoring data types
export interface SystemStatus {
  status: 'healthy' | 'warning' | 'error'
  message?: string
  uptime?: number
  last_check?: string
}

// Backend system response format (from /observer/system)
export interface BackendSystemResponse {
  is_healthy: boolean
  errors: string[]
  components: Record<string, {
    name: string
    is_healthy: boolean
    has_errors: boolean
    status: string
  }>
}

export interface QueueInfo {
  queue_name: string
  queue_length: number
  processing: boolean
  last_updated?: string
}

export interface QueueStats {
  embedding_queue?: QueueInfo
  semantic_queue?: QueueInfo
  other_queues?: Record<string, QueueInfo>
  [key: string]: any
}

export interface ResourceStats {
  total_resources: number
  total_size: number
  by_type?: Record<string, number>
  by_directory?: Record<string, number>
  recent_additions?: number
  [key: string]: any
}

export interface VikingDBCollection {
  collection: string
  index_count: number
  vector_count: number
  status: string
}

export interface VikingDBStatus {
  collections: number
  total_vectors: number
  storage_used: number
  collection_list?: VikingDBCollection[]
  query_performance?: {
    avg_latency_ms?: number
    queries_per_second?: number
  }
  [key: string]: any
}

export interface VLMModel {
  model: string
  provider: string
  prompt_tokens: number
  completion_tokens: number
  total_tokens: number
  last_updated: string
}

export interface VLMStats {
  provider: string
  model: string
  models?: VLMModel[]
  token_usage?: {
    total_tokens?: number
    prompt_tokens?: number
    completion_tokens?: number
  }
  request_count?: number
  avg_response_time_ms?: number
  [key: string]: any
}

export interface SystemInfo {
  cpu_usage?: number
  memory_usage?: number
  disk_usage?: number
  active_sessions?: number
  active_tasks?: number
}

export interface MonitoringSummary {
  system: SystemStatus
  queue: QueueStats
  resources: ResourceStats
  vikingdb: VikingDBStatus
  vlm: VLMStats
  systemInfo: SystemInfo
  last_updated: string
  [key: string]: any
}

// Backend queue response format
export interface BackendQueueResponse {
  name: string
  is_healthy: boolean
  has_errors: boolean
  status: string
  queues: {
    embedding: {
      pending: number
      in_progress: number
      processed: number
      error_count: number
    }
    semantic: {
      pending: number
      in_progress: number
      processed: number
      error_count: number
    }
  }
  services: Record<string, any>
}

// Normalize backend queue response
const normalizeQueueStats = (backend: BackendQueueResponse): QueueStats => ({
  embedding_queue: {
    queue_name: 'embedding',
    queue_length: backend.queues.embedding.pending,
    processing: backend.queues.embedding.in_progress > 0,
    last_updated: new Date().toISOString()
  },
  semantic_queue: {
    queue_name: 'semantic',
    queue_length: backend.queues.semantic.pending,
    processing: backend.queues.semantic.in_progress > 0,
    last_updated: new Date().toISOString()
  }
})

// Backend VikingDB response format
export interface BackendVikingDBResponse {
  name: string
  is_healthy: boolean
  has_errors: boolean
  status: string
}

// Parse ASCII table from VikingDB status
const parseVikingDBTable = (table: string): VikingDBCollection[] => {
  const lines = table.trim().split('\n')
  if (lines.length < 4) {
    return []
  }

  // Find header line (the one with column names)
  let headerLine = -1
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('| Collection |') || lines[i].includes('|Collection|')) {
      headerLine = i
      break
    }
  }

  if (headerLine === -1 || headerLine + 2 >= lines.length) {
    return []
  }

  const results: VikingDBCollection[] = []

  // Start from line after separator (headerLine + 2) and parse until next separator or end
  for (let i = headerLine + 2; i < lines.length; i++) {
    const line = lines[i]
    // Stop if we hit a separator line (starts with +---)
    if (line.trim().startsWith('+') && line.includes('-')) {
      continue
    }

    const columns = line.split('|').map(col => col.trim()).filter(col => col !== '')

    // Expected columns: Collection, Index Count, Vector Count, Status
    if (columns.length >= 4) {
      // Skip TOTAL row
      if (columns[0] === 'TOTAL' || columns[0].toUpperCase() === 'TOTAL') {
        continue
      }

      results.push({
        collection: columns[0],
        index_count: parseInt(columns[1]) || 0,
        vector_count: parseInt(columns[2]) || 0,
        status: columns[3] || 'Unknown'
      })
    }
  }

  return results
}

// Normalize backend VikingDB response
const normalizeVikingDBStatus = (backend: BackendVikingDBResponse): VikingDBStatus => {
  // Try to parse the ASCII table
  const parsedCollections = parseVikingDBTable(backend.status)

  if (parsedCollections.length > 0) {
    // Calculate totals across all collections
    let totalIndexCount = 0
    let totalVectorCount = 0

    for (const col of parsedCollections) {
      totalIndexCount += col.index_count
      totalVectorCount += col.vector_count
    }

    return {
      collections: parsedCollections.length,
      total_vectors: totalVectorCount,
      storage_used: 0,
      collection_list: parsedCollections,
      query_performance: {}
    }
  }

  // Fallback to simple parsing if table parsing fails
  const lines = backend.status.split('\n')
  const dataLine = lines.find(l => l.includes('|  context  |')) || lines.find(l => l.includes('| context |'))

  if (dataLine) {
    const parts = dataLine.split('|').map(s => s.trim()).filter(s => s)
    if (parts.length >= 3) {
      return {
        collections: 1,
        total_vectors: parseInt(parts[2]) || 0,
        storage_used: 0,
        collection_list: [],
        query_performance: {}
      }
    }
  }

  return {
    collections: 0,
    total_vectors: 0,
    storage_used: 0,
    collection_list: [],
    query_performance: {}
  }
}

// Backend VLM response format
export interface BackendVLMResponse {
  name: string
  is_healthy: boolean
  has_errors: boolean
  status: string
}

// Parse ASCII table from VLM status
const parseVLMTable = (table: string): any[] => {
  const lines = table.trim().split('\n')
  if (lines.length < 4) {
    return []
  }

  // Find header line (the one with column names)
  let headerLine = -1
  for (let i = 0; i < lines.length; i++) {
    if (lines[i].includes('|    Model    |') || lines[i].includes('| Model |')) {
      headerLine = i
      break
    }
  }

  if (headerLine === -1 || headerLine + 2 >= lines.length) {
    return []
  }

  const results = []

  // Start from line after separator (headerLine + 2) and parse until next separator or end
  for (let i = headerLine + 2; i < lines.length; i++) {
    const line = lines[i]
    // Stop if we hit a separator line (starts with +---)
    if (line.trim().startsWith('+') && line.includes('-')) {
      continue
    }

    const columns = line.split('|').map(col => col.trim()).filter(col => col !== '')

    // Expected columns: Model, Provider, Prompt, Completion, Total, Last Updated
    if (columns.length >= 6) {
      // Skip TOTAL row
      if (columns[0] === 'TOTAL' || columns[0].toUpperCase() === 'TOTAL') {
        continue
      }

      results.push({
        model: columns[0],
        provider: columns[1],
        prompt_tokens: parseInt(columns[2]) || 0,
        completion_tokens: parseInt(columns[3]) || 0,
        total_tokens: parseInt(columns[4]) || 0,
        last_updated: columns[5]
      })
    }
  }

  return results
}

// Normalize backend VLM response
const normalizeVLMStats = (backend: BackendVLMResponse): VLMStats => {
  // Check for empty or error status
  if (!backend.status || backend.status.includes('No token usage data available.')) {
    return {
      provider: 'OpenAI',
      model: 'gpt-4o',
      token_usage: { total_tokens: 0 },
      request_count: 0
    }
  }

  // Try to parse the ASCII table
  const parsedModels = parseVLMTable(backend.status)

  if (parsedModels.length > 0) {
    // Use the first model for display (backward compatibility)
    const firstModel = parsedModels[0]

    // Calculate totals across all models
    let totalPromptTokens = 0
    let totalCompletionTokens = 0
    let totalAllTokens = 0

    for (const model of parsedModels) {
      totalPromptTokens += model.prompt_tokens
      totalCompletionTokens += model.completion_tokens
      totalAllTokens += model.total_tokens
    }

    return {
      provider: firstModel.provider,
      model: firstModel.model,
      models: parsedModels, // Include all models for table display
      token_usage: {
        prompt_tokens: totalPromptTokens,
        completion_tokens: totalCompletionTokens,
        total_tokens: totalAllTokens
      },
      request_count: parsedModels.length, // Use model count as request count approximation
      avg_response_time_ms: undefined
    }
  }

  // Fallback to simple parsing if table parsing fails
  // Try to extract model and provider from status string
  let model = 'Unknown'
  let provider = 'Unknown'
  let totalTokens = 0

  // Split by lines and look for data rows
  const lines = backend.status.split('\n')
  for (const line of lines) {
    // Look for lines that look like table rows (contain multiple | characters)
    if (line.includes('|') && line.trim() && !line.trim().startsWith('+')) {
      const columns = line.split('|').map(col => col.trim()).filter(col => col !== '')

      if (columns.length >= 6) {
        // Skip TOTAL row
        if (columns[0] === 'TOTAL' || columns[0].toUpperCase() === 'TOTAL') {
          continue
        }

        model = columns[0] || 'Unknown'
        provider = columns[1] || 'Unknown'
        totalTokens = parseInt(columns[4]) || 0
        break
      }
    }
  }

  return {
    provider,
    model,
    models: [], // Empty array when no models parsed
    token_usage: {
      total_tokens: totalTokens,
      prompt_tokens: 0,
      completion_tokens: 0
    },
    request_count: 0,
    avg_response_time_ms: undefined
  }
}

// Monitoring service
export const monitoringService = {
  /**
   * Get system health status (from observer/system)
   */
  getSystemStatus: async (): Promise<APIResponse<SystemStatus>> => {
    return handleAPI<BackendSystemResponse>(
      apiClient.get('/observer/system')
    ).then(res => ({
      ...res,
      data: res.data ? {
        status: res.data.is_healthy ? 'healthy' : (res.data.errors?.length > 0 ? 'error' : 'warning'),
        message: res.data.errors?.join(', ') || undefined
      } : undefined
    }))
  },

  /**
   * Get queue status
   */
  getQueueStatus: async (): Promise<APIResponse<QueueStats>> => {
    return handleAPI<BackendQueueResponse>(
      apiClient.get('/observer/queue')
    ).then(res => ({
      ...res,
      data: res.data ? normalizeQueueStats(res.data) : undefined
    }))
  },

  /**
   * Get VikingDB status
   */
  getVikingDBStatus: async (): Promise<APIResponse<VikingDBStatus>> => {
    return handleAPI<BackendVikingDBResponse>(
      apiClient.get('/observer/vikingdb')
    ).then(res => ({
      ...res,
      data: res.data ? normalizeVikingDBStatus(res.data) : undefined
    }))
  },

  /**
   * Get VLM status
   */
  getVLMStatus: async (): Promise<APIResponse<VLMStats>> => {
    return handleAPI<BackendVLMResponse>(
      apiClient.get('/observer/vlm')
    ).then(res => ({
      ...res,
      data: res.data ? normalizeVLMStats(res.data) : undefined
    }))
  },

  /**
   * Get system info (from observer/system components)
   */
  getSystemInfo: async (): Promise<APIResponse<SystemInfo>> => {
    return handleAPI<BackendSystemResponse>(
      apiClient.get('/observer/system')
    ).then(res => ({
      ...res,
      data: res.data ? {
        active_sessions: 0,
        active_tasks: 0
      } : undefined
    }))
  },

  /**
   * Get all monitoring data
   */
  getAll: async (): Promise<APIResponse<MonitoringSummary>> => {
    try {
      // Fetch all monitoring data in parallel
      const [
        systemResponse,
        queueResponse,
        vikingDBResponse,
        vlmResponse,
        systemInfoResponse,
        resourceStatsResponse
      ] = await Promise.all([
        monitoringService.getSystemStatus(),
        monitoringService.getQueueStatus(),
        monitoringService.getVikingDBStatus(),
        monitoringService.getVLMStatus(),
        monitoringService.getSystemInfo(),
        monitoringService.getResourceStats()
      ])

      const summary: MonitoringSummary = {
        system: systemResponse.data || { status: 'unknown' as any },
        queue: queueResponse.data || { embedding_queue: { queue_name: '', queue_length: 0, processing: false }, semantic_queue: { queue_name: '', queue_length: 0, processing: false } },
        resources: resourceStatsResponse.data || { total_resources: 0, total_size: 0 },
        vikingdb: vikingDBResponse.data || { collections: 0, total_vectors: 0, storage_used: 0 },
        vlm: vlmResponse.data || { provider: '', model: '' },
        systemInfo: systemInfoResponse.data || {},
        last_updated: new Date().toISOString()
      }

      return {
        success: true,
        data: summary
      }
    } catch (error) {
      const apiError = error as APIResponse
      return {
        success: false,
        error: apiError.error || 'Failed to fetch monitoring data'
      }
    }
  },

  /**
   * Get resource statistics
   */
  getResourceStats: async (): Promise<APIResponse<ResourceStats>> => {
    // This would need a dedicated API endpoint
    // For now, return empty stats
    return {
      success: true,
      data: {
        total_resources: 0,
        total_size: 0
      }
    }
  },

  /**
   * Get task statistics
   */
  getTaskStats: async (): Promise<APIResponse<{
    active: number
    completed: number
    failed: number
  }>> => {
    return handleAPI<any>(
      apiClient.get('/tasks')
    ).then(res => ({
      ...res,
      data: res.data ? {
        active: (res.data.filter((t: any) => t.status === 'running').length) || 0,
        completed: (res.data.filter((t: any) => t.status === 'completed').length) || 0,
        failed: (res.data.filter((t: any) => t.status === 'failed').length) || 0
      } : { active: 0, completed: 0, failed: 0 }
    }))
  }
}

export default monitoringService
