'use client'

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { CheckCircle, AlertTriangle, Server, Database } from "lucide-react"
import { useApi } from "@/lib/hooks/use-api"
import { apiClient } from "@/lib/api-client"
import { useEffect } from "react"
import { Skeleton } from "@/components/ui/skeleton"

export function SystemHealthCard() {
  const { data: health, loading, error, execute: fetchHealth } = useApi<any>();

  useEffect(() => {
    fetchHealth(() => apiClient.getSystemHealth());
  }, [fetchHealth]);

  const getStatusIcon = (status: string) => {
    if (status === "ok") {
      return <CheckCircle className="h-4 w-4 text-green-500" />
    }
    return <AlertTriangle className="h-4 w-4 text-red-500" />
  }

  const getStatusColor = (status: string) => {
    if (status === "ok") {
      return "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300"
    }
    return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300"
  }

  const healthMetrics = [
    {
      name: "Database",
      status: health?.database?.status || "loading",
      details: health?.database?.status !== "ok" ? health?.database?.status : null,
      icon: Database,
    },
    {
      name: "Redis",
      status: health?.redis?.status || "loading",
      details: health?.redis?.status !== "ok" ? health?.redis?.status : null,
      icon: Database, // Using Database icon as a substitute for Redis
    },
    {
      name: "Celery Workers",
      status: health?.celery?.status || "loading",
      details: health?.celery?.details,
      icon: Server,
    },
  ]

  if (loading) {
    return (
        <Card>
            <CardHeader>
                <CardTitle>Core Services</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
                {Array.from({ length: 3 }).map((_, i) => (
                    <Skeleton key={i} className="h-12 w-full" />
                ))}
            </CardContent>
        </Card>
    )
  }

  if (error) {
    return <p className="text-destructive">Error fetching system health: {error}</p>
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Core Services Status</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {healthMetrics.map((metric) => (
            <div key={metric.name}>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <metric.icon className="h-5 w-5 text-muted-foreground" />
                  <span className="text-base font-medium">{metric.name}</span>
                  {getStatusIcon(metric.status)}
                </div>
                <Badge className={getStatusColor(metric.status)}>{metric.status}</Badge>
              </div>
              {metric.details && (
                <p className="text-sm text-muted-foreground mt-1 pl-8">{metric.details}</p>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
