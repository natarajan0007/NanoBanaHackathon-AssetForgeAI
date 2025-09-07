'use client'

import { useEffect } from "react"
import { useApi } from "@/lib/hooks/use-api"
import { apiClient } from "@/lib/api-client"
import { Skeleton } from "@/components/ui/skeleton"
import { PlatformsTable } from "./platforms-table"

export function PlatformManagement() {
  const { data: platforms, loading, error, execute: fetchPlatforms } = useApi<any[]>();

  useEffect(() => {
    fetchPlatforms(() => apiClient.getPlatforms());
  }, [fetchPlatforms]);

  if (loading) {
    return <Skeleton className="h-64 w-full" />
  }

  if (error) {
    return <p className="text-destructive">Error fetching platforms: {error}</p>
  }

  return (
    <div>
      <PlatformsTable data={platforms || []} onDataChange={() => fetchPlatforms(() => apiClient.getPlatforms())} />
    </div>
  )
}
