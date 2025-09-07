'use client'

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { Layers, Plus, Settings } from 'lucide-react'
import { useApi } from "@/lib/hooks/use-api"
import { apiClient } from "@/lib/api-client"
import { Skeleton } from "@/components/ui/skeleton"

// This interface matches the PlatformResponse schema from the backend
interface Platform {
  id: string
  name: string
  is_active: boolean
}

export function PlatformManagement() {
  const { data: platforms, loading, error, execute: fetchPlatforms } = useApi<Platform[]>();

  useEffect(() => {
    fetchPlatforms(apiClient.getPlatforms);
  }, [fetchPlatforms]);

  const handleTogglePlatform = (platformId: string, currentStatus: boolean) => {
    // TODO: Backend API does not currently support updating the is_active status.
    // An endpoint like `PUT /api/v1/admin/platforms/{platformId}/status` is needed.
    console.log(`Toggling platform ${platformId} is not yet supported by the API.`);
  };

  const renderPlatformCards = () => {
    if (loading) {
      return Array.from({ length: 4 }).map((_, i) => (
        <Card key={`skeleton-${i}`}>
          <CardHeader><Skeleton className="h-6 w-32" /></CardHeader>
          <CardContent><Skeleton className="h-10 w-full" /></CardContent>
        </Card>
      ));
    }

    if (error) {
      return <p className="text-destructive col-span-full">Error: {error}</p>;
    }

    if (!platforms || platforms.length === 0) {
      return <p className="col-span-full">No platforms found.</p>;
    }

    return platforms.map((platform) => (
      <Card key={platform.id} className="relative">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className={`p-2 rounded-lg bg-muted`}>
                <Layers className="h-5 w-5 text-muted-foreground" />
              </div>
              <div>
                <CardTitle className="text-base">{platform.name}</CardTitle>
              </div>
            </div>
            <Switch
              checked={platform.is_active}
              // TODO: Re-enable this once the backend API supports it.
              disabled={true} 
              onCheckedChange={() => handleTogglePlatform(platform.id, platform.is_active)}
            />
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <Badge variant={platform.is_active ? "default" : "secondary"}>
              {platform.is_active ? "Active" : "Disabled"}
            </Badge>
            <Button variant="outline" size="sm" disabled={true}> 
              <Settings className="h-3 w-3 mr-1" />
              Configure
            </Button>
          </div>
        </CardContent>
      </Card>
    ));
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">Available Platforms</h2>
          <p className="text-sm text-muted-foreground">Enable or disable platforms and manage their formats</p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add Platform
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {renderPlatformCards()}
      </div>

      {/* The statistics card is removed as the API does not provide this data yet */}
    </div>
  )
}
