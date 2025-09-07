'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { CheckCircle, AlertTriangle, Server } from "lucide-react"
import { useApi } from "@/lib/hooks/use-api"
import { apiClient } from "@/lib/api-client"
import { useEffect } from "react"
import { Skeleton } from "@/components/ui/skeleton"

export function SystemHealth() {
  const { data: health, loading, error, execute: fetchHealth } = useApi<any>();

  useEffect(() => {
    fetchHealth(() => apiClient.getCeleryWorkerStats());
  }, [fetchHealth]);

  const getStatusIcon = (status: "online" | "offline") => {
    switch (status) {
      case "online":
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case "offline":
        return <AlertTriangle className="h-4 w-4 text-red-500" />
    }
  }

  const getStatusColor = (status: "online" | "offline") => {
    switch (status) {
      case "online":
        return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300"
      case "offline":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300"
    }
  }

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>System Health</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-16 w-full" />
          ))}
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return <p className="text-destructive">Error fetching system health: {error}</p>
  }

  const workers = health?.workers ? Object.keys(health.workers) : [];

  return (
    <Card>
      <CardHeader>
        <CardTitle>System Health</CardTitle>
        <CardDescription>{workers.length} Celery workers running</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {workers.map((workerName) => (
            <div key={workerName} className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Server className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm font-medium">{workerName.split('@')[0]}</span>
                  {getStatusIcon("online")}
                </div>
                <Badge className={getStatusColor("online")}>Online</Badge>
              </div>
              <div className="text-xs text-muted-foreground">
                Active Tasks: {health.active_tasks[workerName]?.length || 0}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
