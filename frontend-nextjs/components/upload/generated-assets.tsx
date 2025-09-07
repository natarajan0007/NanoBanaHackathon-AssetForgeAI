'use client'

import { useState, useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Download, Plus, Loader2 } from "lucide-react"
import { apiClient } from "@/lib/api-client"
import { useToast } from "@/hooks/use-toast"

// Interface matching the backend's GeneratedAssetResponse schema
interface GeneratedAsset {
  id: string;
  assetUrl: string;
  formatName: string;
  dimensions: { width: number; height: number };
  platformName: string | null;
}

interface GeneratedAssetsProps {
  assets: { [platformName: string]: GeneratedAsset[] };
  onStartNew: () => void;
}

export function GeneratedAssets({ assets, onStartNew }: GeneratedAssetsProps) {
  const [loading, setLoading] = useState<string | null>(null); // Can be 'all' or an asset ID
  const { toast } = useToast();
  const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const allAssets = useMemo(() => Object.values(assets).flat(), [assets]);

  const handleDownload = async (assetIds: string[], downloadType: string) => {
    setLoading(downloadType);
    const response = await apiClient.downloadAssets(assetIds);
    if (response.success) {
      toast({ title: "Download Started", description: "Your file should begin downloading shortly." });
    } else {
      toast({ title: "Download Failed", description: response.error, variant: "destructive" });
    }
    setLoading(null);
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-xl font-semibold text-foreground mb-2">Your Assets Are Ready!</h2>
        <p className="text-muted-foreground">{allAssets.length} optimized formats have been generated for your asset</p>
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button onClick={() => handleDownload(allAssets.map(a => a.id), 'all')} size="lg" disabled={loading !== null}>
            {loading === 'all' ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Download className="h-4 w-4 mr-2" />}
            Download All ({allAssets.length})
          </Button>
          <Button variant="outline" onClick={onStartNew}>
            <Plus className="h-4 w-4 mr-2" />
            Start New Project
          </Button>
        </div>
        <Badge variant="secondary" className="text-sm">
          Total: {allAssets.length} assets
        </Badge>
      </div>

      <div className="space-y-8">
        {Object.entries(assets).map(([platformName, platformAssets]) => (
          <div key={platformName}>
            <h3 className="text-lg font-semibold mb-4">{platformName}</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {platformAssets.map((asset) => (
                <Card key={asset.id} className="overflow-hidden">
                  <div className="aspect-video bg-muted">
                    <img
                      src={`${backendUrl}${asset.assetUrl}`}
                      alt={asset.formatName}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <CardHeader className="pb-2">
                    <CardTitle className="text-base">{asset.formatName}</CardTitle>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="flex items-center justify-between mb-4">
                      <span className="text-sm text-muted-foreground">
                        {asset.dimensions.width} x {asset.dimensions.height}
                      </span>
                      <Badge variant="outline">Ready</Badge>
                    </div>
                    <div className="flex space-x-2">
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex-1 bg-transparent"
                        onClick={() => handleDownload([asset.id], asset.id)}
                        disabled={loading !== null}
                      >
                        {loading === asset.id ? <Loader2 className="h-3 w-3 mr-1 animate-spin" /> : <Download className="h-3 w-3 mr-1" />}
                        Download
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
