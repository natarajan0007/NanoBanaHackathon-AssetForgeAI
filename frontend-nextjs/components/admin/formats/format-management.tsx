'use client'

import { useEffect } from "react"
import { useApi } from "@/lib/hooks/use-api"
import { apiClient } from "@/lib/api-client"
import { Skeleton } from "@/components/ui/skeleton"
import { FormatsTable } from "./formats-table"

export function FormatManagement() {
  const { data: formats, loading, error, execute: fetchFormats } = useApi<any[]>();

  useEffect(() => {
    fetchFormats(() => apiClient.getAdminFormats());
  }, [fetchFormats]);

  if (loading) {
    return <Skeleton className="h-64 w-full" />
  }

  if (error) {
    return <p className="text-destructive">Error fetching formats: {error}</p>
  }

  return (
    <div>
      <FormatsTable data={formats || []} onDataChange={() => fetchFormats(() => apiClient.getAdminFormats())} />
    </div>
  )
}
