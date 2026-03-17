import React, { useState, useEffect } from 'react'
import { resourceService } from '../services/resources'
import { queueService } from '../services/api'

interface StorageStats {
  totalResources: number
  totalSize: number
  resourcesByType: Record<string, number>
  resourcesByUri: Record<string, number>
}

interface QuickStats {
  resources: number
  sessions: number
  totalSize: string
}

interface QueueStatus {
  name?: string
  is_healthy?: boolean
  has_errors?: boolean
  status?: string  // ASCII table string
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
  services: {
    embedding: {
      status: 'running' | 'stopped' | 'error'
      pending: number
      processing: number
      completed: number
      failed: number
    }
    semantic: {
      status: 'running' | 'stopped' | 'error'
      pending: number
      processing: number
      completed: number
      failed: number
    }
  }
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<StorageStats>({
    totalResources: 0,
    totalSize: 0,
    resourcesByType: {},
    resourcesByUri: {}
  })
  const [quickStats, setQuickStats] = useState<QuickStats>({
    resources: 0,
    sessions: 0,
    totalSize: '0 MB'
  })
  const [queueStatus, setQueueStatus] = useState<QueueStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadAllStats()
    const interval = setInterval(loadAllStats, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadStats = async () => {
    try {
      setLoading(true)
      setError('')

      // 获取 resources 目录下的资源
      const resources = await resourceService.list('viking://resources/', 1000)

      // 计算统计数据
      const totalSize = resources.reduce((sum: number, r: any) => sum + (r.size || 0), 0)
      const resourcesByType: Record<string, number> = {}
      const resourcesByUri: Record<string, number> = {}

      resources.forEach((r: any) => {
        // 按类型统计
        const type = r.type || 'unknown'
        resourcesByType[type] = (resourcesByType[type] || 0) + 1

        // 按 URI 前缀统计
        const uriPrefix = r.uri.split('/')[3] || 'other'
        resourcesByUri[uriPrefix] = (resourcesByUri[uriPrefix] || 0) + 1
      })

      setStats({
        totalResources: resources.length,
        totalSize,
        resourcesByType,
        resourcesByUri
      })

      setQuickStats({
        resources: resources.length,
        sessions: 0, // TODO: 从 sessions API 获取
        totalSize: formatSize(totalSize)
      })
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load statistics')
    } finally {
      setLoading(false)
    }
  }

  const loadQueueStatus = async () => {
    try {
      const rawStatus = await queueService.getStatus()
      // Backend returns the exact format we need
      // queues: { embedding/semantic: { pending, in_progress, processed, error_count } }
      // services: { embedding/semantic: { status, pending, processing, completed, failed } }
      setQueueStatus(rawStatus)
    } catch (err) {
      console.error('Failed to load queue status:', err)
    }
  }

  const loadAllStats = async () => {
    await Promise.all([loadStats(), loadQueueStatus()])
  }

  const formatSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`
  }

  const getTypeColor = (type: string): string => {
    const colors: Record<string, string> = {
      design_doc: 'blue',
      code_file: 'green',
      code_module: 'purple',
      session: 'orange',
      api_interface: 'indigo',
      code_style: 'teal',
      memory: 'pink',
      semantic: 'cyan'
    }
    return colors[type] || 'gray'
  }

  const getQueueStatusColor = (status: string): string => {
    const colors: Record<string, string> = {
      running: 'green',
      stopped: 'red',
      error: 'orange'
    }
    return colors[status] || 'gray'
  }

  const ServiceStatusCard: React.FC<{
    title: string
    stats: { pending: number; processing: number; completed: number; failed: number }
    status: 'running' | 'stopped' | 'error'
  }> = ({ title, stats, status }) => {
    const total = stats.pending + stats.processing + stats.completed + stats.failed
    return (
      <div className="bg-white p-4 rounded-lg shadow-sm border">
        <div className="flex items-center justify-between mb-3">
          <h4 className="font-semibold text-gray-800">{title}</h4>
          <span className={`px-2 py-1 rounded-full text-xs font-medium bg-${getQueueStatusColor(status)}-100 text-${getQueueStatusColor(status)}-800`}>
            {status}
          </span>
        </div>
        <div className="grid grid-cols-4 gap-2 text-center">
          <div className="bg-yellow-50 rounded p-2">
            <div className="text-2xl font-bold text-yellow-700">{stats.pending}</div>
            <div className="text-xs text-yellow-600">Pending</div>
          </div>
          <div className="bg-blue-50 rounded p-2">
            <div className="text-2xl font-bold text-blue-700">{stats.processing}</div>
            <div className="text-xs text-blue-600">Processing</div>
          </div>
          <div className="bg-green-50 rounded p-2">
            <div className="text-2xl font-bold text-green-700">{stats.completed}</div>
            <div className="text-xs text-green-600">Completed</div>
          </div>
          <div className="bg-red-50 rounded p-2">
            <div className="text-2xl font-bold text-red-700">{stats.failed}</div>
            <div className="text-xs text-red-600">Failed</div>
          </div>
        </div>
        <div className="mt-2 text-xs text-gray-500 text-center">Total: {total}</div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Dashboard</h2>
        <button
          onClick={loadStats}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          Refresh
        </button>
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 px-4 py-3 rounded-lg mb-4">{error}</div>
      )}

      {loading ? (
        <div className="text-center py-8">Loading statistics...</div>
      ) : (
        <>
          {/* 概览卡片 */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-blue-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Resources</p>
                  <p className="text-3xl font-bold text-blue-600">{quickStats.resources}</p>
                </div>
                <div className="bg-blue-100 p-3 rounded-lg">
                  <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border border-green-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Storage</p>
                  <p className="text-3xl font-bold text-green-600">{quickStats.totalSize}</p>
                </div>
                <div className="bg-green-100 p-3 rounded-lg">
                  <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
                  </svg>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border border-purple-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Resource Types</p>
                  <p className="text-3xl font-bold text-purple-600">{Object.keys(stats.resourcesByType).length}</p>
                </div>
                <div className="bg-purple-100 p-3 rounded-lg">
                  <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                  </svg>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow-sm border border-orange-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Directories</p>
                  <p className="text-3xl font-bold text-orange-600">{Object.keys(stats.resourcesByUri).length}</p>
                </div>
                <div className="bg-orange-100 p-3 rounded-lg">
                  <svg className="w-8 h-8 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                  </svg>
                </div>
              </div>
            </div>
          </div>

          {/* 队列状态 */}
          {queueStatus && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
                <svg className="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
                Queue Status
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <ServiceStatusCard
                  title="Semantic Queue"
                  stats={queueStatus.services.semantic}
                  status={queueStatus.services.semantic.status}
                />
                <ServiceStatusCard
                  title="Embedding Queue"
                  stats={queueStatus.services.embedding}
                  status={queueStatus.services.embedding.status}
                />
              </div>
            </div>
          )}

          {/* 详细统计 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* 按类型统计 */}
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Resources by Type</h3>
              <div className="space-y-3">
                {Object.entries(stats.resourcesByType)
                  .sort(([, a], [, b]) => b - a)
                  .map(([type, count]) => (
                    <div key={type} className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className={`w-3 h-3 rounded-full bg-${getTypeColor(type)}-500 mr-3`} />
                        <span className="text-gray-700 capitalize">{type.replace('_', ' ')}</span>
                      </div>
                      <span className="font-semibold text-gray-900">{count}</span>
                    </div>
                  ))}
                {Object.keys(stats.resourcesByType).length === 0 && (
                  <p className="text-gray-500 text-center py-4">No resources yet</p>
                )}
              </div>
            </div>

            {/* 按目录统计 */}
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Resources by Directory</h3>
              <div className="space-y-3">
                {Object.entries(stats.resourcesByUri)
                  .sort(([, a], [, b]) => b - a)
                  .map(([uri, count]) => (
                    <div key={uri} className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="w-3 h-3 rounded-full bg-indigo-500 mr-3" />
                        <span className="text-gray-700">{uri}</span>
                      </div>
                      <span className="font-semibold text-gray-900">{count}</span>
                    </div>
                  ))}
                {Object.keys(stats.resourcesByUri).length === 0 && (
                  <p className="text-gray-500 text-center py-4">No resources yet</p>
                )}
              </div>
            </div>
          </div>

          {/* 功能入口 */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mt-6">
            <a href="/resources" className="bg-white p-6 rounded-lg shadow-sm border hover:shadow-md transition-shadow">
              <h3 className="text-lg font-semibold text-gray-700 mb-2">Resources</h3>
              <p className="text-gray-600 text-sm">Manage your stored resources</p>
              <p className="text-blue-600 text-sm mt-2">View &rarr;</p>
            </a>
            <a href="/sessions" className="bg-white p-6 rounded-lg shadow-sm border hover:shadow-md transition-shadow">
              <h3 className="text-lg font-semibold text-gray-700 mb-2">Sessions</h3>
              <p className="text-gray-600 text-sm">View and manage conversation sessions</p>
              <p className="text-blue-600 text-sm mt-2">View &rarr;</p>
            </a>
            <a href="/filesystem" className="bg-white p-6 rounded-lg shadow-sm border hover:shadow-md transition-shadow">
              <h3 className="text-lg font-semibold text-gray-700 mb-2">File System</h3>
              <p className="text-gray-600 text-sm">Browse viking:// file system</p>
              <p className="text-blue-600 text-sm mt-2">View &rarr;</p>
            </a>
            <a href="/search" className="bg-white p-6 rounded-lg shadow-sm border hover:shadow-md transition-shadow">
              <h3 className="text-lg font-semibold text-gray-700 mb-2">Search</h3>
              <p className="text-gray-600 text-sm">Semantic and content search</p>
              <p className="text-blue-600 text-sm mt-2">View &rarr;</p>
            </a>
          </div>
        </>
      )}
    </div>
  )
}

export default Dashboard
