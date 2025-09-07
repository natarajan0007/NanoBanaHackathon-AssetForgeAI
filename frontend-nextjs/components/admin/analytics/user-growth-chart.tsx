'use client'

import { useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useApi } from "@/lib/hooks/use-api"
import { apiClient } from "@/lib/api-client"
import { Skeleton } from "@/components/ui/skeleton"

export function UserGrowthChart() {
  const { data, loading, error, execute: fetchData } = useApi<any[]>();

  useEffect(() => {
    fetchData(() => apiClient.getUserGrowthAnalytics());
  }, [fetchData]);

  if (loading) {
    return <Skeleton className="h-80 w-full" />
  }

  if (error) {
    return <p className="text-destructive">Error fetching user growth data: {error}</p>
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>User Growth</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="count" stroke="#8884d8" name="New Users" />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
