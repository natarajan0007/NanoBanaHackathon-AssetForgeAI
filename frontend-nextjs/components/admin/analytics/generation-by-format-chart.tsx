'use client'

import { useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { useApi } from "@/lib/hooks/use-api"
import { apiClient } from "@/lib/api-client"
import { Skeleton } from "@/components/ui/skeleton"

export function GenerationByFormatChart() {
  const { data, loading, error, execute: fetchData } = useApi<any[]>();

  useEffect(() => {
    fetchData(() => apiClient.getGenerationByFormatAnalytics());
  }, [fetchData]);

  if (loading) {
    return <Skeleton className="h-80 w-full" />
  }

  if (error) {
    return <p className="text-destructive">Error fetching generation by format data: {error}</p>
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Asset Generation by Format</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="count" fill="#82ca9d" name="Assets Generated" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  )
}
