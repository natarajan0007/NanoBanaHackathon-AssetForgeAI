'use client'

import { useEffect } from "react"
import { useApi } from "@/lib/hooks/use-api"
import { apiClient } from "@/lib/api-client"
import { Skeleton } from "@/components/ui/skeleton"
import { TextStylesTable } from "./text-styles-table"

export function TextStyleManagement() {
  const { data: textStyles, loading, error, execute: fetchTextStyles } = useApi<any[]>();

  useEffect(() => {
    fetchTextStyles(() => apiClient.getTextStyleSets());
  }, [fetchTextStyles]);

  if (loading) {
    return <Skeleton className="h-64 w-full" />
  }

  if (error) {
    return <p className="text-destructive">Error fetching text styles: {error}</p>
  }

  return (
    <div>
      <TextStylesTable data={textStyles || []} onDataChange={() => fetchTextStyles(() => apiClient.getTextStyleSets())} />
    </div>
  )
}
