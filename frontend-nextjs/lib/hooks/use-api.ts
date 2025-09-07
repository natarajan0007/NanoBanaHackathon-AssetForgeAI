"use client"

import { useState, useCallback } from "react"

interface UseApiState<T> {
  data: T | null
  loading: boolean
  error: string | null
}

export function useApi<T>() {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  })

  const execute = useCallback(async (apiCall: () => Promise<any>) => {
    setState({ data: null, loading: true, error: null })

    try {
      const response = await apiCall()

      if (response.success) {
        setState({ data: response.data, loading: false, error: null })
        return response
      } else {
        setState({ data: null, loading: false, error: response.error || "Unknown error" })
        return response
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error"
      setState({ data: null, loading: false, error: errorMessage })
      return { success: false, error: errorMessage }
    }
  }, [])

  return { ...state, execute, setData: (data: T) => setState(s => ({ ...s, data })) }
}

// Specific hooks for common operations
export function useAssetUpload() {
  return useApi<any>()
}

export function useProjects() {
  return useApi<any[]>()
}

export function useUsers() {
  return useApi<any[]>()
}

export function usePlatforms() {
  return useApi<any[]>()
}

export function useAnalytics() {
  return useApi<any>()
}