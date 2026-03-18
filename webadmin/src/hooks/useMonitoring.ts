import { useQuery } from '@tanstack/react-query'
import { monitoringService, MonitoringSummary } from '../services/monitoring'

// Query key for monitoring
export const MONITORING_QUERY_KEY = ['monitoring']

// Hook options interface
export interface UseMonitoringOptions {
  enabled?: boolean
  refetchInterval?: number
}

// Monitoring hook
export const useMonitoring = (options: UseMonitoringOptions = {}) => {
  const { enabled = true, refetchInterval = 30000 } = options

  return useQuery<MonitoringSummary, Error>({
    queryKey: MONITORING_QUERY_KEY,
    queryFn: async () => {
      const response = await monitoringService.getAll()
      if (!response.success || !response.data) {
        throw new Error('Failed to fetch monitoring data')
      }
      return response.data
    },
    refetchInterval: enabled ? refetchInterval : false,
    refetchOnWindowFocus: true,
    staleTime: 10000 // 10 seconds
  })
}

// Individual monitoring hooks
export const useSystemStatus = () => {
  return useQuery({
    queryKey: ['monitoring', 'system'],
    queryFn: monitoringService.getSystemStatus,
    refetchInterval: 30000
  })
}

export const useQueueStatus = () => {
  return useQuery({
    queryKey: ['monitoring', 'queue'],
    queryFn: monitoringService.getQueueStatus,
    refetchInterval: 30000
  })
}

export const useVikingDBStatus = () => {
  return useQuery({
    queryKey: ['monitoring', 'vikingdb'],
    queryFn: monitoringService.getVikingDBStatus,
    refetchInterval: 60000
  })
}

export const useVLMStatus = () => {
  return useQuery({
    queryKey: ['monitoring', 'vlm'],
    queryFn: monitoringService.getVLMStatus,
    refetchInterval: 60000
  })
}

export const useSystemInfo = () => {
  return useQuery({
    queryKey: ['monitoring', 'system-info'],
    queryFn: monitoringService.getSystemInfo,
    refetchInterval: 30000
  })
}

export default useMonitoring
