import React, { useState, useEffect } from 'react'
import { useResources, useMonitoring, useTaskStats } from '../hooks'
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card'
import { StatusIndicator } from '../components/StatusIndicator'
import { MonitoringAlert } from '../components/MonitoringAlert'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { Button } from '../components/ui/Button'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts'

interface DashboardStats {
  totalResources: number
  totalSize: number
  queueLength: number
  activeTasks: number
  failedTasks: number
}

const Dashboard: React.FC = () => {
  const { data: monitoringData, isLoading: isMonitoringLoading, refetch } = useMonitoring({ enabled: true, refetchInterval: 60000 })
  const { data: taskStats, isLoading: isTaskLoading } = useTaskStats()
  const { data: resourcesData, isLoading: isResourcesLoading } = useResources({ limit: 1000 })
  const [stats, setStats] = useState<DashboardStats>({
    totalResources: 0,
    totalSize: 0,
    queueLength: 0,
    activeTasks: 0,
    failedTasks: 0
  })

  useEffect(() => {
    if (resourcesData?.success && resourcesData.data && resourcesData.data.length > 0) {
      const totalSize = resourcesData.data.reduce((sum: number, r: any) => sum + (r.size || 0), 0)
      setStats(prev => ({
        ...prev,
        totalResources: resourcesData.data!.length,
        totalSize
      }))
    }
  }, [resourcesData?.data])

  useEffect(() => {
    if (monitoringData) {
      setStats(prev => ({
        ...prev,
        queueLength:
          monitoringData.queue?.embedding_queue?.queue_length ||
          monitoringData.queue?.semantic_queue?.queue_length ||
          0
      }))
    }
  }, [monitoringData])

  useEffect(() => {
    if (taskStats?.success && taskStats.data) {
      setStats(prev => ({
        ...prev,
        activeTasks: taskStats.data!.running ?? 0,
        failedTasks: taskStats.data!.failed ?? 0
      }))
    }
  }, [taskStats])

  const queueData = monitoringData?.queue
    ? [
        { name: 'Embedding', length: monitoringData.queue.embedding_queue?.queue_length ?? 0 },
        { name: 'Semantic', length: monitoringData.queue.semantic_queue?.queue_length ?? 0 }
      ]
    : []

  const formatSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`
    if (bytes < 1024 * 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
    return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`
  }

  const isLoading = isMonitoringLoading || isResourcesLoading || isTaskLoading

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <LoadingSpinner size="large" />
      </div>
    )
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-800">System Dashboard</h1>
        <Button onClick={() => refetch()} size="small">
          Refresh
        </Button>
      </div>

      {/* System Status Alert */}
      <MonitoringAlert />

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* System Status Card */}
        <Card>
          <CardHeader>
            <CardTitle>System Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              <StatusIndicator
                status={monitoringData?.system?.status || 'unknown'}
                size="large"
              />
              <span className="text-lg font-medium capitalize">
                {monitoringData?.system?.status || 'Unknown'}
              </span>
            </div>
            {monitoringData?.system?.message && (
              <p className="text-sm text-gray-600 mt-2">
                {monitoringData.system.message}
              </p>
            )}
            <p className="text-xs text-gray-500 mt-2">
              Last updated:{' '}
              {monitoringData?.last_updated
                ? new Date(monitoringData.last_updated).toLocaleString()
                : 'N/A'}
            </p>
          </CardContent>
        </Card>

        {/* Resource Stats Card */}
        <Card>
          <CardHeader>
            <CardTitle>Resources</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats.totalResources.toLocaleString()} resources
            </div>
            <div className="text-sm text-gray-600 mt-1">
              {formatSize(stats.totalSize)} total
            </div>
          </CardContent>
        </Card>

        {/* Queue Status Card */}
        <Card>
          <CardHeader>
            <CardTitle>Queue Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.queueLength} items</div>
            <div className="text-sm text-gray-600 mt-1">
              {monitoringData?.queue?.embedding_queue?.processing ? (
                <span className="text-green-500">Processing</span>
              ) : (
                <span className="text-gray-500">Idle</span>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Task Status Card */}
        <Card>
          <CardHeader>
            <CardTitle>Tasks</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activeTasks} active</div>
            <div className="text-sm text-gray-600 mt-1">
              {stats.failedTasks} failed
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Queue Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Queue Length</CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={queueData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="length" fill="#0088FE" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* VikingDB Status */}
      {monitoringData?.vikingdb && (
        <Card>
          <CardHeader>
            <CardTitle>VikingDB Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <div className="text-sm text-gray-600">Collections</div>
                <div className="text-2xl font-bold">
                  {monitoringData.vikingdb?.collections ?? '0'}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Total Vectors</div>
                <div className="text-2xl font-bold">
                  {monitoringData.vikingdb?.total_vectors?.toLocaleString() ?? '0'}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Storage Used</div>
                <div className="text-2xl font-bold">
                  {formatSize(monitoringData.vikingdb?.storage_used ?? 0)}
                </div>
              </div>
              {monitoringData.vikingdb.query_performance && (
                <div>
                  <div className="text-sm text-gray-600">Avg Latency</div>
                  <div className="text-2xl font-bold">
                    {monitoringData.vikingdb.query_performance.avg_latency_ms?.toFixed(2)}ms
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* VLM Status */}
      {monitoringData?.vlm && (
        <Card>
          <CardHeader>
            <CardTitle>VLM Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <div className="text-sm text-gray-600">Provider</div>
                <div className="text-lg font-medium">
                  {monitoringData.vlm.provider || 'N/A'}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Model</div>
                <div className="text-lg font-medium">{monitoringData.vlm.model || 'N/A'}</div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Total Tokens</div>
                <div className="text-2xl font-bold">
                  {monitoringData.vlm.token_usage?.total_tokens?.toLocaleString() ?? '0'}
                </div>
              </div>
              <div>
                <div className="text-sm text-gray-600">Requests</div>
                <div className="text-2xl font-bold">
                  {monitoringData.vlm.request_count ?? '0'}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default Dashboard
