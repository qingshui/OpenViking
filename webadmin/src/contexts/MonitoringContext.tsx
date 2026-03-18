import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { monitoringService, MonitoringSummary } from '../services/monitoring'

interface MonitoringContextValue {
  data: MonitoringSummary | null
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
}

const MonitoringContext = createContext<MonitoringContextValue | undefined>(undefined)

export const MonitoringProvider = ({ children }: { children: ReactNode }) => {
  const [data, setData] = useState<MonitoringSummary | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const refresh = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await monitoringService.getAll()
      if (response.success && response.data) {
        setData(response.data)
      } else {
        setError(response.error || 'Failed to load monitoring data')
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refresh()
  }, [])

  return (
    <MonitoringContext.Provider value={{ data, loading, error, refresh }}>
      {children}
    </MonitoringContext.Provider>
  )
}

export const useMonitoring = () => {
  const context = useContext(MonitoringContext)
  if (!context) {
    throw new Error('useMonitoring must be used within a MonitoringProvider')
  }
  return context
}

export default MonitoringContext
