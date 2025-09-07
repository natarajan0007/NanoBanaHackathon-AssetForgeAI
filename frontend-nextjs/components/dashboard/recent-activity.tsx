'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Clock, CheckCircle, AlertCircle, Loader2 } from "lucide-react"
import { useApi } from "@/lib/hooks/use-api"
import { apiClient } from "@/lib/api-client"
import { useEffect } from "react"
import { Skeleton } from "@/components/ui/skeleton"
import { formatDistanceToNow } from 'date-fns'

interface Activity {
  id: string
  projectName: string
  status: string
  createdAt: string
}

export function RecentActivity() {
  const { data: activities, loading, error, execute: fetchActivities } = useApi<Activity[]>();

  useEffect(() => {
    fetchActivities(() => apiClient.getRecentActivity());
  }, [fetchActivities]);

  const getActivityIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <Loader2 className="h-4 w-4 text-gray-500 animate-spin" />
      case 'processing':
      case 'generating':
        return <Clock className="h-4 w-4 text-yellow-500" />
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      default:
        return <Clock className="h-4 w-4 text-gray-500" />
    }
  }

  const getActivityMessage = (activity: Activity) => {
    switch (activity.status) {
        case 'pending':
            return `Job for project "${activity.projectName}" is pending.`
        case 'processing':
        case 'generating':
            return `Processing job for project "${activity.projectName}".`
        case 'completed':
            return `Job for project "${activity.projectName}" completed successfully.`
        case 'failed':
            return `Job for project "${activity.projectName}" failed.`
        default:
            return `Update on project "${activity.projectName}".`
    }
  }

  if (loading) {
    return (
        <Card>
            <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>Latest updates on your projects</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
                {Array.from({ length: 5 }).map((_, i) => (
                    <div key={i} className="flex items-start space-x-3">
                        <Skeleton className="h-5 w-5 rounded-full" />
                        <div className="flex-1 space-y-1">
                            <Skeleton className="h-4 w-full" />
                            <Skeleton className="h-3 w-1/2" />
                        </div>
                    </div>
                ))}
            </CardContent>
        </Card>
    )
  }

  if (error) {
    return <p className="text-destructive">Error fetching recent activity: {error}</p>
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
        <CardDescription>Latest updates on your generation jobs</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activities?.map((activity) => (
            <div key={activity.id} className="flex items-start space-x-3">
              <div className="flex-shrink-0 mt-0.5">{getActivityIcon(activity.status)}</div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-foreground">{getActivityMessage(activity)}</p>
                <div className="flex items-center space-x-2 mt-1">
                  <span className="text-xs text-muted-foreground">
                    {formatDistanceToNow(new Date(activity.createdAt), { addSuffix: true })}
                  </span>
                  <Badge variant="outline" className="text-xs">
                    {activity.projectName}
                  </Badge>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
