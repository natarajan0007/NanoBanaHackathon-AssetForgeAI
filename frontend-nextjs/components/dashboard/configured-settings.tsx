'use client'

import { useEffect } from 'react'
import { useApi } from '@/lib/hooks/use-api'
import { apiClient } from '@/lib/api-client'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { SlidersHorizontal, Brush, ShieldCheck, Pencil, Type } from 'lucide-react'

export function ConfiguredSettings() {
  const { data: aiBehavior, loading: loadingAiBehavior, execute: fetchAiBehavior } = useApi<any>()
  const { data: adaptation, loading: loadingAdaptation, execute: fetchAdaptation } = useApi<any>()
  const { data: uploadModeration, loading: loadingUploadModeration, execute: fetchUploadModeration } = useApi<any>()
  const { data: textStyles, loading: loadingTextStyles, execute: fetchTextStyles } = useApi<any[]>()
  const { data: editingRules, loading: loadingEditingRules, execute: fetchEditingRules } = useApi<any>()

  useEffect(() => {
    fetchAiBehavior(() => apiClient.getAiBehaviorSettings())
    fetchAdaptation(() => apiClient.getAdaptationSettings())
    fetchUploadModeration(() => apiClient.getUploadModerationSettings())
    fetchTextStyles(() => apiClient.getTextStyleSetsSettings())
    fetchEditingRules(() => apiClient.getEditingRules())
  }, [fetchAiBehavior, fetchAdaptation, fetchUploadModeration, fetchTextStyles, fetchEditingRules])

  const isLoading = loadingAiBehavior || loadingAdaptation || loadingUploadModeration || loadingTextStyles || loadingEditingRules

  const renderSetting = (label: string, value: string | React.ReactNode, highlight: 'green' | 'red' | 'default' = 'default') => {
    let badgeVariant: "default" | "destructive" | "outline" = "outline";
    if (highlight === 'green') badgeVariant = 'default';
    if (highlight === 'red') badgeVariant = 'destructive';

    return (
      <div className="flex items-center justify-between py-2 border-b">
        <p className="text-muted-foreground">{label}</p>
        {typeof value === 'string' ? <Badge variant={badgeVariant}>{value}</Badge> : value}
      </div>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Configured Settings by Admin</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="space-y-4">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-24 w-full" />
          </div>
        ) : (
          <Tabs defaultValue="ai-behavior">
            <TabsList className="grid w-full grid-cols-5">
              <TabsTrigger value="ai-behavior"><SlidersHorizontal className="w-4 h-4 mr-2" /> AI Behavior</TabsTrigger>
              <TabsTrigger value="adaptation"><Brush className="w-4 h-4 mr-2" /> Adaptation</TabsTrigger>
              <TabsTrigger value="moderation"><ShieldCheck className="w-4 h-4 mr-2" /> Moderation</TabsTrigger>
              <TabsTrigger value="editing"><Pencil className="w-4 h-4 mr-2" /> Editing</TabsTrigger>
              <TabsTrigger value="text-styles"><Type className="w-4 h-4 mr-2" /> Text Styles</TabsTrigger>
            </TabsList>

            <TabsContent value="ai-behavior" className="pt-4">
              {aiBehavior && (
                <div className="space-y-2">
                  {renderSetting("Adaptation Strategy", aiBehavior.adaptationStrategy)}
                  {renderSetting("Image Quality", aiBehavior.imageQuality, aiBehavior.imageQuality === 'high' ? 'green' : 'default')}
                </div>
              )}
            </TabsContent>

            <TabsContent value="adaptation" className="pt-4">
              {adaptation && (
                <div className="space-y-2">
                  {renderSetting("Focal Point Logic", adaptation.focalPointLogic)}
                  {renderSetting("Layout Guidance", adaptation.layoutGuidance || "Not set")}
                </div>
              )}
            </TabsContent>

            <TabsContent value="moderation" className="pt-4">
              {uploadModeration && (
                <div className="space-y-2">
                  {renderSetting("NSFW Alerts", uploadModeration.nsfwAlertsActive ? "Active" : "Inactive", uploadModeration.nsfwAlertsActive ? 'green' : 'red')}
                  {renderSetting("Max File Size (MB)", `${uploadModeration.maxFileSizeMb} MB`)}
                  {renderSetting("Allowed Image Types", <div className="flex gap-1">{uploadModeration.allowedImageTypes.map((type: string) => <Badge key={type} variant="secondary">{type}</Badge>)}</div>)}
                </div>
              )}
            </TabsContent>

            <TabsContent value="editing" className="pt-4">
              {editingRules && (
                <div className="space-y-2">
                  {renderSetting("Editing Enabled", editingRules.editingEnabled ? "Enabled" : "Disabled", editingRules.editingEnabled ? 'green' : 'red')}
                  {renderSetting("Cropping", editingRules.croppingEnabled ? "Enabled" : "Disabled", editingRules.croppingEnabled ? 'green' : 'red')}
                  {renderSetting("Saturation", editingRules.saturationEnabled ? "Enabled" : "Disabled", editingRules.saturationEnabled ? 'green' : 'red')}
                  {renderSetting("Add Text/Logo", editingRules.addTextOrLogoEnabled ? "Enabled" : "Disabled", editingRules.addTextOrLogoEnabled ? 'green' : 'red')}
                  {editingRules.addTextOrLogoEnabled && editingRules.allowedLogoSources && (
                    <div className="pt-2">
                      <h5 className="font-semibold mb-2 text-sm">Allowed Logo Sources</h5>
                      {renderSetting("Max Size (MB)", `${editingRules.allowedLogoSources.maxSizeMb} MB`)}
                      {renderSetting("Allowed Types", <div className="flex gap-1">{editingRules.allowedLogoSources.types.map((type: string) => <Badge key={type} variant="secondary">{type}</Badge>)}</div>)}
                    </div>
                  )}
                </div>
              )}
            </TabsContent>

            <TabsContent value="text-styles" className="pt-4">
              {textStyles && textStyles.length > 0 ? (
                <div className="space-y-4">
                  {textStyles.filter(ts => ts.is_active).map((styleSet: any) => (
                    <div key={styleSet.id} className="p-4 border rounded-lg">
                      <h5 className="font-bold text-lg mb-2">{styleSet.name}</h5>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {Object.entries(styleSet.styles).map(([key, value]: [string, any]) => (
                          <div key={key} className="p-3 bg-muted/50 rounded-md">
                            <p className="capitalize font-semibold text-base mb-2">{key}</p>
                            <p className="text-sm text-muted-foreground">{value.fontFamily}, {value.fontSize}px, {value.fontWeight}</p>
                            <div className="flex items-center mt-2">
                              <div className="w-4 h-4 rounded-full mr-2 border" style={{ backgroundColor: value.color }}></div>
                              <span className="text-sm font-mono">{value.color}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground text-center py-4">No active text style sets.</p>
              )}
            </TabsContent>

          </Tabs>
        )}
      </CardContent>
    </Card>
  )
}