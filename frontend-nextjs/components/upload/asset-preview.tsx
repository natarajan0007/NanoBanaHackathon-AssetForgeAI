"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ArrowLeft, Zap, FileImage, Palette } from "lucide-react"

interface AssetPreviewProps {
  file: { file: File; preview: string } | null
  onStartProcessing: () => void
  onBack: () => void
}

export function AssetPreview({ file, onStartProcessing, onBack }: AssetPreviewProps) {
  if (!file) return null

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes"
    const k = 1024
    const sizes = ["Bytes", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i]
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center space-x-4">
        <Button variant="outline" size="sm" onClick={onBack}>
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>
        <div>
          <h2 className="text-xl font-semibold text-foreground">Preview Your Asset</h2>
          <p className="text-muted-foreground">Review your upload before AI processing</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Asset Preview */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <FileImage className="h-5 w-5" />
              <span>Asset Preview</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="aspect-video bg-muted rounded-lg overflow-hidden mb-4">
              <img
                src={file.preview || "/placeholder.svg"}
                alt="Asset preview"
                className="w-full h-full object-contain"
              />
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Filename:</span>
                <span className="font-medium">{file.file.name}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">File size:</span>
                <span className="font-medium">{formatFileSize(file.file.size)}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Type:</span>
                <Badge variant="outline">{file.file.type}</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Processing Options */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Zap className="h-5 w-5" />
              <span>AI Processing</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-muted-foreground">
              Our AI will analyze your asset and automatically generate optimized versions for different platforms and
              use cases.
            </p>

            <div className="space-y-3">
              <div className="flex items-center space-x-3">
                <div className="rounded-full bg-blue-100 dark:bg-blue-900 p-2">
                  <Palette className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                </div>
                <div>
                  <h4 className="font-medium">Color Analysis</h4>
                  <p className="text-sm text-muted-foreground">Extract brand colors and themes</p>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <div className="rounded-full bg-green-100 dark:bg-green-900 p-2">
                  <FileImage className="h-4 w-4 text-green-600 dark:text-green-400" />
                </div>
                <div>
                  <h4 className="font-medium">Element Detection</h4>
                  <p className="text-sm text-muted-foreground">Identify logos, text, and key elements</p>
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <div className="rounded-full bg-purple-100 dark:bg-purple-900 p-2">
                  <Zap className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                </div>
                <div>
                  <h4 className="font-medium">Format Optimization</h4>
                  <p className="text-sm text-muted-foreground">Suggest optimal formats and sizes</p>
                </div>
              </div>
            </div>

            <Button onClick={onStartProcessing} className="w-full" size="lg">
              <Zap className="h-4 w-4 mr-2" />
              Start AI Processing
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
