'use client'

import { useState, useEffect, useMemo } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Checkbox } from "@/components/ui/checkbox"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ArrowLeft, Zap, FileImage, Layers, Pencil, Sparkles } from "lucide-react"
import { apiClient } from "@/lib/api-client"
import { useApi } from "@/lib/hooks/use-api"
import { Skeleton } from "@/components/ui/skeleton"
import Lightbox from "yet-another-react-lightbox";
import "yet-another-react-lightbox/styles.css";
import { cn } from "@/lib/utils"

// Interface for a single format object, matching the backend schema
interface ApiFormat {
  id: string;
  name: string;
  type: string;
  category: string | null;
  width: number;
  height: number;
}

// Interface for the API response which groups formats
interface FormatsApiResponse {
  resizing: ApiFormat[];
  repurposing: ApiFormat[];
}

interface AssetForPreview {
    id: string;
    previewUrl: string;
    metadata: any;
}

interface FormatSelectionProps {
  assets: AssetForPreview[];
  onFormatSelection: (formats: string[], prompt?: string) => void;
  onBack: () => void;
  editingRules: any;
}

export function FormatSelection({ assets, onFormatSelection, onBack, editingRules }: FormatSelectionProps) {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [selectedFormats, setSelectedFormats] = useState<string[]>([]);
  const [prompt, setPrompt] = useState("");
  const [promptSuggestions, setPromptSuggestions] = useState<string[]>([]);
  const [activeGroup, setActiveGroup] = useState<any[] | null>(null);
  const [lightboxIndex, setLightboxIndex] = useState(0);
  const { data: apiFormats, loading, error, execute: fetchFormats } = useApi<FormatsApiResponse>();
  const { data: generatedAssets, loading: loadingGenerated, execute: fetchGenerated } = useApi<any[]>();
  const { loading: loadingSuggestions, execute: fetchSuggestions } = useApi<string[]>();
  const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const currentAsset = assets?.[selectedIndex];

  useEffect(() => {
    fetchFormats(() => apiClient.getAvailableFormats());
  }, [fetchFormats]);

  useEffect(() => {
    if (currentAsset?.id) {
        fetchGenerated(() => apiClient.getGeneratedAssets(currentAsset.id));
        if (editingRules?.editingEnabled) {
            fetchSuggestions(() => apiClient.getPromptSuggestions(currentAsset.id)).then(res => {
                if(res.success) {
                    setPromptSuggestions(res.data || []);
                }
            });
        }
    }
  }, [currentAsset, fetchGenerated, editingRules, fetchSuggestions]);

  const allFormats = useMemo(() => {
    if (!apiFormats) return [];
    return [...apiFormats.resizing, ...apiFormats.repurposing];
  }, [apiFormats]);

  const groupedAssets = useMemo(() => {
    if (!generatedAssets) return {};
    return generatedAssets.reduce((acc, asset) => {
      const key = asset.formatName || 'Untitled';
      if (!acc[key]) {
        acc[key] = [];
      }
      acc[key].push(asset);
      return acc;
    }, {} as Record<string, any[]>);
  }, [generatedAssets]);

  const handleFormatToggle = (formatId: string) => {
    setSelectedFormats((prev) => (prev.includes(formatId) ? prev.filter((id) => id !== formatId) : [...prev, formatId]));
  };

  const handleGenerate = () => {
    if (selectedFormats.length > 0) {
      onFormatSelection(selectedFormats, prompt);
    }
  };

  const renderFormatCards = () => {
    if (loading) {
        return Array.from({ length: 6 }).map((_, i) => (
            <Card key={`skeleton-${i}`}><CardContent className="p-4"><Skeleton className="h-16 w-full"/></CardContent></Card>
        ));
    }
    if (error) {
        return <p className="text-destructive col-span-full">Error fetching formats: {error}</p>;
    }
    if (allFormats.length === 0) {
        return <p className="col-span-full">No formats have been configured by the administrator.</p>;
    }

    return allFormats.map((format) => (
      <Card
        key={format.id}
        className={`cursor-pointer transition-colors ${
          selectedFormats.includes(format.id) ? 'ring-2 ring-accent' : ''
        }`}
        onClick={() => handleFormatToggle(format.id)}
      >
        <CardContent className='p-4'>
          <div className='flex items-start space-x-3'>
            <Checkbox
              checked={selectedFormats.includes(format.id)}
              readOnly
            />
            <div className='flex-1'>
              <div className='flex items-center space-x-2 mb-1'>
                <Layers className='h-4 w-4 text-muted-foreground' />
                <h4 className='font-medium'>{format.name}</h4>
              </div>
              <p className='text-sm text-muted-foreground mb-1'>{`${format.width} x ${format.height}`}</p>
              <Badge variant='outline' className='text-xs'>
                {format.category || format.type}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    ));
  };

  const renderGeneratedAssets = () => {
    if (loadingGenerated) {
        return <div className="grid grid-cols-4 gap-4"><Skeleton className="h-32 w-full" /><Skeleton className="h-32 w-full" /><Skeleton className="h-32 w-full" /><Skeleton className="h-32 w-full" /></div>;
    }
    if (!generatedAssets || generatedAssets.length === 0) {
        return <p className="text-sm text-muted-foreground">No assets have been generated for this item yet.</p>;
    }
    return (
        <div className="space-y-4">
            {Object.entries(groupedAssets).map(([formatName, assets]) => (
                <div key={formatName}>
                    <h4 className="font-medium mb-2">{formatName}</h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                        {assets.map((genAsset: any, i: number) => (
                            <div key={genAsset.id} className="aspect-square bg-muted rounded-lg overflow-hidden cursor-pointer" onClick={() => { setActiveGroup(assets); setLightboxIndex(i); }}>
                                <img src={`${backendUrl}${genAsset.assetUrl}`} alt={genAsset.formatName} className="w-full h-full object-cover" />
                            </div>
                        ))}
                    </div>
                </div>
            ))}
        </div>
    );
  };

  return (
    <div className='space-y-6'>
      <div className='flex items-center space-x-4'>
        <Button variant='outline' size='sm' onClick={onBack}>
          <ArrowLeft className='h-4 w-4 mr-2' />
          Back
        </Button>
        <div>
          <h2 className='text-xl font-semibold text-foreground'>Select Formats</h2>
          <p className='text-muted-foreground'>Review your assets and choose which formats to generate</p>
        </div>
      </div>

      <div className='grid grid-cols-1 lg:grid-cols-3 gap-6'>
        {/* Asset Selection & Preview Column */}
        <div className="lg:col-span-1 space-y-4">
            <Card>
                <CardHeader>
                    <CardTitle>Asset Preview & Analysis</CardTitle>
                </CardHeader>
                <CardContent className='space-y-4'>
                    {currentAsset ? (
                    <>
                        <div className="aspect-video bg-muted rounded-lg overflow-hidden mb-4 cursor-pointer hover:ring-2 hover:ring-accent transition-all" onClick={() => { setActiveGroup([{ assetUrl: currentAsset.previewUrl }]); setLightboxIndex(0); }}>
                            <img 
                                src={`${backendUrl}${currentAsset.previewUrl}`}
                                alt="Asset preview"
                                className="w-full h-full object-contain"
                            />
                        </div>
                        <div>
                        <h4 className='font-medium mb-2'>Detected Elements</h4>
                        <div className='flex flex-wrap gap-1'>
                            {currentAsset.metadata?.detectedElements?.length > 0 ? (
                            currentAsset.metadata.detectedElements.map((element: string, index: number) => (
                                <Badge key={index} variant='secondary' className='text-xs'>
                                {element}
                                </Badge>
                            ))
                            ) : (
                            <p className="text-sm text-muted-foreground">No specific elements detected.</p>
                            )}
                        </div>
                        </div>
                    </>
                    ) : (
                        <p className="text-sm text-muted-foreground">Asset data is not available.</p>
                    )}
                </CardContent>
            </Card>
            <Card>
                <CardHeader>
                    <CardTitle>Uploaded Assets</CardTitle>
                </CardHeader>
                <CardContent className="grid grid-cols-3 gap-2">
                    {assets.map((asset, index) => (
                        <div 
                            key={asset.id} 
                            className={cn(
                                "aspect-square bg-muted rounded-md overflow-hidden cursor-pointer transition-all",
                                selectedIndex === index ? "ring-2 ring-accent ring-offset-2" : "hover:ring-2 hover:ring-accent/50"
                            )}
                            onClick={() => setSelectedIndex(index)}
                        >
                            <img src={`${backendUrl}${asset.previewUrl}`} alt={`Asset ${index + 1}`} className="w-full h-full object-cover" />
                        </div>
                    ))}
                </CardContent>
            </Card>
        </div>

        {/* Format Selection Column */}
        <div className='lg:col-span-2 space-y-4'>
          <div className='flex items-center justify-between'>
            <h3 className='text-lg font-medium'>Available Formats</h3>
          </div>
          <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
            {renderFormatCards()}
          </div>
          
          {editingRules?.editingEnabled && (
            <div className="pt-4 space-y-3">
                <div>
                    <Label htmlFor="prompt" className="flex items-center mb-2">
                        <Pencil className="w-4 h-4 mr-2"/>
                        Manual Editing Prompt (Optional)
                    </Label>
                    <Input 
                        id="prompt"
                        placeholder="e.g., 'Make the background blue', 'Add a sun to the sky'"
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                    />
                </div>
                <div>
                    <Label className="flex items-center mb-2">
                        <Sparkles className="w-4 h-4 mr-2"/>
                        Prompt Suggestions
                    </Label>
                    {loadingSuggestions ? (
                        <div className="flex flex-wrap gap-2"><Skeleton className="h-6 w-24"/><Skeleton className="h-6 w-32"/><Skeleton className="h-6 w-28"/></div>
                    ) : (
                        <div className="flex flex-wrap gap-2">
                            {promptSuggestions.length > 0 ? (
                                promptSuggestions.map((suggestion, i) => (
                                    <Badge key={i} variant="outline" className="cursor-pointer hover:bg-accent" onClick={() => setPrompt(suggestion)}>{suggestion}</Badge>
                                ))
                            ) : (
                                <p className="text-xs text-muted-foreground">No suggestions available for this asset.</p>
                            )}
                        </div>
                    )}
                </div>
            </div>
          )}

          <div className='flex items-center justify-between pt-4'>
            <p className='text-sm text-muted-foreground'>
              {selectedFormats.length} format{selectedFormats.length !== 1 ? 's' : ''} selected
            </p>
            <Button onClick={handleGenerate} disabled={selectedFormats.length === 0} size='lg'>
              <Zap className='h-4 w-4 mr-2' />
              Generate Assets ({selectedFormats.length})
            </Button>
          </div>
        </div>
      </div>

      {/* Previously Generated Assets Section */}
      <div className="mt-8">
        <Card>
          <CardHeader>
            <CardTitle>Previously Generated Assets for {currentAsset?.filename || "Selected Asset"}</CardTitle>
          </CardHeader>
          <CardContent>
            {renderGeneratedAssets()}
          </CardContent>
        </Card>
      </div>

      {activeGroup && (
        <Lightbox
            open={!!activeGroup}
            close={() => setActiveGroup(null)}
            slides={activeGroup.map(asset => ({ src: `${backendUrl}${asset.assetUrl || asset.previewUrl}` }))}
            index={lightboxIndex}
        />
      )}
    </div>
  )
}

