import { useEffect, useRef, useState } from 'react'
import { useQueryClient } from 'react-query'

interface UseRealTimeUpdatesOptions {
  interval?: number // Polling interval in milliseconds
  queriesToRefresh?: string[] // Query keys to refresh
  enabled?: boolean
  onNewData?: (data: any) => void
}

export function useRealTimeUpdates({
  interval = 10000, // Default 10 seconds
  queriesToRefresh = [],
  enabled = true,
  onNewData,
}: UseRealTimeUpdatesOptions = {}) {
  const queryClient = useQueryClient()
  const [isLive, setIsLive] = useState(false)
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    if (!enabled) {
      setIsLive(false)
      return
    }

    setIsLive(true)
    setLastUpdate(new Date())

    intervalRef.current = setInterval(() => {
      // Refresh all specified queries
      queriesToRefresh.forEach((queryKey) => {
        queryClient.invalidateQueries(queryKey)
      })

      setLastUpdate(new Date())

      if (onNewData) {
        onNewData({ timestamp: new Date() })
      }
    }, interval)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
      setIsLive(false)
    }
  }, [enabled, interval, queriesToRefresh, queryClient, onNewData])

  const toggleLive = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
      setIsLive(false)
    } else {
      // Restart polling
      setIsLive(true)
      intervalRef.current = setInterval(() => {
        queriesToRefresh.forEach((queryKey) => {
          queryClient.invalidateQueries(queryKey)
        })
        setLastUpdate(new Date())
        if (onNewData) {
          onNewData({ timestamp: new Date() })
        }
      }, interval)
    }
  }

  return {
    isLive,
    lastUpdate,
    toggleLive,
  }
}

// SSE-based real-time updates (alternative implementation)
export function useServerSentEvents<T = any>(
  endpoint: string,
  options: {
    enabled?: boolean
    onMessage?: (data: T) => void
    onError?: (error: Event) => void
  } = {}
) {
  const { enabled = true, onMessage, onError } = options
  const [isConnected, setIsConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState<T | null>(null)
  const eventSourceRef = useRef<EventSource | null>(null)

  useEffect(() => {
    if (!enabled) {
      setIsConnected(false)
      return
    }

    const eventSource = new EventSource(endpoint)
    eventSourceRef.current = eventSource

    eventSource.onopen = () => {
      setIsConnected(true)
    }

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        setLastMessage(data)
        if (onMessage) {
          onMessage(data)
        }
      } catch (error) {
        console.error('Failed to parse SSE message:', error)
      }
    }

    eventSource.onerror = (error) => {
      setIsConnected(false)
      if (onError) {
        onError(error)
      }
    }

    return () => {
      eventSource.close()
      eventSourceRef.current = null
      setIsConnected(false)
    }
  }, [endpoint, enabled, onMessage, onError])

  const disconnect = () => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close()
      eventSourceRef.current = null
      setIsConnected(false)
    }
  }

  return {
    isConnected,
    lastMessage,
    disconnect,
  }
}
