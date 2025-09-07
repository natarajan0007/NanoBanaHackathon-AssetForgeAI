'use client'

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Users, FileImage, Zap, TrendingUp } from "lucide-react"
import { useApi } from "@/lib/hooks/use-api"
import { apiClient } from "@/lib/api-client"
import { useEffect } from "react"
import { Skeleton } from "@/components/ui/skeleton"

export function AdminStats() {
  const { data: stats, loading, error, execute: fetchStats } = useApi<any>();

  useEffect(() => {
    fetchStats(() => apiClient.getAdminStats());
  }, [fetchStats]);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-24 w-full" />
        ))}
      </div>
    )
  }

  if (error) {
    return <p className="text-destructive">Error fetching stats: {error}</p>
  }

  const statsData = [
    {
      title: "Total Users",
      value: stats?.totalUsers,
      icon: Users,
    },
    {
      title: "Total Projects",
      value: stats?.totalProjects,
      icon: FileImage,
    },
    {
      title: "Assets Generated",
      value: stats?.totalGeneratedAssets,
      icon: Zap,
    },
    {
      title: "Active Workers",
      value: stats?.activeWorkers,
      icon: TrendingUp,
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {statsData.map((stat) => (
        <Card key={stat.title}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">{stat.title}</CardTitle>
            <stat.icon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">{stat.value}</div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}
