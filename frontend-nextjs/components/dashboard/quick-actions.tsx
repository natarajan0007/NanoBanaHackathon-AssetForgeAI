"use client"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Upload, Zap, FileImage, Palette } from "lucide-react"
import { useRouter } from "next/navigation"

export function QuickActions() {
  const router = useRouter()

  const actions = [
    {
      title: "Upload New Asset",
      description: "Start a new project by uploading your master asset",
      icon: Upload,
      action: () => router.push("/projects/new"),
      primary: true,
    },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle>Quick Actions</CardTitle>
        <CardDescription>Get started with your creative workflow</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 gap-4">
          {actions.map((action, index) => (
            <Button
              key={index}
              variant={action.primary ? "default" : "outline"}
              className="h-auto p-4 flex flex-col items-start space-y-2"
              onClick={action.action}
            >
              <div className="flex items-center space-x-2">
                <action.icon className="h-5 w-5" />
                <span className="font-medium">{action.title}</span>
              </div>
              <span className="text-sm text-left opacity-80">{action.description}</span>
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
